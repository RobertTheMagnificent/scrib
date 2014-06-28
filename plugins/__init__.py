#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os, sys
from core import barf

version = '1.0.1'
barf.Barf('MSG', 'PluginManager version %s' % version)
plugin_dir = os.path.abspath(os.path.dirname(__file__ )) + "/"
sys.path.append(plugin_dir)

for module in os.listdir(os.path.dirname(plugin_dir)):
	if os.path.isfile( plugin_dir + "/" + module ) and module != 'Plugin.py' and module != 'PluginManager.py':
		module_name, ext = os.path.splitext(module)
		library_list = []
		
		if ext == '.py' and module_name != '__init__': # Important, ignore .pyc/other files.
			try:
				module = __import__(module_name)
				barf.Barf('PLG', 'Imported plugin:                \033[1m%s' % module_name)
				library_list.append(module)
			except ImportError as e:
				barf.Barf('ERR', "Failed to load plugin ( IE ):   \033[1m%s" % module_name)
				barf.Barf('TAB', e)

			except NameError as e:
				barf.Barf('ERR', "Failed to load plugin ( NE ):   \033[1m%s" % module_name)
				barf.Barf('TAB', e)
