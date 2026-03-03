#!/usr/bin/env python3
"""
calibre_sync.py — Sync books from Calibre-Web to Jekyll _reading/ collection.

Authenticates with Calibre-Web, discovers shelves named read-YYYY, reading,
and to-read, then creates Markdown files in _reading/ for each book.

Existing files are never overwritten, so manual edits (ratings, notes) are safe.

Required environment variables:
    CALIBRE_WEB_URL   Base URL of your Calibre-Web instance (no trailing slash)
    CALIBRE_WEB_USER  Username
    CALIBRE_WEB_PASS  Password
"""

import os
import re
import sys
import logging
from datetime import date
from pathlib import Path

import requests
from bs4 import BeautifulSoup

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_URL = os.environ.get("CALIBRE_WEB_URL", "").rstrip("/")
USERNAME = os.environ.get("CALIBRE_WEB_USER", "")
PASSWORD = os.environ.get("CALIBRE_WEB_PASS", "")

SCRIPT_DIR = Path(__file__).parent
OUTPUT_DIR = SCRIPT_DIR.parent / "_reading"
TODAY = date.today().isoformat()

FINISHED_RE = re.compile(r"^alevtina-(\d{4})$", re.IGNORECASE)
STATUS_SHELVES = {"alevtina-reading", "alevtina-tbr"}

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str) -> str:
    """Convert a string to a URL-friendly slug."""
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"^-|-$", "", text)
    return text or "untitled"


def shelf_to_status(shelf_name: str) -> tuple[str, str | None]:
    """
    Map a Calibre shelf name to an (IndieWeb status, year) tuple.

    read-YYYY  → ("finished", "YYYY")
    reading    → ("reading",  None)
    to-read    → ("to-read",  None)
    anything else → ("unknown", None)
    """
    m = FINISHED_RE.match(shelf_name)
    if m:
        return "finished", m.group(1)
    if shelf_name.lower() == "alevtina-reading":
        return "reading", None
    if shelf_name.lower() == "alevtina-tbr":
        return "to-read", None
    return "unknown", None


def make_date(status: str, year: str | None) -> str:
    """
    Return the front matter date string for a book entry.

    For finished books the shelf name encodes the year; we use YYYY-01-01
    as a placeholder that you can correct manually.  For in-progress shelves
    we use today so new additions appear at the top of the index.
    """
    if status == "finished" and year:
        return f"{year}-01-01"
    return TODAY


def yaml_str(value: str) -> str:
    """Wrap a value in double-quoted YAML string, escaping inner quotes."""
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def format_author_yaml(authors: list[str]) -> str:
    """Render the author field as a YAML scalar or sequence."""
    if not authors:
        return 'author: ""'
    if len(authors) == 1:
        return f"author: {yaml_str(authors[0])}"
    lines = "\n".join(f"  - {yaml_str(a)}" for a in authors)
    return f"author:\n{lines}"


# ---------------------------------------------------------------------------
# Calibre-Web session
# ---------------------------------------------------------------------------

def get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": "calibre-jekyll-sync/1.0 (jekyll reading log)"})
    return s


