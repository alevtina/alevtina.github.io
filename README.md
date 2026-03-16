# verbovetskaya.com

Personal website. Built with Jekyll 4, hosted on GitHub Pages via GitHub Actions.

## Stack

- **Jekyll 4.3** — static site generator
- **Minima 2.5** — base theme (heavily customized)
- **Sass** — styles via CSS custom properties (dark/light mode)
- **GitHub Actions** — build, deploy, and scheduled webmention refresh
- **webmention.io** — receives incoming webmentions
- **jekyll-webmention_io** — displays webmentions at build time
- **@remy/webmention** — sends outgoing webmentions on deploy
- **[calibre-web-reads](https://github.com/alevtina/calibre-web-reads)** — syncs Calibre-Web shelves to IndieWeb read posts
- **Ravelry API** — syncs knitting projects via `_scripts/ravelry_sync.py`

## File Structure

```
├── _config.yml              # Site configuration
├── _includes/               # Partials (header, footer, webmention templates, etc.)
├── _layouts/                # Page layouts (default, post, book, knit)
├── _posts/                  # Blog posts
├── _reading/                # IndieWeb read posts (synced via calibre-web-reads)
├── _knitting/               # Knitting project files (synced from Ravelry)
├── _scripts/                # Local scripts (Ravelry sync)
├── _data/                   # Webmention cache (auto-generated)
├── assets/                  # Styles and images
├── .github/workflows/       # GitHub Actions (build, deploy, send webmentions)
├── blog/                    # Blog index (index.html, required for jekyll-paginate)
└── *.md                     # Content pages (index, about, presentations, etc.)
```

## Reading Log

Books are synced from Calibre-Web using [calibre-web-reads](https://github.com/alevtina/calibre-web-reads), a standalone Python script that runs locally (the Calibre-Web instance is on the home network, not reachable from GitHub Actions).

To sync:

```sh
cd ../calibre-web-reads
set -a && source .env && set +a
python3 sync.py
```

The script writes new files to `_reading/`, then commits and pushes automatically. Existing files are never overwritten — add ratings and notes freely. See `_reading/README.md` for the front matter reference and how to add books manually.

## Knitting Notebook

Projects are synced from Ravelry using `_scripts/ravelry_sync.py`, a standalone script that runs locally using Basic Auth against the Ravelry API.

To sync:

```sh
cd _scripts
set -a && source .env && set +a
python3 ravelry_sync.py
```

The `.env` file needs `RAVELRY_USERNAME` and `RAVELRY_PASSWORD`. The script writes new files to `_knitting/` and never overwrites existing files — add notes freely. See `_knitting/README.md` for the front matter reference.

After syncing, trigger a Jekyll build manually (GitHub Actions won't auto-trigger from a script push):

```sh
gh workflow run "Build and Deploy Jekyll" --ref main
```

## Adding Blog Posts

Create new posts in `_posts/` with this naming convention:
```
YYYY-MM-DD-title-of-post.md
```

### Front Matter

Front matter template:
```yaml
---
layout: post
title: "Your Post Title"
date: 2025-08-02
author: "Alevtina Verbovetskaya"
excerpt: "Summary of no more than 200 characters."
tags: [library-systems, technology]
---
```

### Table of Contents

Kramdown has native TOC generation built in. To add a TOC to any post, just place this in the markdown where the TOC should appear (usually after an introductory paragraph):

```
## Jump to
{:.no_toc}

* TOC
{:toc}
```
Note the `{:no_toc}` on the "Jump to" heading: that prevents the heading itself from appearing in the TOC.

> [!TIP]
> Exclude any other heading from the TOC using the same syntax:
> ```
> ## This won't appear in the TOC
> {:.no_toc}
> ```

The TOC will auto-generate anchor links from all the `##`, `###`, etc. headings in the post.

## Deployment

Deploys automatically via GitHub Actions on push to main. The workflow:

1. **Build** — Jekyll builds the site with Ruby 3.3
2. **Deploy** — Publishes to GitHub Pages
3. **Send webmentions** — Notifies linked sites via `@remy/webmention` (push only)

A scheduled rebuild runs every 6 hours to pick up new incoming webmentions from webmention.io. Manual rebuilds can be triggered from the Actions tab.

Available at `https://verbovetskaya.com`.

## Webmentions

The site sends and receives [webmentions](https://indieweb.org/Webmention):

- **Receiving**: webmention.io collects mentions; the Jekyll plugin fetches and renders them at build time
- **Sending**: `@remy/webmention` parses the RSS feed and sends mentions to linked sites on each deploy
- **Display**: Custom templates in `_includes/webmentions/` add accessible `<h3>` labels and only render sections that have content
- **Form**: Each post has a submission form for manual webmentions

## Local Development

```sh
bundle install
bundle exec jekyll serve
```

Requires Ruby 3.3+ (managed via `.ruby-version` / rbenv).
