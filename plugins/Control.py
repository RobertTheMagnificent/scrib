#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager

# User command
alias = "control"
command = { alias: "Usage: !control password\nAllow user to have access to bot commands." }

# Plugin Action
class ControlPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == command and len(cmds) > 1 and scrib.source not in scrib.owners:
			msg = ""
			if cmds[1] == scrib.settings.password:
				scrib.owners.append(scrib.source)
				msg = "You've been added to controllers list."
			else:
				msg = "Try again."
			return msg

PluginManager.addPlugin( command, alias, ControlPlugin() )
