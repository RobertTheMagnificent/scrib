from plugins import ScribPlugin

# User Alias and Command
sleep_alias = "!sleep"
sleep_command = { "sleep": "Usage: !sleep \nMake the bot stop talking." }

# Plugin Action
class SleepPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		if command_list[0] == sleep_alias and len(command_list)==1:
			msg = "Going to sleep. Goodnight!"
			scrib.settings.speaking = 0
		else:
			msg = "Zzz..."
		return msg

wake_alias = "!wake"
wake_command = { "wake": "Owner command. Usage: !wake\nAllow the bot to talk." }

class WakePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		if command_list[0] == wake_alias and scrib.settings.speaking == 0:
			scrib.settings.speaking = 1 
			msg = "Whoohoo!"
		else:
			msg = "But I'm already awake..."
		return msg

ScribPlugin.addPlugin( sleep_command, sleep_alias, SleepPlugin() )
ScribPlugin.addPlugin( wake_command, wake_alias, WakePlugin() )
