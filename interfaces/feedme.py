#!/usr/bin/env python
#
# I eat ASCII

import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from core import scrib

class ModFileIn:
	"""
	I learn from ASCII files!
	"""
	def __init__(self, scrib):
		self.barf = scrib.barf
		self.barf('MSG', 'Where is the food located?')
		self.food = raw_input("location: ")

		correct = False
		while correct == False:
			try:		
				f = open(self.food, "r")
			except IOError:
				self.barf('ERR', 'That file does not exist.')
			correct = True
		
		noms = f.read()
		f.close()

		if scrib.debug == 1:
			self.barf('DBG', "scrib: %s; brain: %s" % ( scrib.settings.version, scrib.brain.settings.version ))
		before = "I knew "+`scrib.brain.stats['num_words']`+" words ("+`len(scrib.brain.lines)`+" lines) before reading '%s'" % self.food
		noms = scrib.brain.clean.line(noms)
		# Learn from input
		try:
			self.barf('MSG', noms)
			scrib.brain.learn(noms)
		except KeyboardInterrupt, e:
			# Close database cleanly
			self.barf('ERR', "Early termination.")
		after = "I know "+`scrib.brain.stats['num_words']`+" words ("+`len(scrib.brain.lines)`+" lines) now."
		del scrib
		
		self.barf('ACT', before)
		self.barf('ACT', after)

if __name__ == "__main__":
	my_scrib = scrib.scrib()
	ModFileIn(my_scrib)
	my_scrib.shutdown(my_scrib)
	del my_scrib
