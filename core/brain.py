#!/usr/bin/env python
# -*- coding: utf-8 -*-
import datetime
import hashlib
import os
import re
import shutil
import threading
import time
import zipfile

import barf
import cfg
import clean

class brain:

	def __init__(self):
		self.barf = barf.Barf
		self.cfg = cfg
		self.settings = self.cfg.set()
		self.scribsettings = self.cfg.set()
		self.clean = clean.clean()
	
		self.settings.load("conf/brain.cfg", {
							'debug': 0,
							'learning': 1,
							"censored": [],
							"num_aliases": 0,
							"aliases": {},
							"optimum": 1,
							"version": '0.2.0',
							})

		if self.brain_type(self.settings.version) < 4:
			self.barf('ROL', 'Brain files before 0.2.0 will fail on upgrade.')
			self.barf('ROL', 'We are working on an external conversion script.')
			self.barf('ROL', 'Continue without upgrading.')

		self.scribsettings.load("conf/scrib.cfg", '')

		self.stats = {
							"num_contexts": 0,
							"num_words": 0,
							"max_words": 1000000
							}			
		self.static_answers = self.cfg.set()
		self.static_answers.load("brain/answers.dat", {
							"sentences": {}
							})
		self.unfilterd = {}
		self.timers_started = False
		
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

		self._load()

	def brain_type(self, version):
		marshal = ['0.0.1', '0.1.0', '0.1.1']
		pickle = ['0.1.2', '0.1.3', '0.1.4']
		json = ['0.1.5', '0.1.6', '0.1.7', '0.1.8']
		verfour = ['0.1.9', '0.2.0']
		
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
		elif self.brain_type(version) == 3 or self.brain_type(version) == 4:
			import json
			stuff = json.loads(file)
		return stuff

	def pack(self, file, version, upgrade=False):
		if self.brain_type(version) == 1:
			import marshal
			stuff = marshal.dumps(file)
		elif self.brain_type(version) == 2:
			import cPickle as pickle
			stuff = pickle.dumps(file)
		elif self.brain_type(version) == 3 or self.brain_type(version) == 4:
			import json
			if upgrade == True:
				stuff = json.dumps(file, sort_keys=True, indent=4, separators=(',', ': ')).decode('latin1').encode('utf8', 'replace')
				return stuff
			stuff = json.dumps(file, sort_keys=True, indent=4, separators=(',', ': '))
		return stuff

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
			v = f.read().strip()
			self.barf('MSG', "Current brain version is %s " % v)
			f.close()
			if v != self.settings.version:
				self.barf('ERR', "Brain is version "+v+", but I use "+self.settings.version+".")
				self.barf('ERR', "Would you like to update the brain?")
				c = raw_input("[Y/n]")
				if c[:1].lower() != 'n':
					timestamp = "%s-%s" % (datetime.date.today(), time.strftime("%H%M%S",time.localtime(time.time())))
					shutil.copyfile("brain/cortex.zip", "backups/%s-cortex-%s.zip" % ( self.scribsettings.name, timestamp ))
					self.barf('ACT', "Backup saved to backups/cortex-%s.zip" % timestamp)
					self.barf('ACT', "Starting update, may take a few moments.")
					f = open("brain/words.dat", "rb")
					if self.settings.debug == 1:
						self.barf('DBG', "Reading words...")
					s = f.read()
					f.close()
					self.words = self.unpack(s, v, True)
					del s
					if self.settings.debug == 1:
						self.barf('DBG', "Saving words...")
					f = open("brain/words.dat", "wb")
					s = self.pack(self.words, self.settings.version, True)
					f.write(s)
					f.close()
					del s
					if self.settings.debug == 1:
						self.barf('DBG', "Words converted.")
						self.barf('DBG', "Reading lines...")
					f = open("brain/lines.dat", "rb")
					s = f.read()
					f.close()
					self.lines = self.unpack(s, v)
					if self.settings.optimum == 1:
						if self.settings.debug == 1:
							self.barf('DBG', "Applying filter to adjust to new brain system.")
							self.barf('TAB', "This may take a bit, and will shrink the dataset.")
						try:
							self.auto_rebuild()
						except:
							self.barf('ERR', 'Brain failed to migrate.')
					f = open("brain/lines.dat", "wb")
					s = self.pack(self.lines, self.settings.version, True)
					f.write(s)
					f.close()
					del s
					if self.settings.debug == 1:
						self.barf('DBG', "Lines converted.")
					f = open("brain/version", "wb")
					f.write(self.settings.version)
					f.close()
					if self.settings.debug == 1:
						self.barf('DBG', "Version updated.")
					v = self.settings.version
					self.barf('ACT', "Brain converted successfully! Continuing.")
				else:
					self.settings.version = v # Saves old brain as old brain format.

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
		self.stats['num_words'] = len(self.words)
		num_contexts = 0
		# Get number of contexts
		for x in self.lines.keys():
			num_contexts += len(self.lines[x][0].split())
		self.stats['num_contexts'] = num_contexts
		self.barf('ACT', "%s words and %s contexts loaded" % ( self.stats['num_words'], self.stats['num_contexts'] ))
		
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
								#self.replace(x, z)

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

		#self.settings.save()

	def save_all(self, interface, restart_timer=True):
		"""
		Save ALL THE THINGS Should be moved to private _save()
		"""
		self.barf('SAV', "Writing to my brain...")

		f = open("brain/words.dat", "wb")
		s = self.pack(self.words, self.settings.version)
		f.write(s)
		f.close()
		if self.settings.debug == 1:
			self.barf('DBG', "Words saved.")
		f = open("brain/lines.dat", "wb")
		s = self.pack(self.lines, self.settings.version)
		f.write(s)
		f.close()
		if self.settings.debug == 1:
			self.barf('DBG', "Lines saved.")

		#zip the files
		f = zipfile.ZipFile('brain/cortex.zip', 'w', zipfile.ZIP_DEFLATED)
		f.write('brain/words.dat')
		if self.settings.debug == 1:
			self.barf('DBG', "Words zipped")
		os.remove('brain/words.dat')
		f.write('brain/lines.dat')
		if self.settings.debug == 1:
			self.barf('DBG', "Lines zipped")
		try:
			f.write('brain/version')
			f.close()
			if self.settings.debug == 1:
				self.barf('DBG', "Version zipped")
			os.remove('brain/version')
		except:
			v = open("brain/version", "w")
			v.write(self.settings.version)
			v.close()
			f.write("brain/version")
			if self.settings.debug == 1:
				self.barf('DBG', "Version written and zipped.")
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
		wordlist.sort(lambda x, y: cmp(x[1], y[1]))
		map((lambda x: f.write(str(x[0]) + "\n\r") ), wordlist)
		f.close()
		if self.settings.debug == 1:
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
		if self.settings.debug == 1:
			self.barf('DBG', "Sentences written.")

		# Save settings
		self.settings.save()

		if interface != False:
			interface.settings.save()

		self.barf('SAV', "Brain saved.")

		if restart_timer is True:
			self.autosave = threading.Timer(self.to_sec("125m"), self.save_all)
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

			num_w = self.stats['num_words']
			if num_w != 0:
				num_cpw = self.stats['num_contexts'] / float(num_w) # contexts per word
			else:
				num_cpw = 0

			cleanbody = " ".join(words)

			hashval = hashlib.sha1(cleanbody).hexdigest()[:10]
			if not (num_cpw > 100 and self.settings.learning == 0)and not self.lines.has_key(hashval) :
				self.lines[hashval] = [cleanbody, num_context]
				# Add link for each word
				if self.settings.debug == 1:
					self.barf('DBG', 'hash %s added' % ( hashval ))
				for x in xrange(0, len(words)):
					if self.words.has_key(words[x]):
						self.words[words[x]].append([hashval, x])
					else:
						self.words[words[x]] = [hashval, x]
						self.stats['num_words'] += 1
					self.stats['num_contexts'] += 1
			else:
				self.lines[hashval][1] += num_context

			#is max_words reached, don't learn more
			if self.stats['num_words'] >= self.stats['max_words']:
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
			old_num_words = self.stats['num_words']
			old_num_contexts = self.stats['num_contexts']

			self.words = {}
			self.lines = {}
			self.stats['num_words'] = 0
			self.stats['num_contexts'] = 0

			for k in old_lines.keys():
				filtered_line = self.clean.line(old_lines[k][0])
				self.learn(filtered_line, old_lines[k][1])
			msg = "Rebuilt brain in %0.2fs. Words %d (%+d), contexts %d (%+d)." % \
				  (time.time() - t,
				   old_num_words,
				   self.stats['num_words'] - old_num_words,
				   old_num_contexts,
				   self.stats['num_contexts'] - old_num_contexts)

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

	def to_sec(self, s):
		seconds_per_unit = {"s": 1, "m": 60, "h": 3600, "d": 86400, "w": 604800}
		return int(s[:-1]) * seconds_per_unit[s[-1]]

	def kill_timers(self):
		self.autosave.cancel()
		self.autorebuild.cancel()
