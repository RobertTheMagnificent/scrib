#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
import os
import fileinput
import re
import time

import barf
import brain
import cfg
import process

class scrib:
	"""
	The meat of scrib
	"""
	def __init__(self):
		"""
		Here we'll load settings and set up modules.
		"""
		self.version = "1.2.0"
		self.barf = barf.Barf
		self.brain = brain.brain()
		self.process = process.process()
		self.cfg = cfg
		self.settings = self.cfg.set()
		self.settings.load("conf/scrib.cfg",{
							"name": "scrib",
							"symbol": "!",
							"reply_rate": 100,
							"nick_reply_rate": 100,
							"debug": 0,
							"muted": 0,
							"version": self.version
							})
