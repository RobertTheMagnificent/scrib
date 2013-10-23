from plugins import ScribPlugin
import sys

# User Alias and Command
nick_alias = "!nick"
nick_command = { "nick": "Owner command. Usage: !nick nickname\nChange nickname." }

# Plugin Action
class NickPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == nick_alias and len(command_list) == 1:
			try:
				scrib.connection.nick(command_list[1])
				scrib.settings.myname = command_list[1]
				msg = "Nick changed."
			except:
				msg = "Couldn't change nick."
				pass
		return msg

join_alias = "!join"
join_command = { "join": "Owner command. Usage: !join #chan1 [#chan2 [...]]\nJoin one or more channels." }

class JoinPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == join_alias:
			for x in xrange(1, len(command_list)):
				if not command_list[x] in scrib.chans:
					msg = "Attempting to join channel %s" % command_list[x]
					scrib.chans.append(command_list[x])
					scrib.c.join(command_list[x])
			return msg

part_alias = "!part"
part_command = { "part": "Owner command. Usage: !part #chan1 [#chan2 [...]]\nLeave one or more channels." }

class PartPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == part_alias:
			for x in xrange(1, len(command_list)):
				if command_list[x] in scrib.chans:
					msg = "Leaving channel %s" % command_list[x]
					scrib.chans.remove(command_list[x])
					scrib.c.part(command_list[x])
			return msg

chans_alias = "!chans"
chans_command = { "chans": "Owner command. Usage: !chans\nList channels currently on." }

class ChansPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == chans_alias:
			if len(scrib.channels.keys())==0:
				msg = "I'm currently on no channels"
			else:
				msg = "I'm currently on "
				channels = scrib.channels.keys()
				for x in xrange(0, len(channels)):
					msg = msg+channels[x]+" "
			return msg

quit_alias = "!quit"
quit_command = { "quit": "Owner command. Usage: !quit\nMake the bot quit IRC." }

class QuitPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == quit_alias:
			sys.exit()

quitmsg_alias = "!quitmsg"
quitmsg_command = { "quitmsg": "Owner command. Usage: !quitmsg [message]\nSet the quit message. Without arguments show the current quit message." }

class QuitmsgPlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == quitmsg_alias:
			if len(command_list) > 1:
				scrib.settings.quitmsg = body.split(" ", 1)[1]
				msg = "New quit message is \"%s\"" % scrib.settings.quitmsg
			else:
				msg = "Quit message is \"%s\"" % scrib.settings.quitmsg
		return msg

ignore_alias = "!ignore"
ignore_command = { "ignore": "Owner command. Usage: !ignore [nick1 [nick2 [...]]]\nIgnore one or more nicknames. Without arguments it lists ignored nicknames." }

class IgnorePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == ignore_alias:
			# if no arguments are given say who we are
			# ignoring
			if len(command_list) == 1:
				msg = "I'm ignoring "
				if len(scrib.settings.ignorelist) == 0:
					msg = msg + "nobody"
				else:
					for x in xrange(0, len(scrib.settings.ignorelist)):
						msg = msg + scrib.settings.ignorelist[x] + " "
			# Add everyone listed to the ignore list
			# eg !ignore tom dick harry
			else:
				for x in xrange(1, len(command_list)):
					scrib.settings.ignorelist.append(command_list[x])
					msg = "Ignoring %s" % command_list[x]
		return msg

unignore_alias = "!unignore"
unignore_command = { "unignore": "Owner command. Usage: !unignore nick1 [nick2 [...]]\nUnignores one or more nicknames." }

class UnIgnorePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == unignore_alias:
			# Remove everyone listed from the ignore list
			# eg !unignore tom dick harry
			for x in xrange(1, len(command_list)):
				try:
					scrib.settings.ignorelist.remove(command_list[x])
					msg = "Unignoring %s" % command_list[x]
				except:
					pass
		return msg

replyignore_alias = "!replyignore"
replyignore_command = { "unignore": "Owner command. Usage: !unignore nick1 [nick2 [...]]\nUnignores one or more nicknames." }

class UnIgnorePlugin(ScribPlugin.ScribPlugin):
	def action(self, command_list, scrib):
		if command_list[0] == unignore_alias:
			msg = "Replying to ignored users "
			if len(command_list) == 1:
				if scrib.settings.replyIgnored == 0:
					msg = msg + "off"
				else:
					msg = msg + "on"
			else:
				toggle = command_list[1]
				if toggle == "on":
					msg = msg + "on"
					scrib.settings.replyIgnored = 1
				else:
					msg = msg + "off"
					scrib.settings.replyIgnored = 0
		return msg

ScribPlugin.addPlugin( nick_command, nick_alias, NickPlugin() )
ScribPlugin.addPlugin( join_command, join_alias, JoinPlugin() )
ScribPlugin.addPlugin( part_command, part_alias, PartPlugin() )
ScribPlugin.addPlugin( chans_command, chans_alias, ChansPlugin() )
ScribPlugin.addPlugin( quit_command, quit_alias, QuitPlugin() )
ScribPlugin.addPlugin( quitmsg_command, quitmsg_alias, QuitmsgPlugin() )
ScribPlugin.addPlugin( ignore_command, ignore_alias, IgnorePlugin() )
ScribPlugin.addPlugin( unignore_command, unignore_alias, UnIgnorePlugin() )
ScribPlugin.addPlugin( replyignore_command, replyignore_alias, ReplyIgnorePlugin() )