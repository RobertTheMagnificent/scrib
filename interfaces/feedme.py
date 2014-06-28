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

	# Command list for this module
	commandlist = "FileIn Module Commands:\nNone"
	commanddict = {}
	
	def __init__(self, scrib, args):

		f = open(args[1], "r")
		buffer = f.read()
		f.close()

		if scrib.debug == 1:
			scrib.barf('DBG', "scrib: %s" % scrib.settings)
		before = "I knew "+`scrib.brainstats.num_words`+" words ("+`len(scrib.lines)`+" lines) before reading "+sys.argv[1]
		buffer = scrib.filter_message(buffer)
		# Learn from input
		try:
			scrib.barf(barf.MSG, buffer)
			scrib.learn(buffer)
		except KeyboardInterrupt, e:
			# Close database cleanly
			scrib.barf('ERR', "Early termination.")
		after = "I know "+`scrib.brainstats.num_words`+" words ("+`len(scrib.lines)`+" lines) now."
		del scrib
		
		scrib.barf('ACT', before)
		scrib.barf('ACT', after)

	def shutdown(self):
		pass

	def start(self):
		sys.exit()

	def output(self, message, args):
		pass

if __name__ == "__main__":
	if len(sys.argv) < 2:
		scrib.barf('ERR', "Please specify a filename.")
		sys.exit()
	# start the scrib
	my_scrib = scrib.scrib()
	ModFileIn(my_scrib, sys.argv)
	my_scrib.save_all(False)
	del my_scrib
