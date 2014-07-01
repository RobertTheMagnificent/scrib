#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import fileinput
import re
import time

import barf
import brain
import cfg
import process

class scrib:
	"""
	The meat of scrib
	"""
	def __init__(self):
		"""
		Here we'll load settings and set up modules.
		"""
		self.version = "1.2.0"
		self.barf = barf.Barf # So that we don't have to include it elsewhere.
		self.brain = brain.brain()
		self.process = process.process()
		self.cfg = cfg
		self.settings = self.cfg.set()
		self.settings.load("conf/scrib.cfg",{
							"name": "scrib",
							"symbol": "!",
							"reply_rate": 100,
							"nick_reply_rate": 100,
							"debug": 0,
							"muted": 0,
							"version": self.version
							})


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
		num_pointers = len(pointers)
		print pointers
		for x in pointers:
			l = pointers[0]
			w = pointers[1]

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