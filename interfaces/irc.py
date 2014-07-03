#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import traceback
import thread
sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))
from core import scrib

try:
	from ircbot import *
	from irclib import *
except:
	self.scrib.barf('ERR', "ircbot.py and irclib.py are not found. Please install them to continue.")
	sys.exit(1)

# Let's override some irclib function
def my_remove_connection(self, connection):
	if self.fn_to_remove_socket:
		self.fn_to_remove_socket(connection._get_socket())

IRC._remove_connection = my_remove_connection


class ScribIRC(SingleServerIRCBot):
	"""
	Interfacing some IRC I/O with scrib learn/reply modules!
	"""
	join_msg = "%s"# is here"
	part_msg = "%s"# has left"

	# We are going to store the owner(s) host mask.
	owner_mask = []

	def __init__(self, my_scrib, args):
		"""
		Args will be sys.argv (command prompt arguments)
		"""
		self.scrib = my_scrib
		# load settings

		self.settings = self.scrib.cfg.set()
		self.settings.load("conf/irc.cfg", {
								"realname": "Scrib Bot",
								"servers": [("irc.freenode.net", 6667)],
								"channels": ["#scoundrels"],
								"owners": ["OwnerOne"],
								'reply_rate': 100,
								'nick_reply_rate': 100,
								"owner_passwords": ["Ducks"],
								"quit_message": "Goodbye.",
						   })
		self.scrib.settings.name = my_scrib.settings.name
		self.owners = self.settings.owners[:]
		self.chans = self.settings.channels[:]
		
		self.symbol = self.scrib.getsymbol()

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
					self.scrib.settings.name = args[x + 1]
				except IndexError:
					pass

	def our_start(self):
		#for server in self.settings.servers:
		self.scrib.barf('ACT', "Connecting to %s" % self.settings.servers[0][0])
		SingleServerIRCBot.__init__(self, self.settings.servers, self.scrib.settings.name, self.settings.realname, 2)
		self.start()

	def on_welcome(self, c, e):
		for i in self.chans:
			self.scrib.barf('ACT', "Joining %s" % i)
			c.join(i)

	def shutdown(self):
		try:
			self.die() # disconnect from server
		except AttributeError, e:
			# already disconnected probably (pingout or whatever)
			pass

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

		if kicked == self.scrib.settings.name:
			self.scrib.barf('ACT', "%s was kicked off %s by %s (%s)" % (kicked, target, kicker, reason))

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
		self.scrib.barf('ACT', "Disconnected, shutting down.")
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
			self.scrib.barf('ACT', "My owner is \033[0m%s" % e.source())

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

		# Don't bother with empty messages.
		if body == "":
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
		if target == self.scrib.settings.name or source == self.scrib.settings.name:
			self.scrib.barf('MSG', "%s <%s> \033[0m%s" % (target, source, body))

		# Ignore quoted messages
		if body[0] == "<" or body[0:1] == "\"" or body[0:1] == " <" or body[0] == "[":
			if self.scrib.settings.debug == 1:
				self.scrib.barf('DBG', "Ignoring quoted text.")
			return

		# We want replies reply_rate%, if speaking is on
		muted = self.scrib.settings.muted
		replyrate = self.settings.reply_rate
		nickreplyrate = self.settings.nick_reply_rate

		if self.nick_check(body) == 1:
			replyrate = nickreplyrate
			if self.scrib.settings.debug == 1:
				self.scrib.barf('DBG', "Responding to Highlight")

		# Always reply to private messages
		if e.eventtype() == "privmsg":
			replyrate = 100
			muted = 0

			try:
				if body[0] == self.symbol:
					if self.irc_commands(body, source, target, c, e) == 1: return
					return
			except: pass

		#replace nicknames, including own, with "#nick"
		if e.eventtype() == "pubmsg":
			try:
				if body[0] == self.symbol:
					if self.irc_commands(body, source, target, c, e) == 1: return
			except: pass

			self.scrib.barf('MSG', "%s <%s> \033[0m%s" % (target, source, body))
			body = body.replace(self.scrib.settings.name, "#nick")
			body = body.replace(self.scrib.settings.name.lower(), "#nick")
			for x in self.channels[target].users():
				x = re.sub("[\&\%\+\@\~]","", x)
				if x:
					body = body.replace("@ "+x, "@ #nick")

		# Pass on to scrib
		if source in self.owners and e.source() in self.owner_mask:
			self.scrib.process.msg(self, body, replyrate, learn, (body, source, target, c, e), 1, muted)
		else:
			#start a new thread
			thread.start_new_thread(self.scrib.process.msg,
									(self, body, replyrate, learn, (body, source, target, c, e), 0, muted))

	def irc_commands(self, body, source, target, c, e):
		"""
		Route IRC Commands to the PluginManager.
		"""
		msg = ""
		cmds = body.split()

		### Owner commands (Which is all of them for now)
		if source in self.owners and e.source() in self.owner_mask:
			# Only accept commands that are in the Command List
			if self.scrib.settings.debug == 1:
				self.scrib.barf('DBG', "Command: %s" % cmds[0])
				self.scrib.barf('DBG', "Command list: %s" % str(cmds))
			if cmds[0][1:] in self.commands:
				msg = "%s" % PluginManager.sendMessage(cmds[0][1:], cmds, self, c)


			if cmds[0] == "!reload" and len(cmds) == 2:
				msg = PluginManager.reloadPlugin(cmds[1])

			self.settings.save()

		if msg == "":
			return 0
		else:
			self.output(msg, ("<none>", source, target, c, e))
			return 1

	def nick_check(self, message):
		# Check to see if I'm highlighted
		highlighted = 0
		if self.scrib.settings.name in message:
			highlighted = 1
		return highlighted

	def output(self, message, args):
		"""
		Output a line of text. args = (body, source, target, c, e)
		"""
		if not self.connection.is_connected():
			self.scrib.barf('ERR', "Can't send reply : not connected to server")
			return

		# Unwrap arguments
		body, source, target, c, e = args

		# Decide. should we do a ctcp action?
		if message.find(self.scrib.settings.name + " ") == 0:
			action = 1
			message = message[len(self.scrib.settings.name) + 1:]
		else:
			action = 0

		# Replace nicks with #nick variable
		message = message.replace("#nick", source)

		# Joins replies and public messages
		if e.eventtype() == "join" or e.eventtype() == "quit" or e.eventtype() == "part" or e.eventtype() == "pubmsg":
			if action == 0:
				self.scrib.barf('MSG', "%s <%s> \033[0m%s" % ( target, self.scrib.settings.name, message))
				c.privmsg(target, message)
			else:
				self.scrib.barf('MSG', "%s <%s> /me \033[0m%s" % ( target, self.scrib.settings.name, message))
				c.action(target, message)
		# Private messages
		elif e.eventtype() == "privmsg":
			# normal private msg
			if action == 0:
				self.scrib.barf('MSG', "%s <%s> \033[0m%s" % ( source, self.scrib.settings.name, message))
				c.privmsg(source, message)
				# send copy to owner
				if not source in self.owners:
					c.privmsg(','.join(self.owners), "(From " + source + ") " + body)
					c.privmsg(','.join(self.owners), "(To   " + source + ") " + message)
			# ctcp action priv msg
			else:
				self.scrib.barf('MSG', "%s <%s> /me \033[0m%s" % ( target, self.scrib.settings.name, message))
				c.action(source, message)
				# send copy to owner
				if not source in self.owners:
					map(( lambda x: c.action(x, "(From " + source + ") " + body) ), self.owners)
					map(( lambda x: c.action(x, "(To   " + source + ") " + message) ), self.owners)


if __name__ == "__main__":
	my_scrib = scrib.scrib()
	bot = ScribIRC(my_scrib, sys.argv)
	try:
		bot.our_start()
	except KeyboardInterrupt, e:
		pass
	except SystemExit, e:
		pass
	except:
		my_scrib.barf('ERR', traceback.format_exc())
		my_scrib.barf('ERR', "Oh no, I've crashed! Would you like to save my brain?", False)
		c = raw_input("[Y/n]")
		if c[:1] != 'n':
			my_scrib.shutdown(my_scrib)
	my_scrib.shutdown(my_scrib)