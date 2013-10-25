#! /usr/bin/env python
# -*- coding: utf-8 -*-
import time

def get_time():
	"""
	Make time sexy
	"""
	return time.strftime("\033[0m[%H:%M:%S]", time.localtime(time.time()))

def barf(msg_code, message):
		print get_time() + msg_code + message
