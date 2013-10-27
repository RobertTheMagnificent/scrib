from plugins import ScribPlugin

# User Alias and Command
alias = "!replyrate"
command = { "replyrate": "Usage: !replyrate <num>\n Set the bot's replyrate." }

# Plugin Action
class ReplyRatePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if scrib.settings.debug == 1:
			ScribPlugin.barf(ScribPlugin.DBG, "ReplyRate Plugin activated: %s; %s." % (len(command_list), command_list))
		if command_list[0] == alias and len(command_list) >= 1:
			scrib.settings.reply_chance = int(command_list[1])
			msg = "Now replying to %d%% of messages." % int(command_list[1])
		else:
			msg = "Reply rate is %d%%." % scrib.settings.reply_chance
		return msg

ScribPlugin.addPlugin( command, alias, ReplyRatePlugin() )
