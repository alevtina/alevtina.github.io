---
layout: default
title: Knitting
permalink: /knitting/
description: "Knitting and crochet projects, synced from Ravelry."
---

<div class="knitting-log">
  <h1>Knitting</h1>
  <p>Projects synced from <a href="https://www.ravelry.com/people/alevtina" rel="noopener noreferrer" target="_blank">Ravelry</a>.</p>

  {%- assign all_projects = site.knitting | sort: "date" | reverse -%}

  {%- assign in_progress = all_projects | where: "status", "in-progress" -%}
  {%- if in_progress.size > 0 -%}
  <section class="knitting-section">
    <h2>In Progress</h2>
    <ul class="knitting-list" role="list">
      {%- for project in in_progress -%}
      <li class="knitting-item">
        {%- if project.cover and project.cover != "" -%}
        <a href="{{ project.url | relative_url }}" class="knitting-cover-link" tabindex="-1" aria-hidden="true">
          <img class="knitting-cover" src="{{ project.cover | escape }}" alt="" loading="lazy" />
        </a>
        {%- else -%}
        <a href="{{ project.url | relative_url }}" class="knitting-cover-link" tabindex="-1" aria-hidden="true">
          <div class="knitting-cover-placeholder"></div>
        </a>
        {%- endif -%}
        <div class="knitting-item-info">
          <a class="knitting-title" href="{{ project.url | relative_url }}">{{ project.title | escape }}</a>
          {%- if project.category and project.category != "" -%}
          <span class="knitting-category">{{ project.category | escape }}</span>
          {%- endif -%}
          {%- if project.designer and project.designer != "" -%}
          <span class="knitting-designer">{{ project.designer | escape }}</span>
          {%- endif -%}
        </div>
      </li>
      {%- endfor -%}
    </ul>
  </section>
  {%- endif -%}

  {%- assign finished = all_projects | where: "status", "finished" -%}
  {%- if finished.size > 0 -%}
  <section class="knitting-section">
    <h2>Finished</h2>

    {%- assign years_seen = "" | split: "" -%}
    {%- for project in finished -%}
      {%- assign y = project.date | date: "%Y" -%}
      {%- unless years_seen contains y -%}
        {%- assign years_seen = years_seen | push: y -%}
      {%- endunless -%}
    {%- endfor -%}

    {%- for year in years_seen -%}
    <h3>{{ year }}</h3>
    <ul class="knitting-list" role="list">
      {%- for project in finished -%}
        {%- assign project_year = project.date | date: "%Y" -%}
        {%- if project_year == year -%}
        <li class="knitting-item">
          {%- if project.cover and project.cover != "" -%}
          <a href="{{ project.url | relative_url }}" class="knitting-cover-link" tabindex="-1" aria-hidden="true">
            <img class="knitting-cover" src="{{ project.cover | escape }}" alt="" loading="lazy" />
          </a>
          {%- endif -%}
          <div class="knitting-item-info">
            <a class="knitting-title" href="{{ project.url | relative_url }}">{{ project.title | escape }}</a>
            {%- if project.pattern and project.pattern != "" -%}
            <span class="knitting-pattern">{{ project.pattern | escape }}</span>
            {%- endif -%}
            {%- if project.designer and project.designer != "" -%}
            <span class="knitting-designer">{{ project.designer | escape }}</span>
            {%- endif -%}
            {%- if project.yarn and project.yarn != "" -%}
            <span class="knitting-yarn">{{ project.yarn | escape }}{%- if project.colorway and project.colorway != "" -%} — {{ project.colorway | escape }}{%- endif -%}</span>
            {%- endif -%}
          </div>
        </li>
        {%- endif -%}
      {%- endfor -%}
    </ul>
    {%- endfor -%}
  </section>
  {%- endif -%}

  {%- if all_projects.size == 0 -%}
  <p>No projects yet — run the Ravelry sync workflow to populate this page.</p>
  {%- endif -%}
</div>
