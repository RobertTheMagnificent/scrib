
process_table = {}

def addPlugin( alias, command ):
	process_table[alias] = command

class TestPlugin:
	def action(self, stuff):
		return "Default Action"
