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
			if self.settings.debug == True:
				self.barf('DBG', "Message is type: %s" % type(message))
			# Firstly, make sure it isn't doesn't have a uri.
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
			if self.settings.debug == 1:
				self.barf('DBG', 'Cleaned messages is of type: %s' % type(message))
			return message

	
	# Some more machic to fix some common issues with the teach system
	def teach_filter(self, message):
		message = message.replace("||", "$C4")
		message = message.replace("|-:", "$b7")
		message = message.replace(":-|", "$b6")
		message = message.replace(";-|", "$b5")
		message = message.replace("|:", "$b4")
		message = message.replace(";|", "$b3")
		message = message.replace("=|", "$b2")
		message = message.replace(":|", "$b1")
		return message


	def unfilter_reply(self, message):
		"""
		This undoes the phrase mangling the central code does
		so the bot sounds more human :P
		"""
	
		#barf.Barf('DBG', "Orig Message: %s" % message)

		# Had to write my own initial capitalizing code *sigh*
		message = "%s%s" % (message[:1].upper(), message[1:])
		# Fixes punctuation
		message = message.replace(" ?", "?")
		message = message.replace(" !", "!")
		message = message.replace(" .", ".")
		message = message.replace(" ,", ",")
		message = message.replace(" : ", ": ")
		message = message.replace(" ; ", "; ")
		# Fixes I and I contractions
		message = message.replace(" i ", " I ")
		message = message.replace(" i'", " I'")
		# Fixes the common issues with the teach system
		message = message.replace("$C4", "||")
		message = message.replace("$b7", "|-:")
		message = message.replace("$b6", ";-|")
		message = message.replace("$b5", ":-|")
		message = message.replace("$b4", "|:")
		message = message.replace("$b3", ";|")
		message = message.replace("$b2", "=|")
		message = message.replace("$b1", ":|")
	
		# New emoticon filter that tries to catch almost all variations	
		eyes, nose, mouth = r":;8BX=", r"-~'^O", r")(></\|CDPo39"
		# Removed nose from the pattern for the sake of my sanity
		pattern1 = "[\s][%s][%s][\s]" % tuple(map(re.escape, [eyes, mouth]))
		pattern2 = "[\s][%s][%s][\s]" % tuple(map(re.escape, [mouth, eyes]))
		eye, horzmouth = r"^><vou*@#sxz~-=+", r"-_o.wv"
		pattern3 = "[\s][%s][%s][%s][\s]" % tuple(map(re.escape, [eye, horzmouth, eye]))

		# Add whitespace for less false positives; it will be stripped out of the string later
		if not message == "":
			message = " " + message + " "
		emoticon = re.search(pattern1, message, re.IGNORECASE)
		pattern = pattern1
		if emoticon == None:
			emoticon = re.search(pattern2, message, re.IGNORECASE)
			pattern = pattern2
			if emoticon == None:
				emoticon = re.search(pattern3, message, re.IGNORECASE)
				pattern = pattern3
	
		# Init some strings so it does't barf later
		extra = ""
		emote = ""
	
		if not emoticon == None:
			emoticon = "%s" % emoticon.group()
			emotebeg = re.search(pattern, message, re.IGNORECASE).start()
			emoteend = re.search(pattern, message, re.IGNORECASE).end()
		
			# Remove the whitespace we added earlier
			message = message.strip()
		
			if not emotebeg == 0:
				emotebeg = emotebeg - 1
			if emotebeg == 0:
				emoteend = emoteend - 2
			emote = message[emotebeg:emoteend]
			barf.Barf('DBG', "Emote found: %s" % emote)
			new_message = message[:emotebeg]
			extra = message[emoteend:]
			message = new_message
		
			# Fixes the annoying XP capitalization in words...
			message = message.replace("XP", "xp")
			message = message.replace(" xp", " XP")
			message = message.replace("XX", "xx")
		
		if not message == "":
			# Remove whitespace if it wasn't removed earlier
			message = message.strip()
			if message.endswith(','):
				message = message[:-1]
			if not message.endswith(('.', '!', '?')):
				message = message + "."
			
		if not extra == "":
			extra = extra[1:]
			extra = "%s%s" % (extra[:1].upper(), extra[1:])
			if not extra.endswith(('.', '!', '?')):
				extra = extra + "."
			extra = extra + " "
			
		if not emote == "":
			message = message + extra + emote

		return message
