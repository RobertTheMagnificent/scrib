#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import *
import ctypes
import sys
import os
import shutil
import fileinput
import struct
import datetime
import time
import zipfile
import re
import threading

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
		self.timers_started = False

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
			'limit': "Max number of words allowed.",
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

		self.barf = barf.Barf # So that we don't have to include it elsewhere.
		self.cfg = cfg

		# Attempt to load settings
		self.settings = self.cfg.set()
		self.settings.load("conf/scrib.cfg",{
							"name": "scrib",
							"symbol": "!",
							"reply_rate": 100,
							"nick_reply_rate": 100,
							"learning": 1,
							"debug": 0,
							"muted": 0,
							"max_words": 9001,
							"censored": [],
							"num_aliases": 0,
							"aliases": {},
							"ignore_list": [],
							"optimum": 0,
							"version": self.version
							})

		self.debug = self.settings.debug

		if self.debug == 1:
			self.barf('DBG', "Class scrib initialized.")

		# Brain stats
		self.brain = brain.brain()	
		self.brainstats = {
						"num_contexts": 0,
						"num_words": 0
						}

		self.answers = self.cfg.set()
		self.answers.load("brain/answers.dat", {
							"sentences": {}
							})
		self.unfilterd = {}

		# Starts the timers:
		if self.timers_started is False:
			try:
				self.autosave = threading.Timer(self.to_sec("125m"), self.save_all)
				self.autosave.start()
				self.autorebuild = threading.Timer(self.to_sec("71h"), self.auto_rebuild)
				self.autorebuild.start()
				timers_started = True
			except SystemExit, e:
				self.autosave.cancel()
				self.autorebuild.cancel()

		if dbread("hello") is None:
			dbwrite("hello", "hi #nick")

		# Read the brain
		self.barf('SAV', "Reading my brain...")
		try:
			if os.path.exists('brain/cortex.zip'):
				zfile = zipfile.ZipFile('brain/cortex.zip', 'r')
				for filename in zfile.namelist():
					data = zfile.read(filename)
					file = open(filename, 'w+b')
					file.write(data)
					file.close()
		except (EOFError, IOError), e:
			self.barf('ERR', "No brain found.")
		try:
			f = open("brain/version", "rb")
			v = f.read().strip()
			self.barf('MSG', "Current brain version is %s " % v)
			f.close()
			if v != self.brain.version:
				self.barf('ERR', "Brain is version "+v+", but I use "+self.brain.version+".")
				self.barf('ERR', "Would you like to update the brain?")
				c = raw_input("[Y/n]")
				if c[:1].lower() != 'n':
					timestamp = "%s-%s" % (datetime.date.today(), time.strftime("%H%M%S",time.localtime(time.time())))
					shutil.copyfile("brain/cortex.zip", "backups/cortex-%s.zip" % timestamp)
					self.barf('ACT', "Backup saved to backups/cortex-%s.zip" % timestamp)
					self.barf('ACT', "Starting update, may take a few moments.")
					f = open("brain/words.dat", "rb")
					if self.debug == 1:
						self.barf('DBG', "Reading words...")
					s = f.read()
					f.close()
					self.words = self.unpack(s, v)
					del s
					if self.debug == 1:
						self.barf('DBG', "Saving words...")
					f = open("brain/words.dat", "wb")
					s = self.pack(self.words, self.brain.version, True)
					f.write(s)
					f.close()
					del s
					if self.debug == 1:
						self.barf('DBG', "Words converted.")
						self.barf('DBG', "Reading lines...")
					f = open("brain/lines.dat", "rb")
					s = f.read()
					f.close()
					self.lines = self.unpack(s, v)
					if self.debug == 1:
						self.barf('DBG', "Applying filter to adjust to new brain system.")
						self.barf('TAB', "This may take a bit, and will shrink the dataset.")
					self.auto_rebuild()
					f = open("brain/lines.dat", "wb")
					s = self.pack(self.lines, self.brain.version, True)
					f.write(s)
					f.close()
					del s
					if self.debug == 1:
						self.barf('DBG', "Lines converted.")
					f = open("brain/version", "wb")
					f.write(self.brain.version)
					f.close()
					if self.debug == 1:
						self.barf('DBG', "Version updated.")
					v = self.brain.version
					self.barf('ACT', "Brain converted successfully! Continuing.")
				else:
					self.brain.version = v # Saves old brain as old brain format.

			f = open("brain/words.dat", "rb")
			s = f.read()
			f.close()
			self.words = self.unpack(s, v)
			del s
			f = open("brain/lines.dat", "rb")
			s = f.read()
			f.close()
			self.lines = self.unpack(s, v)
			del s

		except (EOFError, IOError), e:
			# Create new brain
			self.words = {}
			self.lines = {}
			self.barf('ERR', "New brain generated.")

		if self.settings.optimum == 1:
			self.barf('ACT', "Optimizing brain bits...")
			self.auto_rebuild()
		self.barf('ACT', "Calculating words and contexts...")
		self.brainstats['num_words'] = len(self.words)
		num_contexts = 0
		# Get number of contexts
		for x in self.lines.keys():
			num_contexts += len(self.lines[x][0].split())
		self.brainstats['num_contexts'] = num_contexts
		self.barf('ACT', "%s words and %s contexts loaded" % ( self.brainstats['num_words'], self.brainstats['num_contexts'] ))
		
		# Is an aliases update required ?
		count = 0
		for x in self.settings.aliases.keys():
			count += len(self.settings.aliases[x])
		if count != self.settings.num_aliases:
			self.barf('ACT', "Check brain for new aliases.")
			self.settings.num_aliases = count

			for x in self.words.keys():
				#is there aliases ?
				if x[0] != '~':
					for z in self.settings.aliases.keys():
						for alias in self.settings.aliases[z]:
							pattern = "^%s$" % alias
							if self.re.search(pattern, x):
								print "replace %s with %s" % (x, z)
								self.replace(x, z)

			for x in self.words.keys():
				if not (x in self.settings.aliases.keys()) and x[0] == '~':
					print "unlearn %s" % x
					self.settings.num_aliases -= 1
					self.unlearn(x)
					print "unlearned aliases %s" % x


		#unlearn words in the unlearn.txt file.
		try:
			f = open("brain/unlearn.txt", "r")
			while 1:
				word = f.readline().strip('\n')
				if word == "":
					break
				if self.words.has_key(word):
					self.unlearn(word)
			f.close()
		except (EOFError, IOError), e:
			# No words to unlearn
			pass

		#self.settings.save()
	def to_sec(self, s):
		seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
		return int(s[:-1]) * seconds_per_unit[s[-1]]

	# For unpacking a brain. This is just quick and dirty, should be replaced...
	def brain_ver(self, version):
		marshal = ['0.0.1', '0.1.0', '0.1.1']
		pickle = ['0.1.2', '0.1.3', '0.1.4']
		json = ['0.1.5']
		
		if version in marshal:
			return 1
		elif version in pickle:
			return 2
		elif version in json:
			return 3
		else:
			self.barf('ERR', "Invalid brain type")
			return 0

	def unpack(self, file, version):
		if self.brain_ver(version) == 1:
			import marshal
			stuff = marshal.loads(file)
		elif self.brain_ver(version) == 2:
			import cPickle as pickle
			stuff = pickle.loads(file)
		elif self.brain_ver(version) == 3:
			import json
			stuff = json.loads(file, encoding="utf-8")
		return stuff

	def pack(self, file, version, upgrade=False):
		if self.brain_ver(version) == 1:
			import marshal
			stuff = marshal.dumps(file)
		elif self.brain_ver(version) == 2:
			import cPickle as pickle
			stuff = pickle.dumps(file)
		elif self.brain_ver(version) == 3:
			import json
			if upgrade == True:
				s = {}
				for k,v in file.items():
					s.update({k:v})
				stuff = json.dumps(s, sort_keys=True, indent=4, separators=(',', ': '), encoding='latin-1').decode('latin1').encode('utf8') # Compat
				del s
				return stuff

			stuff = json.dumps(file, sort_keys=True, indent=4, separators=(',', ': '), encoding='latin-1').decode('latin-1').encode('utf-8') # Gross
		return stuff

	def save_all(self, interface, restart_timer=True):
		self.barf('SAV', "Writing to my brain...")

		f = open("brain/words.dat", "wb")
		s = self.pack(self.words, self.brain.version)
		f.write(s)
		f.close()
		if self.debug == 1:
			self.barf('DBG', "Words saved.")
		f = open("brain/lines.dat", "wb")
		s = self.pack(self.lines, self.brain.version)
		f.write(s)
		f.close()
		if self.debug == 1:
			self.barf('DBG', "Lines saved.")

		#zip the files
		f = zipfile.ZipFile('brain/cortex.zip', 'w', zipfile.ZIP_DEFLATED)
		f.write('brain/words.dat')
		if self.debug == 1:
			self.barf('DBG', "Words zipped")
		os.remove('brain/words.dat')
		f.write('brain/lines.dat')
		if self.debug == 1:
			self.barf('DBG', "Lines zipped")
		try:
			f.write('brain/version')
			f.close()
			if self.debug == 1:
				self.barf('DBG', "Version zipped")
			os.remove('brain/version')
		except:
			v = open("brain/version", "w")
			v.write(self.brain.version)
			v.close()
			f.write("brain/version")
			if self.debug == 1:
				self.barf('DBG', "Version written and zipped.")
			os.remove('brain/version')


		f = open("brain/words.dat", "w")
		# write each words known
		wordlist = []
		#Sort the list before to export
		for key in self.words.keys():
			try:
				wordlist.append([key, len(self.words[key].encode('utf8'))])
			except:
				pass
		wordlist.sort(lambda x, y: cmp(x[1], y[1]))
		map((lambda x: f.write(str(x[0]) + "\n\r") ), wordlist)
		f.close()
		if self.debug == 1:
			self.barf('DBG', "Words written.")

		f = open("brain/sentences.dat", "w")
		# write each words known
		wordlist = []
		#Sort the list before to export
		for key in self.unfilterd.keys():
			wordlist.append([key, self.unfilterd[key]])
		wordlist.sort(lambda x, y: cmp(y[1], x[1]))
		map((lambda x: f.write(str(x[0]) + "\n") ), wordlist)
		f.close()
		if self.debug == 1:
			self.barf('DBG', "Sentences written.")

		# Save settings
		self.settings.save()

		if interface != False:
			interface.settings.save()

		self.barf('SAV', "Brain saved.")

		if restart_timer is True:
			self.autosave = threading.Timer(self.to_sec("125m"), self.save_all)
			self.autosave.start()
			if self.debug == 1:
				self.barf('DBG', "Restart timer started.")

	def auto_rebuild(self):
		if self.settings.learning == 1:
			t = time.time()

			old_lines = self.lines
			old_num_words = self.brainstats['num_words']
			old_num_contexts = self.brainstats['num_contexts']

			self.words = {}
			self.lines = {}
			self.brainstats['num_words'] = 0
			self.brainstats['num_contexts'] = 0

			for k in old_lines.keys():
				filtered_line = self.filter(old_lines[k][0])
				self.learn(filtered_line, old_lines[k][1])
			msg = "Rebuilt brain in %0.2fs. Words %d (%+d), contexts %d (%+d)." % \
				  (time.time() - t,
				   old_num_words,
				   self.brainstats['num_words'] - old_num_words,
				   old_num_contexts,
				   self.brainstats['num_contexts'] - old_num_contexts)

			# Restarts the timer
			self.autorebuild = threading.Timer(self.to_sec("71h"), self.auto_rebuild)
			self.autorebuild.start()

			return msg
		else:
			return "Learning mode is off; will not rebuild."

	def kill_timers(self):
		self.autosave.cancel()
		self.autorebuild.cancel()

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
				self.barf('DBG', "Parsing commands...")
				if owner == 1:
					self.barf('DBG', 'User is owner.')
				else:
					self.barf('DBG', 'User is not owner.')	

			self.do(interface, body[1:], args, owner)
			return


		# Filter out garbage and do some formatting
		if self.debug == 1:
			self.barf('DBG', "Filtering message...")
		body = self.filter(body)

		# Learn from input

		if self.settings.learning == 1:
			if self.debug == 1:
				self.barf('DBG', "Learning from: %s" % body)
			self.learn(body)


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

				for sentence in self.answers.sentences.keys():
					pattern = "^%s$" % sentence
					if re.search(pattern, body):
						if self.debug == 1:
							self.barf('DBG', "Searching for reply...")
						message = self.answers.sentences[sentence][
							randint(0, len(self.answers.sentences[sentence]) - 1)]
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

	def filter(bot, message):
		"""
		Make easier to learn and reply to.
		"""

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
			#bot.barf('ERR', "Filter: %s" % e)
			pass

		# Strips out urls not ignored before...
		message = re.sub("([a-zA-Z0-9\-_]+?\.)*[a-zA-Z0-9\-_]+?\.[a-zA-Z]{2,5}(\/[a-zA-Z0-9]*)*", "", message)

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
			for z in bot.settings.aliases.keys():
				for alias in bot.settings.aliases[z]:
					pattern = "^%s$" % alias
					if re.search(pattern, words[x]):
						words[x] = z

		message = " ".join(words)

		return message

	def do(self, interface, body, args, owner):
		"""
		Respond to user commands.
		"""
		cmds = body.split()
		sym = self.settings.symbol # For ease of typing
		msg = ""

		if owner == 0 and cmds[0] in self.commands:
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

				elif cmds[0] == "limit":
					msg = "The max limit is "
					if len(cmds) == 1:
						msg += str(self.settings.max_words)
					else:
						limit = int(cmds[1])
						self.settings.max_words = limit
						msg += "now " + cmds[1]

				# Check for broken links in the brain
				elif cmds[0] == "check":
					t = time.time()
					num_broken = 0
					num_bad = 0
					for w in self.words.keys():
						wlist = self.words[w]

						for i in xrange(len(wlist) - 1, -1, -1):
							try:
								line_idx, word_num = struct.unpack("iH", wlist[i])
							except:
								self.barf('ERR', 'The hash table is damaged. Please use !rebuild, then !save.')
								return

							# Nasty critical error we should fix
							if not self.lines.has_key(line_idx):
								self.barf('ACT', "Removing broken link '%s' -> %d." % (w, line_idx))
								num_broken = num_broken + 1
								del wlist[i]
							else:
								# Check pointed to word is correct
								split_line = self.lines[line_idx][0].split()
								if split_line[word_num] != w:
									self.barf('ACT', "Line '%s' word %d is not '%s' as expected." % \
											  (self.lines[line_idx][0],
											   word_num, w.decode('utf8')))
									num_bad = num_bad + 1
									del wlist[i]
						if len(wlist) == 0:
							del self.words[w]
							self.brainstats['num_words'] = self.brainstats['num_words'] - 1
							self.barf('ACT', "\"%s\" vaporized from brain." % w)

					msg = "Checked my brain in %0.2fs. Fixed links: %d broken, %d bad." % \
						  (
						   time.time() - t,
						   num_broken,
						   num_bad)

				elif cmds[0] == "rebuild":
					msg = self.auto_rebuild()

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
					return msg

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
					for x in self.lines.keys():
						# get context
						ctxt = self.lines[x][0]
						# add leading whitespace for easy sloppy search code
						# TODO Find a better, less sloppy way to do this crap
						ctxt = " " + ctxt + " "
						if ctxt.find(context) != -1:
							# Avoid duplicates (2 of a word
							# in a single context)
							num_contexts = len(c) + 1
							if len(c) == 0:
								c.append(self.lines[x][0])
							elif c[len(c) - 1] != self.lines[x][0]:
								c.append(self.lines[x][0])
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
						if self.settings.learning == 0:
							msg += "off"
						else:
							msg += "on"
					else:
						toggle = cmds[1]
						if toggle == "on":
							msg += "on"
							self.settings.learning = 1
						else:
							msg += "off"
							self.settings.learning = 0

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
								msg += "is already censored." % ( cmds[x])
							else:
								self.settings.censored.append(cmds[x])
								self.unlearn(cmds[x])
								msg += "is now censored." % ( cmds[x])
							msg += "\n"

				elif cmds[0] == "uncensor":
					if self.debug == 1:
						self.barf('DBG', "Uncensoring...")
					# Remove words listed from the censor list
					# eg !uncensor tom dick harry
					for x in xrange(1, len(cmds)):
						try:
							self.settings.censored.remove(cmds[x])
							msg = "is uncensored." % ( cmds[x])
						except ValueError, e:
							pass

				elif cmds[0] == 'quit':
					self.kill_timers()
					self.save_all(interface, False)
					self.barf('MSG', 'Goodbye!')
					sys.exit(0)
			
				elif cmds[0] == 'save':
					self.barf('SAV', 'User initiated save')
					self.save_all(interface)
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

				elif cmds[0] == 'learning':
					msg = "Learning mode "
					if len(cmds) == 1:
						if self.settings.learning == 0:
							msg = msg + 'off'
						else:
							msg = msg + 'on'
					else:
						toggle = cmds[1]
						if toggle == 'on':
							msg = msg + 'on'
							self.settings.learning = 1 # Set current session
							self.settings._defaults['learning'] = 1 # Set default to save to file.
						else:
							msg = msg + 'off'
							self.settings.learning = 0
							self.settings._defaults['learning'] = 0

				elif cmds[0] == "alias":
					# List aliases words
					if len(cmds) == 1:
						if len(self.settings.aliases) == 0:
							msg = "No aliases"
						else:
							msg = "I will alias the word(s) %s." \
								  % (", ".join(self.settings.aliases.keys()))
					# add every word listd to alias list
					elif len(cmds) == 2:
						if cmds[1][0] != '~': cmds[1] = '~' + cmds[1]
						if cmds[1] in self.settings.aliases.keys():
							msg = "These words : %s are aliases to %s." \
								  % (" ".join(self.settings.aliases[cmds[1]]), cmds[1] )
						else:
							msg = "The alias %s is not known." % cmds[1][1:]
					elif len(cmds) > 2:
						#create the aliases
						if cmds[1][0] != '~': cmds[1] = '~' + cmds[1]
						if not (cmds[1] in self.settings.aliases.keys()):
							self.settings.aliases[cmds[1]] = [cmds[1][1:]]
							self.replace(cmds[1][1:], cmds[1])
							msg += cmds[1][1:] + " "
						for x in xrange(2, len(cmds)):
							msg += "%s " % cmds[x]
							self.settings.aliases[cmds[1]].append(cmds[x])
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
				num_w = self.brainstats['num_words']
				num_c = self.brainstats['num_contexts']
				num_l = len(self.lines)
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
					if self.words.has_key(word):
						c = len(self.words[word])
						msg = "%s is known (%d contexts)" % ( word, c)
					else:
						msg = "is unknown." % ( word)
				elif len(cmds) > 2:
					# multiple words.
					words = []
					for x in cmds[1:]:
						words.append(x)
					msg = "Number of contexts: "
					for x in words:
						if self.words.has_key(x):
							c = len(self.words[x])
							msg += x + "(" + str(c) + ") "
						else:
							msg += x + "(0) "

		if cmds[0] not in self.commands:
			print self.commands
			msg = cmds[0] + " is not a registered command."

		if msg != "":
			interface.output(sym+msg, args)


	def replace(self, old, new):
		"""
		Replace all occurrences of 'old' in the brain with
		'new'. Nice for fixing learnt typos.
		"""
		try:
			pointers = self.words[old]
		except KeyError, e:
			return "%s is not known." % old
		changed = 0

		for x in pointers:
			# pointers consist of (line, word) to self.lines
			l, w = struct.unpack("iH", x)
			line = self.lines[l][0].split()
			number = self.lines[l][1]
			if line[w] != old:
				# fucked brain
				self.barf('ERR', "Broken link: %s %s" % (x, self.lines[l][0] ))
				continue
			else:
				line[w] = new
				self.lines[l][0] = " ".join(line)
				self.lines[l][1] += number
				changed += 1

		if self.words.has_key(new):
			self.brainstats['num_words'] -= 1
			self.words[new].extend(self.words[old])
		else:
			self.words[new] = self.words[old]
		del self.words[old]
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
		for x in self.lines.keys():
			# get context. pad
			c = " " + self.lines[x][0] + " "
			if c.find(context) != -1:
				# Split line up
				#wlist = self.lines[x][0].split()
				## add touched words to list
				#for w in wlist:
				#	if not w in wordlist:
				#		wordlist.append(w)
				dellist.append(x)
				del self.lines[x]
		words = self.words
		unpack = struct.unpack
		# update links
		for x in wordlist:
			word_contexts = words[x]
			# Check all the word's links (backwards so we can delete)
			for y in xrange(len(word_contexts) - 1, -1, -1):
				# Check for any of the deleted contexts
				if unpack("iH", word_contexts[y])[0] in dellist:
					del word_contexts[y]
					self.brainstats['num_contexts'] = self.brainstats['num_contexts'] - 1
			if len(words[x]) == 0:
				del words[x]
				self.brainstats['num_words'] = self.brainstats['num_words'] - 1
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
			if self.words.has_key(words[x]):
				k = len(self.words[words[x]])
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
			for x in xrange(0, len(self.words[word]) - 1):
				l, w = struct.unpack("iH", self.words[word][x])
				try:
					context = self.lines[l][0]
				except KeyError:
					break
				num_context = self.lines[l][1]
				cwords = context.split()
				#if the word is not the first of the context, look to the previous one
				if cwords[w] != word:
					print context
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
			for x in xrange(0, len(self.words[word])):
				l, w = struct.unpack("iH", self.words[word][x])
				try:
					context = self.lines[l][0]
				except KeyError:
					break
				num_context = self.lines[l][1]
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

	def learn(self, body, num_context=1):
		"""
		Lines should be cleaned (filter()) before passing
		to this.
		"""

		def learn_line(self, body, num_context):
			"""
			Learn from a sentence.
			"""

			words = body.split()
			# Ignore sentences of < 1
			if len(words) < 1:
				return

			# Ignore if the sentence starts with the symbol
			if body[0:1] == self.settings.symbol:
				if self.debug == 1:
					self.barf('ERR', "Not learning: %s" % words)
				return

			#vowels = "aÃ Ã¢eÃ©Ã¨ÃªiÃ®Ã¯oÃ¶Ã´uÃ¼Ã»y"
			vowels = ""
			for x in xrange(0, len(words)):

				nb_voy = 0
				digit = 0
				char = 0
				for c in words[x]:
					if c in vowels:
						nb_voy += 1
					if c.isalpha():
						char += 1
					if c.isdigit():
						digit += 1

				for censored in self.settings.censored:
					pattern = "^%s$" % censored
					if re.search(pattern, words[x]):
						self.barf('ACT', "Censored word %s" % words[x])
						return

				if len(words[x]) > 13 \
					or ( ((nb_voy * 100) / len(words[x]) < 26) and len(words[x]) > 5 ) \
					or ( char and digit ) \
					or ( self.words.has_key(words[x]) == 0 and self.settings.learning == 0 ):
					return
				elif ( "-" in words[x] or "_" in words[x] ):
					words[x] = "#nick"

			num_w = self.brainstats['num_words']
			if num_w != 0:
				num_cpw = self.brainstats['num_contexts'] / float(num_w) # contexts per word
			else:
				num_cpw = 0

			cleanbody = " ".join(words)

			# This allows for use on 64-bit systems
			hashval = ctypes.c_int32(hash(cleanbody)).value

			# Check that context isn't already known
			if not self.lines.has_key(hashval):
				if not (num_cpw > 100 and self.settings.learning == 0):

					self.lines[hashval] = [cleanbody, num_context]
					# Add link for each word
					for x in xrange(0, len(words)):
						if self.words.has_key(words[x]):
							# Add entry. (line number, word number)
							self.words[words[x]].append(struct.pack("iH", hashval, x))
						else:
							self.words[words[x]] = [struct.pack("iH", hashval, x)]
							self.brainstats['num_words'] += 1
						self.brainstats['num_contexts'] += 1
			else:
				self.lines[hashval][1] += num_context

			#is max_words reached, don't learn more
			if self.brainstats['num_words'] >= self.settings.max_words:
				self.settings.learning = 0
				self.barf('ERR', "Had to turn off learning- max_words limit reached!")

		# Split body text into sentences and parse them
		# one by one.
		body += " "
		map((lambda x: learn_line(self, x, num_context)), body.split(". "))

