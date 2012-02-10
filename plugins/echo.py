from plugins import ScribPlugin

class EchoPlugin(ScribPlugin.ScribPlugin):
	def action(self, stuff):
		return stuff

ScribPlugin.addPlugin( "echo", EchoPlugin() )
