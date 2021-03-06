#!/usr/bin/env python
# -*- coding: utf-8 -*-
from random import randint
from bs4 import UnicodeDammit
import datetime
import hashlib
import os
import re
import shutil
import string
import threading
import time
import zipfile

import barf
import cfg
import clean

class brain:

	def __init__(self):
		"""
		Here we'll load settings and set up us the brain.
		"""
		self.version = '0.2.1'
		self.barf = barf.Barf
		self.clean = clean.clean()
		self.cfg = cfg
		self.settings = self.cfg.set()
		
		# Load brain config (or create with these defaults).
		self.settings.load('conf/brain.cfg', {
			'debug': 0,
			'symbol': '!',
			'learning': 1,
			'censored': [],
			'num_words': 0,
			'num_contexts': 0,
			'num_aliases': 0,
			'max_words': 1000000,
			'aliases': {},
			'optimum': 0,
			'ignore_list': []
			})

		self.static_answers = self.cfg.set()
		self.static_answers.load("brain/answers.dat", {
							"sentences": {}
							})
		self.unfilterd = {}
		self.timers_started = False
		
		# Starts the timers:
		if self.timers_started is False:
			try:
				self.autosave = threading.Timer(self.to_sec("125m"), self.__save)
				self.autosave.start()
				self.autorebuild = threading.Timer(self.to_sec("71h"), self.auto_rebuild)
				self.autorebuild.start()
				timers_started = True
			except SystemExit, e:
				self.autosave.cancel()
				self.autorebuild.cancel()

		self._load()

	# Makes !learn and !teach usable
	def dbread(self, key):
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

	def dbwrite(self, key, value):
		if self.dbread(key) is None:
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
	
	def brain_type(self, version):
		"""
		This be awful, yo.
		"""
		marshal = ['0.0.1', '0.1.0', '0.1.1']
		pickle = ['0.1.2', '0.1.3', '0.1.4']
		json = ['0.1.5', '0.1.6', '0.1.7', '0.1.8']
		verfour = ['0.1.9', '0.2.0', '0.2.1']
		
		if version in marshal:
			btype = 1
		elif version in pickle:
			btype = 2
		elif version in json:
			btype = 3
		elif version in verfour:
			btype = 4
		else:
			self.barf('ERR', "Invalid brain type")
			return 0

		return btype

	def unpack(self, file, version, upgrade=False):
		if self.brain_type(version) == 1:
			import marshal
			stuff = marshal.loads(file)
				
		elif self.brain_type(version) == 2:
			import cPickle as pickle
			stuff = pickle.loads(file)
				
		elif self.brain_type(version) >= 3:
			import json
			stuff = json.loads(file)

		if upgrade == True:
			self.upgrade(file)
			
		return stuff
		
	def pack(self, file, version, upgrade=False):
		if self.brain_type(version) == 1:
			#import marshal
			stuff = marshal.dumps(file)
		elif self.brain_type(version) == 2:
			#import cPickle as pickle
			stuff = pickle.dumps(file)
		elif self.brain_type(version) == 3 or self.brain_type(version) == 4:
			import json
			stuff = json.dumps(file, sort_keys=True, indent=4, separators=(',', ': '), encoding='utf-8')

		return stuff


	def upgrade(self, file):
			try:
				tmp = 'brain/tmp'
				self.words = {}
				self.lines = {}
				self.settings.num_words = 0
				self.settings.num_lines = 0
				d = 0
				i = 0
				self.barf('ACT', 'Recompiling...')
				with open(tmp, 'w+') as s:
					for v in s:
						if len(v.split()) < 3:
							s[v][0] = UnicodeDammit(s[v][0])
							f.write(s[v][0].unicode_markup.encode('utf8'))
							i += 1
							if self.settings.debug == 1:
								self.barf('DBG', '%d (%d dumped)' % ( i, d ))
						else:
							d += 1				
				i = 0
				self.barf('ACT', 'Learning...')
				with open(tmp, 'rb') as c:
					for l in c:
						self.learn(self.clean.line(l, self.settings), 1)
						if self.settings.debug == 1:
							self.barf('DBG', '%s ' % l)
				os.remove(tmp)
				
				self.barf('ACT', 'Generating contexs...')
				self.auto_rebuild()
			except Exception, e:
				self.barf('ERR', '%s: %s' % (tmp, e))

	def _load(self):
		"""
		Load the brain.
		"""
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
			v = f.read()
			self.barf('MSG', "Current brain version is %s " % v)
			f.close()
			if v != self.version:
				self.barf('ERR', "Brain is version "+v+", but I use "+self.version+".")
				self.barf('ERR', "Would you like to update the brain?")
				c = raw_input("[Y/n]")
				if c[:1].lower() != 'n':
					timestamp = "%s-%s" % (datetime.date.today(), time.strftime("%H%M%S",time.localtime(time.time())))
					shutil.copyfile("brain/cortex.zip", "backups/%s-cortex-%s.zip" % ( 'backup', timestamp ))
					self.barf('ACT', "Backup saved to backups/cortex-%s.zip" % timestamp)
					self.barf('ACT', "Starting update, may take a few moments.")
					if self.settings.debug == 1:
					#	self.barf('DBG', "Words converted.")
						self.barf('DBG', "Reading lines...")
					f = open("brain/lines.dat", "rb")
					s = f.read()
					f.close()
					self.lines = self.unpack(s, v, True)
					if self.settings.debug == 1:
						self.barf('DBG', 'Found %d lines' % len(self.lines))
					if self.settings.optimum == 1:
						self.words = {}
						self.lines = {}
						if self.settings.debug == 1:
							self.barf('DBG', "Applying filter to adjust to new brain system.")
							self.barf('TAB', "This may take a bit, and may shrink the dataset.")
							try:
								self.auto_rebuild()
							except:
								self.barf('ERR', 'Brain failed to migrate.')
								self.barf('ERR', 'Words: %s' % type(self.words))
								self.barf('ERR', 'Lines: %s' % type(self.lines))
					f = open("brain/lines.dat", "wb")
					s = self.pack(self.lines, self.version)
					f.write(s)
					f.close()
					del s
					if self.settings.debug == 1:
						self.barf('DBG', "Lines converted.")
					f = open("brain/version", "wb")
					f.write(self.version)
					f.close()
					if self.settings.debug == 1:
						self.barf('DBG', 'Found %d words' % len(self.words))
						self.barf('DBG', 'Type: %s' % type(self.words[0]))
					#del s
					if self.settings.debug == 1:
						self.barf('DBG', "Saving words...")
					f = open("brain/words.dat", "wb")
					s = self.pack(self.words, self.version)
					f.write(s)
					f.close()
					del s
					if self.settings.debug == 1:
						self.barf('DBG', "Version updated.")
					v = self.version
				else:
					self.version = v # Saves old brain as old brain format.

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
		self.settings.num_words = len(self.words)
		num_contexts = 0
		# Get number of contexts
		for x in self.lines.keys():
			num_contexts += len(self.lines[x][0].split())
		self.settings.num_contexts = num_contexts
		self.barf('ACT', "%s words and %s contexts loaded" % ( self.settings.num_words, self.settings.num_contexts ))
		
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
							if re.search(pattern, x):
								self.barf('ACT', "Replacing %s with %s" % (x, z))
								self.replace(x, z)

			for x in self.words.keys():
				if not (x in self.settings.aliases.keys()) and x[0] == '~':
					self.barf('ACT', "Unlearning %s" % x)
					self.settings.num_aliases -= 1
					self.unlearn(x)
					self.barf('ACT', "unlearned aliases %s" % x)


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

	def __save(self, interface, restart_timer=True):
		"""
		Save the brain files.
		"""
		self.barf('SAV', "Writing to my brain...")

		f = open("brain/words.dat", "wb")
		s = self.pack(self.words, self.version)
		f.write(s)
		f.close()
		if self.settings.debug == 1:
			self.barf('DBG', "Words saved.")

		f = open("brain/lines.dat", "wb")
		s = self.pack(self.lines, self.version)
		f.write(s)
		f.close()
		if self.settings.debug == 1:
			self.barf('DBG', "Lines saved.")
		
		if self.settings.debug == 1:
			self.barf('DBG', 'Saving version.')
		f = open("brain/version", "wb")
		f.write(self.version)
		f.close()

		#zip the files
		f = zipfile.ZipFile('brain/cortex.zip', 'w', zipfile.ZIP_DEFLATED)
		
		f.write('brain/words.dat')
		if self.settings.debug == 1:
			self.barf('DBG', "Words zipped")
		os.remove('brain/words.dat')

		f.write('brain/lines.dat')
		if self.settings.debug == 1:
			self.barf('DBG', "Lines zipped")
		os.remove('brain/lines.dat')
		
		f.write('brain/version')
		f.close()
		if self.settings.debug == 1:
			self.barf('DBG', "Version zipped")
		os.remove('brain/version')

		f = open("brain/words.dat", "w")
		# write each words known
		wordlist = []
		#Sort the list before to export
		for key in self.words.keys():
			try:
				wordlist.append([key, len(self.words[key])])
			except:
				pass
		
		# Save settings
		if self.settings.debug == 1:
			self.barf('DBG', 'Saving brain settings.')
		self.settings.save()

		# This is causing a headache and I am working on replacing it.
		# ~ cptmashek
		#if self.settings.debug == 1:
		#	self.barf('DBG', 'Saving interface %s' % interface)
		#if interface != False:
		#	interface.settings.save()

		self.barf('SAV', "Brain saved.")

		if restart_timer is True:
			self.autosave = threading.Timer(self.to_sec("125m"), self.__save)
			self.autosave.start()
			if self.settings.debug == 1:
				self.barf('DBG', "Restart timer started.")


	def learn(self, body, num_context=1):
		"""
		Lines should be cleaned (clean.line()) before passing to this.
		"""
		def learn_line(self, body, num_context):
			"""
			Learn from a sentence.
			"""
			if body == 0:
				return
			
			words = body.split()
			#words = str(body).split()
			# Ignore sentences of < 1
			if len(words) < 1:
				return

			for x in xrange(0, len(words)):
				digit = 0
				char = 0
				for c in words[x]:
					if c.isalpha():
						char += 1
					if c.isdigit():
						digit += 1

				for censored in self.settings.censored:
					pattern = "^%s$" % censored
					if re.search(pattern, words[x]):
						self.barf('ACT', "Censored word %s" % words[x])
						return

				if len(words[x]) > 13 and len(words[x]) > 5 or ( char and digit ) \
					or ( self.words.has_key(words[x]) == 0 and self.settings.learning == 0 ):
					return
				elif ( "-" in words[x] or "_" in words[x] ):
					words[x] = "#nick"

			num_w = self.settings.num_words
			if num_w != 0:
				num_cpw = self.settings.num_contexts / float(num_w) # contexts per word
			else:
				num_cpw = 0

			cleanbody = " ".join(words).encode('utf8')

			hashval = hashlib.sha1(cleanbody).hexdigest()[:10]
			if not (num_cpw > 100 and self.settings.learning == 0) and not self.lines.has_key(hashval) :
				self.lines[hashval] = [cleanbody, num_context]
				# Add link for each word
				if self.settings.debug == 1:
					self.barf('DBG', 'Hash %s added' % ( hashval ))
				for x in xrange(0, len(words)):
					if self.words.has_key(words[x]):
						self.words[words[x]].append([hashval, x])
					else:
						self.words[words[x]] = [hashval, x]
						self.settings.num_words += 1
					self.settings.num_contexts += 1
			else:
				self.lines[hashval][1] += num_context

			#is max_words reached, don't learn more
			if self.settings.num_words >= self.settings.max_words:
				self.settings.learning = 0
				self.barf('ERR', "Had to turn off learning- max_words limit reached!")

		# Split body text into sentences and parse them
		# one by one.
		body += " "
		lines = body.split(". ")
		for line in lines:
			learn_line(self, line, num_context)

	def auto_rebuild(self):
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
				filtered_line = self.clean.line(old_lines[k][0], self.settings)
				self.learn(filtered_line, old_lines[k][1])
			msg = "Rebuilt brain in %0.2fs. Words %d (%+d), contexts %d (%+d)." % \
				  (time.time() - t,
				   old_num_words,
				   self.settings.num_words - old_num_words,
				   old_num_contexts,
				   self.settings.num_contexts - old_num_contexts)

			# Restarts the timer
			self.autorebuild = threading.Timer(self.to_sec("71h"), self.auto_rebuild)
			self.autorebuild.start()

			return msg
		else:
			return "Learning mode is off; will not rebuild."

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
		# update links
		for x in wordlist:
			word_contexts = words[x]
			# Check all the word's links (backwards so we can delete)
			for y in xrange(len(word_contexts) - 1, -1, -1):
				# Check for any of the deleted contexts
				if y[0] in dellist:
					del word_contexts[y]
					self.settings.num_contexts = self.settings.num_contexts - 1
			if len(words[x]) == 0:
				del words[x]
				self.settings.num_words = self.settings.num_words - 1
				self.barf('ACT', "\"%s\" vaporized from brain." % x)

	def reply(self, body):
		"""
		Reply to a line of text.
		"""
		if self.settings.debug == 1:
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

		# If the word is in at least these many contexts, it can be chosen.
		known_min = 3
		for x in xrange(0, len(words)):
			if self.words.has_key(words[x]):
				k = len(self.words[words[x]])
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
				if self.settings.debug == 1:
					self.barf('DBG', 'Appending %s' % words[x])
				continue
		# Index now contains list of rarest known words in sentence
		if len(index) == 0:
			return ""
		word = index[randint(0, len(index) - 1)]
		if self.settings.debug == 1:
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
				l = self.words[word][0]
				w = self.words[word][1]
				try:
					context = self.lines[l][0]
				except KeyError, e:
					self.barf('ERR', e)
					break

				num_context = self.lines[l][1]
				cwords = context.split()
				#if the word is not the first of the context, look to the previous one
				if w:
					#look if we can find a pair with the chosen word, and the previous one
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
					self.barf('DBG', 'Word: %s' % ( word ))

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
				l = self.words[word][x][0]
				w = self.words[word][x][1]
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
		num_pointers = len(pointers)
		print pointers
		for x in pointers:
			l = pointers[0]
			w = pointers[1]

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
			self.brain.stats['num_words'] -= 1
			self.words[new].extend(self.words[old])
		else:
			self.words[new] = self.words[old]
		del self.words[old]
		return "%d instances of %s replaced with %s" % ( changed, old, new )
			
	def to_sec(self, s):
		seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
		return int(s[:-1]) * seconds_per_unit[s[-1]]

	def kill_timers(self):
		self.autosave.cancel()
		self.autorebuild.cancel()
		
	def shutdown(self, interface):
		# Save the brain
		self.kill_timers()
		self.__save(interface, False)
		self.barf('MSG', 'Goodbye!')
		# Now we close everything.
		os._exit(0)
