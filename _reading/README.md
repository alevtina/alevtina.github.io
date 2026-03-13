---
published: false
---

# _reading/ — IndieWeb Read Posts

Files in this folder are Jekyll collection items rendered by `_layouts/read.html`
as IndieWeb [read posts](https://indieweb.org/read) with microformats2 markup.

Most files are created automatically by [calibre-web-reads](https://github.com/alevtina/calibre-web-reads). The script
**never overwrites existing files**, so you can freely add notes and ratings
without fear of losing them on the next sync.

---

## Front matter reference

```yaml
---
layout: book
title: "Book Title"           # Required. Wrap in quotes if it contains colons.
book_author: "Author Name"         # Single author as a string.
# author:                     # Multiple authors as a list:
#   - "First Author"
#   - "Second Author"
isbn: "9780000000000"         # ISBN-13 preferred. Leave blank if unknown.
series: "Series Name"         # Omit if not part of a series.
series_part: 1                # Volume/part number within the series.
cover: "https://..."          # Full URL to cover image from Calibre-Web.
status: finished              # finished | reading | to-read
date: 2025-01-15              # For finished books: date read (or YYYY-01-01 placeholder).
                              # For reading/to-read: date added to log.
rating:                       # Fill in manually. Any format you like: "4/5", "★★★★".
tags: []                      # From Calibre tags. Add or remove freely.
calibre_id: 42                # Internal Calibre book ID. Used for reference only.
---
```

The body of the file (after the closing `---`) is rendered as reading notes.
Leave it empty or write whatever you like — Markdown is supported.

---

## Adding a book manually

1. Create a new file: `_reading/YYYY-MM-DD-slug.md`
   - Use the date you finished, started, or want to track the book.
   - The slug is a URL-safe version of the title (lowercase, hyphens, no punctuation).
   - Example: `_reading/2025-06-01-the-left-hand-of-darkness.md`

2. Copy the front matter template above and fill in the fields.

3. Leave `calibre_id:` blank if the book isn't in Calibre.

---

## Editing an existing entry

Open the file and edit freely. The sync script identifies files by filename, so
as long as you don't rename the file, it will keep skipping it on future syncs.

Fields you'll most often fill in manually:
- **`rating:`** — the sync script leaves this blank intentionally.
- **`date:`** — for finished books, the script defaults to `YYYY-01-01` (the shelf
  year). Update it to the actual finish date if you know it.
- Body text — reading notes, quotes, or a short review.

---

## Shelf naming conventions in Calibre-Web

The sync script looks for shelves named `{prefix}-YYYY`, `{prefix}-reading`, and `{prefix}-tbr`, where the prefix defaults to your Calibre-Web username.

| Shelf name         | Status in front matter |
|--------------------|------------------------|
| `alevtina-2024`    | `finished`             |
| `alevtina-2025`    | `finished`             |
| `alevtina-reading` | `reading`              |
| `alevtina-tbr`     | `to-read`              |

Add a new `alevtina-YYYY` shelf each year for finished books.

---

## Running the sync

```sh
cd ../calibre-web-reads
set -a && source .env && set +a
python3 sync.py
```

See [calibre-web-reads](https://github.com/alevtina/calibre-web-reads) for setup and configuration.
