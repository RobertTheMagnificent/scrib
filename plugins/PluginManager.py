#! /usr/bin/env python
# -*- coding: utf-8 -*-

process_table = {}
plugin_commands = {}
plugin_aliases = []

def addPlugin( command, alias, action ):
	global plugin_commands, plugin_aliases
	process_table[alias] = action
	plugin_commands = dict( plugin_commands.items() + command.items() )
	plugin_aliases.append(alias)

class Load:
	def action(self, stuff, scrib, c):
		return "Default Action"
