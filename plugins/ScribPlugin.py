
process_table = {}

def addPlugin( alias, command ):
	print "[UNF][*] Adding %s %s" % (alias, command)
	process_table[alias] = command

class ScribPlugin:
	def action(self, stuff):
		return "Default Action"
