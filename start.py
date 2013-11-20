#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

if __name__ == "__main__":

	def help():
		print "Scrib bot. Usage:"
		print "\tstart.py [options]"
		print "\t--irc (connection info stored in conf/scrib-irc.cfg\n"
		sys.exit(0)

	if "--help" in sys.argv:
		help()
	
	if "--irc" in sys.argv:
		if os.path.isfile("interfaces/scrib_irc.py"):
			os.system("interfaces/scrib_irc.py")
		else:
			print "No IRC interface. Exiting."
			exit(0)
	else:
		help()