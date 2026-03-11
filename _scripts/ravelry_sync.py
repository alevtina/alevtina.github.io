#!/usr/bin/env python3
"""
ravelry_sync.py — Sync knitting/crochet projects from Ravelry to Jekyll _knitting/ collection.

Authenticates with the Ravelry API using a personal API key, fetches all
projects for the configured Ravelry username, and creates Markdown files in
the Jekyll _knitting/ directory.

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


def entry_date(project: dict) -> str:
    status = normalize_status(project.get("status_name", ""))
    if status == "finished" and project.get("completed"):
        return project["completed"][:10]
    if project.get("started"):
        return project["started"][:10]
    return TODAY


def get_session() -> requests.Session:
    s = requests.Session()
    s.auth = (API_USER, API_PASS)
    s.headers.update({"User-Agent": "ravelry-jekyll-sync/1.0"})
    return s


def fetch_projects(session: requests.Session) -> list[dict]:
    """Fetch all projects for the user, handling pagination."""
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
    r = session.get(
        f"{API_BASE}/projects/{RAVELRY_USERNAME}/{permalink}.json",
        timeout=30,
    )
    r.raise_for_status()
    return r.json().get("project", {})


def build_front_matter(detail: dict) -> str:
    name = detail.get("name") or "Untitled"
    pattern = detail.get("pattern") or {}
    pattern_name = pattern.get("name") or detail.get("pattern_name") or ""
    designer = (pattern.get("pattern_author") or {}).get("name") or ""
    pattern_permalink = pattern.get("permalink") or ""
    pattern_url = (
        f"https://www.ravelry.com/patterns/library/{pattern_permalink}"
        if pattern_permalink else ""
    )

    status = normalize_status(detail.get("status_name") or "")
    started = (detail.get("started") or "")[:10]
    completed = (detail.get("completed") or "")[:10]

    first_photo = detail.get("first_photo") or {}
    cover = first_photo.get("medium2_url") or first_photo.get("small2_url") or ""

    yarns = detail.get("yarns") or []
    yarn_name = colorway = yarn_url = ""
    if yarns:
        y = yarns[0]
        yarn_name = y.get("yarn_name") or ""
        colorway = y.get("color_name") or ""
        yarn_permalink = (y.get("yarn") or {}).get("permalink") or ""
        if yarn_permalink:
            yarn_url = f"https://www.ravelry.com/yarns/library/{yarn_permalink}"

    project_permalink = detail.get("permalink") or str(detail.get("id", ""))
    ravelry_url = f"https://www.ravelry.com/projects/{RAVELRY_USERNAME}/{project_permalink}"
    ravelry_id = detail.get("id", "")

    craft_name = (detail.get("craft") or {}).get("name") or detail.get("craft_name") or ""
    tags = detail.get("tag_names") or []
    tags_yaml = "[" + ", ".join(yaml_str(t) for t in tags) + "]" if tags else "[]"
    notes = (detail.get("notes") or "").strip()

    lines = [
        "---",
        "layout: knit",
        f"title: {yaml_str(name)}",
        f"pattern: {yaml_str(pattern_name) if pattern_name else ''}",
        f"designer: {yaml_str(designer) if designer else ''}",
        f"pattern_url: {yaml_str(pattern_url) if pattern_url else ''}",
        f"status: {status}",
        f"started: {yaml_str(started) if started else ''}",
        f"completed: {yaml_str(completed) if completed else ''}",
        f"cover: {yaml_str(cover) if cover else ''}",
        f"yarn: {yaml_str(yarn_name) if yarn_name else ''}",
        f"colorway: {yaml_str(colorway) if colorway else ''}",
        f"yarn_url: {yaml_str(yarn_url) if yarn_url else ''}",
        f"ravelry_url: {yaml_str(ravelry_url)}",
        f"ravelry_id: {ravelry_id}",
        f"craft: {yaml_str(craft_name) if craft_name else ''}",
        f"date: {entry_date(detail)}",
        f"tags: {tags_yaml}",
        "---",
    ]
    if notes:
        lines.append("")
        lines.append(notes)

    return "\n".join(lines) + "\n"


def write_entry(detail: dict, output_dir: Path) -> bool:
    """Write a _knitting/ Markdown file. Returns True if created."""
    name = detail.get("name") or "Untitled"
    slug = slugify(name)
    d = entry_date(detail)
    filepath = output_dir / f"{d}-{slug}.md"

    if filepath.exists():
        log.info("  Skipping existing: %s", filepath.name)
        return False

    filepath.write_text(build_front_matter(detail), encoding="utf-8")
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

    # Index existing files by ravelry_id to skip re-fetching
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

    created = skipped = errors = 0

    for project in all_projects:
        craft = (project.get("craft") or {}).get("name") or project.get("craft_name") or ""
        if CRAFT_FILTER and craft and craft not in CRAFT_FILTER:
            log.info("  Skipping craft=%r: %s", craft, project.get("name"))
            continue

        project_id = project["id"]
        if project_id in existing_ids:
            skipped += 1
            continue

        permalink = project.get("permalink") or str(project_id)

        try:
            detail = fetch_project_detail(session, permalink)
            if write_entry(detail, OUTPUT_DIR):
                created += 1
            else:
                skipped += 1
        except Exception as exc:
            log.error("  Error processing project %d (%s): %s", project_id, project.get("name"), exc)
            errors += 1

    log.info("Done — %d created, %d skipped, %d errors", created, skipped, errors)

    if errors > 0 and created == 0 and skipped == 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
