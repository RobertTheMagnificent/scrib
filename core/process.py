#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randint
import time

import barf
import brain
import cfg
import clean
from plugins import PluginManager

class process:
	"""
	This is where we process commands and messages.
	"""
	def __init__(self):
			# This is where we do some ownership command voodoo.
		self.owner_commands = {
			'alias': "alias [this] [that]",
			'find': "find [word]",
			'forget': "forget [word]",
			'censor': "censor [word]",
			'check': "(deprecated) alias for rebuild",
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
		
		
	def msg(self, interface, body, replyrate, learn, args, owner=0, muted=0):
		"""
		Process message 'body' and pass back to IO module with args.
		If muted == 1 only respond with taught responses.
		"""
		self.cfg = cfg
		self.barf = barf.Barf
		self.clean = clean.clean()
		self.brain = brain.brain()
		self.settings = self.cfg.set()
		self.settings.load("conf/scrib.cfg", '')
		
		if self.settings.debug == 1:
			self.barf('DBG', "Processing message...")

		# add trailing space so sentences are broken up correctly
		body = body + " "

		# Parse commands
		if body[0] == self.settings.symbol:
			if self.settings.debug == 1:
				user = 'user'
				if owner == 1:
					user = 'owner'
				msg = self.barf('DBG', "Parsing commands by %s" % user)

			self.cmd(interface, body[1:], args, owner)
			return


		# Filter out garbage and do some formatting
		if self.settings.debug == 1:
			self.barf('DBG', "Filtering message...")
		body = self.clean.line(body)


		# if status 0 is set, ignore.
		if body == 0:
			return

		# Learn from input
		if self.brain.settings.learning == 1:
			if self.settings.debug == 1:
				self.barf('DBG', "Learning from: %s" % body)
			self.brain.learn(body)


		# Make a reply if desired
		if randint(0, 99) < replyrate:
			if self.settings.debug == 1:
				self.barf('DBG', "Decided to answer...")
			message = ""

			if muted == 0:
				#Look if we can find a prepared answer
				if self.brain.dbread(body):
					if self.settings.debug == 1:
						self.barf('DBG', "Using prepared answer.")
					message = self.clean.unfilter_reply(self.brain.dbread(body))
					if self.settings.debug == 1:
						self.barf('DBG', "Replying with: " + message)
					return

				for sentence in self.brain.static_answers.sentences.keys():
					pattern = "^%s$" % sentence
					if re.search(pattern, body):
						if self.settings.debug == 1:
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
					if self.settings.debug == 1:
						self.barf('DBG', "No prepared answer; thinking...")
					message = self.brain.reply(body)
					if self.settings.debug == 1:
						self.barf('DBG', "Reply formed; unfiltering...")
					message = self.clean.unfilter_reply(message)
					if self.settings.debug == 1:
						self.barf('DBG', "Unfiltered message: " + message)
			else:
				return

			# empty. do not output
			if message == "":
				if self.settings.debug == 1:
					self.barf('DBG', "Message empty.")
				replying = "Not replying."
			else:
				time.sleep(.075 * len(message))
				if self.settings.debug == 1:
					replying = "Reply sent."
				interface.output(message, args)
			if self.settings.debug == 1:
				self.barf('DBG', replying)

	def cmd(self, interface, body, args, owner):
		"""
		Respond to commands.
		"""
		cmds = body.split()
		msg = ""

		if owner == 0 and cmds[0] in self.general_commands.keys():
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
							value = self.brain.clean.teach_filter(' '.join(cmds[1:]).split("|")[1].strip())
							self.brain.dbwrite(key[0:], value[0:])
							if rnum > 1:
								array = ' '.join(cmds[1:]).split("|")
								rcount = 1
								for value in array:
									if rcount == 1:
										rcount = rcount + 1
									else:
										self.brain.dbwrite(key[0:], self.brain.clean.teach_filter(value[0:].strip()))
							else:
								value = ' '.join(cmds[1:]).split("|")[1].strip()
								self.brain.dbwrite(key[0:], self.brain.clean.teach_filter(value[0:]))
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

				elif cmds[0] == "rebuild" or cmds[0] == 'check':
					msg = ''
					if cmds[0] == 'check':
						msg += 'Check has been removed. '
					interface.output(self.settings.symbol+"Rebuilding...", args)
					
					msg += self.brain.auto_rebuild()

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
					if self.settings.debug == 1:
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
					if self.settings.debug == 1:
						self.barf('DBG', "Unlearning...")
					# build context we are looking for
					context = " ".join(cmds[1:])
					if context == "":
						return
					self.barf('ACT', "Looking for: %s" % context)
					# Unlearn contexts containing 'context'
					t = time.time()
					self.brain.unlearn(context)
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
					if self.settings.debug == 1:
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
					self.brain.shutdown(interface)
			
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
				msg = 'scrib: %s; brain: %s' % ( self.version, self.brain.settings.version )

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