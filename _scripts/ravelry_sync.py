#!/usr/bin/env python3
"""
ravelry_sync.py — Sync knitting/crochet projects from Ravelry to Jekyll _knitting/ collection.

Uses the projects/list endpoint plus the project detail endpoint (requires
"Basic Auth: personal account access" credentials from ravelry.com/pro/developer).
The detail endpoint provides notes, yarn details, and pattern URLs.

Existing files are never overwritten, so manual edits are safe.

Required environment variables:
    RAVELRY_API_USER     Ravelry API key username (from ravelry.com/pro/developer)
    RAVELRY_API_PASS     Ravelry API key password

Optional:
    RAVELRY_USERNAME     Ravelry username to sync (default: alevtina)
    JEKYLL_KNITTING_DIR  Path to the _knitting/ directory (default: ./_knitting)
    CRAFT_FILTER         Comma-separated crafts to include (default: Knitting,Crocheting)
"""

import os
import re
import sys
import time
import logging
from datetime import date
from pathlib import Path

import requests

RAVELRY_USERNAME = os.environ.get("RAVELRY_USERNAME", "alevtina")
API_USER = os.environ.get("RAVELRY_API_USER", "")
API_PASS = os.environ.get("RAVELRY_API_PASS", "")

OUTPUT_DIR = Path(os.environ.get("JEKYLL_KNITTING_DIR", "_knitting")).expanduser()

CRAFT_FILTER_RAW = os.environ.get("CRAFT_FILTER", "Knitting,Crocheting")
CRAFT_FILTER = {c.strip() for c in CRAFT_FILTER_RAW.split(",")}

API_BASE = "https://api.ravelry.com"
TODAY = date.today().isoformat()

# Ravelry rate limit: 3 requests/second for basic auth
REQUEST_DELAY = 0.4

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
log = logging.getLogger(__name__)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-{2,}", "-", text)
    text = re.sub(r"^-|-$", "", text)
    return text or "untitled"


