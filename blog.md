---
layout: default
title: Blog
description: "Thoughts on library systems, technology leadership, and digital transformation in academic libraries."
permalink: /blog/
---

<div class="blog-container">
    <section class="blog-hero">
        <div class="blog-hero-content">
            <h1 class="blog-title">Blog</h1>
            <p class="blog-description">
                Insights on library systems, technology leadership, and digital transformation in academic libraries.
            </p>
        </div>
    </section>

    <section class="blog-posts">
        {%- if site.posts.size > 0 -%}
            <div class="posts-grid">
                {%- for post in site.posts -%}
                    <article class="post-card">
                        <div class="post-card-content">
                            <h2 class="post-card-title">
                                <a href="{{ post.url | relative_url }}" class="post-link">
                                    {{ post.title | escape }}
                                </a>
                            </h2>
                            
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
                                    {{ post.excerpt | strip_html | truncatewords: 30 }}
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
                    <h2>Coming Soon</h2>
                    <p>Blog posts will appear here soon. Check back for insights on library systems and technology leadership.</p>
                </div>
            </div>
        {%- endif -%}
    </section>
</div>
