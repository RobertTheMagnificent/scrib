#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager

# User Alias and Command
sleep_alias = "sleep"
sleep_command = { sleep_alias: "Usage: !sleep \nMake the bot stop talking." }

# Plugin Action
class SleepPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == sleep_cmd and len(cmds)==1:
			msg = "Going to sleep. Goodnight!"
			scrib.settings.muted = 1
		else:
			msg = "Zzz..."
		return msg

wake_alias = "wake"
wake_command = { wake_alias: "Owner command. Usage: !wake\nAllow the bot to talk." }

class WakePlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == wake_cmd and scrib.settings.muted == 1:
			scrib.settings.muted = 0
			msg = "Whoohoo!"
		else:
			msg = "But I'm already awake..."
		return msg

PluginManager.addPlugin( sleep_command, sleep_alias, SleepPlugin() )
PluginManager.addPlugin( wake_command, wake_alias, WakePlugin() )
