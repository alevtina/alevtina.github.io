# verbovetskaya.com

Personal website. Built with Jekyll, hosted on GitHub Pages.

## File Structure

```
├── _config.yml           # Site configuration
├── _includes/            # Reusable components
│   ├── head.html
│   ├── header.html       # Avatar, site title, subtitle, nav
│   ├── hero.html         # Homepage intro
│   ├── footer.html
│   ├── gravatar.html     # Gravatar image helper
│   └── latest-blog.html  # Recent posts list
├── _layouts/             # Page templates
│   ├── default.html
│   ├── page.html
│   └── post.html
├── _posts/               # Blog posts
├── assets/
│   ├── main.scss         # Main stylesheet
│   └── img/              # Images and media
├── about.md              # About page
├── bios.md               # Copy/paste bios and headshot
├── blog.md               # Blog listing page
├── index.md              # Homepage
├── presentations.md      # Presentations page
└── 404.html              # Error page
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

## Deployment

Automatically deploys via GitHub Pages on push to main. Available at `https://verbovetskaya.com`.
