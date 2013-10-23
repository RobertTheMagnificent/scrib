#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

# See scrib.py
sys.path.append('core/')
sys.path.append('plugins/')

try:
	from ircbot import *
	from irclib import *
except:
	print "Dearest User,\nircbot.py and irclib.py are not found. Please install them forthwith from\nhttp://python-irclib.sourceforge.net\n\nThank you,\nscrib"
	sys.exit(1)

# Let's override some irclib function
def my_remove_connection(self, connection):
	if self.fn_to_remove_socket:
		self.fn_to_remove_socket(connection._get_socket())

IRC._remove_connection = my_remove_connection

import os
import scrib
import cfgfile
import PluginManager
import random
import traceback
import thread

class ModIRC(SingleServerIRCBot):
	"""
	Interfacing some IRC I/O with scrib learn/reply modules!
	"""
	join_msg = "%s"# is here"
	part_msg = "%s"# has left"

	# We are going to store the owner's host mask :3
	owner_mask = []

	# IRC Command list
	commandlist =   "IRC Module Commands:\n!chans, !control, !ignore, !join, !nick, !part, !private, !quit, !quitmsg, !replyIgnored, !replyrate, !sleep, !unignore, !wake"
	# IRC Command 
	commanddict = {
		"sleep":  "Owner command. Usage: !sleep\nStop the bot talking.",
		"wake": "Owner command. Usage: !wake\nAllow the bot to talk.",
		"join": "Owner command. Usage: !join #chan1 [#chan2 [...]]\nJoin one or more channels.",
		"part": "Owner command. Usage: !part #chan1 [#chan2 [...]]\nLeave one or more channels.",
		"chans": "Owner command. Usage: !chans\nList channels currently on.",
		"nick": "Owner command. Usage: !nick nickname\nChange nickname.",
		"ignore": "Owner command. Usage: !ignore [nick1 [nick2 [...]]]\nIgnore one or more nicknames. Without arguments it lists ignored nicknames.",
		"unignore": "Owner command. Usage: !unignore nick1 [nick2 [...]]\nUnignores one or more nicknames.",
		"replyrate": "Owner command. Usage: !replyrate [rate%]\nSet rate of bot replies to rate%. Without arguments (not an owner-only command) shows the current reply rate.",
		"replyIgnored": "Owner command. Usage: !replyIgnored [on|off]\nAllow/disallow replying to ignored users. Without arguments shows the current setting.",
		"private": "Owner command. Usage: !private [on|off]\nTurn private mode on or off (disable non-owner commands and don't return CTCP VERSION). Without arguments shows the current setting.",
		"quitmsg": "Owner command. Usage: !quitmsg [message]\nSet the quit message. Without arguments show the current quit message.",
		"quit": "Owner command. Usage: !quit\nMake the bot quit IRC.",
		"control": "Usage: !control password\nAllow user to have access to bot commands."
	}

	commandlist += " "+PluginManager.ScribPlugin.plugin_aliases
	commanddict = dict( commanddict.items() + PluginManager.ScribPlugin.plugin_commands.items() )
	
	def __init__(self, my_scrib, args):
		"""
		Args will be sys.argv (command prompt arguments)
		"""
		# Scribbington
		self.scrib = my_scrib
		# load settings
		
		self.settings = cfgfile.cfgset()
		self.settings.load("conf/scrib-irc.cfg",
			{ "myname": ("The bot's nickname", "Scribbington"),
			  "realname": ("Reported 'real name'", "Scrib"),
			  "owners": ("Owner(s) nickname", [ "OwnerNick" ]),
			  "servers": ("IRC Server to connect to (server, port [,password])", [("irc.starchat.net", 6667)]),
			  "chans": ("Channels to auto-join", ["#test"]),
			  "speaking": ("Allow the bot to talk on channels", 1),
			  "private": ("Hide the fact we are a bot", 0),
			  "ignorelist": ("Ignore these nicknames:", []),
			  "replyIgnored": ("Reply but don't learn from ignored people", 0),
			  "reply_chance": ("Chance of reply (%) per message", 33),
			  "quitmsg": ("IRC quit message", "Bye :-("),
			  "password": ("password for control the bot (Edit manually !)", "")
			} )

		self.owners = self.settings.owners[:]
		self.chans = self.settings.chans[:]

		# Parse command prompt parameters
		
		for x in xrange(1, len(args)):
			# Specify servers
			if args[x] == "-s":
				self.settings.servers = []
				# Read list of servers
				for y in xrange(x+1, len(args)):
					if args[y][0] == "-":
						break
					server = args[y].split(":")
					# Default port if none specified
					if len(server) == 1:
						server.append("6667")
					self.settings.servers.append( (server[0], int(server[1])) )
			# Channels
			if args[x] == "-c":
				self.settings.chans = []
				# Read list of channels
				for y in xrange(x+1, len(args)):
					if args[y][0] == "-":
						break
					self.settings.chans.append("#"+args[y])
			# Nickname
			if args[x] == "-n":
				try:
					self.settings.myname = args[x+1]
				except IndexError:
					pass

	def our_start(self):
		print "[%s][~] Connecting to %s " % (scrib.get_time(), self.settings.servers)
		SingleServerIRCBot.__init__(self, self.settings.servers, self.settings.myname, self.settings.realname, 2)

		self.start()

	def on_welcome(self, c, e):
		print "[%s][~] %s" % (scrib.get_time(), self.chans)
		for i in self.chans:
			c.join(i)

	def shutdown(self):
		try:
			self.die() # disconnect from server
		except AttributeError, e:
			# already disconnected probably (pingout or whatever)
			pass

	def get_version(self):
		if self.settings.private:
			# private mode. we shall be a windows luser today
			return "Omnominator"
		else:
			return self.scrib.ver_string

	def on_kick(self, c, e):
		"""
		Process leaving
		"""
		# Parse Nickname!username@host.mask.net to Nickname
		kicked = e.arguments()[0]
		kicker = e.source().split("!")[0]
		target = e.target() #channel
		if len(e.arguments()) >= 2:
			reason = e.arguments()[1]
		else:
			reason = ""

		if kicked == self.settings.myname:
			print "[%s][*] %s was kicked off %s by %s (%s)" % (scrib.get_time(), kicked, target, kicker, reason)

	def on_privmsg(self, c, e):
		self.on_msg(c, e)
	
	def on_pubmsg(self, c, e):
		self.on_msg(c, e)

	def on_ctcp(self, c, e):
		ctcptype = e.arguments()[0]
		if ctcptype == "ACTION":
			self.on_msg(c, e)
		else:
			SingleServerIRCBot.on_ctcp(self, c, e)

	def _on_disconnect(self, c, e):
		# self.channels = IRCDict()
		print "[%s][~] Disconnected.." % scrib.get_time()
		self.connection.execute_delayed(self.reconnection_interval, self._connected_checker)


	def on_msg(self, c, e):
		"""
		Process messages.
		"""
		# Parse Nickname!username@host.mask.net to Nickname
		source = e.source().split("!")[0]
		target = e.target()

		learn = 1

		# First message from owner 'locks' the owner host mask
		if not e.source() in self.owner_mask and source in self.owners:
			self.owner_mask.append(e.source())
			print "[%s][~] My owner is %s" % (scrib.get_time(), e.source())

		# Message text
		if len(e.arguments()) == 1:
			# Normal message
			body = e.arguments()[0]
		else:
			# A CTCP thing
			if e.arguments()[0] == "ACTION":
				body = source + " " + e.arguments()[1]
			else:
				# Ignore all the other CTCPs
				return

		for irc_color_char in [',', "\x03"]:
			debut = body.rfind(irc_color_char)
			if 0 <= debut < 5:
				x = 0
				for x in xrange(debut+1, len(body)):
					if body[x].isdigit() == 0:
						break
				body = body[x:]

		#remove special irc fonts chars
		body = body[body.rfind("\x02")+1:]
		body = body[body.rfind("\xa0")+1:]

		# WHOOHOOO!!
		if target == self.settings.myname or source == self.settings.myname:
			print "[%s][-] %s <%s> %s" % ( scrib.get_time(), target, source, body)

		# Ignore self.
		#if source == self.settings.myname: return


		#replace nicknames by "#nick"
		if e.eventtype() == "pubmsg":
			for x in self.channels[target].users():
				body = body.replace(x, "#nick")
		print "[%s][-] %s <%s> %s" % (scrib.get_time(), target, source, body)

		# Ignore selected nicks
		if self.settings.ignorelist.count(source) > 0 \
			and self.settings.replyIgnored == 1:
			print "[%s][~] Not learning from %s" % (scrib.get_time(), source)
			learn = 0
		elif self.settings.ignorelist.count(source) > 0:
			print "[%s][~] Ignoring %s" % (scrib.get_time(), source)
			return

		# private mode. disable commands for non owners
		if (not source in self.owners) and self.settings.private:
			while body[:1] == "!":
				print "[%s][!] Private mode is on, ignoring command: %s" % (scrib.get_time(), body)
				return

		if body == "":
			return

		# Ignore quoted messages
		if body[0] == "<" or body[0:1] == "\"" or body[0:1] == " <":
			print "[%s][#] Ignoring quoted text." % scrib.get_time()
			return

		# We want replies reply_chance%, if speaking is on
		replyrate = self.settings.speaking * self.settings.reply_chance

		# double reply chance if the text contains our nickname :-)
		if body.find(self.settings.myname ) != -1:
			replyrate = replyrate * 2

		# Always reply to private messages
		if e.eventtype() == "privmsg":
			replyrate = 100

			# Parse ModIRC commands
			if body[0:1] == "!":
				if self.irc_commands(body, source, target, c, e) == 1:return
				return

		# Pass message onto scrib
		if source in self.owners and e.source() in self.owner_mask:
			self.scrib.process_msg(self, body, replyrate, learn, (body, source, target, c, e), owner=1)
		else:
			#start a new thread
			thread.start_new_thread(self.scrib.process_msg, (self, body, replyrate, learn, (body, source, target, c, e)))

	def irc_commands(self, body, source, target, c, e):
		"""
		Special IRC commands.
		"""
		
		msg = ""

		command_list = body.split()
		command_list[0] = command_list[0]

		### User commands
		# Query replyrate
		#if command_list[0] == "!replyrate" and len(command_list)==1:
		#	msg = self.scrib.settings.pubsym+"Reply rate is "+`self.settings.reply_chance`+"%."

		if command_list[0] == "!control" and len(command_list) > 1 and source not in self.owners:
			if command_list[1] == self.settings.password:
				self.owners.append(source)
				self.output("You've been added to controllers list", ("", source, target, c, e))
			else:
				self.output("Try again", ("", source, target, c, e))

		### Owner commands
		if source in self.owners and e.source() in self.owner_mask:

			# Change nick
			if command_list[0] == "!nick":
				try:
					self.connection.nick(command_list[1])
					self.settings.myname = command_list[1]
				except:
					pass
			# private mode
			elif command_list[0] == "!private":
				msg = "$sPrivate mode " % self.settings.pubsym
				if len(command_list) == 1:
					if self.settings.private == 0:
						msg = msg + "off"
					else:
						msg = msg + "on"
				else:
					toggle = command_list[1]
					if toggle == "on":
						msg = msg + "on"
						self.settings.private = 1
					else:
						msg = msg + "off"
						self.settings.private = 0

			# Allow/disallow replying to ignored nicks
			# (they will never be learnt from)
			elif command_list[0] == "!replyIgnored":
				msg = "Replying to ignored users "
				if len(command_list) == 1:
					if self.settings.replyIgnored == 0:
						msg = msg + "off"
					else:
						msg = msg + "on"
				else:
					toggle = command_list[1]
					if toggle == "on":
						msg = msg + "on"
						self.settings.replyIgnored = 1
					else:
						msg = msg + "off"
						self.settings.replyIgnored = 0
			# Stop talking
			elif command_list[0] == "!sleep":
				if self.settings.speaking == 1:
					msg = "Going to sleep.  Goodnight!"
					self.settings.speaking = 0
				else:
					msg = "Zzz.."
			# Wake up again
			elif command_list[0] == "!wake":
				if self.settings.speaking == 0:
					self.settings.speaking = 1
					msg = "Whoohoo!"
				else:
					msg = "But I'm already awake..."
						
			# Join a channel or list of channels
			elif command_list[0] == "!join":
				for x in xrange(1, len(command_list)):
					if not command_list[x] in self.chans:
						msg = "Attempting to join channel %s" % command_list[x]
						self.chans.append(command_list[x])
						c.join(command_list[x])

			# Part a channel or list of channels
			elif command_list[0] == "!part":
				for x in xrange(1, len(command_list)):
					if command_list[x] in self.chans:
						msg = "Leaving channel %s" % command_list[x]
						self.chans.remove(command_list[x])
						c.part(command_list[x])

			# List channels currently on
			elif command_list[0] == "!chans":
				if len(self.channels.keys())==0:
					msg = "I'm currently on no channels"
				else:
					msg = "I'm currently on "
					channels = self.channels.keys()
					for x in xrange(0, len(channels)):
						msg = msg+channels[x]+" "
			# add someone to the ignore list
			elif command_list[0] == "!ignore":
				# if no arguments are given say who we are
				# ignoring
				if len(command_list) == 1:
					msg = "I'm ignoring "
					if len(self.settings.ignorelist) == 0:
						msg = msg + "nobody"
					else:
						for x in xrange(0, len(self.settings.ignorelist)):
							msg = msg + self.settings.ignorelist[x] + " "
				# Add everyone listed to the ignore list
				# eg !ignore tom dick harry
				else:
					for x in xrange(1, len(command_list)):
						self.settings.ignorelist.append(command_list[x])
						msg = "!Done."
			# remove someone from the ignore list
			elif command_list[0] == "!unignore":
				# Remove everyone listed from the ignore list
				# eg !unignore tom dick harry
				for x in xrange(1, len(command_list)):
					try:
						self.settings.ignorelist.remove(command_list[x])
						msg = "Done."
					except:
						pass
			# set the quit message
			elif command_list[0] == "!quitmsg":
				if len(command_list) > 1:
					self.settings.quitmsg = body.split(" ", 1)[1]
					msg = "New quit message is \"%s\"" % self.settings.quitmsg
				else:
					msg = "Quit message is \"%s\"" % self.settings.quitmsg
			# make the scrib quit
			elif command_list[0] == "!quit":
				sys.exit()
			# Change reply rate
			elif command_list[0] == "!replyrate":
				try:
					self.settings.reply_chance = int(command_list[1])
					msg = "Now replying to %d%% of messages." % int(command_list[1])
				except:
					msg = "Reply rate is %d%%." % self.settings.reply_chance

			# Make the commands dynamic
			# self.commanddict should eventually check self.commandlist
			# so we can stop doing [1:]
			elif command_list[0][1:] in self.commanddict:
				out = PluginManager.sendMessage(command_list[0][1:], command_list)
				msg = out

			self.scrib.settings.save()
			self.settings.save()
	
		if msg == "":
			return 0
		else:
			self.output(msg, ("<none>", source, target, c, e))
			return 1
			
	def output(self, message, args):
		"""
		Output a line of text. args = (body, source, target, c, e)
		"""
		if not self.connection.is_connected():
			print "[%s][!] Can't send reply : not connected to server" % scrib.get_time()
			return

		# Unwrap arguments
		body, source, target, c, e = args
		
		# replace by the good nickname
		message = message.replace("#nick", source)

		# Decide. should we do a ctcp action?
		if message.find(self.settings.myname+" ") == 0:
			action = 1
			message = message[len(self.settings.myname)+1:]
		else:
			action = 0

		# Joins replies and public messages
		if e.eventtype() == "join" or e.eventtype() == "quit" or e.eventtype() == "part" or e.eventtype() == "pubmsg":
			if action == 0:
				print "[%s][-] %s <%s> %s" % ( scrib.get_time(), target, self.settings.myname, message)
				c.privmsg(target, message)
			else:
				print "[%s][-] %s <%s> /me %s" % ( scrib.get_time(), target, self.settings.myname, message)
				c.action(target, message)
		# Private messages
		elif e.eventtype() == "privmsg":
			# normal private msg
			if action == 0:
				print "[%s][-] %s <%s> %s" % ( scrib.get_time(), source, self.settings.myname, message)
				c.privmsg(source, message)
				# send copy to owner
				if not source in self.owners:
					c.privmsg(','.join(self.owners), "(From "+source+") "+body)
					c.privmsg(','.join(self.owners), "(To   "+source+") "+message)
			# ctcp action priv msg
			else:
				print "[%s][-] %s <%s> /me %s" % ( scrib.get_time(), target, self.settings.myname, message)
				c.action(source, message)
				# send copy to owner
				if not source in self.owners:
					map ( ( lambda x: c.action(x, "(From "+source+") "+body) ), self.owners)
					map ( ( lambda x: c.action(x, "(To   "+source+") "+message) ), self.owners)


if __name__ == "__main__":
	
	if "--help" in sys.argv:
		print "Scrib irc bot. Usage:"
		print " scrib-irc.py [options]"
		print " -s   server:port"
		print " -c   channel"
		print " -n   nickname"
		print "Defaults stored in scrib-irc.cfg"
		print
		sys.exit(0)
	# start the scrib
	my_scrib = scrib.scrib()
	bot = ModIRC(my_scrib, sys.argv)
	try:
		bot.our_start()
	except KeyboardInterrupt, e:
		pass
	except SystemExit, e:
		pass
	except:
		traceback.print_exc()
		c = raw_input("["+scrib.get_time()+"][!] Oh no, I've crashed! Would you like to save my brain? (y/n)")
		if c[:1] == 'n':
			sys.exit(0)
	bot.disconnect(bot.settings.quitmsg)
	my_scrib.save_all()
	del my_scrib
