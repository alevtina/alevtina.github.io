#!/usr/bin/env python3
"""
sync.py — Sync books from Calibre-Web to Jekyll _reading/ collection.

Authenticates with Calibre-Web, discovers shelves named {prefix}-YYYY,
{prefix}-reading, and {prefix}-tbr (where prefix defaults to your username),
then creates Markdown files in the
Jekyll _reading/ directory for each book. After writing new files,
commits and pushes the Jekyll repo automatically.

Existing files are never overwritten, so manual edits (ratings, notes) are safe.

Required environment variables:
    CALIBRE_WEB_URL      Base URL of your Calibre-Web instance (no trailing slash)
    CALIBRE_WEB_USER     Username
    CALIBRE_WEB_PASS     Password
    JEKYLL_READING_DIR   Absolute path to the _reading/ directory in your Jekyll repo
    JEKYLL_REPO_DIR      Absolute path to the root of your Jekyll repo (for git)

Optional:
    SHELF_PREFIX         Shelf name prefix (defaults to CALIBRE_WEB_USER).
                         Override if your shelves use a different prefix than your username.
    PRUNE_REMOVED        Set to "true" to delete _reading/ files for books no longer
                         on any shelf (equivalent to passing --prune on the command line).
                         Default: files are kept as-is and a warning is logged.
    REFRESH_METADATA     Set to "true" to re-fetch and update Calibre-owned metadata fields
                         (title, author, ISBN, cover, series, tags, etc.) in existing files
                         (equivalent to passing --refresh on the command line).
                         Preserves rating, date, status, and any body content.
                         Default: existing files are never modified for metadata changes.
"""

import argparse
import os
import re
import subprocess
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

OUTPUT_DIR = Path(os.environ.get("JEKYLL_READING_DIR", "")).expanduser()
JEKYLL_REPO_DIR = Path(os.environ.get("JEKYLL_REPO_DIR", "")).expanduser()

# Shelf prefix: defaults to the Calibre-Web username.
# Override with SHELF_PREFIX if your shelf names use a different prefix.
SHELF_PREFIX = os.environ.get("SHELF_PREFIX", USERNAME).lower()
FINISHED_RE = re.compile(rf"^{re.escape(SHELF_PREFIX)}-(\d{{4}})$", re.IGNORECASE)
STATUS_SHELVES = {f"{SHELF_PREFIX}-reading", f"{SHELF_PREFIX}-tbr"}

TODAY = date.today().isoformat()

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


def title_slug(title: str) -> str:
    """Slugify only the main title — everything before the first colon.

    "Dune: Messiah" → "dune", not "dune-messiah".
    Falls back to the full title if there is no colon or the part before it is empty.
    """
    main = title.split(":", 1)[0].strip()
    return slugify(main or title)


def shelf_to_status(shelf_name: str) -> tuple[str, str | None]:
    """
    Map a Calibre shelf name to an (IndieWeb status, year) tuple.

    {prefix}-YYYY    → ("finished", "YYYY")
    {prefix}-reading → ("reading",  None)
    {prefix}-tbr     → ("to-read",  None)
    anything else       → ("unknown", None)
    """
    m = FINISHED_RE.match(shelf_name)
    if m:
        return "finished", m.group(1)
    if shelf_name.lower() == f"{SHELF_PREFIX}-reading":
        return "reading", None
    if shelf_name.lower() == f"{SHELF_PREFIX}-tbr":
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
# Cover image resolution
# ---------------------------------------------------------------------------

