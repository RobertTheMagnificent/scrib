#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager

# User command
alias = "echo"
command = { alias: "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class EchoPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == command and len(cmds) >= 1:
			phrase=""
			for x in xrange (1, len (cmds)):
				phrase = phrase + str(cmds[x]) + " "
			return phrase

PluginManager.addPlugin( command, alias, EchoPlugin() )
