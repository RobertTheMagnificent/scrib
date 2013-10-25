#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

# Message Codes
ACT = '\033[93m [~] '
MSG = '\033[94m [-] '
SAV = '\033[92m [#] '
PLG = '\033[35m [*] '
DBG = '\033[1;91m [$] '
ERR = '\033[91m [!] '

def disable(self):
	ACT = ''
	MSG = ''
	SAV = ''
	PLG = ''
	DBG = ''
	ERR = ''

def get_time():
	"""
	Make time sexy
	"""
	return time.strftime("\033[0m[%H:%M:%S]", time.localtime(time.time()))

def barf(msg_code, message):
		print get_time() + msg_code + message
