from plugins import ScribPlugin

# User Alias and Command
alias = "!private"
command = { "replyrate": "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class PrivatePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		if command_list[0] == alias and len(command_list)==1:
			msg = "$sPrivate mode " % scrib.settings.pubsym
			if len(command_list) == 1:
				if scrib.settings.private == 0:
					msg = msg + "off"
				else:
					msg = msg + "on"
			else:
				toggle = command_list[1]
				if toggle == "on":
					msg = msg + "on"
					scrib.settings.private = 1
				else:
					msg = msg + "off"
					scrib.settings.private = 0
		return msg

ScribPlugin.addPlugin( command, alias, PrivatePlugin() )