def login(session: requests.Session) -> None:
    """
    Authenticate with Calibre-Web.

    Fetches the login page to extract the CSRF token (Flask-WTF style),
    then POSTs credentials.  Raises RuntimeError on failure.
    """
    login_url = f"{BASE_URL}/login"
    log.info("Fetching login page: %s", login_url)

    resp = session.get(login_url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # CSRF token — Calibre-Web uses Flask-WTF hidden input
    csrf_token = ""
    csrf_input = soup.find("input", {"name": "csrf_token"})
    if csrf_input:
        csrf_token = csrf_input.get("value", "")
    else:
        # Some builds expose it as a meta tag instead
        csrf_meta = soup.find("meta", {"name": "csrf-token"})
        if csrf_meta:
            csrf_token = csrf_meta.get("content", "")
        else:
            log.warning("No CSRF token found on login page; proceeding without it")

    payload = {
        "username": USERNAME,
        "password": PASSWORD,
        "csrf_token": csrf_token,
        "remember_me": "on",
    }
    log.info("Logging in as %s", USERNAME)
    resp = session.post(login_url, data=payload, timeout=30, allow_redirects=True)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    # Verify success: look for a logout link anywhere in the page
    logout = (
        soup.find("a", href=re.compile(r"/logout", re.I))
        or soup.find("a", string=re.compile(r"logout|sign.?out", re.I))
    )
    if logout:
        log.info("Login successful")
        return

    # Check for an explicit error message
    error_el = soup.find(class_=re.compile(r"\b(alert|error|flash)\b", re.I))
    if error_el:
        raise RuntimeError(f"Login failed: {error_el.get_text(strip=True)}")

    # If we were redirected back to /login, credentials were wrong
    if "/login" in resp.url:
        raise RuntimeError(
            "Login failed — still on the login page. "
            "Check CALIBRE_WEB_USER and CALIBRE_WEB_PASS."
        )

    log.warning(
        "Could not confirm login via a logout link, but not on the login page either. "
        "Proceeding; subsequent requests will reveal any auth problems."
    )


def discover_shelves(session: requests.Session) -> dict[str, int]:
    """
    Return {shelf_name: shelf_id} for every shelf we care about.

    Matches shelves named read-YYYY, reading, and to-read.
    """
    url = f"{BASE_URL}/shelf/list"
    log.info("Fetching shelf list: %s", url)

    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    # Shelf links look like /shelf/<id> or /shelf/<id>/0
    shelf_links = soup.find_all("a", href=re.compile(r"/shelf/\d+"))
    if not shelf_links:
        raise RuntimeError(
            f"No shelf links found at {url}. "
            "The page structure may have changed, or authentication failed."
        )

    shelves: dict[str, int] = {}
    seen_ids: set[int] = set()

    for link in shelf_links:
        href = link.get("href", "")
        m = re.search(r"/shelf/(\d+)", href)
        if not m:
            continue
        shelf_id = int(m.group(1))
        if shelf_id in seen_ids:
            continue
        seen_ids.add(shelf_id)

        # Shelf name is the link text; child elements may hold it
        name_el = link.find(class_=re.compile(r"shelf.?name|name", re.I)) or link
        name = name_el.get_text(strip=True)
        if not name:
            continue

        status, _ = shelf_to_status(name)
        if status != "unknown":
            shelves[name] = shelf_id
            log.info("  Found shelf %r → id=%d (status: %s)", name, shelf_id, status)

    if not shelves:
        log.warning(
            "No matching shelves found. "
            "Expected shelf names like 'alevtina-2024', 'alevtina-reading', 'alevtina-tbr'."
        )
    return shelves


def get_shelf_book_ids(session: requests.Session, shelf_id: int, shelf_name: str) -> list[int]:
    """
    Return all Calibre book IDs on the given shelf, handling pagination.

    Calibre-Web paginates shelves at /shelf/<id>/<offset>.
    """
    book_ids: list[int] = []
    offset = 0

    while True:
        # Try offset-in-path style first (common in newer builds)
        url = f"{BASE_URL}/shelf/{shelf_id}/{offset}" if offset > 0 else f"{BASE_URL}/shelf/{shelf_id}"
        log.info("  Fetching shelf page: %s", url)

        resp = session.get(url, timeout=30)
        if resp.status_code == 404 and offset > 0:
            break
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "html.parser")
        book_links = soup.find_all("a", href=re.compile(r"/book/\d+"))

        if not book_links:
            if offset == 0:
                log.warning("  No book links found on shelf %r (id=%d)", shelf_name, shelf_id)
            break

        page_ids: list[int] = []
        seen_on_page: set[int] = set()
        for link in book_links:
            m = re.search(r"/book/(\d+)", link.get("href", ""))
            if m:
                bid = int(m.group(1))
                if bid not in seen_on_page:
                    seen_on_page.add(bid)
                    page_ids.append(bid)

        book_ids.extend(page_ids)

        # Continue paginating if there might be more
        next_link = soup.find("a", string=re.compile(r"next|»|›", re.I)) or soup.find("a", rel="next")
        if next_link and len(page_ids) >= 10:
            offset += len(page_ids)
        else:
            break

    return book_ids


