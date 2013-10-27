Scrib, the IRC ChatBot
======================
<pre>
License:		GNU GPLv2
Authors:        See AUTHORS
</pre>

Scrib is an IRC learning chat bot that self-optimizes. It can also be taught through various commands.

Scrib's origins lie within the sources of Pyborg, which was written by Tom Morton and Sébastian Dailly. It was a simple Markov chain-driven bot, similar to MegaHAL, but with the unique ability to learn patterns of speech by figuring out what words go together well. This gives the bot the ability to come up with its own replies, as well as repeating previously learned phrases. There have been pieces absorbed from the Alia fork of Pyborg, as well.

Though Scrib is based on Pyborg, very little of the bot is compatible with any other Pyborg (including the original)! The intention is to morph this bot into something more robust, while maintaining speed and reliability and extendability.


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
We are in the process of moving all commands to the plugin architecture. These are the commands that have been plugin-ized.

Public/Private Commands
---------------
_(These are only public if private is set to 0)_
* Control (to become a controller of the bot)
 * !control
* Echo (echoes what you type)
 * !echo

Owner Commands
----------------
_(These are only available to listed bot owners)_
* Basic IRC Commands:
 * !join
 * !part,
 * !nick,
 * !chans,
 * !quitmsg,
 * !quit,
 * !ignore,
 * !unignore,
 * !replyIgnore
* Private (command setting control)
 * !private
* Reply Rate (verbosity of the bot)
 * !replyrate
* Sleep and Wake (force a bot to be quiet)
 * !sleep
 * !wake

Plugins
-------
_(These are bundles that extend functionality through other services)_
* Twitter (Tweet last statement and/or select statements to tweet on bot's own)
 * !tweet
 * More TBD

Optional
--------
* [megahal](http://megahal.alioth.debian.org/) Most distros: install megahal
* [espeak](http://espeak.sourceforge.net/) Most distros: install espeak
* [Python Twitter Tools](http://mike.verdone.ca/twitter/) Most distros: easy_install twitter (For Twitter plugin)
MegaHAL is an alternative parser that is totally unsupported and kind of, well, deprecated. At some point, it should probably be decoupled from scrib.

Notes
-----
* feedme.py lets you fill scrib's brain with text from a file.
* Will be moving to using PyBrain. Maybe. Eventually.

[!] = Error
[#] = loading/saving brain
[~] = action
[-] = message

TODO
====
* Consolidate configuration to make easier to use
* Break code into more manageable chunks
* Adopt a better coding policy
