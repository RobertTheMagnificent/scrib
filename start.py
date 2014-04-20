#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os

if __name__ == "__main__":

	def help():
		print "Scrib bot. Usage:"
		print "\tstart.py [options]"
		print "\t--irc (connection info stored in conf/scrib-irc.cfg"
		print "\t--feedme [filename] (text file to process)"
		print "\n"
		sys.exit(0)

	def dirCheck():
		if not os.path.exists("conf"):
			os.makedirs("conf")
		
	if "--help" in sys.argv:
		help()

	if "--irc" in sys.argv:
		dirCheck()
		if os.path.isfile(os.path.join("interfaces", "scrib_irc.py")):
			os.system(os.path.join("interfaces", "scrib_irc.py"))
		else:
			print "No IRC interface. Exiting."
		sys.exit(0)

	if "--feedme" in sys.argv:
		dirCheck()
		if sys.argv[2]:
			if os.path.isfile(os.path.join("interfaces", "feedme.py")):
				os.system(os.path.join("interfaces", "feedme.py" %s) % sys.argv[2])
		sys.exit(0)

	else:
		dirCheck()
		os.system(os.path.join("interfaces","default.py"))
		print os.name
		sys.exit(0)
