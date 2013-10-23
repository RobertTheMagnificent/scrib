from plugins import ScribPlugin

# User Alias and Command
alias = "!echo"
command = { "echo": "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class EchoPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list):
		if command_list[0] == alias and len(command_list) >= 1:
			phrase=""
			for x in xrange (1, len (command_list)):
				phrase = phrase + str(command_list[x]) + " "
			return phrase

ScribPlugin.addPlugin( command, alias, EchoPlugin() )
