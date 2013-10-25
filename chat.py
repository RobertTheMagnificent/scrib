#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Scrib Offline line input module

import string
import sys

sys.path.append('core/')
sys.path.append('plugins/')

import time
import scrib
import PluginManager
import cfgfile

class ModLineIn:
		"""
		Module to interface console input and output with the Scrib learn
		and reply modules. Allows offline chat with Scrib.
		"""
		# Command list for this module
		commandlist = "LineIn Module Commands:\n!quit"
		commanddict = { "quit": "Usage: !quit\nQuits Scrib and saves the dictionary" }

		def __init__(self, my_scrib):
				self.scrib = my_scrib
				self.start()

				self.settings = cfgfile.cfgset()
				self.settings.load("conf/scrib-irc.cfg",
					{ "myname": ("The bot's nickname", "Scribbington"),
					} )

		#myname = self.settings.myname

		def start(self):
				#scrib.barf(scrib.ACT, "Scrib offline chat!")
				scrib.barf(scrib.ACT, "Type !quit to leave")
				#myname = self.settings.myname
				#scrib.barf(scrib.ACT, "You're talking to %s." %myname)
				scrib.barf(scrib.ACT, "To begin, please enter your name.\033[0m")
				name = raw_input("> ")
				time.sleep(1)
				scrib.barf(scrib.MSG, "Hello %s." %name)
				while 1:
						try:
								body = raw_input("> ")
						except (KeyboardInterrupt, EOFError), e:
								print
								return
						if body == "":
								continue
						if body[0] == "!":
								if self.linein_commands(body):
										continue
						# Pass message to borg
						self.scrib.process_msg(self, body, 100, 1, ( name ), owner = 1)

		def linein_commands(self, body):
				command_list = string.split(body)
				command_list[0] = string.lower(command_list[0])

				if command_list[0] == "!quit":
						sys.exit(0)

		def output(self, message, args):
				"""
				Output a line of text.
				"""
				message = message.replace("#nick", args)
				time.sleep(1)
				scrib.barf(scrib.MSG, message + "\033[0m")

if __name__ == "__main__":
		# start the pyborg
		my_scrib = scrib.scrib()
		try:
				ModLineIn(my_scrib)
		except SystemExit:
				pass
		my_scrib.save_all()
		del my_scrib


