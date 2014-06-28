#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager
import os

# User command
command = "fortune"

# Plugin Action
class EchoPlugin(PluginManager.Load):
	def action(self, cmds, scrib, c):
		if scrib.scrib.settings.debug == 1:
			PluginManager.barf(PluginManager.DBG, "Fortune Plugin activated.")
		if cmds[0] == command and len(cmds) >= 1:
			msg = "".join([i for i in os.popen('fortune').readlines()]).replace('\n\n','\n').replace('\n', ' ')
			msg = self.filter(msg)

PluginManager.addPlugin( command, EchoPlugin() )
