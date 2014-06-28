#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager
import sys

nick_cmd = "!nick"
class NickPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		msg = ""
		if cmds[0] == nick_cmd and len(cmds) == 2:
			try:
				scrib.connection.nick(cmds[1])
				scrib.settings.myname = cmds[1]
				msg = "Nick changed."
			except:
				msg = "Couldn't change nick."
				pass
		return msg

join_cmd = "!join"
class JoinPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		msg = ""
		if cmds[0] == join_cmd:
			for x in xrange(1, len(cmds)):
				if not cmds[x] in scrib.chans:
					msg = "Attempting to join channel %s" % cmds[x]
					scrib.chans.append(cmds[x])
					c.join(cmds[x])
			return msg

part_cmd = "!part"
class PartPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		msg = ""
		if cmds[0] == part_cmd:
			for x in xrange(1, len(cmds)):
				if cmds[x] in scrib.chans:
					msg = "Leaving channel %s" % cmds[x]
					scrib.chans.remove(cmds[x])
					c.part(cmds[x])
			return msg

chans_cmd = "!chans"
class ChansPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		msg = ""
		if cmds[0] == chans_cmd:
			if len(scrib.channels.keys())==0:
				msg = "I'm currently on no channels"
			else:
				msg = "I'm currently on "
				channels = scrib.channels.keys()
				for x in xrange(0, len(channels)):
					msg = msg+channels[x]+" "
			return msg

quit_cmd = "!quit"
class QuitPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == quit_cmd:
			sys.exit()

quitmsg_cmd = "!quitmsg"
class QuitmsgPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		msg = ""
		if cmds[0] == quitmsg_cmd:
			if len(cmds) > 1:
				scrib.settings.quitmsg = body.split(" ", 1)[1]
				msg = "New quit message is \"%s\"" % scrib.settings.quitmsg
			else:
				msg = "Quit message is \"%s\"" % scrib.settings.quitmsg
		return msg

ignore_cmd = "!ignore"
class IgnorePlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == ignore_cmd:
			# if no arguments are given say who we are
			# ignoring
			if len(cmds) == 1:
				msg = "I'm ignoring "
				if len(scrib.settings.ignorelist) == 0:
					msg = msg + "nobody"
				else:
					for x in xrange(0, len(scrib.settings.ignorelist)):
						msg = msg + scrib.settings.ignorelist[x] + " "
			# Add everyone listed to the ignore list
			# eg !ignore tom dick harry
			else:
				for x in xrange(1, len(cmds)):
					scrib.settings.ignorelist.append(cmds[x])
					msg = "Ignoring %s" % cmds[x]
		return msg

unignore_cmd = "!unignore"
class UnIgnorePlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		msg = ""
		if cmds[0] == unignore_cmd:
			# Remove everyone listed from the ignore list
			# eg !unignore tom dick harry
			for x in xrange(1, len(cmds)):
				try:
					scrib.settings.ignorelist.remove(cmds[x])
					msg = "Unignoring %s" % cmds[x]
				except:
					pass
		return msg

PluginManager.addPlugin( nick_cmd, NickPlugin() )
PluginManager.addPlugin( join_cmd, JoinPlugin() )
PluginManager.addPlugin( part_cmd, PartPlugin() )
PluginManager.addPlugin( chans_cmd, ChansPlugin() )
PluginManager.addPlugin( quit_cmd, QuitPlugin() )
PluginManager.addPlugin( quitmsg_cmd, QuitmsgPlugin() )
PluginManager.addPlugin( ignore_cmd, IgnorePlugin() )
PluginManager.addPlugin( unignore_cmd, UnIgnorePlugin() )
