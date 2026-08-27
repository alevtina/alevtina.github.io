---
layout: post
title: "A palace for no one"
date: 2026-08-27
author: "Alevtina Verbovetskaya"
excerpt: "I built a full volunteer shift scheduler nobody asked for."
categories: [personal]
tags: [technology, aphantasia, side-projects]
---
Point me at a problem and I turn into a machine. Doesn't matter if anyone asked for a solution, or if the problem was even mine to solve. I do not stop until the thing exists.

The latest example: nobody asked me to build a volunteer shift scheduler for my kid's microschool, small enough that you can count the students on both hands. There was no committee meeting, no request, no line item. I had an idea about how sign-ups, calendars, and coordinator notifications could work together, and within a couple of days I had a working Google Sheet, a Form, an Apps Script, automated Calendar invites, email notifications routed to the right coordinator, data validation, the whole thing. I used Claude Code to build most of it, going back and forth, feature by feature, bug by bug.

It works. It's good.

No one is using it.

## Why I have to build the thing to think about the thing

I have aphantasia. I don't have a mind's eye. When people say "picture a beach," I get sand and water—facts, not a picture. No time of day, no crowd, nothing to look at. So instead of holding an idea in my head, I build a rough version of it and turn that over in my hands instead: a doc, a spreadsheet, a script, something running in front of me that I can poke at.

You can see this all over the scheduler. While testing, I imagined someone hitting "submit" and thinking, *Yes, but I can only make the first hour.* There wasn't a good way to say that, so I added a comment field. The notification email originally just confirmed a submitted shift. Then I looked at it and thought: why shouldn't the director be able to click straight into the Calendar event and edit the shift? So I added that too. None of it was planned in advance. I just kept finding gaps because the thing was finally sitting in front of me.

I needed the proof of concept to exist so I could hand it to someone and say, "Here, this is what was in my head. Can you see it? Do you understand what I mean?" I can't sketch an idea in a sentence and have it land the way it does for me. What I can hand someone is a working thing. The build is the pitch.

## Ahead of myself

I built an entire, working system before I knew whether anyone else wanted it. It's technically live: two program directors have real Calendar-linked email addresses configured, the Form works, the notifications work, and none of it has been discussed with the directors or handed to a single volunteer. So, yes, I may have gotten a little ahead of myself.

I might be the only one who thinks an arguably overengineered volunteer scheduler is worth building for a place that's already $35,000 in the red. Tuition is sliding-scale with no income verification, so there's no lever to pull when a year goes bad, and no staff to spare for anything beyond keeping the doors open. There are bigger problems here I can't fix, and maybe building is what I do when I need to feel like I'm doing something.

Or maybe this is simply how I contribute: I see a problem, I make a thing, and then I put it on the table and see if anyone else finds it useful.