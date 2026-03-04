---
layout: default
title: Reading Log
permalink: /reading/
description: "Books I've read, am reading, and want to read."
---

<div class="reading-log">
  <h1>Reading Log</h1>
  <p>Books I've read, am reading, and want to read—synced from Calibre-Web and published as <a href="https://indieweb.org/read">IndieWeb read posts</a>.</p>

  {%- assign all_reading = site.reading | sort: "date" | reverse -%}

  {%- comment -%} Currently Reading {%- endcomment -%}
  {%- assign currently_reading = all_reading | where: "status", "reading" -%}
  {%- if currently_reading.size > 0 -%}
  <section class="reading-section">
    <h2>Currently Reading</h2>
    <ul class="reading-list" role="list">
      {%- for book in currently_reading -%}
      {%- if book.author.first -%}
        {%- assign book_author = book.author | join: " and " -%}
      {%- else -%}
        {%- assign book_author = book.author -%}
      {%- endif -%}
      <li class="reading-item h-entry">
        <a class="u-url" href="{{ book.url | absolute_url }}" hidden></a>
        <data class="p-x-read-status" value="reading" hidden></data>
        <div class="p-read-of h-cite">
          {%- if book.cover and book.cover != "" -%}
          <a href="{{ book.url | relative_url }}" class="reading-cover-link" tabindex="-1" aria-hidden="true">
            <img class="reading-cover" src="{{ book.cover | escape }}" alt="" loading="lazy" />
          </a>
          {%- else -%}
          <a href="{{ book.url | relative_url }}" class="reading-cover-link" tabindex="-1" aria-hidden="true">
            <div class="reading-cover-placeholder"></div>
          </a>
          {%- endif -%}
          <div class="reading-item-info">
            <a class="p-name reading-title" href="{{ book.url | relative_url }}">{{ book.title | escape }}</a>
            {%- if book_author != "" -%}
            <span class="p-author reading-author">{{ book_author | escape }}</span>
            {%- endif -%}
            {%- if book.year -%}
            <span class="reading-year">{{ book.year }}</span>
            {%- endif -%}
          </div>
        </div>
      </li>
      {%- endfor -%}
    </ul>
  </section>
  {%- endif -%}

  {%- comment -%} Want to Read {%- endcomment -%}
  {%- assign to_read = all_reading | where: "status", "to-read" -%}
  {%- if to_read.size > 0 -%}
  <section class="reading-section">
    <h2>Want to Read</h2>
    <ul class="reading-list" role="list">
      {%- for book in to_read -%}
      {%- if book.author.first -%}
        {%- assign book_author = book.author | join: " and " -%}
      {%- else -%}
        {%- assign book_author = book.author -%}
      {%- endif -%}
      <li class="reading-item h-entry">
        <a class="u-url" href="{{ book.url | absolute_url }}" hidden></a>
        <data class="p-x-read-status" value="to-read" hidden></data>
        <div class="p-read-of h-cite">
          {%- if book.cover and book.cover != "" -%}
          <a href="{{ book.url | relative_url }}" class="reading-cover-link" tabindex="-1" aria-hidden="true">
            <img class="reading-cover" src="{{ book.cover | escape }}" alt="" loading="lazy" />
          </a>
          {%- else -%}
          <a href="{{ book.url | relative_url }}" class="reading-cover-link" tabindex="-1" aria-hidden="true">
            <div class="reading-cover-placeholder"></div>
          </a>
          {%- endif -%}
          <div class="reading-item-info">
            <a class="p-name reading-title" href="{{ book.url | relative_url }}">{{ book.title | escape }}</a>
            {%- if book_author != "" -%}
            <span class="p-author reading-author">{{ book_author | escape }}</span>
            {%- endif -%}
            {%- if book.year -%}
            <span class="reading-year">{{ book.year }}</span>
            {%- endif -%}
          </div>
        </div>
      </li>
      {%- endfor -%}
    </ul>
  </section>
  {%- endif -%}

  {%- comment -%} Finished — grouped by year {%- endcomment -%}
  {%- assign finished = all_reading | where: "status", "finished" -%}
  {%- if finished.size > 0 -%}
  <section class="reading-section">
    <h2>Finished</h2>

    {%- comment -%} Collect unique years in reverse-chronological order {%- endcomment -%}
    {%- assign years_seen = "" | split: "" -%}
    {%- for book in finished -%}
      {%- assign y = book.date | date: "%Y" -%}
      {%- unless years_seen contains y -%}
        {%- assign years_seen = years_seen | push: y -%}
      {%- endunless -%}
    {%- endfor -%}

    {%- for year in years_seen -%}
    <h3>{{ year }}</h3>
    <ul class="reading-list" role="list">
      {%- for book in finished -%}
        {%- assign book_year = book.date | date: "%Y" -%}
        {%- if book_year == year -%}
        {%- if book.author.first -%}
          {%- assign book_author = book.author | join: " and " -%}
        {%- else -%}
          {%- assign book_author = book.author -%}
        {%- endif -%}
        <li class="reading-item h-entry">
          <a class="u-url" href="{{ book.url | absolute_url }}" hidden></a>
          <data class="p-x-read-status" value="finished" hidden></data>
          <div class="p-read-of h-cite">
            {%- if book.cover and book.cover != "" -%}
            <a href="{{ book.url | relative_url }}" class="reading-cover-link" tabindex="-1" aria-hidden="true">
              <img class="reading-cover" src="{{ book.cover | escape }}" alt="" loading="lazy" />
            </a>
            {%- endif -%}
            <div class="reading-item-info">
              <a class="p-name reading-title" href="{{ book.url | relative_url }}">{{ book.title | escape }}</a>
              {%- if book_author != "" -%}
              <span class="p-author reading-author">{{ book_author | escape }}</span>
              {%- endif -%}
              {%- if book.year -%}
              <span class="reading-year">{{ book.year }}</span>
              {%- endif -%}
              {%- if book.rating -%}
              {%- assign _rparts = book.rating | split: "/" -%}
              {%- assign _rnum = _rparts[0] | plus: 0 -%}
              <span class="reading-rating star-rating" role="img" aria-label="{{ _rnum }} out of 5 stars">
                {%- for i in (1..5) -%}
                  {%- if i <= _rnum -%}<span class="star star--filled" aria-hidden="true">★</span>{%- else -%}<span class="star star--empty" aria-hidden="true">☆</span>{%- endif -%}
                {%- endfor -%}
              </span>
              {%- endif -%}
            </div>
          </div>
        </li>
        {%- endif -%}
      {%- endfor -%}
    </ul>
    {%- endfor -%}
  </section>
  {%- endif -%}

  {%- if all_reading.size == 0 -%}
  <p>No entries yet — run the Calibre sync workflow to populate this page.</p>
  {%- endif -%}
</div>
