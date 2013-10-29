from plugins import ScribPlugin
from core import barf

# User Alias and Command
alias = "!replyrate"
command = { "replyrate": "Usage: !replyrate <num>\n Set the bot's replyrate." }

# Plugin Action
class ReplyRatePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib, c):
		#if scrib.settings.debug == 1:
		#	barf(DBG, "ReplyRate Plugin activated")
		if command_list[0] == alias and len(command_list) == 2:
			scrib.settings.reply_chance = int(command_list[1])
			msg = "Now replying to %d%% of messages." % int(command_list[1])
		else:
			msg = "Reply rate is %d%%." % scrib.settings.reply_chance
		return msg

ScribPlugin.addPlugin( command, alias, ReplyRatePlugin() )
