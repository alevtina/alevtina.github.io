---
layout: post
title: "Drupal 7: Friendly URLs for personal user contact forms"
date: "2013-09-17"
categories: 
  - "cms"
tags: 
  - "alias"
  - "contact"
  - "contact-form"
  - "drupal"
  - "form"
  - "friendly-urls"
  - "modules"
  - "pathauto"
  - "redirect"
  - "subpathauto"
  - "support-site"
  - "upgrade"
---

I've been working with [Drupal](http://www.drupal.org/) for the last year in my current position (as University Web & Mobile Systems Librarian at the [City University of New York](http://www.cuny.edu/)) and I have a love-hate relationship with it. I appreciate its power and agility but curse its complexity, especially for the lay end-user. The biggest project thus far has been moving the department's support site from Drupal 6 to the newest version of Drupal 7. There's no easy way to accomplish this so I've been doing it manually, using [Node Export](https://drupal.org/project/node_export) and [Feeds](https://drupal.org/project/feeds) to move data from one instance to the other. It's been tedious work but manageable since it's a small site.

One of the biggest [Y U NO WORK!?](http://knowyourmeme.com/memes/y-u-no-guy) moments was trying to figure out why users' personal contact forms were not conforming to the friendly URL pattern I'd set up with [Pathauto](https://drupal.org/project/pathauto/):

![Drupal 7 Pathauto User Paths](http://blog.verbovetskaya.com/wp-content/uploads/2013/09/d7_-_pathauto_-_user_paths.png)

No matter what I did, the users' contact forms were always located at `user/[uid]/contact` (and not at the desired `users/[user:name]/contact`). The thing that confused me the most, though, was that this wasn't a problem in our current D6 instance and that's because Pathauto 6.x-1.6 contains a separate field for user contact forms paths:

![Drupal 6 Pathauto User Paths](http://blog.verbovetskaya.com/wp-content/uploads/2013/09/d6_-_pathauto_-_user_paths.png)

Frustratingly, there's no such field in Pathauto 7.x-1.2.

...There is, however, [Sub-pathauto](https://drupal.org/project/subpathauto)— a totally separate module that does exactly what it sounds like. It creates sub-path URL aliases for patterns created with Pathauto. I installed it\* as soon as I learned about its existence:

{% highlight terminal %}
$ drush dl subpathauto
$ drush en -y subpathauto
$ drush cc all
{% endhighlight %}

And, _presto_! Users' personal contact forms are now at the desired `users/[user:name]/contact` location. (However, they are also at the previous—and undesired—`user/[uid]/contact` location so be sure to install [Redirect](https://drupal.org/project/redirect) to remove the duplicated URLs.)

Now why didn't Pathauto for D7 come standard with this functionality?

* * *

\* [Drush](https://github.com/drush-ops/drush) is seriously awesome.
