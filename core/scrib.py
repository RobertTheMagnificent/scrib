#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import *
import sys
import os
import fileinput
import re
import time

import barf
import brain
import cfg
from plugins import PluginManager

# Makes !learn and !teach usable
def dbread(key):
	value = None
	if os.path.isfile("brain/prepared.dat"):
		file = open("brain/prepared.dat")
		for line in file.readlines():
			reps = int(len(line.split(":=:")) - 1)
			data = line.split(":=:")[0]
			dlen = r'\b.{2,}\b'
			if re.search(dlen, key, re.IGNORECASE):
				if key in data or data in key:
					if reps > 1:
						repnum = randint(1, int(reps))
						value = line.split(":=:")[repnum].strip()
					else:
						value = line.split(":=:")[1].strip()
					break
			else:
				value = None
				break

		file.close()
	return value


def dbwrite(key, value):
	if dbread(key) is None:
		file = open("brain/prepared.dat", "a")
		file.write(str(key) + ":=:" + str(value) + "\n")
		file.close()

	else:
		for line in fileinput.input("brain/prepared.dat", inplace=1):
			data = line.split(":=:")[0]
			dlen = r'\b.{2,}\b'
			if re.search(dlen, key, re.IGNORECASE):
				if key.lower() in data.lower() or data.lower() in key.lower():
					print str(line.strip()) + ":=:" + str(value)
			else:
				print line.strip()

# Some more machic to fix some common issues with the teach system
def teach_filter(message):
	message = message.replace("||", "$C4")
	message = message.replace("|-:", "$b7")
	message = message.replace(":-|", "$b6")
	message = message.replace(";-|", "$b5")
	message = message.replace("|:", "$b4")
	message = message.replace(";|", "$b3")
	message = message.replace("=|", "$b2")
	message = message.replace(":|", "$b1")
	return message


def unfilter_reply(message):
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


