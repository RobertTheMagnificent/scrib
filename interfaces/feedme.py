#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from core import scrib

class ModFileIn:
	"""
	I learn from ASCII files!
	"""
	def __init__(self, scrib):
		self.scrib = scrib
		self.scrib.barf('MSG', 'Where is the food located?')
		self.food = raw_input("location: ")

		correct = False
		while correct == False:
			try:		
				f = open(self.food, "r")
			except IOError:
				self.scrib.barf('ERR', 'That file does not exist.')
			correct = True
		
		noms = f.read()
		f.close()

		if scrib.debug == 1:
			self.scrib.barf('DBG', "scrib: %s; brain: %s" % ( self.scrib.getsetting('scrib', 'version'), self.scrib.process.brain.version))
		before = "I knew "+`self.scrib.getsetting('brain', 'num_words')`+" words ("+`len(scrib.process.brain.lines)`+" lines) before reading '%s'" % self.food
		noms = scrib.process.brain.clean.line(noms, self.scrib.process.brain.settings)
		# Learn from input
		try:
			self.scrib.barf('MSG', noms)
			scrib.process.brain.learn(noms)
		except KeyboardInterrupt, e:
			# Close database cleanly
			self.scrib.barf('ERR', "Early termination.")
		after = "I know "+`self.scrib.getsetting('brain', 'num_words')`+" words ("+`len(scrib.process.brain.lines)`+" lines) now."
		del scrib
		
		self.scrib.barf('ACT', before)
		self.scrib.barf('ACT', after)

if __name__ == "__main__":
	my_scrib = scrib.scrib()
	ModFileIn(my_scrib)
	my_scrib.shutdown(my_scrib)
	del my_scrib
