#! /usr/bin/env python
# -*- coding: utf-8 -*-

process_table = {}
plugin_commands = []

def addPlugin( command, action ):
	global plugin_commands, plugin_aliases
	process_table[command] = action
	plugin_commands.append(command)

class Load:
	def action(self, stuff, scrib, c):
		return "Default Action"
