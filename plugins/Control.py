from plugins import ScribPlugin

# User Alias and Command
alias = "!control"
command = { "control": "Usage: !control password\nAllow user to have access to bot commands." }

# Plugin Action
class ControlPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		if command_list[0] == alias and len(command_list) > 1 and scrib.source not in scrib.owners:
			msg = ""
			if command_list[1] == scrib.settings.password:
				scrib.owners.append(scrib.source)
				msg = "You've been added to controllers list."
			else:
				msg = "Try again."
			return msg

ScribPlugin.addPlugin( command, alias, ControlPlugin() )
