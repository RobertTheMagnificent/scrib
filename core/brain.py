#!/usr/bin/env python
# -*- coding: utf-8 -*-

import scrib

class brain:

	def __init__(self):
		# This is where we set internal versioning.
		self.version = '0.1.4'
		self.cfg = scrib.cfg
		self.settings = self.cfg.set()
		#self.brain_dir = os.path.abspath(os.path.dirname(__file__ )) + "/brains/"
		
		self.settings.load("conf/brain.cfg", {
								'debug': 0,
								'version': self.version,
							})
