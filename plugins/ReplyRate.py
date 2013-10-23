from plugins import ScribPlugin

# User Alias and Command
alias = "!replyrate"
command = { "replyrate": "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class ReplyRatePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list):
		if command_list[0] == alias and len(command_list)==1:
			msg = ModIRC.scrib.settings.pubsym+"Reply rate is "+`self.settings.reply_chance`+"%."
		return msg

ScribPlugin.addPlugin( command, alias, ReplyRatePlugin() )
