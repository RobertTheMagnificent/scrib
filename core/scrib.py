#!/usr/bin/env python
# -*- coding: utf-8 -*-
  
from random import *
import sys
import os
import marshal
import struct
import time
import zipfile
import re

# sys.path.append('../core')

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
			i = message.index(")", index+1)
			message = message[0:i]+message[i+1:]
			# And remove the (
			message = message[0:index]+message[index+1:]
	except ValueError, e:
		pass

	words = message.split()
	if bot.settings.process_with == "scrib":
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
	import re
	import cfgfile

	coreVer = "0.6.5"
	brainVer = "0.0.1"
	ver_string = "!I am a version %s scrib." % coreVer
	ver_string += " My braintechnology is at %s." % brainVer

	# Main command list
	commandlist = "!Scrib commands:\n!check, !contexts, !help, !known, !learning, !rebuild, !replace, !unlearn, !purge, !version, !words, !limit, !alias, !save, !censor, !uncensor, !owner, !fortune. !tweet, !date"
	commanddict = {
		"help": "!Owner command. Usage: !help [command]\n!Prints information about using a command, or a list of commands if no command is given.",
		"version": "!Usage: !version\n!Display what version of Scrib we are running.",
		"words": "!Usage: !words\n!Display how many words are known.",
		"known": "!Usage: !known word1 [word2 [...]]\n!Displays if one or more words are known, and how many contexts are known.",
		"contexts": "!Owner command. Usage: !contexts <phrase>\n!Print contexts containing <phrase>.",
		"unlearn": "!Owner command. Usage: !unlearn <expression>\n!Remove all occurances of a word or expression from the brain. For example '!unlearn of of' would remove all contexts containing double 'of's.",
		"purge": "!Owner command. Usage: !purge [number]\n!Remove all occurances of the words that appears in less than <number> contexts.",
		"replace": "!Owner command. Usage: !replace <old> <new>\n!Replace all occurances of word <old> in the brain with <new>.",
		"learning": "!Owner command. Usage: !learning [on|off]\n!Toggle bot learning. Without arguments shows the current setting.",
		"check": "!Owner command. Usage: !check\n!Checks the brain for broken links. Shouldn't happen, but worth trying if you get KeyError crashes.",
		"rebuild": "!Owner command. Usage: !rebuild\n!Rebuilds brain links from the lines of known text. Takes a while. You probably don't need to do it unless the brain is very screwed.",
		"censor": "!Owner command. Usage: !censor [word1 [...]]\n!Prevent the bot using one or more words. Without arguments lists the currently censored words.",
		"uncensor": "!Owner command. Usage: !uncensor word1 [word2 [...]]\n!Remove censorship on one or more words.",
		"limit": "!Owner command. Usage: !limit [number]\n!Set the number of words that pyBorg can learn.",
		"alias": "!Owner command. Usage: !alias : Show the differents aliases\n!alias <alias> : show the words attached to this alias\n!alias <alias> <word> : link the word to the alias.",
		"owner": "!Usage: !owner password\n!Add the user in the owner list.",
		"tweet": "!Usage: !tweet\n!Currently doesn't do anything useful.",
		"fortune": "!Usage: !fortune\n!Tells you something interesting.",
		"date": "!Usage: !date\n!Tells you the date."
	}

	def __init__(self):
		"""
		Open the brain. Resize as required.
		"""
		# Attempt to load settings
		self.settings = self.cfgfile.cfgset()
		self.settings.load("conf/scrib.cfg",
			{ "num_contexts": ("Total word contexts", 0),
			  "num_words":	("Total unique words known", 0),
			  "max_words":	("max limits in the number of words known", 6000),
			  "learning":	("Allow the bot to learn", 1),
			  "ignore_list":("Words that can be ignored for the answer", ['!.', '?.', "'", ',', ';']),
			  "censored":	("Don't learn the sentence if one of those words is found", []),
			  "num_aliases":("Total of aliases known", 0),
			  "aliases":	("A list of similars words", {}),
			  "process_with":("Which module will we use to generate replies? (scrib|megahal)", "scrib"),
			  "pubsym": ("Symbol to append to cmd msgs in public", "!"),
			  "no_save"	:("If True, Scrib doesn't save his brain and configuration to disk", "False")
			} )

		self.answers = self.cfgfile.cfgset()
		self.answers.load("data/answers.txt",
			{ "sentences":	("A list of prepared answers", {})
			} )
		self.unfilterd = {}

		# Read the brain
		if self.settings.process_with == "scrib":
			print "[#] Reading my brain..."
			try:
				zfile = zipfile.ZipFile('data/archive.zip','r')
				for filename in zfile.namelist():
					data = zfile.read(filename)
					file = open(filename, 'w+b')
					file.write(data)
					file.close()
			except (EOFError, IOError), e:
				print "[!] No zip found"
			try:

				f = open("data/version", "rb")
				s = f.read()
				f.close()
				if s != self.brainVer:
					print "[!] Error loading the brain.\nPlease convert it before launching scrib."
					sys.exit(1)

				f = open("data/words.dat", "rb")
				s = f.read()
				f.close()
				self.words = marshal.loads(s)
				del s
				f = open("data/lines.dat", "rb")
				s = f.read()
				f.close()
				self.lines = marshal.loads(s)
				del s
			except (EOFError, IOError), e:
				# Create new database
				self.words = {}
				self.lines = {}
				print "[!] Error reading saves. New database created."

			# Is a resizing required?
			if len(self.words) != self.settings.num_words:
				print "[~] Updating my brain's information..."
				self.settings.num_words = len(self.words)
				num_contexts = 0
				# Get number of contexts
				for x in self.lines.keys():
					num_contexts += len(self.lines[x][0].split())
				self.settings.num_contexts = num_contexts
				# Save new values
				self.settings.save()
				
			# Is an aliases update required ?
			compteur = 0
			for x in self.settings.aliases.keys():
				compteur += len(self.settings.aliases[x])
			if compteur != self.settings.num_aliases:
				print "[~] Check brain for new aliases."
				self.settings.num_aliases = compteur

				for x in self.words.keys():
					#is there aliases ?
					if x[0] != '~':
						for z in self.settings.aliases.keys():
							for alias in self.settings.aliases[z]:
								pattern = "^%s$" % alias
								if self.re.search(pattern, x):
									print "replace %s with %s" %(x, z)
									self.replace(x, z)

				for x in self.words.keys():
					if not (x in self.settings.aliases.keys()) and x[0] == '~':
						print "unlearn %s" % x
						self.settings.num_aliases -= 1
						self.unlearn(x)
						print "unlearned aliases %s" % x


			#unlearn words in the unlearn.txt file.
			try:
				f = open("data/unlearn.txt", "r")
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



	def save_all(self):
		if self.settings.process_with == "scrib" and self.settings.no_save != "True":
			print "[#] Writing to my brain..."

			try:
				zfile = zipfile.ZipFile('data/archive.zip','r')
				for filename in zfile.namelist():
					data = zfile.read(filename)
					file = open(filename, 'w+b')
					file.write(data)
					file.close()
			except (OSError, IOError), e:
				print "[!] No brain zip found. Is this the first time scrib has been launched?"


			f = open("data/words.dat", "wb")
			s = marshal.dumps(self.words)
			f.write(s)
			f.close()
			f = open("data/lines.dat", "wb")
			s = marshal.dumps(self.lines)
			f.write(s)
			f.close()

			#save the version
			f = open("data/version", "w")
			f.write(self.brainVer)
			f.close()


			#zip the files
			f = zipfile.ZipFile('data/archive.zip','w',zipfile.ZIP_DEFLATED)
			f.write('data/words.dat')
			f.write('data/lines.dat')
			f.write('data/version')
			f.close()

			try:
				os.remove('data/words.dat')
				os.remove('data/lines.dat')
				os.remove('data/version')
			except (OSError, IOError), e:
				print "[!] Could not remove the files."

			f = open("data/words.txt", "w")
			# write each words known
			wordlist = []
			#Sort the list befor to export
			for key in self.words.keys():
				wordlist.append([key, len(self.words[key])])
			wordlist.sort(lambda x,y: cmp(x[1],y[1]))
			map( (lambda x: f.write(str(x[0])+"\n\r") ), wordlist)
			f.close()

			f = open("data/sentences.txt", "w")
			# write each words known
			wordlist = []
			#Sort the list befor to export
			for key in self.unfilterd.keys():
				wordlist.append([key, self.unfilterd[key]])
			wordlist.sort(lambda x,y: cmp(y[1],x[1]))
			map( (lambda x: f.write(str(x[0])+"\n") ), wordlist)
			f.close()


			# Save settings
			self.settings.save()

	def process_msg(self, io_module, body, replyrate, learn, args, owner=0):
		"""
		Process message 'body' and pass back to IO module with args.
		If owner==1 allow owner commands.
		"""

		try:
			if self.settings.process_with == "megahal": import mh_python
		except:
			self.settings.process_with = "scrib"
			self.settings.save()
			print "Could not find megahal python library\nProgram ending"
			sys.exit(1)

		# add trailing space so sentences are broken up correctly
		body = body + " "

		# Parse commands
		if body[0:1] == "!":
			self.do_commands(io_module, body, args, owner)
			return

		# Filter out garbage and do some formatting
		body = filter_message(body, self)
	
		# Learn from input
		if learn == 1:
			if self.settings.process_with == "scrib":
				self.learn(body)
			elif self.settings.process_with == "megahal" and self.settings.learning == 1:
				mh_python.learn(body)

		# Make a reply if desired
		if randint(0, 99) < replyrate:

			message  = ""

			#Look if we can find a prepared answer
			for sentence in self.answers.sentences.keys():
				pattern = "^%s$" % sentence
				if re.search(pattern, body):
					message = self.answers.sentences[sentence][randint(0, len(self.answers.sentences[sentence])-1)]
					break
				else:
					if body in self.unfilterd:
						self.unfilterd[body] = self.unfilterd[body] + 1
					else:
						self.unfilterd[body] = 0

			if message == "":
				if self.settings.process_with == "scrib":
					message = self.reply(body)
				elif self.settings.process_with == "megahal":
					message = mh_python.doreply(body)

			# single word reply: always output
			if len(message.split()) == 1:
				io_module.output(message, args)
				return
			# empty. do not output
			if message == "":
				return
			# else output
			if owner==0: time.sleep(.2*len(message))
			io_module.output(message, args)
	
	def do_commands(self, io_module, body, args, owner):
		"""
		Respond to user commands.
		"""
		msg = ""

		command_list = body.split()
		command_list[0] = command_list[0]

		# Guest commands.
	
		# Version string
		if command_list[0] == "!version":
			msg = self.ver_string

		# How many words do we know?
		elif command_list[0] == "!words" and self.settings.process_with == "scrib":
			num_w = self.settings.num_words
			num_c = self.settings.num_contexts
			num_l = len(self.lines)
			if num_w != 0:
				num_cpw = num_c/float(num_w) # contexts per word
			else:
				num_cpw = 0.0
			msg = "%sI know %d words (%d contexts, %.2f per word), 1%d lines." % ( self.settings.pubsym, num_w, num_c, num_cpw, num_l)
				
		# Do I know this word
		elif command_list[0] == "!known" and self.settings.process_with == "scrib":
			if len(command_list) == 2:
				# single word specified
				word = command_list[1]
				if self.words.has_key(word):
					c = len(self.words[word])
					msg = "%s%s is known (%d contexts)" % (self.settings.pubsym, word, c)
				else:
					msg = "%s%s is unknown." % (self.settings.pubsym, word)
			elif len(command_list) > 2:
				# multiple words.
				words = []
				for x in command_list[1:]:
					words.append(x)
				msg = "%sNumber of contexts: " % self.settings.pubsym
				for x in words:
					if self.words.has_key(x):
						c = len(self.words[x])
						msg += x+"/"+str(c)+" "
					else:
						msg += x+"/0 "
	
		# Owner commands
		if owner == 1:
			# Save the brain
			if command_list[0] == "!save":
				self.save_all()
				msg = "%sBrain has been saved!" % self.settings.pubsym

			# Command list
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
							io_module.output(i, args)
					else:
						msg = "%sNo help on command '%s'" % (self.settings.pubsym, cmd)
				else:
					for i in self.commandlist.split("\n"):
						io_module.output(i, args)
					for i in io_module.commandlist.split("\n"):
						io_module.output(i, args)

			# Change the max_words setting
			elif command_list[0] == "!limit" and self.settings.process_with == "scrib":
				msg = "%sThe max limit is " % self.settings.pubsym
				if len(command_list) == 1:
					msg += str(self.settings.max_words)
				else:
					limit = int(command_list[1])
					self.settings.max_words = limit
					msg += "now " + command_list[1]

			
			# Check for broken links in the brain
			elif command_list[0] == "!check" and self.settings.process_with == "scrib":
				t = time.time()
				num_broken = 0
				num_bad = 0
				for w in self.words.keys():
					wlist = self.words[w]

					for i in xrange(len(wlist)-1, -1, -1):
						line_idx, word_num = struct.unpack("iH", wlist[i])

						# Nasty critical error we should fix
						if not self.lines.has_key(line_idx):
							print "%sRemoving broken link '%s' -> %d." % (self.settings.pubsym, w, line_idx)
							num_broken = num_broken + 1
							del wlist[i]
						else:
							# Check pointed to word is correct
							split_line = self.lines[line_idx][0].split()
							if split_line[word_num] != w:
								print "%sLine '%s' word %d is not '%s' as expected." % \
									(self.settings.pubsym, 
									self.lines[line_idx][0],
									word_num, w)
								num_bad = num_bad + 1
								del wlist[i]
					if len(wlist) == 0:
						del self.words[w]
						self.settings.num_words = self.settings.num_words - 1
						print "\"%s\" vaped totally" % w

				msg = "%sChecked my brain in %0.2fs. Fixed links: %d broken, %d bad." % \
					(self.settings.pubsym, 
					time.time()-t,
					num_broken,
					num_bad)

			# Rebuild the brain by discarding the word links and
			# re-parsing each line
			elif command_list[0] == "!rebuild" and self.settings.process_with == "scrib":
				if self.settings.learning == 1:
					t = time.time()

					old_lines = self.lines
					old_num_words = self.settings.num_words
					old_num_contexts = self.settings.num_contexts

					self.words = {}
					self.lines = {}
					self.settings.num_words = 0
					self.settings.num_contexts = 0

					for k in old_lines.keys():
						self.learn(old_lines[k][0], old_lines[k][1])

					msg = "%sRebuilt brain in %0.2fs. Words %d (%+d), contexts %d (%+d)." % \
							(self.settings.pubsym, 
							time.time()-t,
							old_num_words,
							self.settings.num_words - old_num_words,
							old_num_contexts,
							self.settings.num_contexts - old_num_contexts)

			#Remove rare words
			elif command_list[0] == "!purge" and self.settings.process_with == "scrib":
				t = time.time()

				liste = []
				compteur = 0

				if len(command_list) == 2:
				# limited occurences a effacer
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

				
				#Compte les mots inferieurs a cette limite
					c = len(self.words[w])
					if c < 2 or ( digit and char ):
						liste.append(w)
						compteur += 1
						if compteur == c_max:
							break

				if c_max < 1:
					#io_module.output(str(compteur)+" words to remove", args)
					io_module.output("%s words to remove" %compteur, args)
					return

				#supprime les mots
				for w in liste[0:]:
					self.unlearn(w)

				msg = "%sPurged brain in %0.2fs. %d words removed." % \
						(self.settings.pubsym, 
						time.time()-t,
						compteur)
				
			# Change a typo in the brain
			elif command_list[0] == "!replace" and self.settings.process_with == "scrib":
				if len(command_list) < 3:
					return
				old = command_list[1]
				new = command_list[2]
				msg = self.replace(old, new)

			# Print contexts [flooding...:-]
			elif command_list[0] == "!contexts" and self.settings.process_with == "scrib":
				# This is a large lump of data and should
				# probably be printed, not module.output XXX

				# build context we are looking for
				context = " ".join(command_list[1:])
				if context == "":
					return
				io_module.output(self.settings.pubsym+"Contexts containing \""+context+"\":", args)
				# Build context list
				# Pad it
				context = " "+context+" "
				c = []
				# Search through contexts
				for x in self.lines.keys():
					# get context
					ctxt = self.lines[x][0]
					# add leading whitespace for easy sloppy search code
					ctxt = " "+ctxt+" "
					if ctxt.find(context) != -1:
						# Avoid duplicates (2 of a word
						# in a single context)
						if len(c) == 0:
							c.append(self.lines[x][0])
						elif c[len(c)-1] != self.lines[x][0]:
							c.append(self.lines[x][0])
				x = 0
				while x < 5:
					if x < len(c):
						io_module.output("%s"+c[x], args) % self.settings.pubsym
					x += 1
				if len(c) == 5:
					return
				if len(c) > 10:
					io_module.output("%s...("+`len(c)-10`+" skipped)...", args) % self.settings.pubsym
				x = len(c) - 5
				if x < 5:
					x = 5
				while x < len(c):
					io_module.output("%s"+c[x], args) % self.settings.pubsym
					x += 1

			# Remove a word from the vocabulary [use with care]
			elif command_list[0] == "!unlearn" and self.settings.process_with == "scrib":
				# build context we are looking for
				context = " ".join(command_list[1:])
				
				if context == "":
					return
				print "Looking for: "+context
				# Unlearn contexts containing 'context'
				t = time.time()
				self.unlearn(context)
				# we don't actually check if anything was
				# done..
				msg = "%sUnlearn done in %0.2fs" % (self.settings.pubsym, time.time()-t)

			# Query/toggle bot learning
			elif command_list[0] == "!learning":
				msg = "%sLearning mode " % self.settings.pubsym
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
			elif command_list[0] == "!censor" and self.settings.process_with == "scrib":
				# no arguments. list censored words
				if len(command_list) == 1:
					if len(self.settings.censored) == 0:
						msg = "%sNo words censored." % self.settings.pubsym
					else:
						msg = "%sI will not use the word(s) %s" % (self.settings.pubsym, ", ".join(self.settings.censored))
				# add every word listed to censored list
				else:
					for x in xrange(1, len(command_list)):
						if command_list[x] in self.settings.censored:
							msg += "%s%s is already censored." % (self.settings.pubsym, command_list[x])
						else:
							self.settings.censored.append(command_list[x])
							self.unlearn(command_list[x])
							msg += "%s%s is now censored." % c(self.settings.pubsym, ommand_list[x])
						msg += "\n"

			# remove a word from the censored list
			elif command_list[0] == "!uncensor" and self.settings.process_with == "scrib":
				# Remove everyone listed from the ignore list
				# eg !unignore tom dick harry
				for x in xrange(1, len(command_list)):
					try:
						self.settings.censored.remove(command_list[x])
						msg = "%s%s is uncensored." % (self.settings.pubsym, command_list[x])
					except ValueError, e:
						pass

			elif command_list[0] == "!alias" and self.settings.process_with == "scrib":
				# no arguments. list aliases words
				if len(command_list) == 1:
					if len(self.settings.aliases) == 0:
						msg = "%sNo aliases" % self.settings.pubsym
					else:
						msg = "%sI will alias the word(s) %s." \
						% (self.settings.pubsym, ", ".join(self.settings.aliases.keys()))
				# add every word listed to alias list
				elif len(command_list) == 2:
					if command_list[1][0] != '~': command_list[1] = '~' + command_list[1]
					if command_list[1] in self.settings.aliases.keys():
						msg = "%sThese words : %s are aliases to %s." \
						% (self.settings.pubsym, " ".join(self.settings.aliases[command_list[1]]), command_list[1] )
					else:
						msg = "%sThe alias %s is not known." % (self.settings.pubsym, command_list[1][1:])
				elif len(command_list) > 2:
					#create the aliases
					msg = "%sThe words : " % self.settings.pubsym
					if command_list[1][0] != '~': command_list[1] = '~' + command_list[1]
					if not(command_list[1] in self.settings.aliases.keys()):
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
				msg = "%s".join([i for i in os.popen('fortune').readlines()]).replace('\n\n', '\n').replace('\n', ' ') % self.settings.pubsym
			
			# Tweeter command
			elif command_list[0] == "!tweet":
				msg = '%stest :3' % self.settings.pubsym
			# Date command
			elif command_list[0] == "!date":
				msg = "%sIt is ".join(i for i in os.popen('date').readlines()) % self.settings.pubsym
			# Quit
			elif command_list[0] == "!quit":
				# Close the brain
				self.save_all()
				print "[#] Saved my brain. Goodbye!"
				sys.exit()
				
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
			return self.settings.pubsym+old+" not known."
		changed = 0

		for x in pointers:
			# pointers consist of (line, word) to self.lines
			l, w = struct.unpack("iH", x)
			line = self.lines[l][0].split()
			number = self.lines[l][1]
			if line[w] != old:
				# fucked brain
				print "%sBroken link: %s %s" % (self.settings.pubsym, x, self.lines[l][0] )
				continue
			else:
				line[w] = new
				self.lines[l][0] = " ".join(line)
				self.lines[l][1] += number
				changed += 1

		if self.words.has_key(new):
			self.settings.num_words -= 1
			self.words[new].extend(self.words[old])
		else:
			self.words[new] = self.words[old]
		del self.words[old]
		return "%s%d instances of %s replaced with %s" % ( self.settings.pubsym, changed, old, new )

	def unlearn(self, context):
		"""
		Unlearn all contexts containing 'context'. If 'context'
		is a single word then all contexts containing that word
		will be removed, just like the old !unlearn <word>
		"""
		# Pad thing to look for
		# We pad so we don't match 'shit' when searching for 'hit', etc.
		context = " "+context+" "
		# Search through contexts
		# count deleted items
		dellist = []
		# words that will have broken context due to this
		wordlist = []
		for x in self.lines.keys():
			# get context. pad
			c = " "+self.lines[x][0]+" "
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
			for y in xrange(len(word_contexts)-1, -1, -1):
				# Check for any of the deleted contexts
				if unpack("iH", word_contexts[y])[0] in dellist:
					del word_contexts[y]
					self.settings.num_contexts = self.settings.num_contexts - 1
			if len(words[x]) == 0:
				del words[x]
				self.settings.num_words = self.settings.num_words - 1
				print "\"%s\" vaped totally" %x

	def reply(self, body):
		"""
		Reply to a line of text.
		"""
		# split sentences into list of words
		_words = body.split(" ")
		words = []
		for i in _words:
			words += i.split()
		del _words

		if len(words) == 0:
			return ""
		
		
		#remove words on the ignore list
		#words = filter((lambda x: x not in self.settings.ignore_list and not x.isdigit() ), words)
		words = [x for x in words if x not in self.settings.ignore_list and not x.isdigit()]

		# Find rarest word (excluding those unknown)
		index = []
		known = -1
		#The word has to bee seen in already 3 contexts differents for being choosen
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
		if len(index)==0:
			return ""
		word = index[randint(0, len(index)-1)]

		# Build sentence backwards from "chosen" word
		sentence = [word]
		done = 0
		while done == 0:
			#create a brain which will contain all the words we can find before the "chosen" word
			pre_words = {"" : 0}
			#this is to prevent a case where we have an ignore_listed word
			word = str(sentence[0].split(" ")[0])
			for x in xrange(0, len(self.words[word]) -1 ):
				l, w = struct.unpack("iH", self.words[word][x])
				context = self.lines[l][0]
				num_context = self.lines[l][1]
				cwords = context.split()
				#if the word is not the first of the context, look to the previous one
				if cwords[w] != word:
					print context
				if w:
					#look if we can find a pair with the choosen word, and the previous one
					if len(sentence) > 1 and len(cwords) > w+1:
						if sentence[1] != cwords[w+1]:
							continue

					#if the word is in ignore_list, look to the previous word
					look_for = cwords[w-1]
					if look_for in self.settings.ignore_list and w > 1:
						look_for = cwords[w-2]+" "+look_for

					#saves how many times we can find each word
					if not(pre_words.has_key(look_for)):
						pre_words[look_for] = num_context
					else :
						pre_words[look_for] += num_context


				else:
					pre_words[""] += num_context

			#Sort the words
			liste = pre_words.items()
			liste.sort(lambda x,y: cmp(y[1],x[1]))
			
			numbers = [liste[0][1]]
			for x in xrange(1, len(liste) ):
				numbers.append(liste[x][1] + numbers[x-1])

			#take one of them from the list (randomly)
			mot = randint(0, numbers[len(numbers) -1])
			for x in xrange(0, len(numbers)):
				if mot <= numbers[x]:
					mot = liste[x][0]
					break

			#if the word is already choosen, pick the next one
			while mot in sentence:
				x += 1
				if x >= len(liste) -1:
					mot = ''
				mot = liste[x][0]

			mot = mot.split(" ")
			mot.reverse()
			if mot == ['']:
				done = 1
			else:
				map( (lambda x: sentence.insert(0, x) ), mot )

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
			post_words = {"" : 0}
			word = str(sentence[-1].split(" ")[-1])
			for x in xrange(0, len(self.words[word]) ):
				l, w = struct.unpack("iH", self.words[word][x])
				context = self.lines[l][0]
				num_context = self.lines[l][1]
				cwords = context.split()
				#look if we can find a pair with the choosen word, and the next one
				if len(sentence) > 1:
					if sentence[len(sentence)-2] != cwords[w-1]:
						continue

				if w < len(cwords)-1:
					#if the word is in ignore_list, look to the next word
					look_for = cwords[w+1]
					if look_for in self.settings.ignore_list and w < len(cwords) -2:
						look_for = look_for+" "+cwords[w+2]

					if not(post_words.has_key(look_for)):
						post_words[look_for] = num_context
					else :
						post_words[look_for] += num_context
				else:
					post_words[""] += num_context
			#Sort the words
			liste = post_words.items()
			liste.sort(lambda x,y: cmp(y[1],x[1]))
			numbers = [liste[0][1]]
			
			for x in xrange(1, len(liste) ):
				numbers.append(liste[x][1] + numbers[x-1])

			#take one of them from the list (randomly)
			mot = randint(0, numbers[len(numbers) -1])
			for x in xrange(0, len(numbers)):
				if mot <= numbers[x]:
					mot = liste[x][0]
					break

			x = -1
			while mot in sentence:
				x += 1
				if x >= len(liste) -1:
					mot = ''
					break
				mot = liste[x][0]


			mot = mot.split(" ")
			if mot == ['']:
				done = 1
			else:
				map( (lambda x: sentence.append(x) ), mot )

		sentence = pre_words[:-2] + sentence

		#Replace aliases
		for x in xrange(0, len(sentence)):
			if sentence[x][0] == "~": sentence[x] = sentence[x][1:]

		#Insert space between each words
		map( (lambda x: sentence.insert(1+x*2, " ") ), xrange(0, len(sentence)-1) ) 

		#correct the ' & , spaces problem
		#the code is not very good and can be improved but it does the job...
		for x in xrange(0, len(sentence)):
			if sentence[x] == "'":
				sentence[x-1] = ""
				sentence[x+1] = ""
			if sentence[x] == ",":
				sentence[x-1] = ""

		#return as string..
		return "".join(sentence)

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
				print "[!] Not learning: %s" %words
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
						print "[~] Censored word %s" %words[x]
						return

				if len(words[x]) > 13 \
				or ( ((nb_voy*100) / len(words[x]) < 26) and len(words[x]) > 5 ) \
				or ( char and digit ) \
				or ( self.words.has_key(words[x]) == 0 and self.settings.learning == 0 ):
					return
				elif ( "-" in words[x] or "_" in words[x] ) :
					words[x]="#nick"


			num_w = self.settings.num_words
			if num_w != 0:
				num_cpw = self.settings.num_contexts/float(num_w) # contexts per word
			else:
				num_cpw = 0

			cleanbody = " ".join(words)

			# Hash collisions we don't care about. 2^32 is big :-)
			hashval = hash(cleanbody)

			# Check that context isn't already known
			if not self.lines.has_key(hashval):
				if not(num_cpw > 100 and self.settings.learning == 0):
					
					self.lines[hashval] = [cleanbody, num_context]
					# Add link for each word
					for x in xrange(0, len(words)):
						if self.words.has_key(words[x]):
							# Add entry. (line number, word number)
							self.words[words[x]].append(struct.pack("iH", hashval, x))
						else:
							self.words[words[x]] = [ struct.pack("iH", hashval, x) ]
							self.settings.num_words += 1
						self.settings.num_contexts += 1
			else :
				self.lines[hashval][1] += num_context

			#is max_words reached, don't learn more
			if self.settings.num_words >= self.settings.max_words: self.settings.learning = 0

		# Split body text into sentences and parse them
		# one by one.
		body += " "
		map ( (lambda x : learn_line(self, x, num_context)), body.split(". "))
