---
layout: default
title: Blog
description: "Writing about whatever's on my mind."
permalink: /blog/
---

<div class="blog-page">
    <h1>Blog</h1>
    <p>{{ page.description }}</p>

    {%- if site.posts.size > 0 -%}
    <ul class="post-list">
        {%- for post in site.posts -%}
        <li>
            <div class="post-title">
                <a href="{{ post.url | relative_url }}">{{ post.title | escape }}</a>
            </div>
            <div class="post-meta">{{ post.date | date: "%B %-d, %Y" }}</div>
            {%- if post.tags and post.tags.size > 0 -%}
            <div class="post-tags">
                {%- for tag in post.tags -%}
                    <a href="/tags/{{ tag | slugify }}/" class="tag">{{ tag }}</a>
                {%- endfor -%}
            </div>
            {%- endif -%}
            {%- if post.excerpt -%}
            <div class="post-excerpt">
                {{ post.excerpt | strip_html | truncatewords: 30 }}
                <a href="{{ post.url | relative_url }}">Read more &rarr;</a>
            </div>
            {%- endif -%}
        </li>
        {%- endfor -%}
    </ul>
    {%- else -%}
    <p>Posts coming soon.</p>
    {%- endif -%}
</div>
