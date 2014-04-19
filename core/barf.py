#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Barf, a cli message system.
#
# Author: Sina Mashek <mashek@thescoundrels.net>
# Version 1.2
# License: Expat, http://cptmashek.mit-license.org

import datetime
import time

class Barf:
	msg_codes = {
		"DEF": '\033[0m    ',
		"ACT": '\033[93m [~]',
		"MSG": '\033[94m [-]',
		"SAV": '\033[92m [#]',
		"PLG": '\033[35m [*]',
		"DBG": '\033[1;91m [$]',
		"ERR": '\033[91m [!]',
		"ROL": '\033[33m [ ]',
		"TAB": '\t',
	}
	
	def __init__(self, code, message, time=True):
		if "debug = true" or "debug = True" in open('options.cfg').read():
			if code not in self.msg_codes:
				code = "DEF"

			if code == "TAB":
				print self.timeless_barf(code, message)
			else:
				print self.barf(code, message, time)

	def disable(self):
		DEF = ''
		ACT = ''
		MSG = ''
		SAV = ''
		PLG = ''
		DBG = ''
		ERR = ''

	def get_time(self):
		"""
		Make time sexy
		"""
		return time.strftime("[%H:%M:%S] ", time.localtime(time.time()))

	def get_time_for_file(self):
		return "%s-%s" % (datetime.date.today(), time.strftime("%H%M%S",time.localtime(time.time())))

	def barf(self, code, message, time):
		if time == False:
			return self.timeless_barf(code, message)
		else:
			return self.raw_barf(code, message)

	def raw_barf(self, code, message):
		return self.color(code, self.get_time() + message) + self.msg_codes["DEF"]

	def timeless_barf(self, code, message):
		return self.color(code, message) + self.msg_codes["DEF"]

	def color(self, code, message):
		return "%s %s" % (self.msg_codes[code], message)

