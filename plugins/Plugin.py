#! /usr/bin/env python
# -*- coding: utf-8 -*-
from plugins import PluginManager

def sendMessage( event, text, scrib, c ):
	if Plugin.process_table[event] != '':
		return Plugin.process_table[event].action(text, scrib, c)
	else:
		return ''

def reloadPlugin( event ):
	if Plugin.process_table[event] != '':
		reload(event)
		return "Reloaded %s" % event
	else:
		return 'Reloading error'
