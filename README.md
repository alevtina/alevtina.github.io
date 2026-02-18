# verbovetskaya.com

Personal website. Built with Jekyll, hosted on GitHub Pages.

## Technology Stack

- **Jekyll 4.3.2** - Static site generator
- **GitHub Pages** - Hosting and deployment
- **Sass/SCSS** - Stylesheet preprocessing
- **Gravatar** - Profile image management
- **Semantic HTML** - Accessibility and SEO optimization

## File Structure

```
├── _config.yml           # Site configuration
├── _includes/            # Reusable components
│   ├── about.html
│   ├── contact.html
│   ├── head.html
│   ├── header.html
│   ├── hero.html
│   ├── footer.html
│   ├── gravatar.html
│   ├── latest-blog.html
│   ├── presentations.html
│   └── skills.html
├── _layouts/             # Page templates
│   ├── default.html
│   ├── page.html
│   └── post.html
├── _posts/               # Blog posts
├── assets/
│   ├── main.scss         # Main stylesheet
│   └── img/              # Images and media
├── 404.html              # Error 404 page
├── blog.md               # Blog landing page
├── index.md              # Homepage content
└── README.md             # This file
```

## Content Management

### Adding Blog Posts

Create new posts in the `_posts/` directory with this naming convention:
```
YYYY-MM-DD-title-of-post.md
```

Use this front matter template:
```yaml
---
layout: post
title: "Your Post Title"
date: 2025-08-02
author: "Alevtina Verbovetskaya"
excerpt: "Summary of no more than 200 characters."
tags: [library-systems, technology, leadership]
---

Your content here...
```

### Updating Personal Information

Edit `_config.yml` to update:
- Contact information
- Bio and professional details
- Social media links
- Site metadata

### Customizing Design

The site uses CUNY Blue (`#0033A1`) as the accent color. To modify colors, edit the CSS custom properties in `assets/main.scss`:

```scss
:root {
    --accent: #0033A1;
    --highlight: #FFB71B;
    // ... other color variables
}
```

## Deployment

The site automatically deploys via GitHub Pages when changes are pushed to the main branch. It's available at: `https://verbovetskaya.com`

## Performance Features

- **System fonts**: No web font downloads required
- **Optimized images**: Gravatar integration for profile photos
- **Minimal CSS**: Only necessary styles included
- **Progressive enhancement**: Works without JavaScript
- **Responsive images**: Proper sizing and optimization

## Accessibility Features

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **WCAG AA compliance**: Color contrast meets 4.5:1 minimum
- **Keyboard navigation**: Full site navigation without mouse
- **Screen reader support**: Proper ARIA labels and descriptions
- **Reduced motion support**: Respects user preferences
- **Focus indicators**: Visible keyboard navigation

## Browser Support

- Modern browsers (Chrome, Firefox, Safari, Edge)
- Mobile browsers (iOS Safari, Chrome Mobile)
- Works with JavaScript disabled
- Accessible to screen readers
- Automatic dark mode support with manual toggle
