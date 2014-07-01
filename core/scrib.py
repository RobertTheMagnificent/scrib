#!/usr/bin/env python
# -*- coding: utf-8 -*-
import barf
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
		self.version = '1.2.0'
		self.barf = barf.Barf
		self.cfg = cfg
		self.settings = cfg.set()
		
		# Load scrib config (or create with these defaults).
		self.settings.load('conf/scrib.cfg', {
			'name': 'scrib',
			'debug': 0,
			'muted': 0,
			'version': self.version
			})
		
		self.process = process.process()
		
		self.barf('ACT', 'scrib initialized')

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