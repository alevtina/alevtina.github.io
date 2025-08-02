# Alevtina Verbovetskaya - Professional Website

My professional website showcasing expertise in library systems and technology leadership at The City University of New York.

## Features

- ✨ **Modern Design**: Clean, professional layout with contemporary styling
- 🌙 **Automatic Dark Mode**: Responds to user's OS theme preference
- 📱 **Mobile-First**: Fully responsive design optimized for all devices
- ♿ **Accessible**: WCAG AA compliant with proper semantic markup
- ⚡ **Fast**: Optimized performance with minimal dependencies
- 🔧 **Jekyll-Powered**: Easy to maintain and deploy on GitHub Pages
- 📝 **Integrated Blog**: Professional blog with latest post showcase

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
│   ├── head.html
│   ├── header.html
│   ├── footer.html
│   └── gravatar.html
├── _layouts/             # Page templates
│   ├── default.html
│   └── post.html
├── _posts/               # Blog posts
├── assets/
│   ├── main.scss         # Main stylesheet
│   └── images/           # Images and media
├── blog/
│   └── index.md          # Blog landing page
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

The site uses a clean blue color scheme (`#0033A1`). To modify colors, edit the CSS custom properties in `assets/main.scss`:

```scss
:root {
    --brand-blue: #0033A1;
    --accent-primary: var(--brand-blue);
    --accent-primary-hover: #002080;
    // ... other color variables
}
```

## Deployment

The site automatically deploys via GitHub Pages when changes are pushed to the main branch. It's available at: `https://alevtina.github.io`

## Performance Features

- **System fonts**: No web font downloads required
- **Optimized images**: Gravatar integration for profile photos
- **Minimal CSS**: Only necessary styles included
- **Progressive enhancement**: Works without JavaScript
- **Responsive images**: Proper sizing and optimization

## Accessibility Features

- **Semantic HTML**: Proper heading hierarchy and landmarks
- **WCAG AA compliance**: Color contrast and interactive elements
- **Keyboard navigation**: Full site navigation without mouse
- **Screen reader support**: Proper ARIA labels and descriptions
- **Reduced motion support**: Respects user preferences
- **Focus indicators**: Visible keyboard navigation

## Browser Support

- ✅ Modern browsers (Chrome, Firefox, Safari, Edge)
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)
- ✅ Works with JavaScript disabled
- ✅ Accessible to screen readers
- ✅ Automatic dark mode support
