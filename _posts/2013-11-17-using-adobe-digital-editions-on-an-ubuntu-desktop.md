---
layout: post
title: "Using Adobe Digital Editions on an Ubuntu desktop"
date: "2013-11-17"
categories: 
  - "general"
tags: 
  - "ade"
  - "adobe"
  - "adobe-digital-editions"
  - "digital-editions"
  - "e-readers"
  - "nook"
  - "ubuntu"
  - "wine"
  - "winetricks"
---

[I recently purchased a new laptop and installed the Ubuntu OS on it.](https://acid-stars.com/2013/11/16/need-moar-tech/trackback/) However, in my excitement to install a UNIX-like working environment, I forgot that some software works only with the two major operating systems (i.e., Windows and Mac). Namely, I needed to install [Adobe Digital Editions](http://www.adobe.com/products/digital-editions.html) on my new machine and panicked briefly when I realized I couldn't do that. But after some quick research, I learned how to install ADE and then have it recognize my e-reader.

1. Open the Ubuntu Software Center and search for [Wine](http://www.winehq.org/). Install it.
![ebook_software_center](/assets/img/ebook_software_center.png)

2. From the dash, open Winetricks. Choose "install an app." Select "adobe\_diged" and hit OK.
![ebook_winetricks_install_ade](/assets/img/ebook_winetricks_install_ade.png)

3. Go through the installation steps. Agree to the EULA. Authorize the computer with your Adobe ID. Close ADE.
![ebook_ade_authorize](/assets/img/ebook_ade_authorize.png)

4. From the dash, open Winetricks. Choose "select adobe_diged (Adobe Digital Editions)" and then select "Run winecfg." Under the "Drives" tab, create a new drive letter N (it auto-mounts elsewhere but does not keep changes), add directory `/media/nook/` (or the specific location of your Nook on your machine), and change type to "Floppy drive" (under advanced options).
![ebook_winecfg_drives](/assets/img/ebook_winecfg_drives.png)

That's it! You now have ADE 1.7.2 installed on your Ubuntu machine that can be accessed from the dash. Use it to download library e-books, authorize protected PDFs, move books to your Nook\*, and so on.

\* I've only tested this setup with a [Nook](http://www.barnesandnoble.com/nook/) but I assume the same steps will work for all other ADE-supported e-reading devices.

**Resources**

* [Howto install Adobe Digital Editions on Ubuntu 12.04 and use it with an e-book reader](http://robert.penz.name/440/howto-install-adobe-digital-editions-on-ubuntu-12-04-and-use-it-with-an-e-book-reader/)
* [Using Adobe Digital Editions to transfer books to the Nook, or a workaround](http://askubuntu.com/questions/32549/using-adobe-digital-editions-to-transfer-books-to-the-nook-or-a-workaround/308569#308569)