def fetch_public_cover(isbn: str, title: str = "", authors: list | None = None) -> str:
    """
    Return the best publicly-accessible cover URL for a book, or "" if none found.

    1. OpenLibrary covers API by ISBN (fast HEAD probe; ?default=false → 404 = no cover)
    2. OpenLibrary search API by ISBN → cover by internal ID (broader catalog coverage)
    3. OpenLibrary search API by title + first author (catches alternate-edition ISBNs)
    """
    if isbn:
        # 1. OpenLibrary direct ISBN cover
        ol_check = f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg?default=false"
        try:
            r = requests.head(ol_check, timeout=8, allow_redirects=True)
            if r.status_code == 200:
                log.info("  Cover: OpenLibrary (ISBN) for %s", isbn)
                return f"https://covers.openlibrary.org/b/isbn/{isbn}-L.jpg"
        except Exception:
            pass

        # 2. OpenLibrary search API by ISBN → cover by internal numeric ID
        try:
            r = requests.get(
                f"https://openlibrary.org/search.json?isbn={isbn}&fields=cover_i",
                timeout=10,
            )
            if r.status_code == 200:
                docs = r.json().get("docs", [])
                if docs and docs[0].get("cover_i"):
                    cover_id = docs[0]["cover_i"]
                    log.info("  Cover: OpenLibrary (cover_i=%s) for ISBN %s", cover_id, isbn)
                    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        except Exception:
            pass

    # 3. OpenLibrary title + author search (finds covers on alternate editions)
    if title and authors:
        import urllib.parse
        first_author = authors[0] if authors else ""
        params = urllib.parse.urlencode({"title": title, "author": first_author, "fields": "cover_i", "limit": "1"})
        try:
            r = requests.get(f"https://openlibrary.org/search.json?{params}", timeout=10)
            if r.status_code == 200:
                docs = r.json().get("docs", [])
                if docs and docs[0].get("cover_i"):
                    cover_id = docs[0]["cover_i"]
                    log.info("  Cover: OpenLibrary (title search, cover_i=%s) for %r", cover_id, title)
                    return f"https://covers.openlibrary.org/b/id/{cover_id}-L.jpg"
        except Exception:
            pass

    if isbn:
        log.warning("  Cover: no public cover found for ISBN %s", isbn)
    return ""


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

    Tries /shelf/list first; falls back to the home page if that returns 404
    (some Calibre-Web builds expose shelf links only on the home page).
    Matches shelves named {prefix}-YYYY, {prefix}-reading, and {prefix}-tbr.
    """
    candidates = [f"{BASE_URL}/shelf/list", BASE_URL + "/"]
    soup = None

    for url in candidates:
        log.info("Fetching shelf list: %s", url)
        resp = session.get(url, timeout=30)
        if resp.status_code == 404:
            log.info("  %s returned 404, trying next location", url)
            continue
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")
        if soup.find_all("a", href=re.compile(r"/shelf/\d+")):
            break  # found shelf links
        soup = None

    if soup is None:
        raise RuntimeError(
            "No shelf links found at /shelf/list or /. "
            "The page structure may have changed, or authentication failed."
        )

    shelves: dict[str, int] = {}
    seen_ids: set[int] = set()

    for link in soup.find_all("a", href=re.compile(r"/shelf/\d+")):
        href = link.get("href", "")
        m = re.search(r"/shelf/(\d+)", href)
        if not m:
            continue
        shelf_id = int(m.group(1))
        if shelf_id in seen_ids:
            continue
        seen_ids.add(shelf_id)

        # Shelf name is the link text; child elements may hold it.
        # Calibre-Web may append a count badge without whitespace (e.g. "alice-20251").
        # Try the raw text and then versions with 1–3 trailing digits stripped until
        # we find a name that matches a known pattern.
        name_el = link.find(class_=re.compile(r"shelf.?name|name", re.I)) or link
        raw_name = name_el.get_text(strip=True)

        name = None
        for n in range(4):
            candidate = raw_name[:-n] if n > 0 else raw_name
            if not candidate:
                break
            s, _ = shelf_to_status(candidate)
            if s != "unknown":
                name = candidate
                break
        if not name:
            continue

        status, _ = shelf_to_status(name)
        shelves[name] = shelf_id
        log.info("  Found shelf %r → id=%d (status: %s)", name, shelf_id, status)

    if not shelves:
        log.warning(
            "No matching shelves found. "
            f"Expected shelf names like '{SHELF_PREFIX}-2024', '{SHELF_PREFIX}-reading', '{SHELF_PREFIX}-tbr'."
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
        meta["_calibre_cover"] = (BASE_URL + src) if src.startswith("/") else src
    else:
        meta["_calibre_cover"] = ""
        log.warning("  No cover image found for book %d (%s)", book_id, meta["title"])

    # -- Publication year -----------------------------------------------------
    pub_div = soup.find(class_="publishing-date")
    if pub_div:
        m = re.search(r"\b(\d{4})\b", pub_div.get_text())
        if m:
            meta["year"] = m.group(1)

    # -- Structured metadata (ISBN, series, tags) -----------------------------
    _extract_metadata(soup, meta, book_id, url)

    # -- Resolve best public cover URL ----------------------------------------
    meta.pop("_calibre_cover", None)
    meta["cover"] = fetch_public_cover(meta.get("isbn", ""), meta.get("title", ""), meta.get("authors", []))

    return meta


def _extract_metadata(soup: BeautifulSoup, meta: dict, book_id: int, url: str) -> None:
    """
    Extract ISBN, series, series_part, and tags from the book detail page.

    Tries three layout strategies in order: <dl>, <table>, and labeled <div>
    pairs.  Falls back to full-text regex search for ISBN if nothing else works.
    """
    # Series links — Calibre-Web renders series as an <a href="/series/..."> link
    # in the book description area, separate from the DL/table metadata block.
    # Extract this first so the early-return strategies below don't skip it.
    series_link = soup.find("a", href=re.compile(r"/series/", re.I))
    if series_link and "series" not in meta:
        text = series_link.get_text(strip=True)
        m = re.match(r"^(.+?)\s*[\[#(]\s*(\d+(?:\.\d+)?)\s*[\])]?\s*$", text)
        if m:
            meta["series"] = m.group(1).strip()
            try:
                meta["series_part"] = int(float(m.group(2)))
            except ValueError:
                meta["series_part"] = m.group(2)
        elif text:
            meta["series"] = text
            # Index might be in surrounding text, in several formats:
            #   "My Series [2]" / "My Series (2)" / "My Series #2" (number after name)
            #   "Book 2 of My Series" (Calibre-Web modal format, number before name)
            parent_text = series_link.parent.get_text(strip=True) if series_link.parent else ""
            idx = re.search(r"[\[#(]\s*(\d+(?:\.\d+)?)\s*[\])]?", parent_text)
            if not idx:
                idx = re.search(r"book\s+(\d+(?:\.\d+)?)\s+of", parent_text, re.IGNORECASE)
            if idx:
                try:
                    meta["series_part"] = int(float(idx.group(1)))
                except ValueError:
                    meta["series_part"] = idx.group(1)
        if meta.get("series"):
            log.info("  Series: %r [%s] for book %d", meta["series"], meta.get("series_part", "?"), book_id)

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

    # Strategy 4: Calibre-Web identifiers div.
    # Custom identifier types (eISBN, etc.) store the raw value as the href:
    #   <a href="9780593716724">EbookISBN</a>
    # The standard "isbn" type links to a lookup service, ISBN only in the URL:
    #   <a href="https://www.worldcat.org/isbn/9780593716724">ISBN</a>
    # So we search for an ISBN pattern in both the href and the link text.
    ISBN_RE = re.compile(r"(97[89]\d{10}|\d{9}[\dX])")
    if "isbn" not in meta:
        id_div = soup.find(class_="identifiers")
        if id_div:
            for a in id_div.find_all("a"):
                for source in (a.get("href", ""), a.get_text(strip=True)):
                    candidate = re.sub(r"[\s\-]", "", source)
                    m = ISBN_RE.search(candidate)
                    if m:
                        meta["isbn"] = m.group(1)
                        log.info("  ISBN found in identifiers div for book %d: %s", book_id, m.group(1))
                        break
                if "isbn" in meta:
                    break

    # Fallback: scan full page text for ISBN-13/10
    if "isbn" not in meta:
        page_text = soup.get_text()
        isbn_match = re.search(r"\b(97[89]\d{10}|\d{9}[\dX])\b", page_text)
        if isbn_match:
            candidate = isbn_match.group(0)
            if re.match(r"^(978|979)\d{10}$", candidate) or re.match(r"^\d{9}[\dX]$", candidate):
                meta["isbn"] = candidate
                log.info("  ISBN found via text scan for book %d: %s", book_id, candidate)

    # Fallback: series index — if we have the series name but not the position,
    # scan the full page text for the number in any common format:
    #   "Book 3 of Part of Your World"  (Calibre-Web modal: number BEFORE name)
    #   "Part of Your World [3]" / "(3)" / "#3"  (number AFTER name)
    if meta.get("series") and "series_part" not in meta:
        page_text_for_series = soup.get_text()
        series_escaped = re.escape(meta["series"])
        idx_match = (
            re.search(rf"book\s+(\d+(?:\.\d+)?)\s+of\s+{series_escaped}", page_text_for_series, re.IGNORECASE)
            or re.search(rf"{series_escaped}\s*[\[#\-(,]?\s*(?:book\s+)?(\d+(?:\.\d+)?)", page_text_for_series, re.IGNORECASE)
        )
        if idx_match:
            try:
                meta["series_part"] = int(float(idx_match.group(1)))
                log.info("  Series index found via page text scan for book %d: %s", book_id, meta["series_part"])
            except ValueError:
                pass

    # Fallback: tag links (Calibre-Web uses /category/ paths for tags)
    if not meta.get("tags"):
        tag_links = soup.find_all("a", href=re.compile(r"/(tags?|categor)[^/]*/stored/", re.I))
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
        if re.search(r"\bid\b", key):
            # "Series ID" → the book's numeric position within the series
            if "series" in meta:
                try:
                    meta.setdefault("series_part", int(float(val)))
                except ValueError:
                    pass
        else:
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
    year = meta.get("year", "")
    series = meta.get("series", "")
    series_part = meta.get("series_part", "")
    cover = meta.get("cover", "")
    tags = meta.get("tags", [])
    calibre_id = meta.get("calibre_id", "")

    isbn_line = f"isbn: {yaml_str(isbn)}" if isbn else "isbn:"
    year_line = f"year: {year}" if year else "year:"
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
{year_line}
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


def refresh_entry(meta: dict, md_file: Path) -> bool:
    """
    Refresh Calibre-owned front matter fields in an existing _reading/ file.

    Rebuilds the front matter from fresh metadata while preserving user-owned
    fields (rating) and the body below the front matter.  The date and status
    fields are also preserved — reconcile_shelves handles those separately.

    Returns True if the file was modified.
    """
    content = md_file.read_text(encoding="utf-8")

    parts = content.split("---", 2)
    if len(parts) < 3:
        log.warning("  %s: cannot parse front matter, skipping refresh", md_file.name)
        return False
    body = parts[2]  # everything after the closing ---

    rating_match = re.search(r"^rating:(.*)$", content, re.MULTILINE)
    date_match   = re.search(r"^date:\s*(\S+)", content, re.MULTILINE)
    status_match = re.search(r"^status:\s*(\S+)", content, re.MULTILINE)

    existing_date   = date_match.group(1)   if date_match   else TODAY
    existing_status = status_match.group(1) if status_match else "to-read"
    existing_rating = rating_match.group(1) if rating_match else ""

    new_content = build_front_matter(meta, existing_status, existing_date)
    new_content = re.sub(r"^rating:.*$", f"rating:{existing_rating}", new_content, flags=re.MULTILINE)
    new_content += body

    if new_content == content:
        return False

    md_file.write_text(new_content, encoding="utf-8")
    log.info("  Refreshed: %s", md_file.name)
    return True


def write_entry(meta: dict, status: str, entry_date: str, output_dir: Path) -> bool:
    """
    Write a _reading/ Markdown file for one book.

    Returns True if a new file was created, False if the file already existed
    (existing files are never overwritten to preserve manual edits).
    """
    slug = title_slug(meta["title"])
    filepath = output_dir / f"{entry_date}-{slug}.md"

    if filepath.exists():
        log.info("  Skipping existing file: %s", filepath.name)
        return False

    filepath.write_text(build_front_matter(meta, status, entry_date), encoding="utf-8")
    log.info("  Created: %s", filepath.name)
    return True


# ---------------------------------------------------------------------------
# Reconciliation
# ---------------------------------------------------------------------------

def reconcile_shelves(
    calibre_now: dict[int, tuple[str, str]],
    output_dir: Path,
    prune: bool = False,
) -> tuple[int, int]:
    """
    Update status and date in existing _reading/ files whose book has moved
    to a different shelf since it was first synced.

    calibre_now maps calibre_id → (status, entry_date) based on the current
    shelf contents.  Files whose calibre_id is no longer on any shelf are
    deleted when prune=True, or left untouched with a warning otherwise.

    Returns (updated, pruned).
    """
    updated = 0
    pruned = 0

    for md_file in sorted(output_dir.glob("*.md")):
        if md_file.name == "README.md":
            continue

        content = md_file.read_text(encoding="utf-8")

        cid_match = re.search(r"^calibre_id:\s*(\d+)\s*$", content, re.MULTILINE)
        if not cid_match:
            continue
        calibre_id = int(cid_match.group(1))

        if calibre_id not in calibre_now:
            if prune:
                log.info("  Pruning %s: book %d no longer on any shelf", md_file.name, calibre_id)
                md_file.unlink()
                pruned += 1
            else:
                log.warning(
                    "  %s: book %d is no longer on any shelf (keeping file as-is; use --prune to delete)",
                    md_file.name, calibre_id,
                )
            continue

        new_status, new_date = calibre_now[calibre_id]

        status_match = re.search(r"^status:\s*(\S+)\s*$", content, re.MULTILINE)
        if not status_match:
            continue
        current_status = status_match.group(1)

        if current_status == new_status:
            continue

        log.info(
            "  Reconciling %s: status %s → %s, date → %s",
            md_file.name, current_status, new_status, new_date,
        )
        content = re.sub(r"^status:.*$", f"status: {new_status}", content, flags=re.MULTILINE)
        content = re.sub(r"^date:.*$", f"date: {new_date}", content, flags=re.MULTILINE)
        md_file.write_text(content, encoding="utf-8")
        updated += 1

    return updated, pruned


# ---------------------------------------------------------------------------
# Git
# ---------------------------------------------------------------------------

def git_commit_and_push(repo_dir: Path, created: int) -> None:
    """Stage _reading/, commit, and push the Jekyll repo."""
    log.info("Committing and pushing changes...")
    try:
        # -A stages new files, modifications, AND deletions.
        subprocess.run(
            ["git", "-C", str(repo_dir), "add", "-A", "_reading/"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo_dir), "commit", "-m", "sync: reading log"],
            check=True,
        )
        subprocess.run(
            ["git", "-C", str(repo_dir), "push"],
            check=True,
        )
        log.info("Push complete — GitHub Pages will rebuild shortly.")
    except subprocess.CalledProcessError as exc:
        log.error("Git operation failed: %s", exc)
        log.error("New files were written but not pushed. Commit and push manually.")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--prune",
        action="store_true",
        default=os.environ.get("PRUNE_REMOVED", "").lower() in ("1", "true", "yes"),
        help=(
            "Delete _reading/ files for books no longer on any Calibre-Web shelf. "
            "Can also be enabled with PRUNE_REMOVED=true. "
            "Default: keep files and log a warning."
        ),
    )
    parser.add_argument(
        "--refresh",
        action="store_true",
        default=os.environ.get("REFRESH_METADATA", "").lower() in ("1", "true", "yes"),
        help=(
            "Re-fetch and update Calibre-owned metadata fields (title, author, ISBN, "
            "cover, series, tags, etc.) in existing _reading/ files. "
            "Preserves rating, date, status, and body content. "
            "Can also be enabled with REFRESH_METADATA=true. "
            "Default: existing files are never modified for metadata changes."
        ),
    )
    args = parser.parse_args()

    # Validate required environment variables
    missing = [
        v for v in (
            "CALIBRE_WEB_URL", "CALIBRE_WEB_USER", "CALIBRE_WEB_PASS",
            "JEKYLL_READING_DIR", "JEKYLL_REPO_DIR",
        )
        if not os.environ.get(v)
    ]
    if missing:
        for v in missing:
            log.error("Required environment variable %s is not set.", v)
        sys.exit(1)

    if not OUTPUT_DIR.is_dir():
        log.error("JEKYLL_READING_DIR does not exist or is not a directory: %s", OUTPUT_DIR)
        sys.exit(1)

    if not JEKYLL_REPO_DIR.is_dir():
        log.error("JEKYLL_REPO_DIR does not exist or is not a directory: %s", JEKYLL_REPO_DIR)
        sys.exit(1)

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

    created = refreshed = skipped = errors = 0
    calibre_now: dict[int, tuple[str, str]] = {}  # calibre_id → (status, entry_date)

    # Build calibre_id → file index once.  Used to prevent duplicate files when a
    # book's title (and therefore its slug) changes in Calibre, and to locate
    # existing files for --refresh without relying on the current slug.
    id_to_file: dict[int, Path] = {}
    for md_file in OUTPUT_DIR.glob("*.md"):
        if md_file.name == "README.md":
            continue
        fc = md_file.read_text(encoding="utf-8")
        m = re.search(r"^calibre_id:\s*(\d+)\s*$", fc, re.MULTILINE)
        if m:
            id_to_file[int(m.group(1))] = md_file

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
            calibre_now[book_id] = (status, entry_date)
            try:
                meta = get_book_metadata(session, book_id)
                if book_id in id_to_file:
                    # Book already has a file — don't create a duplicate even if
                    # the title (and slug) has changed since the file was created.
                    if args.refresh and refresh_entry(meta, id_to_file[book_id]):
                        refreshed += 1
                    else:
                        skipped += 1
                elif write_entry(meta, status, entry_date, OUTPUT_DIR):
                    created += 1
                    id_to_file[book_id] = OUTPUT_DIR / f"{entry_date}-{title_slug(meta['title'])}.md"
                else:
                    skipped += 1
            except Exception as exc:
                log.error("  Error processing book %d: %s", book_id, exc)
                errors += 1

    reconciled, pruned = reconcile_shelves(calibre_now, OUTPUT_DIR, prune=args.prune)

    log.info(
        "Done — %d created, %d refreshed, %d reconciled, %d pruned, %d skipped (no change), %d errors",
        created, refreshed, reconciled, pruned, skipped, errors,
    )

    if created > 0 or refreshed > 0 or reconciled > 0 or pruned > 0:
        git_commit_and_push(JEKYLL_REPO_DIR, created)

    # Exit non-zero only if every book failed (likely an auth or structural issue)
    if errors > 0 and created == 0 and refreshed == 0 and reconciled == 0 and pruned == 0 and skipped == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
