import time
process_table = {}
plugin_commands = {}

def get_time():
	return time.strftime("%H:%M:%S", time.localtime(time.time()))

def addPlugin( command, alias, action ):
	process_table[alias] = action
	plugin_commands = dict( plugin_commands.items() + command.items() )

class ScribPlugin:
	def action(self, stuff):
		return "Default Action"
