#!/usr/bin/env python
# -*- coding: utf-8 -*-

from random import *
from barf import *
import ctypes
import sys
import os
import shutil
import fileinput
import cPickle as pickle
import struct
import time
import zipfile
import re
import threading

timers_started = 0


def to_sec(s):
	seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
	return int(s[:-1]) * seconds_per_unit[s[-1]]

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
	# This was causing issues with words ending with 'i'
	#message = message.replace(" i'", " I'")
	# Fixes the common issues with the teach system
	message = message.replace("$C4", "||")
	message = message.replace("$b7", "|-:")
	message = message.replace("$b6", ";-|")
	message = message.replace("$b5", ":-|")
	message = message.replace("$b4", "|:")
	message = message.replace("$b3", ";|")
	message = message.replace("$b2", "=|")
	message = message.replace("$b1", ":|")
	# Fixes emoticons that don't work in lowercase
	# Needs to add support for D: and DX
	emoticon = re.search("(:|x|;|=|8){1}(-)*(p|x|d){1}", message, re.IGNORECASE)
	if not emoticon == None:
		emoticon = "%s" % emoticon.group()
		message = message.replace(emoticon, emoticon.upper())
		# Fixes the annoying XP capitalization in words...
		message = message.replace("XP", "xp")
		message = message.replace(" xp", " XP")
		message = message.replace("XX", "xx")

	return message


def filter_message(message, bot):
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
	message = message.replace("0 . o", "0.o")
	message = message.replace("o . o", "o.o")
	message = message.replace("O . O", "O.O")
	message = message.replace("< . <", "<.<")
	message = message.replace("> . >", ">.>")
	message = message.replace("> . <", ">.<")
	message = message.replace(": ?", ":?")
	message = message.replace(":- ?", ":-?")
	message = message.replace(", , l , ,", ",,l,,")
	message = message.replace("@ . @", "@.@")

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


