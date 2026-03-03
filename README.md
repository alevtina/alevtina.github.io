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
- **GoatCounter** — privacy-friendly analytics

## File Structure

```
├── _config.yml              # Site configuration + webmention settings
├── _includes/
│   ├── head.html            # <head> with meta, webmention endpoints
│   ├── header.html          # Avatar, site title, subtitle, nav
│   ├── hero.html            # Homepage intro
│   ├── footer.html          # Copyright, social links (rel="me")
│   ├── gravatar.html        # Gravatar image helper
│   ├── latest-blog.html     # Recent posts list
│   └── webmentions/         # Custom webmention templates
│       ├── webmentions.html # General mentions (renders nothing if empty)
│       ├── likes.html       # Likes facepile with h3 label
│       ├── reposts.html     # Reposts facepile with h3 label
│       └── replies.html     # Reply cards with h3 label
├── _layouts/
│   ├── default.html
│   ├── page.html
│   └── post.html            # Includes webmentions section + form
├── _posts/                  # Blog posts
├── _data/                   # Webmention cache (auto-generated)
├── assets/
│   ├── main.scss            # Main stylesheet
│   └── img/                 # Images and media
├── .github/workflows/
│   └── deploy.yml           # Build, deploy, send webmentions
├── about.md                 # About page (redirects from /experience)
├── bios.md                  # Copy/paste bios and headshot
├── blog.md                  # Blog listing page
├── index.md                 # Homepage
├── presentations.md         # Presentations page
└── 404.html                 # Error page
```

## Adding Blog Posts

Create new posts in `_posts/` with this naming convention:
```
YYYY-MM-DD-title-of-post.md
```

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

## Adding TOC

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

