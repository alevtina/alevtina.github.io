# _knitting/

Knitting and crochet project files, synced from Ravelry via `_scripts/ravelry_sync.py`.

Each file is named `{date}-{slug}.md` where date is the completion date for
finished projects, or the start date for in-progress and hibernating projects.

**Existing files are never overwritten by the sync script**, so it's safe to
edit the notes, tags, or any other field manually.

## Front matter fields

| Field | Description |
|-------|-------------|
| `title` | Project name |
| `pattern` | Pattern name |
| `designer` | Designer name |
| `pattern_url` | Link to pattern on Ravelry |
| `status` | `finished`, `in-progress`, `hibernating`, or `frogged` |
| `started` | Start date (ISO) |
| `completed` | Completion date (ISO) |
| `cover` | Photo URL from Ravelry |
| `yarn` | Yarn name |
| `colorway` | Colorway name |
| `yarn_url` | Link to yarn on Ravelry |
| `ravelry_url` | Link to project on Ravelry |
| `ravelry_id` | Ravelry project ID (used by sync script to identify existing files) |
| `craft` | `Knitting` or `Crocheting` |
| `date` | Date used for sorting (completion date or start date) |
| `tags` | Tags from Ravelry |

Body content (below the `---`) is the project notes from Ravelry, preserved on first sync.
