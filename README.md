# Scrib, a Python IRC Chat Bot
<pre>
License:	GNU GPL v2 <https://www.gnu.org/licenses/old-licenses/gpl-2.0.html#SEC1>
Authors:	See AUTHORS
</pre>

[ ![Codeship Status for scoundrels/scrib](https://codeship.io/projects/cf8473b0-129d-0131-7f02-02093dca7a42/status?branch=master)](https://codeship.io/projects/7883)

Scrib is a chat bot that learns from conversations, and self-optimizes its information. 

Scrib's ancestors include PyBorg and Alia, but with the intention to be far more extendible (via PluginManager) and more robust.  
Their brains *might* be upgradable into the new system. Let us know if you try!

## What You'll Need
* [python-irclib](http://python-irclib.sourceforge.net)
* [BeautifulSoup](http://www.crummy.com/software/BeautifulSoup/)

Install them via your OS repository, the links above, or `pip install -r requirements.txt`

## The interfaces
Scrib comes with three interfaces by default:

* Command line: 'python start.py' starts the default command interface.
* IRC: 'python start.py irc' loads the irc interface (and makes accessible irc plugins)
* Feedme: 'python start.py feedme' Interactive way to 'feed' scrib data from plaintext documents.

## Initial Setup
* Run `./start.py`, enter your name, then `!quit`. This generates configuration files.
* Navigate to `conf/` and edit `scrib.cfg` and `brain.cfg` to your liking.
**Note**: Other interfaces and plugins may generate new configuration files (such as irc), so you will want to edit those too.

## Configuration
Here's an outline of configuration file options:

### scrib.cfg
_(General Scrib options)_
```
{
    "debug": 0,			Toggles debug mode for core scrib functionality. 
    "muted": 0, 		Toggles whether or not scrib can speak.
	"reply_rate": 100, 			Percent chance of reply per line (hectic in busy channels)
    "nick_reply_rate": 100, 	Percent chance of reply when highlighted.
    "version": "1.2.0", Denotes the version scrib was last time it ran (automatically changes on updates)
    "name": "scrib"		The name you want your scrib to have.
}
```
### brain.cfg
```
{
    "num_aliases": 0, 	This is the number of aliases this scrib knows. (Auto updates)
    "symbol": "!", 		This is the symbol that you use to send commands. If no command, scrib will ignore any line starting with it.
    "num_contexts": 0,  This is the number of aliases this scrib knows. (Auto updates)
    "ignore_list": [], 	These are the users the bot ignores.
    "max_words": 1000000, This is the maximum words this scrib can know. 
    "learning": 1, 		Toggles whether or not this scrib will learn from chats.
    "debug": 0, 		Toggles debug mode for brain functions.
    "num_words": 0, 	This is the number of words this scrib knows. (Auto updates)
    "optimum": 0, 		Toggles a more aggressive "optimal" state for the brain (Highly Unstable at this time)
    "censored": [], 	These words are censored and scrib will not learn.
    "aliases": {}		This is a dictionary of words that will be aliased.
}
```
### irc.cfg
_(IRC-specific options)_
```
{
    "channels": [
        "#scoundrels"			All the channels you want the scrib to join, comma separated.
    ], 
    "quit_message": "Goodbye.", What the scrib says when it leaves a chat room.
    "owners": [
        "OwnerOne"				A list of people authorized to send owner commands to scrib.
    ], 
    "realname": "Scrib Bot", 	The "real name" reported to the IRC server(s)

    "owner_passwords": [
        "Ducks"					The password(s) used to let persons take ownership of scrib.
    ], 
    "servers": [
        [
            "irc.freenode.net", List of server and port to join on start.
            6667
        ]
    ]
}
```

## Commands
[TODO: Compile a list of built-in commands.]

## Notes
Table of representation regarding terminal output.
```
[!] = Error
[#] = loading/saving brain
[~] = action
[-] = message
```
