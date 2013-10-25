#! /usr/bin/env python
# -*- coding: utf-8 -*-
import sys

# See scrib.py
sys.path.append('core/')
sys.path.append('plugins/')

import os
import scrib
import cfgfile
import PluginManager
import random
import traceback

from scribirc import ModIRC
from chat import ModLineIn

import threading
from threading import Thread

class scribtalk:
		"""
		Let's interface Scrib with ALL OF THE modules!
		"""
		# Command list for this module
		commandlist = "LineIn Module Commands:\n!quit"
		commanddict = { "quit": "Usage: !quit\nQuits Scrib and saves the dictionary" }

		def __init__(self, my_scrib):
				self.scrib = my_scrib
				self.start()

def scribirc():
	bot.our_start()

def scribterm():
	ModLineIn(my_scrib)

if __name__ == "__main__":
	
	if "--help" in sys.argv:
		print "Scrib bot. Usage:"
		print " start.py [options]"
		print " -s   server:port"
		print " -c   channel"
		print " -n   nickname"
		print "Defaults stored in scrib-irc.cfg"
		print
		sys.exit(0)
	# start the scrib
	my_scrib = scrib.scrib()
	bot = ModIRC(my_scrib, sys.argv)
	try:
		Thread(target = scribirc).start()
		Thread(target = scribterm).start()
	except KeyboardInterrupt, e:
		pass
	except SystemExit, e:
		pass
	except:
		traceback.print_exc()
		c = raw_input("\033[94m"+scrib.get_time()+" \033[91m[!] Oh no, I've crashed! Would you like to save my brain? (yes/no)\033[0m")
		if c[:1] == 'n':
			sys.exit(0)
	bot.disconnect(bot.settings.quitmsg)
	my_scrib.save_all()
	del my_scrib

