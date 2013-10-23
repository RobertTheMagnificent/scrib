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

	# Message Codes
	ACT = '\033[93m [~] '
	MSG = '\033[94m [-] '
	SAV = '\033[92m [#] '
	ERR = '\033[91m [!] '

	def disable(self):
		self.ACT = ''
		self.MSG = ''
		self.SAV = ''
		self.ERR = ''
	
	def barf(self, msg_code, message):
		print scrib.get_time() + msg_code + message

	"""
	Interfacing some IRC I/O with scrib learn/reply modules!
	"""
	join_msg = "%s"# is here"
	part_msg = "%s"# has left"

	# We are going to store the owner's host mask :3
	owner_mask = []

	commandlist = PluginManager.ScribPlugin.plugin_aliases
	commanddict = PluginManager.ScribPlugin.plugin_commands
	
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
		#print scrib.get_time() + self.ACT + "Connecting to %s " %self.settings.servers
		self.barf(self, self.ACT, "Connecting to %s " % self.settings.servers)
		SingleServerIRCBot.__init__(self, self.settings.servers, self.settings.myname, self.settings.realname, 2)

		self.start()

	def on_welcome(self, c, e):
		print scrib.get_time() + self.ACT + "%s" %self.chans
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
			print scrib.get_time() + self.ACT + "%s was kicked off %s by %s (%s)" % (kicked, target, kicker, reason)

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
		print scrib.get_time() + self.ACT + "Disconnected.."
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
			print scrib.get_time() + self.ACT + "My owner is %s" %e.source()

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
			print scrib.get_time() + self.MSG + "%s <%s> %s" % (target, source, body)

		# Ignore self.
		#if source == self.settings.myname: return


		#replace nicknames by "#nick"
		if e.eventtype() == "pubmsg":
			for x in self.channels[target].users():
				body = body.replace(x, "#nick")
		print scrib.get_time() + self.MSG + "%s <%s> %s" % (target, source, body)

		# Ignore selected nicks
		if self.settings.ignorelist.count(source) > 0 \
			and self.settings.replyIgnored == 1:
			print scrib.get_time() + self.ACT + "Not learning from %s" %source
			learn = 0
		elif self.settings.ignorelist.count(source) > 0:
			print scrib.get_time() + self.ACT + "Ignoring %s" %source
			return

		# private mode. disable commands for non owners
		if (not source in self.owners) and self.settings.private:
			while body[:1] == "!":
				print scrib.get_time() + self.ERR + "Private mode is on, ignoring command: %s" %body
				return

		if body == "":
			return

		# Ignore quoted messages
		if body[0] == "<" or body[0:1] == "\"" or body[0:1] == " <":
			print scrib.get_time() + self.SAV + "Ignoring quoted text."
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
		All IRC commands have been turned into plugins. :D
		"""
		
		msg = ""

		command_list = body.split()
		command_list[0] = command_list[0]

		### Owner commands (Which is all of them for now)
		if source in self.owners and e.source() in self.owner_mask:
			# Make the commands dynamic
			# self.commanddict should eventually check self.commandlist
			# so we can stop doing [1:]
			if command_list[0][1:] in self.commanddict:
				msg = PluginManager.sendMessage(command_list[0][1:], command_list, self)

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
			print scrib.get_time() + self.ERR + "Can't send reply : not connected to server"
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
				print scrib.get_time() + self.MSG + "%s <%s> %s" % ( target, self.settings.myname, message)
				c.privmsg(target, message)
			else:
				print scrib.get_time() + self.MSG + "%s <%s> /me %s" % ( target, self.settings.myname, message)
				c.action(target, message)
		# Private messages
		elif e.eventtype() == "privmsg":
			# normal private msg
			if action == 0:
				print scrib.get_time() + self.MSG + "%s <%s> %s" % ( source, self.settings.myname, message)
				c.privmsg(source, message)
				# send copy to owner
				if not source in self.owners:
					c.privmsg(','.join(self.owners), "(From "+source+") "+body)
					c.privmsg(','.join(self.owners), "(To   "+source+") "+message)
			# ctcp action priv msg
			else:
				print scrib.get_time() + self.MSG + "%s <%s> /me %s" % ( target, self.settings.myname, message)
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
		c = raw_input("\033[94m"+scrib.get_time()+" \033[91m[!] Oh no, I've crashed! Would you like to save my brain? (yes/no)\033[0m")
		if c[:1] == 'n':
			sys.exit(0)
	bot.disconnect(bot.settings.quitmsg)
	my_scrib.save_all()
	del my_scrib
