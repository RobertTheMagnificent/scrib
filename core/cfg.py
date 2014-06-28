# -*- coding: utf-8 -*-
#
# scrib config file manager
import json
import string
import time

import barf

def _load_config(filename):
	try:
		f = open(filename, 'r')
	except IOError, e:
		return None

	config = json.load(f)
	f.close()

	barf.Barf('MSG', filename + ' successfully loaded.')

	return config
		
def _save_config(filename, fields):
	"""
	This saves a dictionary to json
	"""
	f = ''
	with open(filename, 'w+') as out:
		f = f+str(json.dump(fields, out, indent=4))
	barf.Barf('SAV', filename + ' successfully saved.')

class set:

	def load(self, filename, defaults):
		"""
		Load scrib settings.
		"""
		self._defaults = defaults
		self._filename = filename

		# try to load saved ones
		vars = _load_config(filename)
		if vars == None:
			# none found. this is new
			vars = self._defaults
			self.save()
			self.load(filename, self._defaults)
			return
		for i in vars.keys():
			self.__dict__[i] = vars[i]
		self._defaults = vars

	def save(self):
		"""
		Save scrib settings
		"""
		
		_save_config(self._filename, self._defaults)

