#! /usr/bin/env python
# -*- coding: utf-8 -*-
import getopt
import sys
import os

from core import barf
from core import cfg	

interface_dir = os.path.abspath(os.path.dirname(__file__ )) + "/interfaces/"
interface_list = []
def register_interfaces():
	for interface in os.listdir(os.path.dirname(interface_dir)):
		if os.path.isfile(interface_dir + "/" + interface):
			interface_name, ext = os.path.splitext(interface)
		
			if ext == '.py' and interface_name != '__init__':
				try:
					barf.Barf('PLG', 'Registered interface:           \033[1m%s' % interface_name)
					interface_list.append(interface_name)

				except ImportError as e:
					barf.Barf('ERR', "Failed to register interface ( IE ):   \033[1m%s" % interface_name)
					barf.Barf('TAB', e)

				except NameError as e:
					barf.Barf('ERR', "Failed to register interface ( NE ):   \033[1m%s" % interface_name)
					barf.Barf('TAB', e)

	return interface_list

core_interfaces = ['help'] # This should populate with all available interfaces.
registered_interfaces = register_interfaces()
interfaces = core_interfaces + registered_interfaces

def usage():
	barf.Barf('DEF', 'scrib bot. Usage:', False)
	barf.Barf('TAB', 'start.py [interface]', False)
	sys.exit(0)

def load(interface):
	barf.Barf("MSG", "Loading scrib...")
	os.system(os.path.join('interfaces',interface+'.py'))
	sys.exit()

def main(argv):
	"""
	Let's get this party started!
	"""

	try:
		opts, args = getopt.getopt(argv, "hg:d", interfaces)
	except getopt.GetoptError:
		barf.Barf('DEF', "That is not a valid argument. Try --help", False)
		sys.exit(2)


if __name__ == "__main__":
	def dirCheck(thisdir):
		if not os.path.exists(thisdir):
			os.makedirs(thisdir)
		
	dirCheck('conf')
	if len(sys.argv) > 1:
		if sys.argv[1] in interfaces:
			load(sys.argv[1])
	else:
		load('default')

