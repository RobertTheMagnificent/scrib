process_table = {}

def get_time():
	return time.strftime("%H:%M:%S", time.localtime(time.time()))

def addPlugin( alias, command ):
	print "[%s][*] Adding %s, %s" % (get_time(), alias, command)
	process_table[alias] = command

class ScribPlugin:
	def action(self, stuff):
		return "Default Action"