class scrib:
	import cfgfile

	# Main command list
	commandlist = "Owner commands:\n!alias, !censor, !check, !context, !learning, !limit, !prune, !rebuild, !replace, !save, !uncensor, !unlearn\nPublic commands:\n!date, !fortune, !help, !known, !owner, !version, !words"
	commanddict = {
		"alias": "Usage: !alias : Show the difference aliases\n!alias <alias> : show the words attached to this alias\n!alias <alias> <word> : link the word to the alias.",
		"censor": "Usage: !censor [word1 [...]]\nPrevent the bot using one or more words. Without arguments lists the currently censored words.",
		"check": "Usage: !check\nChecks the brain for broken links. Shouldn't happen, but worth trying if you get KeyError crashes.",
		"context": "Usage: !context <phrase>\nPrint contexts containing <phrase>.",
		"learning": "Usage: !learning [on|off]\nToggle bot learning. Without arguments shows the current setting.",
		"learn": "Owner command. Usage: !learn trigger | response\nTeaches the bot to respond the any words similar to the trigger word or phrase with a certain response",
		"teach": "Owner command. Usage: !teach trigger | response\nTeaches the bot to respond the any words similar to the trigger word or phrase with a certain response",
		"forget": "Owner command. Usage: !forget trigger\nForces the bot to forget all previously learned responses to a certain trigger word or phrase",
		"find": "Owner command. Usage: !find trigger\nFinds all matches to the trigger word or phrase and displays the amount of matches",
		"responses": "Owner command. Usage: !responses\nDisplays the total number of trigger/response pairs the bot has learned",
		"limit": "Usage: !limit [number]\nSet the number of words that Scrib can learn.",
		"prune": "Usage: !prune [number]\nRemove all occurrences of the words that appears in less than <number> contexts.",
		"rebuild": "Usage: !rebuild\nRebuilds brain links from the lines of known text. Takes a while. You probably don't need to do it unless the brain is very screwed.",
		"replace": "Usage: !replace <old> <new>\nReplace all occurrences of word <old> in the brain with <new>.",
		"save": "Usage: !save\nSave Scrib's brain.",
		"uncensor": "Usage: !uncensor word1 [word2 [...]]\nRemove censorship on one or more words.",
		"unlearn": "Usage: !unlearn <expression>\nRemove all occurrences of a word or expression from the brain. For example '!unlearn of of' would remove all contexts containing double 'of's.",
		"date": "Usage: !date\nTells you the date.",
		"fortune": "Usage: !fortune\nTells you something interesting.",
		"help": "Usage: !help [command]\nPrints information about using a command, or a list of commands if no command is given.",
		"known": "Usage: !known word1 [word2 [...]]\nDisplays if one or more words are known, and how many contexts are known.",
		"owner": "Usage: !owner password\nAdd the user in the owner list.",
		"version": "Usage: !version\nDisplay what version of Scrib we are running.",
		"words": "Usage: !words\nDisplay how many words are known."
	}

	def __init__(self):
		"""
		Open the brain. Resize as required.
		"""
		# Attempt to load settings
		self.settings = self.cfgfile.cfgset()
		self.settings.load("conf/scrib.cfg",
						   {"max_words": ("max limits in the number of words known", 6000),
							"learning": ("Allow the bot to learn", 1),
							"ignore_list": ("Words that can be ignored for the answer", ['!.', '?.', "'", ',', ';']),
							"censored": ("Don't learn the sentence if one of those words is found", []),
							"num_aliases": ("Total of aliases known", 0),
							"debug": ("Debug mode adds verbose output to terminal", 0),
							"aliases": ("A list of similar words", {}),
							"pubsym": ("Symbol to append to cmd msgs in public", "!"),
							"no_save": ("If True, Scrib doesn't save his brain and configuration to disk", "False")
						   })

		self.debug = self.settings.debug

		if self.debug == 1:
			barf(DBG, "Class scrib initialized.")

		# Brain stats
		self.brainstats = self.cfgfile.cfgset()
		self.brainstats.load("brain/knowledge",
							 {"num_contexts": ("Total word contexts", 0),
							  "num_words": ("Total unique words known", 0)
							 })

		self.answers = self.cfgfile.cfgset()
		self.answers.load("brain/answers.dat",
						  {"sentences": ("A list of prepared answers", {})
						  })
		self.unfilterd = {}

		self.version = self.cfgfile.cfgset()
		self.version.load("VERSION",
						  {"core": ("Core version of Scrib", 0),
						   "brain": ("Brain version of Scrib", 0),
						  })

		# Starts the timers:
		global timers_started
		if timers_started is False:
			try:
				self.autosave = threading.Timer(to_sec("125m"), self.save_all)
				self.autosave.start()
				self.autopurge = threading.Timer(to_sec("5h"), self.auto_optimise)
				self.autopurge.start()
				self.autorebuild = threading.Timer(to_sec("71h"), self.auto_rebuild)
				self.autorebuild.start()
				timers_started = True
			except SystemExit, e:
				self.autosave.cancel()
				self.autopurge.cancel()
				self.autorebuild.cancel()

		if dbread("hello") is None:
			dbwrite("hello", "hi #nick")

		# Read the brain
		barf(SAV, "Reading my brain...")
		try:
			zfile = zipfile.ZipFile('brain/cortex.zip', 'r')
			for filename in zfile.namelist():
				data = zfile.read(filename)
				file = open(filename, 'w+b')
				file.write(data)
				file.close()
		except (EOFError, IOError), e:
			barf(ERR, "No zip found, or perhaps corrupt? Attempting to recover.")
		try:
			f = open("brain/version", "rb")
			s = f.read()
			barf(MSG, "Current brain version is %s " % s)
			f.close()
			if s != self.version.brain:
				import marshal
				barf(ERR, "Brain version incorrect.")
				c = raw_input(raw_barf(ERR, "Would you like to update the brain? (Y/n) "))
				if c[:1].lower() != 'n':
					timestamp = get_time_for_file()
					shutil.copyfile("brain/cortex.zip", "brain/cortex-%s.zip" % timestamp)
					barf(ACT, "Backup saved to brain/cortex-%s.zip" % timestamp)
					barf(ACT, "Starting update, may take a few moments.")
					f = open("brain/words.dat", "rb")
					if self.debug == 1:
						barf(DBG, "Reading words...")
					s = f.read()
					f.close()
					self.words = self.unpack(s)
					del s
					if self.debug == 1:
						barf(DBG, "Saving words...")
					f = open("brain/words.dat", "wb")
					s = pickle.dumps(self.words)
					f.write(s)
					f.close()
					del s
					if self.debug == 1:
						barf(DBG, "Words converted.")
						barf(DBG, "Reading lines...")
					f = open("brain/lines.dat", "rb")
					s = f.read()
					f.close()
					self.lines = self.unpack(s)
					if self.debug == 1:
						barf(DBG, "Applying filter to adjust to new brain system.\n               This may take several minutes...")
					self.auto_rebuild()
					f = open("brain/lines.dat", "wb")
					s = pickle.dumps(self.lines)
					f.write(s)
					f.close()
					del s
					if self.debug == 1:
						barf(DBG, "Lines converted.")
					f = open("brain/version", "wb")
					f.write(self.version.brain)
					f.close()
					if self.debug == 1:
						barf(DBG, "Version updated.")
					barf(ACT, "Brain converted successfully! Continuing.")

					if self.debug == 1:
						barf(DBG, "Brain saved.")
					self.clean_up()

			f = open("brain/words.dat", "rb")
			s = f.read()
			f.close()
			self.words = pickle.loads(s)
			del s
			f = open("brain/lines.dat", "rb")
			s = f.read()
			f.close()
			self.lines = pickle.loads(s)
			del s
		except (EOFError, IOError), e:
			# Create new brain
			self.words = {}
			self.lines = {}
			barf(ERR, "New brain generated.")

		# Is a resizing required?
		if len(self.words) != self.brainstats.num_words:
			barf(ACT, "Updating my brain's information...")
			self.brainstats.num_words = len(self.words)
			num_contexts = 0
			# Get number of contexts
			for x in self.lines.keys():
				num_contexts += len(self.lines[x][0].split())
			self.brainstats.num_contexts = num_contexts
			# Save new values
			self.brainstats.save()

		# Is an aliases update required ?
		count = 0
		for x in self.settings.aliases.keys():
			count += len(self.settings.aliases[x])
		if count != self.settings.num_aliases:
			barf(ACT, "Check brain for new aliases.")
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

		self.settings.save()

	# For unpacking a brain. This is just quick and dirty, should be replaced...
	def unpack(self, file):
		if self.version.brain == "0.1.0" or self.version.brain == "0.1.1":
			stuff = marshal.loads(file)
		else:
			stuff = pickle.loads(file)
		return stuff

	def save_all(self, restart_timer=True):
		if self.settings.no_save != "True":
			barf(SAV, "Writing to my brain...")

			#try:
			#	zfile = zipfile.ZipFile('brain/cortex.zip', 'r')
			#	for filename in zfile.namelist():
			#		data = zfile.read(filename)
			#		file = open(filename, 'w+b')
			#		file.write(data)
			#		file.close()
			#	if self.debug == 1:
			#		barf(DBG, "Cortex saved.")
			#except:
			#	barf(ERR, "No brain found, or it's broken. Attempting to restore...")
			#	try:
			#		os.remove('brain/cortex.zip')
			#	except:
			#		pass

			f = open("brain/words.dat", "wb")
			s = pickle.dumps(self.words)
			f.write(s)
			f.close()
			if self.debug == 1:
				barf(DBG, "Words saved.")
			f = open("brain/lines.dat", "wb")
			s = pickle.dumps(self.lines)
			f.write(s)
			f.close()
			if self.debug == 1:
				barf(DBG, "Lines saved.")

			#zip the files
			f = zipfile.ZipFile('brain/cortex.zip', 'w', zipfile.ZIP_DEFLATED)
			f.write('brain/words.dat')
			if self.debug == 1:
				barf(DBG, "Words zipped")
			f.write('brain/lines.dat')
			if self.debug == 1:
				barf(DBG, "Lines zipped")
			try:
				f.write('brain/version')
				f.close()
				if self.debug == 1:
					barf(DBG, "Version zipped")
			except:
				f = open("brain/version", "w")
				f = write(self.version.brain)
				f.write('brain/version')
				f.close()
				if self.debug == 1:
					barf(DBG, "Version written.")

			f = open("brain/words.dat", "w")
			# write each words known
			wordlist = []
			#Sort the list before to export
			for key in self.words.keys():
				try:
					wordlist.append([key, len(self.words[key])])
				except:
					pass
			wordlist.sort(lambda x, y: cmp(x[1], y[1]))
			map((lambda x: f.write(str(x[0]) + "\n\r") ), wordlist)
			f.close()
			if self.debug == 1:
				barf(DBG, "Words written.")

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
				barf(DBG, "Sentences written.")

			if restart_timer is True:
				self.autosave = threading.Timer(to_sec("125m"), self.save_all)
				self.autosave.start()
				if self.debug == 1:
					barf(DBG, "Restart timer started.")

			# Save settings
			self.settings.save()
			self.brainstats.save()
			self.version.save()
			self.clean_up()

			barf(SAV, "Brain saved.")
			sys.exit(1)

	def clean_up(self):
		barf(DBG, "clean_up used but not implemented...")
		#if self.debug == 1:
		#	barf(DBG,"Cleaning up brain.")
		#try:
			#os.remove('brain/words.dat')
			#os.remove('brain/lines.dat')
			#os.remove('brain/version')
			#if self.debug == 1:
			#	barf(DBG, "Cleaned up brain mess.")
		#except (OSError, IOError), e:
		#	barf(ERR, "Could not remove the files.")

	def auto_rebuild(self):
		if self.settings.learning == 1:
			t = time.time()

			old_lines = self.lines
			old_num_words = self.brainstats.num_words
			old_num_contexts = self.brainstats.num_contexts

			self.words = {}
			self.lines = {}
			self.brainstats.num_words = 0
			self.brainstats.num_contexts = 0

			for k in old_lines.keys():
				filtered_line = filter_message(old_lines[k][0], self)
				self.learn(filtered_line, old_lines[k][1])

			# Restarts the timer
			self.autorebuild = threading.Timer(to_sec("71h"), self.auto_rebuild)
			self.autorebuild.start()

	def kill_timers(self):
		self.autosave.cancel()
		self.autopurge.cancel()
		self.autorebuild.cancel()

	def process_msg(self, io_module, body, replyrate, learn, args, owner=0, not_quiet=1):
		"""
		Process message 'body' and pass back to IO module with args.
		If owner==1 allow owner commands.
		If not_quiet==0 only respond with taught responses.
		"""

		if self.debug == 1:
			barf(DBG, "Processing message...")

		# add trailing space so sentences are broken up correctly
		body = body + " "

		# Parse commands
		if body[0] == "!":
			barf(DBG, "Parsing commands, not generating reply...")
			self.do_commands(io_module, body, args, owner)
			return

		# Filter out garbage and do some formatting
		if self.debug == 1:
			barf(DBG, "Filtering message...")
		body = filter_message(body, self)

		# Learn from input
		if learn == 1:
			if self.debug == 1:
				barf(DBG, "Learning from: " + body)
			self.learn(body)

		# Make a reply if desired
		if randint(0, 99) < replyrate:
			if self.debug == 1:
				barf(DBG, "Decided to answer...")
			message = ""

			#Look if we can find a prepared answer
			if dbread(body):
				if self.debug == 1:
					barf(DBG, "Using prepared answer.")
				message = unfilter_reply(dbread(body))
				if self.debug == 1:
					barf(DBG, "Replying with: " + message)
			if not_quiet == 1:
				for sentence in self.answers.sentences.keys():
					pattern = "^%s$" % sentence
					if re.search(pattern, body):
						if self.debug == 1:
							barf(DBG, "Searching for reply...")
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
						barf(DBG, "No prepared answer; thinking...")
					message = self.reply(body)
					if self.debug == 1:
						barf(DBG, "Reply formed; unfiltering...")
					message = unfilter_reply(message)
					if self.debug == 1:
						barf(DBG, "Unfiltered message: " + message)
			else:
				return

			# empty. do not output
			if message == "":
				if self.debug == 1:
					barf(DBG, "Not replying; message empty.")
				return
			if self.debug == 1:
				replying = "Not replying."
			#  else output
			if len(message) >= self.settings.length:
				time.sleep(3)
			else:
				time.sleep(.1 * len(message))
				if self.debug == 1:
					replying = "Reply sent."
				io_module.output(message, args)
			if self.debug == 1:
				barf(DBG, replying)

	def do_commands(self, io_module, body, args, owner):
		"""
		Respond to user commands.
		"""
		msg = ""

		command_list = body.split()
		command_list[0] = command_list[0]

		# Guest commands. These should be executable by anyone
		# Unless private = 1

		# Version string
		if command_list[0] == "!version":
			brain = self.version.brain
			core = self.version.core
			msg = "%s I am a scrib version %s. My brain version is %s." % (self.settings.pubsym, core, brain)


		# These, however, should never be public.

		# Learn/Teach commands
		if command_list[0] == "!teach" or command_list[0] == "!learn":
			try:
				key = ' '.join(command_list[1:]).split("|")[0].strip()
				key = re.sub("[\.\,\?\*\"\'!]", "", key)
				rnum = int(len(' '.join(command_list[1:]).split("|")) - 1)
				if "#nick" in key:
					msg = "%s Stop trying to teach me something that will break me!" % self.settings.pubsym
				else:
					value = teach_filter(' '.join(command_list[1:]).split("|")[1].strip())
					dbwrite(key[0:], value[0:])
					if rnum > 1:
						array = ' '.join(command_list[1:]).split("|")
						rcount = 1
						for value in array:
							if rcount == 1:
								rcount = rcount + 1
							else:
								dbwrite(key[0:], teach_filter(value[0:].strip()))
					else:
						value = ' '.join(command_list[1:]).split("|")[1].strip()
						dbwrite(key[0:], teach_filter(value[0:]))
					msg = "%s New response learned for %s" % (self.settings.pubsym, key)
			except:
				msg = "%s I couldn't learn that!" % self.settings.pubsym

		# Forget command
		if command_list[0] == "!forget":
			if os.path.isfile("brain/prepared.dat"):
				try:
					key = ' '.join(command_list[1:]).strip()
					for line in fileinput.input("brain/prepared.dat", inplace=1):
						data = line.split(":=:")[0]
						dlen = r'\b.{2,}\b'
						if re.search(dlen, key, re.IGNORECASE):
							if key.lower() in data.lower() or data.lower() in key.lower():
								pass
						else:
							print line.strip()
						msg = "%s I've discarded '%s' from my brain." % (self.settings.pubsym, key)
				except:
					msg = "%s Sorry, I couldn't forget that!" % (self.settings.pubsym)
			else:
				msg = "%s You have to teach me before you can make me forget it!" % self.settings.pubsym

		# Find response command
		if command_list[0] == "!find":
			if os.path.isfile("brain/prepared.dat"):
				rcount = 0
				matches = ""
				key = ' '.join(command_list[1:]).strip()
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
					msg = "%s I have no match for %s" % (self.settings.pubsym, key)
				elif rcount == 1:
					msg = "%s I found 1 match: %s" % (self.settings.pubsym, matches)
				else:
					msg = "%s I found %d matches: %s" % (self.settings.pubsym, rcount, matches)
			else:
				msg = "%s You need to teach me something first!" % self.settings.pubsym

		if command_list[0] == "!responses":
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
					msg = "%s I've learned no responses" % self.settings.pubsym
				elif rcount == 1:
					msg = "%s I've learned only 1 response" % self.settings.pubsym
				else:
					msg = "%s I've learned %d responses" % (self.settings.pubsym, rcount)
			else:
				msg = "%s You need to teach me something first!" % self.settings.pubsym

		# How many words do we know?
		elif command_list[0] == "!words":
			num_w = self.brainstats.num_words
			num_c = self.brainstats.num_contexts
			num_l = len(self.lines)
			if num_w != 0:
				num_cpw = num_c / float(num_w) # contexts per word
			else:
				num_cpw = 0.0
			msg = "%s I know %d words (%d contexts, %.2f per word), 1%d lines." % (
				self.settings.pubsym, num_w, num_c, num_cpw, num_l)

		# Do I know this word
		elif command_list[0] == "!known":
			if len(command_list) == 2:
				# single word specified
				word = command_list[1]
				if self.words.has_key(word):
					c = len(self.words[word])
					msg = "%s %s is known (%d contexts)" % (self.settings.pubsym, word, c)
				else:
					msg = "%s %s is unknown." % (self.settings.pubsym, word)
			elif len(command_list) > 2:
				# multiple words.
				words = []
				for x in command_list[1:]:
					words.append(x)
				msg = "%s Number of contexts: " % self.settings.pubsym
				for x in words:
					if self.words.has_key(x):
						c = len(self.words[x])
						msg += x + "/" + str(c) + " "
					else:
						msg += x + "/0 "

		# Owner commands
		if owner == 1:
			# Save the brain
			if command_list[0] == "!save":
				msg = "%s Saving brain..." % self.settings.pubsym
				self.save_all(False)
				msg = "%s Brain has been saved!" % self.settings.pubsym

			# Command list
			# TODO: Help should broken into Guest and Owner modules
			elif command_list[0] == "!help":
				if len(command_list) > 1:
					# Help for a specific command
					cmd = command_list[1]
					dic = None
					if cmd in self.commanddict.keys():
						dic = self.commanddict
					elif cmd in io_module.commanddict.keys():
						dic = io_module.commanddict
					if dic:
						for i in dic[cmd].split("\n"):
							io_module.output(self.settings.pubsym + i, args)
					else:
						msg = "%s No help on command '%s'" % (self.settings.pubsym, cmd)
				else:
					dic = self.commandlist
					for i in dic.split("\n"):
						io_module.output(self.settings.pubsym + " " + i, args)

			# Change the max_words setting
			elif command_list[0] == "!limit":
				msg = "%s The max limit is " % self.settings.pubsym
				if len(command_list) == 1:
					msg += str(self.settings.max_words)
				else:
					limit = int(command_list[1])
					self.settings.max_words = limit
					msg += "now " + command_list[1]

			# Check for broken links in the brain
			elif command_list[0] == "!check":
				t = time.time()
				num_broken = 0
				num_bad = 0
				for w in self.words.keys():
					wlist = self.words[w]

					for i in xrange(len(wlist) - 1, -1, -1):
						line_idx, word_num = struct.unpack("iH", wlist[i])

						# Nasty critical error we should fix
						if not self.lines.has_key(line_idx):
							barf(ACT, "Removing broken link '%s' -> %d." % (w, line_idx))
							num_broken = num_broken + 1
							del wlist[i]
						else:
							# Check pointed to word is correct
							split_line = self.lines[line_idx][0].split()
							if split_line[word_num] != w:
								barf(ACT, "Line '%s' word %d is not '%s' as expected." % \
										  (self.lines[line_idx][0],
										   word_num, w))
								num_bad = num_bad + 1
								del wlist[i]
					if len(wlist) == 0:
						del self.words[w]
						self.brainstats.num_words = self.brainstats.num_words - 1
						barf(ACT, "\"%s\" vaporized from brain." % w)

				msg = "%s Checked my brain in %0.2fs. Fixed links: %d broken, %d bad." % \
					  (self.settings.pubsym,
					   time.time() - t,
					   num_broken,
					   num_bad)

			# Rebuild the brain by discarding the word links and
			# Re-parsing each line
			elif command_list[0] == "!rebuild":
				if self.settings.learning == 1:
					t = time.time()

					old_lines = self.lines
					old_num_words = self.brainstats.num_words
					old_num_contexts = self.brainstats.num_contexts

					self.words = {}
					self.lines = {}
					self.brainstats.num_words = 0
					self.brainstats.num_contexts = 0

					for k in old_lines.keys():
						self.learn(old_lines[k][0], old_lines[k][1])

					msg = "%s Rebuilt brain in %0.2fs. Words %d (%+d), contexts %d (%+d)." % \
						  (self.settings.pubsym,
						   time.time() - t,
						   old_num_words,
						   self.brainstats.num_words - old_num_words,
						   old_num_contexts,
						   self.brainstats.num_contexts - old_num_contexts)

			# Remove rare words
			elif command_list[0] == "!prune":
				if self.debug == 1:
					barf(DBG, "Pruning...")
				t = time.time()

				list = []
				count = 0

				if len(command_list) == 2:
				# Occurrences to erase
					c_max = command_list[1]
				else:
					c_max = 0

				c_max = int(c_max)

				for w in self.words.keys():

					digit = 0
					char = 0
					for c in w:
						if c.isalpha():
							char += 1
						if c.isdigit():
							digit += 1


					# If the word limit is lower than this
					c = len(self.words[w])
					if c < 2 or ( digit and char ):
						list.append(w)
						count += 1
						if count == c_max:
							break

				if c_max < 1:
					io_module.output("%s %s words to remove" % (self.settings.pubsym, count), args)
					return

				# Remove the words
				for w in list[0:]:
					self.unlearn(w)

				msg = "%s Purged brain in %0.2fs. %d words removed." % \
					  (self.settings.pubsym,
					   time.time() - t,
					   count)

			# Change a typo in the brain
			elif command_list[0] == "!replace":
				if len(command_list) < 3:
					return
				old = command_list[1]
				new = command_list[2]
				msg = self.replace(old, new)

			# Barf the contents to avoid chat spamming.
			elif command_list[0] == "!context":
				if self.debug == 1:
					barf(DBG, "Checking contexts...")

				# build context we are looking for
				context = " ".join(command_list[1:])
				num_contexts = len(context)
				if context == "":
					return

				context = " ".join(command_list[1:])

				barf(ACT, "=========================================")
				barf(ACT, "Printing %s contexts containing \033[1m'%s'" % (num_contexts, context))
				barf(ACT, "=========================================")

				# Build context list
				# Pad it
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
						if len(c) == 0:
							c.append(self.lines[x][0])
						elif c[len(c) - 1] != self.lines[x][0]:
							c.append(self.lines[x][0])
				x = 0
				while x < 5:
					if x < len(c):
						lines = c
						barf(ACT, "%s" % lines[x])
					x += 1
				if len(c) == 5:
					return
				if x < 5:
					x = 5
				while x < len(c):
					lines = c
					barf(ACT, "%s" % lines[x])
					x += 1

				barf(ACT, "=========================================")

			# Remove a word from the vocabulary [use with care]
			elif command_list[0] == "!unlearn":
				if self.debug == 1:
					barf(DBG, "Unlearning...")
				# build context we are looking for
				context = " ".join(command_list[1:])
				if context == "":
					return
				barf(ACT, "Looking for: %s" % context)
				# Unlearn contexts containing 'context'
				t = time.time()
				self.unlearn(context)
				# we don't actually check if anything was
				# done..
				msg = "%s Unlearn done in %0.2fs" % (self.settings.pubsym, time.time() - t)

			# Query/toggle bot learning
			elif command_list[0] == "!learning":
				msg = "%s Learning mode " % self.settings.pubsym
				if len(command_list) == 1:
					if self.settings.learning == 0:
						msg += "off"
					else:
						msg += "on"
				else:
					toggle = command_list[1]
					if toggle == "on":
						msg += "on"
						self.settings.learning = 1
					else:
						msg += "off"
						self.settings.learning = 0

			# add a word to the 'censored' list
			elif command_list[0] == "!censor":
				# no arguments. list censored words
				if len(command_list) == 1:
					if len(self.settings.censored) == 0:
						msg = "%s No words censored." % self.settings.pubsym
					else:
						msg = "%s I will not use the word(s) %s" % (
							self.settings.pubsym, ", ".join(self.settings.censored))
				# add every word listd to censored list
				else:
					for x in xrange(1, len(command_list)):
						if command_list[x] in self.settings.censored:
							msg += "%s %s is already censored." % (self.settings.pubsym, command_list[x])
						else:
							self.settings.censored.append(command_list[x])
							self.unlearn(command_list[x])
							msg += "%s %s is now censored." % (self.settings.pubsym, command_list[x])
						msg += "\n"

			# remove a word from the censored list
			elif command_list[0] == "!uncensor":
				if self.debug == 1:
					barf(DBG, "Uncensoring...")
				# Remove words listed from the censor list
				# eg !uncensor tom dick harry
				for x in xrange(1, len(command_list)):
					try:
						self.settings.censored.remove(command_list[x])
						msg = "%s %s is uncensored." % (self.settings.pubsym, command_list[x])
					except ValueError, e:
						pass

			elif command_list[0] == "!alias":
				# List aliases words
				if len(command_list) == 1:
					if len(self.settings.aliases) == 0:
						msg = "%s No aliases" % self.settings.pubsym
					else:
						msg = "%s I will alias the word(s) %s." \
							  % (self.settings.pubsym, ", ".join(self.settings.aliases.keys()))
				# add every word listd to alias list
				elif len(command_list) == 2:
					if command_list[1][0] != '~': command_list[1] = '~' + command_list[1]
					if command_list[1] in self.settings.aliases.keys():
						msg = "%s These words : %s are aliases to %s." \
							  % (
							self.settings.pubsym, " ".join(self.settings.aliases[command_list[1]]), command_list[1] )
					else:
						msg = "%s The alias %s is not known." % (self.settings.pubsym, command_list[1][1:])
				elif len(command_list) > 2:
					#create the aliases
					msg = "%s The words : " % self.settings.pubsym
					if command_list[1][0] != '~': command_list[1] = '~' + command_list[1]
					if not (command_list[1] in self.settings.aliases.keys()):
						self.settings.aliases[command_list[1]] = [command_list[1][1:]]
						self.replace(command_list[1][1:], command_list[1])
						msg += command_list[1][1:] + " "
					for x in xrange(2, len(command_list)):
						msg += "%s " % command_list[x]
						self.settings.aliases[command_list[1]].append(command_list[x])
						#replace each words by his alias
						self.replace(command_list[x], command_list[1])
					msg += "have been aliased to %s." % command_list[1]

			# Fortune command
			elif command_list[0] == "!fortune":
				msg = self.settings.pubsym + "" \
					.join([i for i in os.popen('fortune').readlines()]).replace('\n\n','\n').replace('\n', ' ')
				msg = filter_message(msg)
			# Date command
			elif command_list[0] == "!date":
				msg = self.settings.pubsym + " It is ".join(i for i in os.popen('date').readlines())
			# Quit
			elif command_list[0] == "!quit":
				# Close the brain
				barf(ACT, "Goodbye!")
				sys.exit(0)

			# Save changes
			self.settings.save()

		if msg != "":
			io_module.output(msg, args)

	def replace(self, old, new):
		"""
		Replace all occurrences of 'old' in the brain with
		'new'. Nice for fixing learnt typos.
		"""
		try:
			pointers = self.words[old]
		except KeyError, e:
			return self.settings.pubsym + old + "%s %s not known."
		changed = 0

		for x in pointers:
			# pointers consist of (line, word) to self.lines
			l, w = struct.unpack("iH", x)
			line = self.lines[l][0].split()
			number = self.lines[l][1]
			if line[w] != old:
				# fucked brain
				barf(ERR, "Broken link: %s %s" % (x, self.lines[l][0] ))
				continue
			else:
				line[w] = new
				self.lines[l][0] = " ".join(line)
				self.lines[l][1] += number
				changed += 1

		if self.words.has_key(new):
			self.brainstats.num_words -= 1
			self.words[new].extend(self.words[old])
		else:
			self.words[new] = self.words[old]
		del self.words[old]
		return "%s %d instances of %s replaced with %s" % ( self.settings.pubsym, changed, old, new )

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
				wlist = self.lines[x][0].split()
				# add touched words to list
				for w in wlist:
					if not w in wordlist:
						wordlist.append(w)
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
					self.brainstats.num_contexts = self.brainstats.num_contexts - 1
			if len(words[x]) == 0:
				del words[x]
				self.brainstats.num_words = self.brainstats.num_words - 1
				barf(ACT, "\"%s\" vaporized from brain." % x)

	def reply(self, body):
		"""
		Reply to a line of text.
		"""
		try:
			if self.debug == 1:
				barf(DBG, "Forming a reply...")

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
				barf(DBG, "Chosen root word: %s" % word)

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
					context = self.lines[l][0]
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
					context = self.lines[l][0]
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
		except:
			return ""

	def learn(self, body, num_context=1):
		"""
		Lines should be cleaned (filter_message()) before passing
		to this.
		"""

		def learn_line(self, body, num_context):
			"""
			Learn from a sentence.
			"""

			words = body.split()
			# Ignore sentences of < 1 words XXX was <3
			if len(words) < 1:
				return

			# Ignore if the sentence starts with an exclamation
			if body[0:1] == "!":
				if self.debug == 1:
					barf(ERR, "Not learning: %s" % words)
				return

			vowels = "aÃ Ã¢eÃ©Ã¨ÃªiÃ®Ã¯oÃ¶Ã´uÃ¼Ã»y"
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
						barf(ACT, "Censored word %s" % words[x])
						return

				if len(words[x]) > 13 \
					or ( ((nb_voy * 100) / len(words[x]) < 26) and len(words[x]) > 5 ) \
					or ( char and digit ) \
					or ( self.words.has_key(words[x]) == 0 and self.settings.learning == 0 ):
					return
				elif ( "-" in words[x] or "_" in words[x] ):
					words[x] = "#nick"

			num_w = self.brainstats.num_words
			if num_w != 0:
				num_cpw = self.brainstats.num_contexts / float(num_w) # contexts per word
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
							self.brainstats.num_words += 1
						self.brainstats.num_contexts += 1
			else:
				self.lines[hashval][1] += num_context

			#is max_words reached, don't learn more
			if self.brainstats.num_words >= self.settings.max_words:
				self.settings.learning = 0
				barf(ERR, "Had to turn off learning- max_words limit reached!")

		# Split body text into sentences and parse them
		# one by one.
		body += " "
		map((lambda x: learn_line(self, x, num_context)), body.split(". "))

