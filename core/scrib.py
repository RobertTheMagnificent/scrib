#!/usr/bin/env python
# -*- coding: utf-8 -*-
import barf
import cfg
import process

"""
	So, the plan here is to do checks (configuration, plugin, brain sanity)
	since we do virtually NONE of that. We just blindly run and crash.
	It sucks. :( This is where we'll do more sane importing too, so we aren't
	importing the same files over and over again. 
	
	This is where we will also expose internals for plugins to use.
	
	- cptmashek, 20140701
"""

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
			'reply_rate': 100,
			'nick_reply_rate': 100,
			'version': self.version
			})
		
		self.process = process.process()
		
		self.barf('MSG', 'Scrib %s initialized' % self.version)

	
	def shutdown(self, interface):
		return self.process.brain.shutdown(interface)

	def getsymbol(self):
		return self.process.brain.settings.symbol