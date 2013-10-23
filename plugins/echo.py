from plugins import ScribPlugin

# User Alias and Command
alias = "!echo"
command = { "echo": "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class EchoPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list):
		if len(command_list) >= 2:
			phrase=""
			for x in xrange (2, len (command_list)):
				phrase = phrase + str(command_list[x]) + " "
			return phrase
			#self.output(phrase, ("", command_list[1], "", c, e))
		

ScribPlugin.addPlugin( command, alias, EchoPlugin() )
