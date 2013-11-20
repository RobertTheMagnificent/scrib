#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Scrib default LineIn interface.
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from core import barf
from core import scrib
from plugins import PluginManager
import traceback
import time
import string

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

		def start(self):
				barf.barf(barf.ACT, "Scrib offline chat!")
				barf.barf(barf.ACT, "Type !quit to leave")
				barf.barf(barf.ACT, "Enter your name?\033[0m")
				name = raw_input("> ")
				time.sleep(1)
				barf.barf(barf.MSG, "Hello %s." %name)
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
				barf.barf(barf.MSG, message + "\033[0m")

if __name__ == "__main__":
		my_scrib = scrib.scrib()
		try:
			ModLineIn(my_scrib)
		except SystemExit:
			pass
		except:
			traceback.print_exc()
			c = raw_input(barf.raw_barf(barf.ERR, "Oh no, I've crashed! Would you like to save my brain? (Y/n) "))
			if c[:1] == 'n':
				sys.exit(0)
		my_scrib.save_all(False)
		del my_scrib

