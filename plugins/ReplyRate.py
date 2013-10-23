from plugins import ScribPlugin

# User Alias and Command
alias = "!replyrate"
command = { "replyrate": "Usage: !echo message\nMake the bot mimic your message." }

# Plugin Action
class ReplyRatePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		msg = ""
		if command_list[0] == alias and len(command_list)==1:
			msg = "Reply rate is "+`scrib.settings.reply_chance`+"%."
		elif len(command_list)<=2:
			try:
				scrib.settings.reply_chance = int(command_list[1])
				msg = "Now replying to %d%% of messages." % int(command_list[1])
			except:
				msg = "Reply rate is %d%%." % scrib.settings.reply_chance
			return msg

ScribPlugin.addPlugin( command, alias, ReplyRatePlugin() )
