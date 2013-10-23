Scrib, the IRC ChatBot
======================
<pre>
License:        GNU AGPLv3 or later
Author:         Sina Mashek 
Email:          mashek [ at ] thescoundrels [ dot ] net
</pre>

What You'll Need
----------------
* [python-irclib](http://python-irclib.sourceforge.net) Most distros: install python-irclib

Initial Setup
-------------
* Please edit the configuration files in conf/ before running.

Configuration
=============
Here's an outline of configuration file options.

scrib.cfg
---------
_(Internal options)_

scrib-irc.cfg
-------------
_(IRC-specific options)_

Commands
========
These are the currently built-in commands.

Public/Private Commands
---------------
_(These are only public if private is set to 0)_

Owner Commands
----------------
_(These are only available to listed bot owners)_


Optional
--------
* [megahal](http://megahal.alioth.debian.org/) Most distros: install megahal
* [espeak](http://espeak.sourceforge.net/) Most distros: install espeak

MegaHAL is an alternative parser that is totally unsupported and kind of, well, deprecated. At some point, it should probably be decoupled from scrib.

Notes
-----
* feedme.py lets you fill scrib's brain with text from a file.
* Will be moving to using PyBrain. Maybe. Eventually.

TODO
====
* Consolidate configuration to make easier to use
* Break code into more manageable chunks
* Adopt a better coding policy