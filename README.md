Scrib, the IRC ChatBot
======================
<pre>
License:	GNU GPLv2
Authors:	See AUTHORS
</pre>
[![Build Status](https://travis-ci.org/scoundrels/scrib.png?branch=master)](https://travis-ci.org/scoundrels/scrib)

Scrib is a learning chat bot that self-optimizes. It can also be taught through various commands.

Scrib's origins lie within the sources of Pyborg, which was written by Tom Morton and Sébastian Dailly. It was a simple Markov chain-driven bot, similar to MegaHAL, but with the unique ability to learn patterns of speech by figuring out what words go together well. This gives the bot the ability to come up with its own replies, as well as repeating previously learned phrases. There have been pieces absorbed from the Alia fork of Pyborg, as well.

Though Scrib is based on Pyborg, very little of the bot is compatible with any other Pyborg (including the original)! The intention is to morph this bot into something more robust, while maintaining speed, reliability and providing extendability though use of the PluginManager.

IRC is no longer the main focus of scrib, but rather, one of the several ways to interact.

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
_(General Scrib options)_
```
pubsym	= '!'			This is the "public symbol" that the bot will prepend to any command reply.
num_aliases	= 0 		This is the number of total aliases known. *Needs to be moved to brain/knowledge*
no_save	= 'False'		Setting this to true will disable brain saving.
ignore_list	= ['!']		This is a list of items to ignore and not reply *Doesn't seem to work*
length	= 25			This is the length of formed reply. If it goes over this number of characters, the bot won't reply.
max_words	= 10600		This is the maximum number of words allowed in the bot's brain.
learning	= 1			This toggles whether the bot is in learning mode.
debug	= 0				This toggles whether or not the bot is in debug mode. Debug mode makes more verbose terminal messages.
censored	= ['']		If a statement contains any words in this list, that message is ignored.
aliases	= {}			These are a list of similar words.
```

scrib-irc.cfg
-------------
_(IRC-specific options)_
```
owners = ['']			This lets you set a list of people that can use all bot commands.
reply_chance = 50		This is the percent(%) chance that the bot will reply.
nick_reply_chance = 100	This is the percent(%) chance that the bot will reply when highlighted.
realname = 'Bot Name'	This is the 'real name' reported to the IRC server.
myname = 'scrib'		This is your bot's nickname.
replyIgnored = 0		Setting this to 1 will allow your bot to reply to people that are on the ignore list, but not learn from them.
servers = [('', 6667)]	This is a list of servers that your bot can connect to. For now, only one is supported.
ignorelist = ['']		This is the list of ignored nicks.
private = 1				Setting this to 0 will allow others to use the public IRC commands.
chans = ['']			These are the channels the bot will join, across all servers.
password = 'sekrit'		This is your admin password. Generally you won't want to give this out.
speaking = 1			This toggles whether or not the bot talks.
quitmsg = 'Quitting.'	This is the message channels see when the bot quits IRC.
```
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


```
[!] = Error
[#] = loading/saving brain
[~] = action
[-] = message
```

TODO
====
* Consolidate configuration to make easier to use
* Break code into more manageable chunks
* Adopt a better coding policy
