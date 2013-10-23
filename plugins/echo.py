from plugins import ScribPlugin

class EchoPlugin(ScribPlugin.ScribPlugin):
	def action(self, stuff):
		return stuff

ScribPlugin.plugincommands['!echo'] = "Usage: !echo message\nMake the bot mimic your message."
ScribPlugin.addPlugin( "echo", EchoPlugin() )
