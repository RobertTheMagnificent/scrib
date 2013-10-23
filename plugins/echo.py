from plugins import ScribPlugin

# User Alias and Command
alias = "!echo"
command = { "echo": "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class EchoPlugin(ScribPlugin.ScribPlugin):
	def action(self, stuff):
		return stuff

ScribPlugin.addPlugin( command, alias, EchoPlugin() )
