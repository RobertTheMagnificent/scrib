#!/usr/bin/env python

from core import cfgfile
from setuptools import setup

settings = cfgfile.cfgset()
settings.load('VERSION', 
		{'brain': ('Brain version', ''), 
		'core': ('Core version', '')
		})

long_description = open('README.md', 'r').read()

setup(
	name="scrib",
	version=settings.core,
	packages=['scrib',],
	package_data={'scrib': ['*.py'],},
	author="Sina Mashek",
	author_email="mashek@thescoundrels.net",
	long_description=long_description,
	description="learning bot",
	license="GPLv2",
	url="http://scoundrels.github.io/scrib",
	platforms=['any']
)