def get_book_metadata(session: requests.Session, book_id: int) -> dict:
    """
    Scrape the book detail page and return a metadata dict.

    Keys: title, authors, isbn, series, series_part, cover, tags, calibre_id.
    Raises RuntimeError with a clear message when required fields are missing.
    """
    url = f"{BASE_URL}/book/{book_id}"
    log.info("  Fetching book %d: %s", book_id, url)

    resp = session.get(url, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    meta: dict = {"calibre_id": book_id, "authors": [], "tags": []}

    # -- Title ----------------------------------------------------------------
    # Calibre-Web renders the title in an <h2> or an element with class "book-title"
    title_el = (
        soup.find(class_=re.compile(r"book.?title", re.I))
        or soup.find("h2")
        or soup.find("h1")
    )
    if not title_el:
        raise RuntimeError(
            f"Could not find a title element for book {book_id} ({url}). "
            "Page structure may have changed."
        )
    meta["title"] = title_el.get_text(strip=True)
    if not meta["title"]:
        raise RuntimeError(f"Title element was empty for book {book_id} ({url}).")

    # -- Authors --------------------------------------------------------------
    author_links = soup.find_all("a", href=re.compile(r"/author/\d+", re.I))
    if author_links:
        meta["authors"] = list(
            dict.fromkeys(a.get_text(strip=True) for a in author_links if a.get_text(strip=True))
        )
    else:
        author_el = soup.find(class_=re.compile(r"\bauthor\b", re.I))
        if author_el:
            meta["authors"] = [author_el.get_text(strip=True)]
        else:
            log.warning("  No authors found for book %d (%s)", book_id, meta["title"])

    # -- Cover ----------------------------------------------------------------
    cover_img = (
        soup.find("img", class_=re.compile(r"cover|book.?img", re.I))
        or soup.find("img", src=re.compile(r"/cover/\d+", re.I))
    )
    if not cover_img:
        # Try inside a div with class "cover"
        cover_div = soup.find(class_=re.compile(r"\bcover\b", re.I))
        if cover_div:
            cover_img = cover_div.find("img")

    if cover_img and cover_img.name == "img":
        src = cover_img.get("src", "")
        meta["cover"] = (BASE_URL + src) if src.startswith("/") else src
    else:
        meta["cover"] = ""
        log.warning("  No cover image found for book %d (%s)", book_id, meta["title"])

    # -- Structured metadata (ISBN, series, tags) -----------------------------
    _extract_metadata(soup, meta, book_id, url)

    return meta


def _extract_metadata(soup: BeautifulSoup, meta: dict, book_id: int, url: str) -> None:
    """
    Extract ISBN, series, series_part, and tags from the book detail page.

    Tries three layout strategies in order: <dl>, <table>, and labeled <div>
    pairs.  Falls back to full-text regex search for ISBN if nothing else works.
    """
    # Strategy 1: definition list (dt/dd)
    dl = soup.find("dl")
    if dl:
        for dt, dd in zip(dl.find_all("dt"), dl.find_all("dd")):
            _assign_field(meta, dt.get_text(strip=True).lower().rstrip(":"), dd.get_text(strip=True), dd)
        return

    # Strategy 2: table rows
    for table in soup.find_all("table"):
        rows = table.find_all("tr")
        for row in rows:
            cells = row.find_all(["th", "td"])
            if len(cells) >= 2:
                _assign_field(meta, cells[0].get_text(strip=True).lower().rstrip(":"), cells[1].get_text(strip=True), cells[1])
        if "isbn" in meta or "series" in meta or meta.get("tags"):
            return

    # Strategy 3: labeled div pairs (Calibre-Web 0.6+)
    for label_el in soup.find_all(class_=re.compile(r"book.?meta|detail.?label|field.?label", re.I)):
        key = label_el.get_text(strip=True).lower().rstrip(":")
        val_el = label_el.find_next_sibling()
        if val_el:
            _assign_field(meta, key, val_el.get_text(strip=True), val_el)

    # Fallback: scan full page text for ISBN-13/10
    if "isbn" not in meta:
        page_text = soup.get_text()
        isbn_match = re.search(r"\b(97[89]\d{10}|\d{9}[\dX])\b", page_text)
        if isbn_match:
            candidate = isbn_match.group(0)
            if re.match(r"^(978|979)\d{10}$", candidate) or re.match(r"^\d{9}[\dX]$", candidate):
                meta["isbn"] = candidate
                log.info("  ISBN found via text scan for book %d: %s", book_id, candidate)

    # Fallback: tag links
    if not meta.get("tags"):
        tag_links = soup.find_all("a", href=re.compile(r"/(tags?|categories)/", re.I))
        if tag_links:
            meta["tags"] = list(
                dict.fromkeys(t.get_text(strip=True) for t in tag_links if t.get_text(strip=True))
            )


def _assign_field(meta: dict, key: str, val: str, el) -> None:
    """Map a raw key/value pair from the page into the metadata dict."""
    if not val:
        return

    if "isbn" in key:
        isbn = re.sub(r"[\s\-]", "", val)
        if re.match(r"^(978|979)\d{10}$", isbn) or re.match(r"^\d{9}[\dX]$", isbn):
            meta["isbn"] = isbn

    elif "series" in key and "series_part" not in key:
        # Calibre-Web may include the index in the same field: "Series Name [3]"
        m = re.match(r"^(.+?)\s*[\[#(]\s*(\d+(?:\.\d+)?)\s*[\])]?\s*$", val)
        if m:
            meta.setdefault("series", m.group(1).strip())
            try:
                meta.setdefault("series_part", int(float(m.group(2))))
            except ValueError:
                meta.setdefault("series_part", m.group(2))
        else:
            meta.setdefault("series", val)

    elif re.search(r"\b(part|volume|index|number)\b", key):
        if "series" in meta and "series_part" not in meta:
            try:
                meta["series_part"] = int(float(val))
            except ValueError:
                pass

    elif re.search(r"\b(tags?|categor|genre)\b", key):
        if el:
            tag_links = el.find_all("a")
            if tag_links:
                meta["tags"] = [t.get_text(strip=True) for t in tag_links if t.get_text(strip=True)]
            elif val:
                meta["tags"] = [t.strip() for t in re.split(r"[,;]", val) if t.strip()]


# ---------------------------------------------------------------------------
# File creation
# ---------------------------------------------------------------------------

def build_front_matter(meta: dict, status: str, entry_date: str) -> str:
    """Return the complete YAML front matter block for a _reading/ entry."""
    authors = meta.get("authors", [])
    author_line = format_author_yaml(authors)

    isbn = meta.get("isbn", "")
    series = meta.get("series", "")
    series_part = meta.get("series_part", "")
    cover = meta.get("cover", "")
    tags = meta.get("tags", [])
    calibre_id = meta.get("calibre_id", "")

    isbn_line = f"isbn: {yaml_str(isbn)}" if isbn else "isbn:"
    series_line = f"series: {yaml_str(series)}" if series else "series:"
    series_part_line = f"series_part: {series_part}" if series_part != "" else "series_part:"
    cover_line = f"cover: {yaml_str(cover)}" if cover else "cover:"
    tags_line = "[" + ", ".join(yaml_str(t) for t in tags) + "]" if tags else "[]"

    return f"""\
---
layout: read
title: {yaml_str(meta['title'])}
{author_line}
{isbn_line}
{series_line}
{series_part_line}
{cover_line}
status: {status}
date: {entry_date}
rating:
tags: {tags_line}
calibre_id: {calibre_id}
---
"""


def write_entry(meta: dict, status: str, entry_date: str, output_dir: Path) -> bool:
    """
    Write a _reading/ Markdown file for one book.

    Returns True if a new file was created, False if the file already existed
    (existing files are never overwritten to preserve manual edits).
    """
    slug = slugify(meta["title"])
    filepath = output_dir / f"{entry_date}-{slug}.md"

    if filepath.exists():
        log.info("  Skipping existing file: %s", filepath.name)
        return False

    filepath.write_text(build_front_matter(meta, status, entry_date), encoding="utf-8")
    log.info("  Created: %s", filepath.name)
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    # Validate required environment variables
    missing = [v for v in ("CALIBRE_WEB_URL", "CALIBRE_WEB_USER", "CALIBRE_WEB_PASS") if not os.environ.get(v)]
    if missing:
        for v in missing:
            log.error("Required environment variable %s is not set.", v)
        sys.exit(1)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    session = get_session()

    try:
        login(session)
    except Exception as exc:
        log.error("Authentication failed: %s", exc)
        sys.exit(1)

    try:
        shelves = discover_shelves(session)
    except Exception as exc:
        log.error("Failed to discover shelves: %s", exc)
        sys.exit(1)

    if not shelves:
        log.info("No matching shelves — nothing to sync.")
        sys.exit(0)

    created = skipped = errors = 0

    for shelf_name, shelf_id in shelves.items():
        status, year = shelf_to_status(shelf_name)
        entry_date = make_date(status, year)
        log.info("Processing shelf %r → status=%s, date=%s", shelf_name, status, entry_date)

        try:
            book_ids = get_shelf_book_ids(session, shelf_id, shelf_name)
        except Exception as exc:
            log.error("Failed to list books on shelf %r: %s", shelf_name, exc)
            errors += 1
            continue

        log.info("  %d book(s) on shelf %r", len(book_ids), shelf_name)

        for book_id in book_ids:
            try:
                meta = get_book_metadata(session, book_id)
                if write_entry(meta, status, entry_date, OUTPUT_DIR):
                    created += 1
                else:
                    skipped += 1
            except Exception as exc:
                log.error("  Error processing book %d: %s", book_id, exc)
                errors += 1

    log.info("Done — %d created, %d skipped (already exist), %d errors", created, skipped, errors)

    # Exit non-zero only if every book failed (likely an auth or structural issue)
    if errors > 0 and created == 0 and skipped == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
