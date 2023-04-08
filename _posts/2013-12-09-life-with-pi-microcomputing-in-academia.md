---
layout: post
title: "Life with Pi: Microcomputing in Academia"
date: "2013-12-09"
last_modified_at: "2023-04-08"
categories: [research]
tags: [arduino, beaglebone, conference, microcomputers, microcomputing, presentation, raspberry-pi, single-board-computers]
---

Last Friday, I co-led a presentation on single-board computers at the [2013 CUNY IT Conference](http://www.centerdigitaled.com/events/CUNY-IT-Conference-2013.html). Since it was a very well-attended session (where we had great discussions with the attendees), I thought I'd provide a brief recap and link to the presentation material.

### Life with Pi: Microcomputing in Academia

![Life with Pi: Microcomputing in Academia](http://blog.verbovetskaya.com/wp-content/uploads/2013/12/life_with_pi_-_microcomputing_in_academia.png)

#### Introduction to single-board computers

[Allie Verbovetskaya](http://www.verbovetskaya.com/), Web & Mobile Systems Librarian / CUNY

Before we began with the "formal" presentation, I showed a brief video: 

<iframe src="//player.vimeo.com/video/55658574?title=0&amp;byline=0&amp;portrait=0&amp;color=ffffff" width="800" height="450" frameborder="0" webkitallowfullscreen mozallowfullscreen="" allowfullscreen=""></iframe>

Once the audience was thoroughly confused, I explained that the [BeetBox](http://scott.j38.net/interactive/beetbox/) is a quite literal "beatbox" that uses beets as percussion instruments. To achieve this, there are touch sensors in the beets that are wired to a Raspberry Pi. To emit the drum sounds, there is an amplifier and a speaker also hooked up to the RPi. There is a Python program that's running on the RPi and translating the touches into drum samples. The RPi powers this apparatus behind-the-scenes.

But what is a Raspberry Pi? It is a type of microcomputer. So what's a microcomputer? It's a single-board computer that's small, cheap, and open source. It's about the size of a credit card and varies in price from $25 up to $100. As such, it's quite an affordable little machine, containing all the parts of a functional computer: microprocessor, RAM, I/O, power supply, and so on.

The most popular microcomputer—at the moment, anyway—is the [Raspberry Pi](http://www.raspberrypi.org/). It's $25 for the base model and $35 for the "souped up" version (with more RAM and ports). Another one that comes up frequently is the [BeagleBone](http://beagleboard.org/Products/BeagleBone) (brought to you by [Texas Instruments](http://www.ti.com/), the calculator guys) and it's quite a bit more expensive at $89. And, the one that's been around the longest, is the [Arduino](http://www.arduino.cc/). They have several boards but the Uno board costs $30.

So now that we understand what they are... what are they for? Well, they can be used for hobbies, such as [building a retro arcade gaming station](http://learn.adafruit.com/retro-gaming-with-raspberry-pi) or [home brewing](http://brewpi.com/). Or they can be used to solve specific problems, such as the [RFID pet feeder](http://www.instructables.com/id/RFID-pet-feeder/) which was created by someone who needed to feed one of his cats a medicated food and, therefore, could not have his two cats eating each other's food. (What the creator did was program an Arduino to move the lid on the appropriate food dish based on the cat that approaches the feeding station. This is done via RFID chips that have been attached to the cats' collars. That way, when Sick Cat approaches the feeding area, her food is made available to her. When she walks away, the lid slides back over so no one cat eat. Then, when Healthy Cat gets hungry, the lid covering her food opens so she can eat. And so on.) Another use is for data collection, such as the [Botanicalls kit](http://www.botanicalls.com/) which allows a user to measure a plant's comfort levels (moisture in the soil, amount of sunlight, etc.) and tweet "status updates" so you can tell when your plant is thirsty or too hot. (It will also respond to changes in its status, so if it's thirsty and you watered it, it'll submit a tweet of thanks.)

So you can begin to see how microcomputers can be used for more than basic tinkering. But you may also be thinking: "That's great but I'm not a programmer!" And that's OK! You don't have to be. Because these microcomputers are open source, there are large and dedicated communities surrounding each. There are plenty of tutorials and guides online—as well as complete projects!—that you can use to get started. You can also seek help from many places, including:

- [http://www.adafruit.com/](http://www.adafruit.com/)
- [http://www.makezine.com/](http://www.makezine.com/)
- [http://www.themagpi.com/](http://www.themagpi.com/)
- [http://www.element14.com/](http://www.element14.com/)
- [http://raspberrypi.stackexchange.com/](http://raspberrypi.stackexchange.com/)

But why should you bother to do any of this? Well, there are actually uses beyond recreation. In fact, there is evidence of more and more applications in academia. My colleague Junior discussed uses in the classroom while Robin explained how microcomputers can be used in and for research. Steve discussed the benefits of teaching microcomputing techniques and explain why computational literacy is becoming more important in today's world. The presentation was then rounded out with demonstrations of projects that each of us had constructed, followed by questions from the audience.

#### Uses in pedagogy

[Junior Tidal](http://www.juniortidal.com/), Web Services & Multimedia Librarian / NYCCT

Junior discussed uses of microcomputers in the classroom, including:

- Individual research stations
- Cross-disciplinary projects
- Testing environment for coding projects
- Class/course web server per class/student for ad hoc storage or collaboration
- Paperless archive repository for classes

You can also see Junior's write-up of our presentation for more information about his section: [http://juniortidal.com/2013/12/life-of-pi/](http://juniortidal.com/2013/12/life-of-pi/).

#### Uses in research

[Robin Davis](http://www.robincamille.com/), Emerging Technologies & Distance Services Librarian / John Jay College

Robin opened with several real-life examples of microcomputers currently being used for research purposes. She then outlined other venues for using single-board computers in and for research:

- Cheap, disposable computing in the lab or studio
- Use inexpensive sensors (e.g., temperature, motion, light, GPS, acceleration, etc.)
- Build prototypes quickly
- Maintain tight control over your machine(s)
- Topic of publication (both scholarly and popular)

For a complete overview of Robin's contribution to the presentation, see the write-up on her website: [http://www.robincamille.com/presentations/microcomputing/](http://www.robincamille.com/presentations/microcomputing/).

#### Computational literacy

[Stephen Zweibel](http://www.zweibel.org/), Visiting Lecturer (Librarian) / Hunter College

Steve discussed the importance of computational literacy and how microcomputers can be used to teach this literacy to the next generation of learners. He defined "computational literacy" as the ability to use computers and computational technologies to solve problems, and explained how it supports algorithmic thinking and collaboration.

#### Demonstrations

- I discussed setting up a personal Dropbox-clone using an [ownCloud](http://www.owncloud.com/) instance on a Raspberry Pi-powered web server, to be used as a classroom repository or just a safe place to store potentially sensitive materials.
- Junior demonstrated his "auto-citation" project. Using the [Open Library API](https://openlibrary.org/developers/api), he created a script that makes it possible to scan an ISBN (or enter it manually) and get a citation (in APA, MLA, and Chicago styles) in return.
- Robin showed a light level logger, wherein she used Python to read data submitted by a 95¢ photocell sensor wired on a breadboard (hooked up to a Raspberry Pi).
- Steve described the concept of a [LibraryBox](http://jasongriffey.net/librarybox/) (digital file repository available via its own Wi-Fi signal) and encouraged the audience to connect to his LibraryBox network and download some documents to see his project in action.

### Presentation Material

The slides are available online: [http://www.robincamille.com/jj/cunyit/](http://www.robincamille.com/jj/cunyit/).

We also created a handout that was made available at the presentation. You can download it from [http://www.robincamille.com/jj/cunyit/handout.pdf](http://www.robincamille.com/jj/cunyit/handout.pdf).

### Colophon

The four co-presenters worked on this presentation collaboratively using git and a shared repository on [GitHub](http://www.github.com/): [https://github.com/szweibel/CUNY-IT-Presentation](https://github.com/szweibel/CUNY-IT-Presentation). It was the first time any of us has used GitHub in this manner and it proved quite successful.

We used the [reveal.js presentation framework](https://github.com/hakimel/reveal.js/) for our slides. It's very easy to use and provides beautiful (and responsive!) slidedecks.
