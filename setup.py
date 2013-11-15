#!/usr/bin/env python

from setuptools import setup

long_description = open('README.md', 'r').read()

setup(
	name="scrib",
	version="0.7.4",
	packages=['scrib',],
	package_data={'scrib': ['*.py'],},
	author="Sina Mashek",
	author_email="mashek@thescoundrels.net",
	long_description=long_description,
	description="learning bot"
	license="GPLv2",
	url="http://scoundrels.github.io/scrib",
	platforms=['any']
)
