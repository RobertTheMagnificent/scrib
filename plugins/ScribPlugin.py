import time
process_table = {}
plugin_commands = {}
plugin_aliases = []

def get_time():
	return time.strftime("\033[0m[%H:%M:%S]", time.localtime(time.time()))

def barf(msg_code, message):
		print get_time() + msg_code + message

# Message Codes
ACT = '\033[93m [~] '
MSG = '\033[94m [-] '
SAV = '\033[92m [#] '
ERR = '\033[91m [!] '

def addPlugin( command, alias, action ):
	global plugin_commands, plugin_aliases
	process_table[alias[1:]] = action
	plugin_commands = dict( plugin_commands.items() + command.items() )
	plugin_aliases.extend(alias)

class ScribPlugin:
	def action(self, stuff, scrib):
		return "Default Action"
