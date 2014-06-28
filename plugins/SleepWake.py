#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager

# User Alias and Command
sleep_cmd = "!sleep"

# Plugin Action
class SleepPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == sleep_cmd and len(cmds)==1:
			msg = "Going to sleep. Goodnight!"
			scrib.settings.muted = 0
		else:
			msg = "Zzz..."
		return msg

wake_cmd = "!wake"
class WakePlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if cmds[0] == wake_cmd and scrib.settings.muted == 0:
			scrib.settings.speaking = 1 
			msg = "Whoohoo!"
		else:
			msg = "But I'm already awake..."
		return msg

PluginManager.addPlugin( sleep_command, sleep_cmd, SleepPlugin() )
PluginManager.addPlugin( wake_command, wake_cmd, WakePlugin() )
