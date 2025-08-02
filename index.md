---
layout: default
title: Home
description: "University Director of Library Systems at The City University of New York. Leading digital transformation and technology innovation in academic library systems."
---

<section class="hero">
    <div class="hero-content">
        {% include gravatar.html size="200" class="hero-image" %}
        <h1 class="hero-title">{{ site.author.name }}</h1>
        <p class="hero-subtitle">{{ site.author.title }}</p>
        <p class="hero-description">
            {{ site.author.bio }}
        </p>
        <a href="#contact" class="cta-button">Get In Touch</a>
    </div>
</section>

<section id="about" class="section">
    <h2 class="section-title">About</h2>
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
                I'm committed to leveraging emerging technologies to enhance library services, from implementing modern integrated library systems to developing digital scholarship platforms that support 21st-century research and learning.
            </p>
        </div>
    </div>
</section>

<section id="experience" class="section">
    <h2 class="section-title">Professional Experience</h2>
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
                • Spearheaded migration to next-generation library management systems<br>
                • Implemented comprehensive digital asset management solutions<br>
                • Enhanced user experience through modern discovery interfaces<br>
                • Established robust data governance and security protocols
            </p>
        </div>
    </div>
</section>

<section id="skills" class="section">
    <h2 class="section-title">Areas of Expertise</h2>
    <div class="skills-grid">
        <div class="skill-item">
            <div class="skill-title">Library Technology Systems</div>
            <div>ILS, Discovery, Digital Collections</div>
        </div>
        <div class="skill-item">
            <div class="skill-title">Project Management</div>
            <div>Strategic Planning, Implementation</div>
        </div>
        <div class="skill-item">
            <div class="skill-title">User Experience</div>
            <div>Interface Design, Accessibility</div>
        </div>
        <div class="skill-item">
            <div class="skill-title">Team Leadership</div>
            <div>Cross-functional Collaboration</div>
        </div>
    </div>
</section>

<section id="contact" class="section">
    <h2 class="section-title">Contact</h2>
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
