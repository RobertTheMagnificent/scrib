from plugins import ScribPlugin

# User Alias and Command
alias = "!control"
command = { "control": "Usage: !control password\nAllow user to have access to bot commands." }

# Plugin Action
class ControlPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list):
		if command_list[0] == alias and len(command_list) > 1 and ModIRC.source not in ModIRC.owners:
			if command_list[1] == ModIRC.settings.password:
				ModIRC.owners.append(ModIRC.source)
				msg "You've been added to controllers list!"
			else:
				msg = "Try again."
		return msg

ScribPlugin.addPlugin( command, alias, ControlPlugin() )