class scrib:
	"""
	The meat of scrib
	"""

	def __init__(self):
		"""
		Here we'll load settings and set up modules.
		"""
		self.version = "1.1.1"

		self.barf = barf.Barf # So that we don't have to include it elsewhere.
		# Brain stuff.
		self.brain = brain.brain()
		
		# This is where we do some ownership command voodoo.
		self.owner_commands = {
			'alias': "alias [this] [that]",
			'find': "find [word]",
			'forget': "forget [word]",
			'censor': "censor [word]",
			'check': "Checks hash table for consistency.",
			'context': "context [word] (outputs to console)",
			'learn': "learn [word]",
			'learning': "Toggles bot learning.",
			'rebuild': "Performs a brain rebuild. Is desructive.",
			'replace': "replace [current] [new]",
			'replyrate': "Shows/sets the reply rate.",
			'save': "Saves the brain.",
			'uncensor': "uncensor [word1] [word2] [word3] ...",
			'unlearn': "unlearn [word]",
			'quit': "Shut the bot down."
		}
		self.general_commands = {
			'date': "Shows the date.",
			'help': "Shows commands.",
			'known': "known [word]",
			'owner': "Shows owner.",
			'version': "Displays bot version.",
			'words': "Shows number of words and contexts."
		}
		self.plugin_commands = PluginManager.plugin_commands
		self.commands = self.general_commands.keys() + self.owner_commands.keys() + self.plugin_commands.keys()

		self.cfg = cfg
		self.settings = self.cfg.set()
		self.settings.load("conf/scrib.cfg",{
							"name": "scrib",
							"self.settings.symbol": "!",
							"reply_rate": 100,
							"nick_reply_rate": 100,
							"debug": 0,
							"muted": 0,
							"ignore_list": [],
							"version": self.version
							})
		self.debug = self.settings.debug

		if dbread("hello") is None:
			dbwrite("hello", "hi #nick")

	def process(self, interface, body, replyrate, learn, args, owner=0, muted=0):
		"""
		Process message 'body' and pass back to IO module with args.
		If muted == 1 only respond with taught responses.
		"""

		if self.debug == 1:
			self.barf('DBG', "Processing message...")

		# add trailing space so sentences are broken up correctly
		body = body + " "

		# Parse commands
		if body[0] == self.settings.symbol:
			if self.debug == 1:
				user = 'user'
				if owner == 1:
					user = 'owner'
				msg = self.barf('DBG', "Parsing commands by %s" % user)

			self.do(interface, body[1:], args, owner)
			return


		# Filter out garbage and do some formatting
		if self.debug == 1:
			self.barf('DBG', "Filtering message...")
		body = self.brain.clean.line(body)


		# if status 0 is set, ignore.
		if body == 0:
			return

		# Learn from input
		if self.brain.settings.learning == 1:
			if self.debug == 1:
				self.barf('DBG', "Learning from: %s" % body)
			self.brain.learn(body)


		# Make a reply if desired
		if randint(0, 99) < replyrate:
			if self.debug == 1:
				self.barf('DBG', "Decided to answer...")
			message = ""

			if muted == 0:
				#Look if we can find a prepared answer
				if dbread(body):
					if self.debug == 1:
						self.barf('DBG', "Using prepared answer.")
					message = unfilter_reply(dbread(body))
					if self.debug == 1:
						self.barf('DBG', "Replying with: " + message)
					return

				for sentence in self.brain.static_answers.sentences.keys():
					pattern = "^%s$" % sentence
					if re.search(pattern, body):
						if self.debug == 1:
							self.barf('DBG', "Searching for reply...")
						message = self.brain.static_answers.sentences[sentence][
							randint(0, len(self.brain.static_answers.sentences[sentence]) - 1)]
						break
					else:
						if body in self.unfilterd:
							self.unfilterd[body] = self.unfilterd[body] + 1
						else:
							self.unfilterd[body] = 0

				if message == "":
					if self.debug == 1:
						self.barf('DBG', "No prepared answer; thinking...")
					message = self.reply(body)
					if self.debug == 1:
						self.barf('DBG', "Reply formed; unfiltering...")
					message = unfilter_reply(message)
					if self.debug == 1:
						self.barf('DBG', "Unfiltered message: " + message)
			else:
				return

			# empty. do not output
			if message == "":
				if self.debug == 1:
					self.barf('DBG', "Message empty.")
				replying = "Not replying."
			else:
				time.sleep(.075 * len(message))
				if self.debug == 1:
					replying = "Reply sent."
				interface.output(message, args)
			if self.debug == 1:
				self.barf('DBG', replying)

	def do(self, interface, body, args, owner):
		"""
		Respond to commands.
		"""
		cmds = body.split()
		msg = ""

		if owner == 0 and cmds[0] in self.general.commands.keys():
			msg = "Sorry, but you're not an owner."
		
		if cmds[0] in self.commands:
			# Owner commands
			if owner == 1:
				if cmds[0] == "learn":
					try:
						key = ' '.join(cmds[1:]).split("|")[0].strip()
						key = re.sub("[\.\,\?\*\"\'!]", "", key)
						rnum = int(len(' '.join(cmds[1:]).split("|")) - 1)
						if "#nick" in key:
							msg = "Yeah, that won't work."
						else:
							value = teach_filter(' '.join(cmds[1:]).split("|")[1].strip())
							dbwrite(key[0:], value[0:])
							if rnum > 1:
								array = ' '.join(cmds[1:]).split("|")
								rcount = 1
								for value in array:
									if rcount == 1:
										rcount = rcount + 1
									else:
										dbwrite(key[0:], teach_filter(value[0:].strip()))
							else:
								value = ' '.join(cmds[1:]).split("|")[1].strip()
								dbwrite(key[0:], teach_filter(value[0:]))
							msg = "New response learned for %s" % key
					except Exception, e:
						msg = "I couldn't learn that: %s" % e

				elif cmds[0] == "forget":
					if os.path.isfile("brain/prepared.dat"):
						try:
							key = ' '.join(cmds[1:]).strip()
							for line in fileinput.input("brain/prepared.dat", inplace=1):
								data = line.split(":=:")[0]
								dlen = r'\b.{2,}\b'
								if re.search(dlen, key, re.IGNORECASE):
									if key.lower() in data.lower() or data.lower() in key.lower():
										pass
								else:
									print line.strip()
								msg = "Poof! '%s' is gone." % key
						except Exception, e:
							msg = "Sorry, I couldn't forget that: %s" % e
					else:
						msg = "I cannot forget what I do not know."

				elif cmds[0] == "find":
					if os.path.isfile("brain/prepared.dat"):
						rcount = 0
						matches = ""
						key = ' '.join(cmds[1:]).strip()
						file = open("brain/prepared.dat")
						for line in file.readlines():
							data = line.split(":=:")[0]
							dlen = r'\b.{2,}\b'
							if re.search(dlen, key, re.IGNORECASE):
								if key.lower() in data.lower() or data.lower() in key.lower():
									if key.lower() is "":
										pass
									else:
										rcount = rcount + 1
										if matches == "":
											matches = data
										else:
											matches = matches + ", " + data
						file.close()
						if rcount < 1:
							msg = "I have no match for %s" % (key)
						elif rcount == 1:
							msg = "I found 1 match: %s" % (matches)
						else:
							msg = "I found %d matches: %s" % (rcount, matches)
					else:
						msg = "Sorry, but I don't know know what you're on about."

				elif cmds[0] == "responses":
					if os.path.isfile("brain/prepared.dat"):
						rcount = 0
						file = open("brain/prepared.dat")
						for line in file.readlines():
							if line is "":
								pass
							else:
								rcount = rcount + 1
						file.close()
						if rcount < 1:
							msg = "I've learned no responses"
						elif rcount == 1:
							msg = "I've learned only 1 response"
						else:
							msg = "I've learned %d responses" % rcount
					else:
						msg = "You need to teach me something first!"

				# Check for broken links in the brain
				elif cmds[0] == "check":
					t = time.time()
					num_broken = 0
					num_bad = 0
					if self.settings.debug == 1:
						self.barf('DBG', 'Check commencing...')
					for w in self.brain.words.keys():
						w = w.encode('utf8', 'ignore')
						wlist = self.brain.words[w]
						if self.settings.debug == 1:
							self.barf('DBG', 'Checking %s against %s' % (w, wlist))
						for i in xrange(len(wlist) - 1, -1, -1):
							try:
								if self.settings.debug == 1:
									self.barf('DBG', "Trying %" % wlist[i])
									self.barf('DBG', '%s' % wlist[i])
								line_idx, word_num = wlist[i]
								if self.settings.debug == 1:
									self.barf('DBG', "line_idx: %s" % line_idx)
							except:
								msg = 'The hash table is malformed. Please use !rebuild, then !save.'
								self.barf('ERR', msg)
								interface.output(self.settings.symbol+msg, args)
								return
						
							# Nasty critical error we should fix
							if not self.brain.lines.has_key(line_idx):
								self.barf('ACT', "Removing broken link '%s' -> %d." % (w, line_idx))
								num_broken = num_broken + 1
								del wlist[i]
							else:
								# Check pointed to word is correct
								split_line = self.brain.lines[line_idx][0].split()
								if split_line[word_num] != w:
									self.barf('ACT', "Line '%s' word %d is not '%s' as expected." % \
											  (self.brain.lines[line_idx][0],
											   word_num, w))
									num_bad = num_bad + 1
									del wlist[i]
						if len(wlist) == 0:
							del self.brain.words[w]
							self.brain.stats['num_words'] = self.brain.stats['num_words'] - 1
							self.barf('ACT', "\"%s\" vaporized from brain." % w)

					msg = "Checked my brain in %0.2fs. Fixed links: %d broken, %d bad." % \
						  (
						   time.time() - t,
						   num_broken,
						   num_bad)

				elif cmds[0] == "rebuild":
					interface.output(self.settings.symbol+"Rebuilding...", args)
					msg = self.brain.auto_rebuild()

				elif cmds[0] == "replace":
					if len(cmds) < 3:
						return
					old = cmds[1]
					new = cmds[2]
					msg = self.replace(old, new)

				elif cmds[0] == "replyrate":
					if len(cmds) == 2:
						self.settings.reply_rate = int(cmds[1])
						msg = "Now replying to %d%% of messages." % int(cmds[1])
					else:
						msg = "Reply rate is %d%%." % self.settings.reply_rate

				elif cmds[0] == "context":
					if self.debug == 1:
						self.barf('DBG', "Checking contexts...")

					# build context we are looking for
					context = " ".join(cmds[1:])
					if context == "":
						return

					find_context = " ".join(cmds[1:])
					num_contexts = ""

					# Build context list
					context = " " + context + " "
					c = []
					# Search through contexts
					for x in self.brain.lines.keys():
						# get context
						ctxt = self.brain.lines[x][0]
						# add leading whitespace for easy sloppy search code
						# TODO Find a better, less sloppy way to do this crap
						ctxt = " " + ctxt + " "
						if ctxt.find(context) != -1:
							# Avoid duplicates (2 of a word
							# in a single context)
							num_contexts = len(c) + 1
							if len(c) == 0:
								c.append(self.brain.lines[x][0])
							elif c[len(c) - 1] != self.brain.lines[x][0]:
								c.append(self.brain.lines[x][0])
					x = 0

					if num_contexts != "":
						self.barf('ACT', "=========================================")
						self.barf('ACT', "Printing %d contexts containing \033[1m'%s'" % (num_contexts, find_context))
						self.barf('ACT', "=========================================")
					else:
						self.barf('ACT', "=========================================")
						self.barf('ACT', "No contexts to print containing \033[1m'%s'" % find_context)

					while x < 5:
						if x < len(c):
							lines = c
							self.barf('ACT', "%s" % lines[x])
						x += 1
					if len(c) == 5:
						return
					if x < 5:
						x = 5
					while x < len(c):
						lines = c
						self.barf('ACT', "%s" % lines[x])
						x += 1

					self.barf('ACT', "=========================================")

				# Remove a word from the vocabulary [use with care]
				elif cmds[0] == "unlearn":
					if self.debug == 1:
						self.barf('DBG', "Unlearning...")
					# build context we are looking for
					context = " ".join(cmds[1:])
					if context == "":
						return
					self.barf('ACT', "Looking for: %s" % context)
					# Unlearn contexts containing 'context'
					t = time.time()
					self.unlearn(context)
					# we don't actually check if anything was
					# done..
					msg = "Unlearn done in %0.2fs" % ( time.time() - t)
					msg += " You may want to !check the brain, to be safe."

				elif cmds[0] == "learning":
					msg = "Learning mode "
					if len(cmds) == 1:
						if self.brain.settings.learning == 0:
							msg += "off"
						else:
							msg += "on"
					else:
						toggle = cmds[1]
						if toggle == "on":
							msg += "on"
							self.brain.settings.learning = 1
						else:
							msg += "off"
							self.brain.settings.learning = 0

				elif cmds[0] == "censor":
					# no arguments. list censored words
					if len(cmds) == 1:
						if len(self.settings.censored) == 0:
							msg = "No words censored."
						else:
							msg = "I will not use the word(s) %s" % (
								 ", ".join(self.settings.censored))
					# add every word listd to censored list
					else:
						for x in xrange(1, len(cmds)):
							if cmds[x] in self.settings.censored:
								msg += "%s is already censored." % ( cmds[x])
							else:
								self.settings.censored.append(cmds[x])
								self.unlearn(cmds[x])
								msg += "%s is now censored." % ( cmds[x])
							msg += "\n"

				elif cmds[0] == "uncensor":
					if self.debug == 1:
						self.barf('DBG', "Uncensoring...")
					# Remove words listed from the censor list
					# eg !uncensor tom dick harry
					for x in xrange(1, len(cmds)):
						try:
							self.settings.censored.remove(cmds[x])
							msg = "%s is uncensored." % ( cmds[x])
						except ValueError, e:
							pass

				elif cmds[0] == 'quit':
					self.shutdown(interface)
			
				elif cmds[0] == 'save':
					self.barf('SAV', 'User initiated save')
					self.brain.save_all(interface)
					msg = "Saved!"

				elif cmds[0] == 'debug':
					msg = "debug mode "
					if len(cmds) == 1:
						if self.settings.debug == 0:
							msg = msg + 'off'
						else:
							msg = msg + 'on'
					else:
						toggle = cmds[1]
						if toggle == 'on':
							msg = msg + 'on'
							self.settings.debug = 1 # Set current session
							self.settings._defaults['debug'] = 1 # Set default to save to file.
						else:
							msg = msg + 'off'
							self.settings.debug = 0
							self.settings._defaults['debug'] = 0

				elif cmds[0] == "alias":
					# List aliases words
					if len(cmds) == 1:
						if len(self.brain.settings.aliases) == 0:
							msg = "No aliases"
						else:
							msg = "I will alias the word(s) %s." \
								  % (", ".join(self.brain.settings.aliases.keys()))
					# add every word listd to alias list
					elif len(cmds) == 2:
						if cmds[1][0] != '~': cmds[1] = '~' + cmds[1]
						if cmds[1] in self.brain.settings.aliases.keys():
							msg = "These words : %s are aliases to %s." \
								  % (" ".join(self.brain.settings.aliases[cmds[1]]), cmds[1] )
						else:
							msg = "The alias %s is not known." % cmds[1][1:]
					elif len(cmds) > 2:
						#create the aliases
						if cmds[1][0] != '~': cmds[1] = '~' + cmds[1]
						if not (cmds[1] in self.brain.settings.aliases.keys()):
							self.brain.settings.aliases[cmds[1]] = [cmds[1][1:]]
							self.replace(cmds[1][1:], cmds[1])
							msg += cmds[1][1:] + " "
						for x in xrange(2, len(cmds)):
							msg += "%s " % cmds[x]
							self.brain.settings.aliases[cmds[1]].append(cmds[x])
							#replace each words by his alias
							self.replace(cmds[x], cmds[1])
						msg += "have been aliased to %s." % cmds[1]

			# Publicly accessible commands
			if cmds[0] == 'help':
				if owner == 0 or owner == 1:
					msg = "General commands: "
					msg += ', '.join(str(cmd) for cmd in self.general_commands)
				if owner == 1:
					msg += " :: Owner commands: "
					msg += ', '.join(str(cmd) for cmd in self.owner_commands)
				if self.plugin_commands:
					msg += " :: Plugin commands: "
					msg += ', '.join(str(cmd) for cmd in self.plugin_commands)

			elif cmds[0] == "version":
				msg = 'scrib: %s; brain: %s' % ( self.version, self.brain.version )

			elif cmds[0] == "!date":
				msg = "It is ".join(i for i in os.popen('date').readlines())

			elif cmds[0] == "words":
				num_w = self.brain.stats['num_words']
				num_c = self.brain.stats['num_contexts']
				num_l = len(self.brain.lines)
				if num_w != 0:
					num_cpw = num_c / float(num_w) # contexts per word
				else:
					num_cpw = 0.0
				msg = "I know %d words (%d contexts, %.2f per word), 1%d lines." % (
					 num_w, num_c, num_cpw, num_l)

			elif cmds[0] == "known":
				if len(cmds) == 2:
					# single word specified
					word = cmds[1]
					if self.brain.words.has_key(word):
						c = len(self.brain.words[word])
						msg = "%s is known (%d contexts)" % ( word, c)
					else:
						msg = "%s is unknown." % ( word)
				elif len(cmds) > 2:
					# multiple words.
					words = []
					for x in cmds[1:]:
						words.append(x)
					msg = "Number of contexts: "
					for x in words:
						if self.brain.words.has_key(x):
							c = len(self.brain.words[x])
							msg += x + "(" + str(c) + ") "
						else:
							msg += x + "(0) "

		if cmds[0] not in self.commands:
			#msg = cmds[0] + " is not a registered command."
			self.barf('MSG', 'Ignoring a secret.')

		if msg != "":
			interface.output(self.settings.symbol+msg, args)


	def replace(self, old, new):
		"""
		Replace all occurrences of 'old' in the brain with
		'new'. Nice for fixing learnt typos.
		"""
		try:
			pointers = self.brain.words[old]
		except KeyError, e:
			return "%s is not known." % old
		changed = 0

		for x in pointers:
			# pointers consist of (line, word) to self.brain.lines
			l = x[0]
			w = x[1]
			line = self.brain.lines[l][0].split()
			number = self.brain.lines[l][1]
			if line[w] != old:
				# fucked brain
				self.barf('ERR', "Broken link: %s %s" % (x, self.brain.lines[l][0] ))
				continue
			else:
				line[w] = new
				self.brain.lines[l][0] = " ".join(line)
				self.brain.lines[l][1] += number
				changed += 1

		if self.brain.words.has_key(new):
			self.brain.stats['num_words'] -= 1
			self.brain.words[new].extend(self.brain.words[old])
		else:
			self.brain.words[new] = self.brain.words[old]
		del self.brain.words[old]
		return "%d instances of %s replaced with %s" % ( changed, old, new )

	def unlearn(self, context):
		"""
		Unlearn all contexts containing 'context'. If 'context'
		is a single word then all contexts containing that word
		will be removed, just like the old !unlearn <word>
		"""
		# Pad thing to look for
		# We pad so we don't match 'shit' when searching for 'hit', etc.
		context = " " + context + " "
		# Search through contexts
		# count deleted items
		dellist = []
		# words that will have broken context due to this
		wordlist = []
		for x in self.brain.lines.keys():
			# get context. pad
			c = " " + self.brain.lines[x][0] + " "
			if c.find(context) != -1:
				# Split line up
				#wlist = self.brain.lines[x][0].split()
				## add touched words to list
				#for w in wlist:
				#	if not w in wordlist:
				#		wordlist.append(w)
				dellist.append(x)
				del self.brain.lines[x]
		words = self.brain.words
		# update links
		for x in wordlist:
			word_contexts = words[x]
			# Check all the word's links (backwards so we can delete)
			for y in xrange(len(word_contexts) - 1, -1, -1):
				# Check for any of the deleted contexts
				if y[0] in dellist:
					del word_contexts[y]
					self.brain.stats['num_contexts'] = self.brain.stats['num_contexts'] - 1
			if len(words[x]) == 0:
				del words[x]
				self.brain.stats['num_words'] = self.brain.stats['num_words'] - 1
				self.barf('ACT', "\"%s\" vaporized from brain." % x)

	def reply(self, body):
		"""
		Reply to a line of text.
		"""
		if self.debug == 1:
			self.barf('DBG', "Forming a reply...")

		# split sentences into list of words
		_words = body.split(" ")
		words = []
		for i in _words:
			words += i.split()
		del _words

		if len(words) == 0:
			return ""

		#remove words on the ignore list
		words = [x for x in words if x not in self.settings.ignore_list and not x.isdigit()]

		# Find rarest word (excluding those unknown)
		index = []
		known = -1

		# If the word is in at least three contexts, it can be chosen.
		known_min = 3
		for x in xrange(0, len(words)):
			if self.brain.words.has_key(words[x]):
				k = len(self.brain.words[words[x]])
				if self.settings.debug == 1:
					self.barf('DBG', 'k: %s,' % (words[x]))
			else:
				continue
			if (known == -1 or k < known) and k > known_min:
				index = [words[x]]
				known = k
				continue
			elif k == known:
				index.append(words[x])
				continue
		# Index now contains list of rarest known words in sentence
		if len(index) == 0:
			return ""
		word = index[randint(0, len(index) - 1)]
		if self.debug == 1:
			self.barf('DBG', "Chosen root word: %s" % word)

		# Build sentence backwards from "chosen" word
		sentence = [word]
		done = 0
		while done == 0:
			#create a brain which will contain all the words we can find before the "chosen" word
			pre_words = {"": 0}
			#this is to prevent a case where we have an ignore_listd word
			word = str(sentence[0].split(" ")[0])
			for x in xrange(0, len(self.brain.words[word]) - 1):
				l = self.brain.words[word][0]
				w = self.brain.words[word][1]
				try:
					context = self.brain.lines[l][0]
				except KeyError:
					break
				num_context = self.brain.lines[l][1]
				cwords = context.split()
				#if the word is not the first of the context, look to the previous one
				if w:
					#look if we can find a pair with the choosen word, and the previous one
					if len(sentence) > 1 and len(cwords) > w + 1:
						if sentence[1] != cwords[w + 1]:
							continue
					#if the word is in ignore_list, look to the previous word
					look_for = cwords[w - 1]
					if look_for in self.settings.ignore_list and w > 1:
						look_for = cwords[w - 2] + " " + look_for
					#saves how many times we can find each word
					if not (pre_words.has_key(look_for)):
						pre_words[look_for] = num_context
					else:
						pre_words[look_for] += num_context
				else:
					pre_words[""] += num_context
			if self.settings.debug == 1:
				self.barf('DBG', 'Context: %s' % context)
				self.barf('DBG', 'l: %s, w: %s' % (l, w))
				self.barf('DBG', 'cwords[w]: %s, word: %s' % ( cwords[w], word ))

			#Sort the words
			list = pre_words.items()
			list.sort(lambda x, y: cmp(y[1], x[1]))

			numbers = [list[0][1]]
			for x in xrange(1, len(list)):
				numbers.append(list[x][1] + numbers[x - 1])

			#take one of them from the list (randomly)
			mot = randint(0, numbers[len(numbers) - 1])
			for x in xrange(0, len(numbers)):
				if mot <= numbers[x]:
					mot = list[x][0]
					break

			#if the word is already chosen, pick the next one
			while mot in sentence:
				x += 1
				if x >= len(list) - 1:
					mot = ''
				mot = list[x][0]

			mot = mot.split(" ")
			mot.reverse()
			if mot == ['']:
				done = 1
			else:
				map((lambda x: sentence.insert(0, x) ), mot)

		pre_words = sentence
		sentence = sentence[-2:]

		# Now build sentence forwards from "chosen" word

		#We've got
		#cwords:	...	cwords[w-1]	cwords[w]	cwords[w+1]	cwords[w+2]
		#sentence:	...	sentence[-2]	sentence[-1]	look_for	look_for ?

		#we are looking, for a cwords[w] known, and maybe a cwords[w-1] known, what will be the cwords[w+1] to choose.
		#cwords[w+2] is need when cwords[w+1] is in ignored list


		done = 0
		while done == 0:
			#create a brain which will contain all the words we can find before the "chosen" word
			post_words = {"": 0}
			word = str(sentence[-1].split(" ")[-1])
			for x in xrange(0, len(self.brain.words[word])):
				l = self.brain.words[word][x][0]
				w = self.brain.words[word][x][1]
				try:
					context = self.brain.lines[l][0]
				except KeyError:
					break
				num_context = self.brain.lines[l][1]
				cwords = context.split()
				#look if we can find a pair with the chosen word, and the next one
				if len(sentence) > 1:
					if sentence[len(sentence) - 2] != cwords[w - 1]:
						continue

				if w < len(cwords) - 1:
					#if the word is in ignore_list, look to the next word
					look_for = cwords[w + 1]
					if look_for in self.settings.ignore_list and w < len(cwords) - 2:
						look_for = look_for + " " + cwords[w + 2]

					if not (post_words.has_key(look_for)):
						post_words[look_for] = num_context
					else:
						post_words[look_for] += num_context
				else:
					post_words[""] += num_context
			#Sort the words
			list = post_words.items()
			list.sort(lambda x, y: cmp(y[1], x[1]))
			numbers = [list[0][1]]

			for x in xrange(1, len(list)):
				numbers.append(list[x][1] + numbers[x - 1])

			#take one of them from the list (randomly)
			mot = randint(0, numbers[len(numbers) - 1])
			for x in xrange(0, len(numbers)):
				if mot <= numbers[x]:
					mot = list[x][0]
					break

			x = -1
			while mot in sentence:
				x += 1
				if x >= len(list) - 1:
					mot = ''
					break
				mot = list[x][0]

			mot = mot.split(" ")
			if mot == ['']:
				done = 1
			else:
				map((lambda x: sentence.append(x) ), mot)

		sentence = pre_words[:-2] + sentence

		#Replace aliases
		for x in xrange(0, len(sentence)):
			if sentence[x][0] == "~": sentence[x] = sentence[x][1:]

		#Insert space between each words
		map((lambda x: sentence.insert(1 + x * 2, " ") ), xrange(0, len(sentence) - 1))

		#correct the ' & , spaces problem
		#the code is not very good and can be improved but it does the job...
		for x in xrange(0, len(sentence)):
			if sentence[x] == "'":
				sentence[x - 1] = ""
				sentence[x + 1] = ""
			if sentence[x] == ",":
				sentence[x - 1] = ""

		#return as string..
		return "".join(sentence)

		# Ignore if the sentence starts with the self.settings.symbol
		if body[0:1] == self.settings.symbol:
			if self.debug == 1:
				self.barf('ERR', "Not learning: %s" % words)
			return
		else:
			self.brain.learn(self, body, num_context=1)
	
	def shutdown(self, interface):
		# Save the brain
		self.brain.kill_timers()
		self.brain.save_all(False)
		self.barf('MSG', 'Goodbye!')
		
		# Now we close everything.
		os._exit(0)