def yaml_str(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"')
    return f'"{escaped}"'


def normalize_status(status_name: str) -> str:
    return {
        "finished": "finished",
        "in progress": "in-progress",
        "hibernating": "hibernating",
        "frogged": "frogged",
    }.get((status_name or "").lower(), "unknown")


def parse_date(value: str) -> str:
    """Normalize a Ravelry date string to ISO format (YYYY-MM-DD)."""
    if not value:
        return ""
    return value[:10].replace("/", "-")


def entry_date(project: dict) -> str:
    """Return the date to use for the filename and front matter date field."""
    status = normalize_status(project.get("status_name", ""))
    if status == "finished":
        d = parse_date(project.get("completed") or "")
        if d:
            return d
    d = parse_date(project.get("started") or "")
    return d or TODAY


def get_session() -> requests.Session:
    s = requests.Session()
    s.auth = (API_USER, API_PASS)
    s.headers.update({"User-Agent": "ravelry-jekyll-sync/1.0"})
    return s


def fetch_projects(session: requests.Session) -> list[dict]:
    """Fetch all projects for the user from the list endpoint, handling pagination."""
    projects = []
    page = 1
    while True:
        r = session.get(
            f"{API_BASE}/projects/{RAVELRY_USERNAME}/list.json",
            params={"page": page, "page_size": 100},
            timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        batch = data.get("projects", [])
        projects.extend(batch)
        if data.get("paginator", {}).get("last_page", 1) <= page:
            break
        page += 1
    return projects


def fetch_project_detail(session: requests.Session, permalink: str) -> dict:
    """Fetch full project detail including notes, yarn, and pattern URL."""
    time.sleep(REQUEST_DELAY)
    r = session.get(
        f"{API_BASE}/projects/{RAVELRY_USERNAME}/{permalink}.json",
        timeout=30,
    )
    if r.status_code == 200:
        return r.json().get("project", {})
    log.warning("  Detail fetch failed (HTTP %d) for %s", r.status_code, permalink)
    return {}



def split_name(raw: str) -> tuple[str, str]:
    """Split "Category | Title" into (category, title). Falls back to ("", raw)."""
    if " | " in raw:
        category, title = raw.split(" | ", 1)
        return category.strip(), title.strip()
    return "", raw.strip()


def extract_notes(detail: dict) -> str:
    """Return plain notes text from project detail, preferring HTML-stripped version."""
    # notes_html contains formatted HTML; notes is plain text
    notes = detail.get("notes") or ""
    return notes.strip()


def build_front_matter(project: dict, detail: dict) -> str:
    raw_name = project.get("name") or "Untitled"
    category, name = split_name(raw_name)
    pattern_name = project.get("pattern_name") or ""

    status = normalize_status(project.get("status_name") or "")
    started = parse_date(project.get("started") or "")
    completed = parse_date(project.get("completed") or "")

    first_photo = project.get("first_photo") or {}
    cover = first_photo.get("medium2_url") or first_photo.get("small2_url") or ""

    project_permalink = project.get("permalink") or str(project.get("id", ""))
    ravelry_url = f"https://www.ravelry.com/projects/{RAVELRY_USERNAME}/{project_permalink}"
    ravelry_id = project.get("id", "")

    craft_name = project.get("craft_name") or ""
    rating = project.get("rating") or ""
    tags = project.get("tag_names") or []
    tags_yaml = "[" + ", ".join(yaml_str(t) for t in tags) + "]" if tags else "[]"

    # Detail endpoint fields
    pattern_url = ""
    yarn = ""
    colorway = ""
    yarn_url = ""
    designer = ""

    if detail:
        pattern_id = detail.get("pattern_id")
        if pattern_id:
            pattern_url = f"https://www.ravelry.com/patterns/library/{pattern_id}"


        packs = detail.get("packs") or []
        if packs:
            first_pack = packs[0]
            yarn_data = first_pack.get("yarn") or {}
            yarn = yarn_data.get("name") or ""
            colorway = (first_pack.get("colorway_name")
                        or first_pack.get("personal_color_name")
                        or "")
            yarn_permalink = yarn_data.get("permalink") or ""
            if yarn_permalink:
                yarn_url = f"https://www.ravelry.com/yarns/library/{yarn_permalink}"

    lines = [
        "---",
        "layout: knit",
        f"title: {yaml_str(name)}",
        f"category: {yaml_str(category) if category else ''}",
        f"pattern: {yaml_str(pattern_name) if pattern_name else ''}",
        f"designer: {yaml_str(designer) if designer else ''}",
        f"pattern_url: {yaml_str(pattern_url) if pattern_url else ''}",
        f"status: {status}",
        f"started: {yaml_str(started) if started else ''}",
        f"completed: {yaml_str(completed) if completed else ''}",
        f"cover: {yaml_str(cover) if cover else ''}",
        f"yarn: {yaml_str(yarn) if yarn else ''}",
        f"colorway: {yaml_str(colorway) if colorway else ''}",
        f"yarn_url: {yaml_str(yarn_url) if yarn_url else ''}",
        f"rating: {rating}",
        f"ravelry_url: {yaml_str(ravelry_url)}",
        f"ravelry_id: {ravelry_id}",
        f"craft: {yaml_str(craft_name) if craft_name else ''}",
        f"date: {entry_date(project)}",
        f"tags: {tags_yaml}",
        "---",
    ]

    content = "\n".join(lines) + "\n"

    notes = extract_notes(detail)
    if notes:
        content += "\n" + notes + "\n"

    return content


def write_entry(project: dict, detail: dict, output_dir: Path) -> bool:
    """Write a _knitting/ Markdown file. Returns True if created."""
    _, name = split_name(project.get("name") or "Untitled")
    slug = slugify(name)
    d = entry_date(project)
    filepath = output_dir / f"{d}-{slug}.md"

    if filepath.exists():
        log.info("  Skipping existing: %s", filepath.name)
        return False

    filepath.write_text(build_front_matter(project, detail), encoding="utf-8")
    log.info("  Created: %s", filepath.name)
    return True


def main() -> None:
    missing = [v for v in ("RAVELRY_API_USER", "RAVELRY_API_PASS") if not os.environ.get(v)]
    if missing:
        for v in missing:
            log.error("Required environment variable %s is not set.", v)
        sys.exit(1)

    if not OUTPUT_DIR.is_dir():
        log.error("Output directory does not exist: %s", OUTPUT_DIR)
        sys.exit(1)

    existing_ids: set[int] = set()
    for md_file in OUTPUT_DIR.glob("*.md"):
        if md_file.name == "README.md":
            continue
        m = re.search(r"^ravelry_id:\s*(\d+)", md_file.read_text(encoding="utf-8"), re.MULTILINE)
        if m:
            existing_ids.add(int(m.group(1)))

    session = get_session()

    try:
        all_projects = fetch_projects(session)
    except Exception as exc:
        log.error("Failed to fetch projects: %s", exc)
        sys.exit(1)

    log.info("Fetched %d projects from Ravelry", len(all_projects))

    created = skipped = 0

    for project in all_projects:
        craft = project.get("craft_name") or ""
        if CRAFT_FILTER and craft and craft not in CRAFT_FILTER:
            log.info("  Skipping craft=%r: %s", craft, project.get("name"))
            continue

        project_id = project["id"]
        if project_id in existing_ids:
            skipped += 1
            continue

        permalink = project.get("permalink") or str(project_id)
        detail = fetch_project_detail(session, permalink)

        if write_entry(project, detail, OUTPUT_DIR):
            created += 1
        else:
            skipped += 1

    log.info("Done — %d created, %d skipped", created, skipped)


if __name__ == "__main__":
    main()
