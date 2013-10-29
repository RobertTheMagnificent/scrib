import os
import sys
from plugins import ScribPlugin

plugin_dir = os.path.abspath(os.path.dirname(__file__ )) + "/"

sys.path.append(plugin_dir)

for module in os.listdir(os.path.dirname(plugin_dir)):
	if os.path.isfile( plugin_dir + "/" + module ):
		module_name, ext = os.path.splitext(module)
		library_list = []
		if ext == '.py' and module_name != '__init__': # Important, ignore .pyc/other files.
			try:
				module = __import__(module_name)
				ScribPlugin.barf.barf(ScribPlugin.barf.PLG, 'Imported plugin:                \033[1m%s' % module_name)
				library_list.append(module)
			except ImportError as e:
				ScribPlugin.barf.barf(ScribPlugin.barf.ERR, "Failed to load plugin ( IE ):   \033[1m%s" % module_name)
				print e

			except NameError as e:
				ScribPlugin.barf.barf(ScribPlugin.barf.ERR, "Failed to load plugin ( NE ):   \033[1m%s" % module_name)
				print e
