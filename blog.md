---
layout: default
title: Blog
description: "Thoughts on library systems, technology leadership, and digital transformation in academic libraries."
permalink: /blog/
---

<div class="blog-container">
    <section class="blog-hero" aria-labelledby="blog-title">
        <div class="blog-hero-content">
            <h1 class="blog-title" id="blog-title">Blog</h1>
            <p class="blog-description">
                Insights on library systems, technology leadership, and digital transformation in academic libraries.
            </p>
        </div>
    </section>

    <section class="blog-posts" aria-labelledby="posts-title">
        <h2 class="sr-only" id="posts-title">Blog Posts</h2>
        {%- if site.posts.size > 0 -%}
            <div class="posts-grid">
                {%- for post in site.posts -%}
                    <article class="post-card">
                        <div class="post-card-content">
                            <h3 class="post-card-title">
                                <a href="{{ post.url | relative_url }}" class="post-link">
                                    {{ post.title | escape }}
                                </a>
                            </h3>
                            
                            <div class="post-card-meta">
                                <time datetime="{{ post.date | date_to_xmlschema }}">
                                    {{ post.date | date: "%B %-d, %Y" }}
                                </time>
                                {%- if post.author -%}
                                    <span class="meta-separator">•</span>
                                    <span class="post-author">{{ post.author }}</span>
                                {%- endif -%}
                            </div>
                            
                            {%- if post.excerpt -%}
                                <div class="post-card-excerpt">
                                    {%- if post.excerpt contains site.excerpt_separator -%}
                                        {{ post.excerpt | strip_html | strip }}
                                    {%- else -%}
                                        {{ post.excerpt | strip_html | truncatewords: 30 }}
                                    {%- endif -%}
                                </div>
                            {%- endif -%}
                            
                            {%- if post.tags and post.tags.size > 0 -%}
                                <div class="post-card-tags">
                                    {%- for tag in post.tags limit: 3 -%}
                                        <span class="tag">{{ tag }}</span>
                                    {%- endfor -%}
                                </div>
                            {%- endif -%}
                            
                            <a href="{{ post.url | relative_url }}" class="read-more-link">
                                Read More →
                            </a>
                        </div>
                    </article>
                {%- endfor -%}
            </div>
        {%- else -%}
            <div class="no-posts">
                <div class="no-posts-content">
                    <h3>Coming Soon</h3>
                    <p>Blog posts will appear here soon. Check back for insights on library systems and technology leadership.</p>
                </div>
            </div>
        {%- endif -%}
    </section>
</div>
