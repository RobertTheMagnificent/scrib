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
		self.barf = barf.Barf
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

	"""
	So, the plan here is to do checks (configuration, plugin, brain sanity)
	here, since we do virtually NONE of that. We just blindly run and crash.
	It sucks. :( This is where we'll do more sane importing too, so we aren't
	importing the same files over and over again. 
	
	For example, you will know (as of this note) that the brain loads twice
	and some of the config files load 3-4 times each. This is very bad and
	has led to some undesirable results. For testing purposes, however,
	it isn't breaking anything (famous last words amirite).
	
	You'll probably hate me for it but I am doing it to slim down the memory
	footprint and keep things far more consistent. - cptmashek, 20140701
	"""