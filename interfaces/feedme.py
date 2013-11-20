#!/usr/bin/env python
#
# I eat ASCII

import sys
import os

sys.path.append(os.path.abspath(os.path.dirname(__file__) + '/../'))

from core import barf
from core import scrib

class ModFileIn:
	"""
	I learn from ASCII files!
	"""

	# Command list for this module
	commandlist = "FileIn Module Commands:\nNone"
	commanddict = {}
	
	def __init__(self, Scrib, args):

		f = open(args[1], "r")
		buffer = f.read()
		f.close()

		if Scrib.debug == 1:
			barf.barf(barf.DBG, "Scrib: %s" % Scrib.settings)
		before = "I knew "+`Scrib.brainstats.num_words`+" words ("+`len(Scrib.lines)`+" lines) before reading "+sys.argv[1]
		buffer = Scrib.filter_message(buffer)
		# Learn from input
		try:
			barf.barf(barf.MSG, buffer)
			Scrib.learn(buffer)
		except KeyboardInterrupt, e:
			# Close database cleanly
			barf.barf(barf.ERR, "Early termination.")
		after = "I know "+`Scrib.brainstats.num_words`+" words ("+`len(Scrib.lines)`+" lines) now."
		del Scrib
		
		barf.barf(barf.ACT, before)
		barf.barf(barf.ACT, after)

	def shutdown(self):
		pass

	def start(self):
		sys.exit()

	def output(self, message, args):
		pass

if __name__ == "__main__":
	if len(sys.argv) < 2:
		barf.barf(barf.ERR, "Please specify a filename.")
		sys.exit()
	# start the scrib
	my_scrib = scrib.scrib()
	ModFileIn(my_scrib, sys.argv)
	my_scrib.save_all(False)
	del my_scrib
