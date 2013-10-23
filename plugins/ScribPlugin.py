import time
process_table = {}
plugin_commands = {}

def get_time():
	return time.strftime("%H:%M:%S", time.localtime(time.time()))

def addPlugin( alias, command ):
	process_table[alias] = command

class ScribPlugin:
	def action(self, stuff):
		return "Default Action"
