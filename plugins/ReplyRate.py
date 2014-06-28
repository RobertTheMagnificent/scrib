from plugins import PluginManager
from core import barf

# User command
command = "!replyrate"

# Plugin Action
class ReplyRatePlugin(PluginManager.Load):
	def action(self, command_list, scrib, c):
		#if scrib.settings.debug == 1:
		#	barf(DBG, "ReplyRate Plugin activated")
		if command_list[0] == command and len(command_list) == 2:
			scrib.settings.reply_chance = int(command_list[1])
			msg = "Now replying to %d%% of messages." % int(command_list[1])
		else:
			msg = "Reply rate is %d%%." % scrib.settings.reply_chance
		return msg

PluginManager.addPlugin( command, command, ReplyRatePlugin() )
