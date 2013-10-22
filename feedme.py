#!/usr/bin/env python
#
# I eat ASCII

import string
import sys

sys.path.append('core')
import scrib

class ModFileIn:
	"""
	I learn from ASCII files!
	"""

	# Command list for this module
	commandlist = "FileIn Module Commands:\nNone"
	commanddict = {}
	
	def __init__(self, Borg, args):

		f = open(args[1], "r")
		buffer = f.read()
		f.close()

		print "I knew "+`Borg.settings.num_words`+" words ("+`len(Borg.lines)`+" lines) before reading "+sys.argv[1]
		buffer = scrib.filter_message(buffer, Borg)
		# Learn from input
		try:
			print buffer
			Borg.learn(buffer)
		except KeyboardInterrupt, e:
			# Close database cleanly
			print "Premature termination :-("
		print "I know "+`Borg.settings.num_words`+" words ("+`len(Borg.lines)`+" lines) now."
		del Borg

	def shutdown(self):
		pass

	def start(self):
		sys.exit()

	def output(self, message, args):
		pass

if __name__ == "__main__":
	if len(sys.argv) < 2:
		print "Specify a filename."
		sys.exit()
	# start the scrib
	my_scrib = scrib.scrib()
	ModFileIn(my_scrib, sys.argv)
	my_scrib.save_all()
	del my_scrib

