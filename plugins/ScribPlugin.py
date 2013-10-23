import time
process_table = {}
plugin_commands = {}
plugin_aliases = {}

def get_time():
	return time.strftime("%H:%M:%S", time.localtime(time.time()))

def addPlugin( command, alias, action ):
	global plugin_commands, plugin_aliases
	process_table[alias[1:]] = action
	plugin_commands = dict( plugin_commands.items() + command.items() )
	plugin_aliases = dict( plugin_aliases.items() + alias.items() )

class ScribPlugin:
	def action(self, stuff, scrib):
		return "Default Action"
