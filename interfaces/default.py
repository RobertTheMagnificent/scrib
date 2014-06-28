#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Scrib default LineIn interface.
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

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
				self.settings = my_scrib.settings # compat, kinda gross
				self.start()

		def start(self):
				self.scrib.barf('ACT', "Scrib offline chat!")
				self.scrib.barf('ACT', "Type !quit to leave")
				self.scrib.barf('ACT', "Enter your name?\033[0m")
				name = raw_input("> ")
				time.sleep(1)
				self.scrib.barf('MSG', "Hello %s." %name)
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

						# Pass message to scrib
						self.scrib.process(self, body, 100, 1, ( name ), owner = 1)

		def linein_commands(self, body):
				command_list = string.split(body)
				command_list[0] = string.lower(command_list[0])

		def output(self, message, args):
				"""
				Output a line of text.
				"""
				message = message.replace("#nick", args)
				self.scrib.barf('MSG', message + "\033[0m")

if __name__ == "__main__":
		try:
			my_scrib = scrib.scrib()
		except ValueError, e:
			from core import barf
			barf.Barf('ERR', traceback.format_exc())
			sys.exit(0)

		try:
			ModLineIn(my_scrib)
		except SystemExit:
			pass
		except:
			my_scrib.barf('ERR', traceback.format_exc())
			my_scrib.barf('ERR', "Oh no, I've crashed! Would you like to save my brain?", False)
			c = raw_input("[Y/n]")
			if c[:1] != 'n':
				my_scrib.save_all(my_scrib)
		del my_scrib
		sys.exit(0)
