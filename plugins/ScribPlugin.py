import time
process_table = {}
plugin_commands = {}
plugin_aliases = []

# I don't like this... Should be using
# the one in scrib.py...
def get_time():
	return time.strftime("\033[0m[%H:%M:%S]", time.localtime(time.time()))

def addPlugin( command, alias, action ):
	global plugin_commands, plugin_aliases
	process_table[alias[1:]] = action
	plugin_commands = dict( plugin_commands.items() + command.items() )
	plugin_aliases.extend(alias)

class ScribPlugin:
	def action(self, stuff, scrib):
		return "Default Action"
