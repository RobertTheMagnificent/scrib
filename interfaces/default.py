#! /usr/bin/env python
# -*- coding: utf-8 -*-
# Scrib default LineIn interface.
import os
import string
import sys
import time
import traceback

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from core import scrib

class ModLineIn:
		"""
		Module to interface console input and output with the Scrib learn
		and reply modules. Allows offline chat with Scrib.
		"""

		def __init__(self, my_scrib):
			self.scrib = my_scrib
			self.settings = self.scrib.settings #compat. yuk.
			self.barf = self.scrib.barf
			self.start()

		def start(self):
			self.barf('ACT', "Scrib offline chat!")
			self.barf('ACT', "Type !quit to leave")
			self.barf('ACT', "Enter your name?\033[0m")
			name = raw_input("> ")
			self.barf('MSG', "Hello %s." %name)
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
					my_scrib.process.msg(self, body, 100, 1, ( name ), owner = 1)

		def linein_commands(self, body):
			command_list = string.split(body)
			command_list[0] = string.lower(command_list[0])

		def output(self, message, args):
			"""
			Output a line of text.
			"""
			message = message.replace("#nick", args)
			self.barf('MSG', message + "\033[0m")

if __name__ == "__main__":
	try:
		my_scrib = scrib.scrib()
	except ValueError, e:
		from core import barf
		my_scrib.barf('ERR', traceback.format_exc())
		sys.exit(0)

	try:
		ModLineIn(my_scrib)
	except SystemExit:
		pass
	except:
		from core import barf
		barf.Barf('ERR', traceback.format_exc())
		barf.Barf('ERR', "Oh no, I've crashed! Would you like to save my brain?", False)
		c = raw_input("[Y/n]")
		if c[:1] != "n":
			my_scrib.process.brain.shutdown(my_scrib)