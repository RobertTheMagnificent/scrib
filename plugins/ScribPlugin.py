from core import barf

process_table = {}
plugin_commands = {}
plugin_aliases = []

def addPlugin( command, alias, action ):
	global plugin_commands, plugin_aliases
	process_table[alias[1:]] = action
	plugin_commands = dict( plugin_commands.items() + command.items() )
	plugin_aliases.append(alias)

class ScribPlugin:
	def action(self, stuff, scrib):
		return "Default Action"
