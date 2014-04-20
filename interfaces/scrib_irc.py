#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

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

from core import scrib
from core import barf
from core import cfgfile
from plugins import PluginManager
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
	commanddict = PluginManager.ScribPlugin.plugin_commands

	def __init__(self, my_scrib, args):
		"""
		Args will be sys.argv (command prompt arguments)
		"""
		self.scrib = my_scrib
		# load settings

		self.settings = cfgfile.cfgset()
		self.settings.load("conf/scrib-irc.cfg",
						   {"myname": ("The bot's nickname", "Scrib"),
							"realname": ("Reported 'real name'", "Scrib"),
							"filter": ("Do we filter our replies or just blindly speak?", 1),
							"owners": ("Owner(s) nickname", ["OwnerNick"]),
							"servers": ("IRC Server to connect to (server, port [,password])", [("irc.freenode.net", 6667)]),
							"chans": ("Channels to auto-join", ["#scoundrels"]),
							"speaking": ("Allow the bot to talk on channels", 1),
							"private": ("Hide the fact we are a bot", 0),
							"ignorelist": ("Ignore these nicknames:", []),
							"replyIgnored": ("Reply but don't learn from ignored people", 0),
							"reply_chance": ("Chance of reply (%) per message", 33),
							"nick_reply_chance": ("Chance of reply (%) per message when mentioned", 100),
							"quitmsg": ("IRC quit message", "Bye :-("),
							"password": ("password for control the bot (Edit manually !)", "")
						   })

		self.owners = self.settings.owners[:]
		self.chans = self.settings.chans[:]

		# Parse command prompt parameters

		for x in xrange(1, len(args)):
			# Specify servers
			if args[x] == "-s":
				self.settings.servers = []
				# Read list of servers
				for y in xrange(x + 1, len(args)):
					if args[y][0] == "-":
						break
					server = args[y].split(":")
					# Default port if none specified
					if len(server) == 1:
						server.append("6667")
					self.settings.servers.append((server[0], int(server[1])))
			# Channels
			if args[x] == "-c":
				self.settings.chans = []
				# Read list of channels
				for y in xrange(x + 1, len(args)):
					if args[y][0] == "-":
						break
					self.settings.chans.append("#" + args[y])
			# Nickname
			if args[x] == "-n":
				try:
					self.settings.myname = args[x + 1]
				except IndexError:
					pass

	def our_start(self):
		barf.Barf('ACT', "Connecting to \033[1m%s" % self.settings.servers)
		SingleServerIRCBot.__init__(self, self.settings.servers, self.settings.myname, self.settings.realname, 2)

		self.start()

	def on_welcome(self, c, e):
		barf.Barf('ACT', "Joining \033[1m%s" % self.chans)
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
			return "Omnomnomicon"
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
			barf.Barf('ACT', "%s was kicked off %s by %s (%s)" % (kicked, target, kicker, reason))

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
		barf.Barf('ACT', "Disconnected..")
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
			barf.Barf('ACT', "My owner is \033[0m%s" % e.source())

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
				for x in xrange(debut + 1, len(body)):
					if body[x].isdigit() == 0:
						break
				body = body[x:]

		#remove special irc fonts chars
		body = body[body.rfind("\x02") + 1:]
		body = body[body.rfind("\xa0") + 1:]

		# WHOOHOOO!!
		if target == self.settings.myname or source == self.settings.myname:
			barf.Barf('MSG', "%s <%s> \033[0m%s" % (target, source, body))

		# Ignore self.
		if source == self.settings.myname: return

		# Ignore selected nicks
		if self.settings.ignorelist.count(source) > 0 and self.settings.replyIgnored == 1:
			barf.Barf('ACT', "Not learning from %s" % source)
			learn = 0
		elif self.settings.ignorelist.count(source) > 0:
			barf.Barf('ACT', "Ignoring %s" % source)
			return

		# private mode. disable commands for non owners
		if (not source in self.owners) and self.settings.private:
			while body[:1] == "!":
				barf.Barf('ACT', "Private mode is on, ignoring command: %s" % body)
				return

		if body == "":
			return

		# Ignore quoted messages
		if body[0] == "<" or body[0:1] == "\"" or body[0:1] == " <" or body[0] == "[":
			if self.settings.debug == 1:
				barf.Barf('DBG', "Ignoring quoted text.")
			return

		# We want replies reply_chance%, if speaking is on
		not_quiet = self.settings.speaking
		replyrate = not_quiet * self.settings.reply_chance
		nickreplyrate = not_quiet * self.settings.nick_reply_chance

		if self.nick_check(body) == 1:
			replyrate = nickreplyrate
			if self.settings.debug == 1:
				barf.Barf('DBG', "Responding to Highlight")

		# Always reply to private messages
		if e.eventtype() == "privmsg":
			replyrate = 100
			not_quiet = 1

			try:
				if body[0] == "!": # was [1:0]
					if self.irc_commands(body, source, target, c, e) == 1: return
					return
			except: pass

		#replace nicknames, including own, with "#nick"
		if e.eventtype() == "pubmsg":
			try:
				if body[0] == "!":
					if self.irc_commands(body, source, target, c, e) == 1: return
			except: pass

			barf.Barf('MSG', "%s <%s> \033[0m%s" % (target, source, body))
			body = body.replace(self.settings.myname, "#nick")
			body = body.replace(self.settings.myname.lower(), "#nick")
			for x in self.channels[target].users():
				x = re.sub("[\&\%\+\@\~]","", x)
				if x:
					# Disabled due to bug #76
					#body = body.replace(x+":", "#nick:")
					body = body.replace("@ "+x, "@ #nick")

		if body == "": return

		if self.settings.debug == 1:
			barf.Barf('DBG', "Body empty, no reply.")


		# Pass on to scrib
		if source in self.owners and e.source() in self.owner_mask:
			self.scrib.process_msg(self, body, replyrate, learn, (body, source, target, c, e), 1, not_quiet)
		else:
			#start a new thread
			thread.start_new_thread(self.scrib.process_msg,
									(self, body, replyrate, learn, (body, source, target, c, e), 0, not_quiet))

	def irc_commands(self, body, source, target, c, e):
		"""
		Route IRC Commands to the PluginManager.
		"""

		msg = ""
		command_list = body.split()
		command_list[0] = command_list[0]

		### Owner commands (Which is all of them for now)
		if source in self.owners and e.source() in self.owner_mask:
			# Only accept commands that are in the Command List
			if self.scrib.debug == 1:
				barf.Barf('DBG', "Command: %s" % command_list[0])
				barf.Barf('DBG', "Command list: %s" % str(command_list))
			if command_list[0][1:] in self.commanddict:
				msg = "%s %s" % (self.scrib.settings.pubsym, PluginManager.sendMessage(command_list[0][1:], command_list, self, c))


			if command_list[0] == "!reload" and len(command_list) == 2:
				msg = PluginManager.reloadPlugin(command_list[1])

			self.scrib.settings.save()
			self.settings.save()

		if msg == "":
			return 0
		else:
			self.output(msg, ("<none>", source, target, c, e))
			return 1

	def nick_check(self, message):
		# Check to see if I'm highlighted
		highlighted = 0
		if message.find(self.settings.myname) != -1:
			highlighted = 1
		return highlighted

	def output(self, message, args):
		"""
		Output a line of text. args = (body, source, target, c, e)
		"""
		if not self.connection.is_connected():
			barf.Barf('ERR', "Can't send reply : not connected to server")
			return

		# Unwrap arguments
		body, source, target, c, e = args

		# Decide. should we do a ctcp action?
		if message.find(self.settings.myname + " ") == 0:
			action = 1
			message = message[len(self.settings.myname) + 1:]
		else:
			action = 0

		# Replace nicks with #nick variable
		message = message.replace("#nick", source)

		# Joins replies and public messages
		if e.eventtype() == "join" or e.eventtype() == "quit" or e.eventtype() == "part" or e.eventtype() == "pubmsg":
			if action == 0:
				barf.Barf('MSG', "%s <%s> \033[0m%s" % ( target, self.settings.myname, message))
				c.privmsg(target, message)
			else:
				barf.Barf('MSG', "%s <%s> /me \033[0m%s" % ( target, self.settings.myname, message))
				c.action(target, message)
		# Private messages
		elif e.eventtype() == "privmsg":
			# normal private msg
			if action == 0:
				barf.Barf('MSG', "%s <%s> \033[0m%s" % ( source, self.settings.myname, message))
				c.privmsg(source, message)
				# send copy to owner
				if not source in self.owners:
					c.privmsg(','.join(self.owners), "(From " + source + ") " + body)
					c.privmsg(','.join(self.owners), "(To   " + source + ") " + message)
			# ctcp action priv msg
			else:
				barf.Barf('MSG', "%s <%s> /me \033[0m%s" % ( target, self.settings.myname, message))
				c.action(source, message)
				# send copy to owner
				if not source in self.owners:
					map(( lambda x: c.action(x, "(From " + source + ") " + body) ), self.owners)
					map(( lambda x: c.action(x, "(To   " + source + ") " + message) ), self.owners)


if __name__ == "__main__":
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
		c = raw_input(barf.raw_barf('ERR', "Oh no, I've crashed! Would you like to save my brain? (Y/n) "))
		if c[:1] == 'n':
			sys.exit(0)
	bot.disconnect(bot.settings.quitmsg)
	my_scrib.save_all(False)
	del my_scrib
