---
layout: post
title: "Linking to Aleph OPAC and search results"
date: "2013-10-28"
author: "Alevtina Verbovetskaya"
excerpt: "Linking to Aleph OPAC searches requires removing session IDs from URLs and using specific parameters like find_scan_code—here's how to create persistent, proxied links."
categories: 
  - "ils"
tags: 
  - "aleph"
  - "ccl"
  - "link"
  - "opac"
  - "search"
---

**Update**: This post was updated in August 2014 to reflect the new URL for the CUNY Catalog.

[Linking to the Aleph OPAC](#linking-to-the-aleph-opac) is easy. [Linking to a specific search](#linking-to-a-specific-search) is... well, it's not as easy and it requires some practice. I'll explain how to do them both.

### Linking to the Aleph OPAC

I don't know how other institutions do it but, at CUNY, we encourage folks to [proxy their OPAC links](http://www.oclc.org/support/services/ezproxy/documentation/example/opac.en.html). This ensures that when a user attempts to view an e-resource, he/she will be able to authenticate himself/herself and gain access to that resource. Otherwise, the user will be stuck behind a paywall.

So what does the URL look like? In its simplest form, it's just the URL to the OPAC prefixed by the proxy URL:

`http://central.ezproxy.cuny.edu:2048/login?url=http://libsearch.cuny.edu/F/`

Of course, this is going just through the central office proxy server (ensuring access only to CUNY-wide e-resources, not campus-specific ones) and doesn't specify a "local base," or a library scope, so it defaults to the union (or all CUNY libraries) view. To tailor this link to your specific library, you will need to know your college's [proxy server](http://support.cunylibraries.org/libraries/proxy-servers) and your [Aleph local base](http://support.cunylibraries.org/libraries/local-base-values). Then you'll end up with a link that looks like this:

`https://login.remote.baruch.cuny.edu/login?qurl=http://libsearch.cuny.edu/F/?func=find-b-0&local_base=BARUCH`

Using this properly formatted URL, your patrons will be defaulted to their local library search scope and they will be pinged for authentication when they reach a licensed e-resource.

### Linking to a specific search

But what about when you want to link to a specific search? For example, a faculty member would like to link to all the library's holdings of Junot Diaz's work from her Blackboard course site. How can we help her with this?

It's not enough to just do a search and then copy & paste the resulting URL. You will be stuck with a unique session ID in that URL that will expire and cause the link to default to the basic search screen. This then leads to confusion and frantic emails. The simplest solution, then, is to take that search result URL...

`http://libsearch.cuny.edu/F/7C3C7V4U65QEI7DY79FFUP7LIKY3K1289DEAALI48L6LJF4D34-13445?func=find-e&find_scan_code=FIND_WAU&request=junot+diaz&local_base=LEHMAN`

...and remove the session ID. In the URL above, it's the gobbledygook (yes, that's the technical term for it) after the `F/` and before the `?func`. So the new, persistent (and proxied!) URL will be:

`http://memex.lehman.cuny.edu:2048/login?url=http://libsearch.cuny.edu/F/?func=find-e&find_scan_code=FIND_WAU&request=junot+diaz&local_base=LEHMAN`

There are several things to note here:

- This is scoped to Lehman College and goes through their proxy server. If you want to narrow it to your own library (or broaden it to all the CUNY libraries), choose the appropriate [Aleph local base](http://support.cunylibraries.org/libraries/local-base-values) and [proxy server](http://support.cunylibraries.org/libraries/proxy-servers).
- The `find_scan_code` parameter has the value `FIND_WAU`, which means we're searching for a keyword (that's the `find` part) in the author field (that's the `wau` part). If you need to perform a different search, you will need to select a different search type (or value for the `find_scan_code` parameter):
    - `FIND_WRD`: All Fields
    - `SCAN_TTL`: Title begins with
    - `SCAN_AUT`: Author, last name first
    - `SCAN_SUL`: Subject begins with
    - `FIND_WTI`: Keyword in title
    - `FIND_WAU`: Keyword in author
    - `FIND_WSU`: Keyword in subject
    - `SCAN_SUC`: Children's subject begins with
    - `SCAN_SUM`: MeSH subject begins with
    - `SCAN_SHL`: Call number
    - `SCAN_ISBN`: Browse ISBN
    - `SCAN_ISSN`: Browse ISSN
    - `SCAN_SYS`: Browse Aleph system number
- The `request` parameter is where you enter your query. Spaces need to be replaced with a plus sign (+). In our example above, notice how the query reads `junot+diaz`.

It is also possible to construct a much more complicated URL: `https://login.remote.baruch.cuny.edu/login?qurl=http://libsearch.cuny.edu/F/?func=find-c&ccl_term=wow%3Dbb%20and%20wti%3DAmerican+directories&local_base=U-JOURNAL`

Here, instead of a `find_scan_code`, we're using a `ccl_term` (Common Command Language), which is a way to construct a more complex search in the URL. Furthermore, the query for the [2-letter OWN code](http://support.cunylibraries.org/libraries/own-codes) (`wow=bb`) and keyword in title (`wti=American+directories`) used in the `ccl_term` parameter in this example includes escape sequences for some of the following characters:

- `=` represented as `%3D`
- `"` represented as `%22`
- `(` represented as `%28`
- `)` represented as `%29`
- (space) represented as `%20`

These characters have to be escaped in the `ccl_term` parameter. For a list of the CCL terms, see the [CUNY Catalog help files](http://libsearch.cuny.edu/F/?func=file&file_name=help-1#ccl).

### Embedding a search box

Instructions for embedding a search box to the CUNY Catalog from anywhere (e.g., LibGuides, SerialsSolutons, etc.) are too long to include in this post. However, they are available on the [Support @ OLS](http://support.cunylibraries.org/systems/aleph/web-opac/search-box) website.
