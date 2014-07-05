#!/usr/bin/env python
# -*- coding: utf-8 -*-
import barf
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
	Setting up gatekeeping.
	"""
	def __init__(self):
		"""
		Here we'll load settings and set up modules.
		"""
		self.barf = barf.Barf
		self.process = process.process()
		self.debug = self.getsetting('brain', 'debug')		

		self.barf('MSG', 'Scrib %s initialized' % self.process.version)

	
	"""
	Down here, we are making some methods that give interfaces and plugins
	information in a controllable (and updatable) way.
	"""
	
	def setcfg(self):
		"""
		Simple wrapper for cfg.set()
		"""
		return self.process.cfg.set()

	def save_all(self, interface, restart_timer=True):
		self.savesettings()
		self.process.brain.__save(interface, restart_timer)

	def shutdown(self, interface):
		"""
		Shuts us the scrib down.
		"""
		self.__save()
		return self.process.brain.shutdown(interface)

	def setsetting(self, module, setting, set):
		"""
		Set brain setting.
		"""
		try:
			if module == 'scrib':
				mod = self.process.settings
			elif module == 'brain':
				mod = self.process.brain.settings
			setattr(mod, setting, set)
		except AttributeError:
			self.barf('ERR', 'No %s setting in %s' % ( setting, module ))

	def getsetting(self, module, setting):
		"""
		Get brain setting.
		"""
		try:
			if module == 'scrib':
				return getattr(self.process.settings, setting)
			elif module == 'brain':
				return getattr(self.process.brain.settings, setting)
		except AttributeError:
			self.barf('ERR', 'No %s setting in %s' % ( setting, module ))
	
	def __save(self):
		if self.debug == 1:
			self.barf('DBG', 'Saving process settings.')
		self.process.settings.save()