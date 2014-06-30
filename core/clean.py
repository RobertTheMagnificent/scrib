#! /usr/bin/env python
# -*- coding: utf-8 -*-
import re

import brain
import cfg

class clean:

	def __init__(self):
		self.settings = cfg.set()
		self.barf = brain.barf.Barf
		self.settings.load('conf/brain.cfg', '', True)

	def line(self, message):
			"""
			Sanitize incoming data for ease of learning.
			"""
			if message == '':
				return '';
				
			# Make sure it isn't doesn't have a uri-like thing.
			urls = ['://']
			for url in urls:
				if url in message:
					brain.barf.Barf('ACT', 'URI-like thing detected. Ignoring.')
					return 0
			message = re.sub("([a-zA-Z0-9\-_]+?\.)*[a-zA-Z0-9\-_]+?\.[a-zA-Z]{2,5}(\/[a-zA-Z0-9]*)*", "", message)

			# remove garbage
			message = message.replace("\"", "")
			message = message.replace("\n", " ")
			message = message.replace("\r", " ")

			# remove matching brackets
			index = 0
			try:
				while 1:
					index = message.index("(", index)
					# Remove matching ) bracket
					i = message.index(")", index + 1)
					message = message[0:i] + message[i + 1:]
					# And remove the (
					message = message[0:index] + message[index + 1:]
			except ValueError, e:				
				pass # will just say 'substring not found' on every line that hasn't the above.

			# Strips out mIRC Control codes
			ccstrip = re.compile("\x1f|\x02|\x12|\x0f|\x16|\x03(?:\d{1,2}(?:,\d{1,2})?)?", re.UNICODE)
			message = ccstrip.sub("", message)

			# Few of my fixes...
			message = message.replace(": ", " : ")
			message = message.replace("; ", " ; ")
			# ^--- because some : and ; might be smileys...
			message = message.replace("`", "'")

			message = message.replace("?", " ? ")
			message = message.replace("!", " ! ")
			message = message.replace(".", " . ")
			message = message.replace(",", " , ")

			# Fixes broken emoticons...
			message = message.replace("^ . ^", "^.^")
			message = message.replace("- . -", "-.-")
			message = message.replace("O . o", "O.o")
			message = message.replace("o . O", "o.O")
			message = message.replace("o . o", "o.o")
			message = message.replace("O . O", "O.O")
			message = message.replace("< . <", "<.<")
			message = message.replace("> . >", ">.>")
			message = message.replace("> . <", ">.<")
			message = message.replace(": ?", ":?")
			message = message.replace(":- ?", ":-?")
			message = message.replace(", , l , ,", ",,l,,")
			message = message.replace("@ . @", "@.@")
			message = message.replace("D :", "D:")
			message = message.replace("c :", "c:")
			message = message.replace("C :", "C:")

			words = message.split()
			for x in xrange(0, len(words)):
				#is there aliases ?
				for z in self.settings.aliases.keys():
					if self.settings.debug == 1:
						self.barf('DBG', 'Is %s in keys?' % z)
					for alias in self.settings.aliases[z]:
						pattern = "^%s$" % alias
						if re.search(pattern, words[x]):
							if self.settings.debug == 1:
								self.barf('DBG', 'Checking if %s is in %s' % ( z, words[x] ))
							words[x] = z

			message = " ".join(words)
			return message
