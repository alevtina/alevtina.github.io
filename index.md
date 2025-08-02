---
layout: default
title: Home
description: "University Director of Library Systems at The City University of New York. Leading digital transformation and technology innovation in academic library systems."
---

<section class="hero" aria-labelledby="hero-title">
    <div class="hero-content">
        {% include gravatar.html size="200" class="hero-image" %}
        <h1 class="hero-title" id="hero-title">{{ site.author.name }}</h1>
        <p class="hero-subtitle">{{ site.author.title }}</p>
        <p class="hero-description">
            {{ site.author.bio }}
        </p>
        <a href="#contact" class="cta-button">Get In Touch</a>
    </div>
</section>

<section id="about" class="section" aria-labelledby="about-title">
    <h2 class="section-title" id="about-title">About</h2>
    <div class="card-grid">
        <div class="card">
            <h3 class="card-title">Leadership & Vision</h3>
            <p class="card-content">
                As University Director of Library Systems at CUNY, I oversee the strategic planning and implementation of library technology infrastructure across multiple campuses, ensuring seamless access to information resources for students, faculty, and researchers.
            </p>
        </div>
        <div class="card">
            <h3 class="card-title">Innovation Focus</h3>
            <p class="card-content">
                I drive practical innovation by implementing and integrating technologies that improve library services. My work enhances discovery, transparency, accessibility, and the user experience across the CUNY system.
            </p>
        </div>
    </div>
</section>

<section id="experience" class="section" aria-labelledby="experience-title">
    <h2 class="section-title" id="experience-title">Professional Experience</h2>
    <div class="card-grid">
        <div class="card">
            <p class="card-subtitle">Current Position</p>
            <h3 class="card-title">University Director of Library Systems</h3>
            <p class="card-content">
                <strong>{{ site.author.organization }}</strong><br>
                Leading technology strategy and operations for CUNY's library system, managing enterprise-level implementations, and fostering collaboration across 25+ campus libraries to deliver innovative information services.
            </p>
        </div>
        <div class="card">
            <h3 class="card-title">Key Achievements</h3>
            <p class="card-content">
                • Led CUNY-wide migration to a next-generation library services platform<br>
                • Strengthened system integrations across library and university-wide technologies<br>
                • Enhanced user experience through modern discovery interfaces<br>
                • Built a collaborative, mission-driven team culture
            </p>
        </div>
    </div>
</section>

<section id="skills" class="section" aria-labelledby="skills-title">
    <h2 class="section-title" id="skills-title">Areas of Expertise</h2>
    <div class="skills-grid">
        <div class="skill-item">
            <div class="skill-title">Library Systems Strategy</div>
            <div>Enterprise platforms (Alma, Primo VE), system migrations, discovery optimization, digital infrastructure planning</div>
        </div>
        <div class="skill-item">
            <div class="skill-title">Project Leadership & Implementation</div>
            <div> Strategic planning, vendor management, cross-campus coordination, change management</div>
        </div>
        <div class="skill-item">
            <div class="skill-title">User Experience & Web Services</div>
            <div>Interface design, accessibility, authentication (SSO), custom tools for service transparency</div>
        </div>
        <div class="skill-item">
            <div class="skill-title">Team & Organizational Development</div>
            <div>Team leadership, staff mentoring, operational governance, collaborative culture-building</div>
        </div>
    </div>
</section>

<section id="contact" class="section" aria-labelledby="contact-title">
    <h2 class="section-title" id="contact-title">Contact</h2>
    <div class="contact-grid">
        <div class="contact-item">
            <div class="contact-icon">📧</div>
            <h3 class="contact-title">Email</h3>
            <a href="mailto:{{ site.contact.email }}" class="contact-link">{{ site.contact.email }}</a>
        </div>
        {%- if site.contact.linkedin -%}
        <div class="contact-item">
            <div class="contact-icon">💼</div>
            <h3 class="contact-title">LinkedIn</h3>
            <a href="{{ site.contact.linkedin }}" target="_blank" rel="noopener noreferrer" class="contact-link">Connect on LinkedIn</a>
        </div>
        {%- endif -%}
        <div class="contact-item">
            <div class="contact-icon">🏛️</div>
            <h3 class="contact-title">Institution</h3>
            <a href="{{ site.contact.institution_url }}" target="_blank" rel="noopener noreferrer" class="contact-link">{{ site.contact.institution }}</a>
        </div>
    </div>
</section>

{%- if site.posts.size > 0 -%}
<section id="latest-blog" class="section" aria-labelledby="latest-blog-title">
    <h2 class="section-title" id="latest-blog-title">Latest from the Blog</h2>
    {%- assign latest_post = site.posts.first -%}
    <div class="latest-post-card">
        <div class="latest-post-content">
            <h3 class="latest-post-title">
                <a href="{{ latest_post.url | relative_url }}" class="latest-post-link">
                    {{ latest_post.title | escape }}
                </a>
            </h3>
            
            <div class="latest-post-meta">
                <time datetime="{{ latest_post.date | date_to_xmlschema }}">
                    {{ latest_post.date | date: "%B %-d, %Y" }}
                </time>
                {%- if latest_post.author -%}
                    <span class="meta-separator">•</span>
                    <span class="post-author">{{ latest_post.author }}</span>
                {%- endif -%}
            </div>
            
            {%- if latest_post.excerpt -%}
                <div class="latest-post-excerpt">
                    {{ latest_post.excerpt | strip_html | truncatewords: 40 }}
                </div>
            {%- endif -%}
            
            {%- if latest_post.tags and latest_post.tags.size > 0 -%}
                <div class="latest-post-tags">
                    {%- for tag in latest_post.tags limit: 4 -%}
                        <span class="tag">{{ tag }}</span>
                    {%- endfor -%}
                </div>
            {%- endif -%}
            
            <div class="latest-post-actions">
                <a href="{{ latest_post.url | relative_url }}" class="read-post-button">
                    Read Full Post →
                </a>
                <a href="{{ '/blog' | relative_url }}" class="view-all-link">
                    View All Posts
                </a>
            </div>
        </div>
    </div>
</section>
{%- endif -%}
