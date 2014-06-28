#!/usr/bin/env python

from setuptools import setup

settings = cfg.set()

long_description = open('README.md', 'r').read()

setup(
	name="scrib",
	version=settings.version,
	packages=['scrib',],
	package_data={'scrib': ['*.py'],},
	author="Sina Mashek, Tristy Hopkins",
	author_email="mashek@thescoundrels.net",
	long_description=long_description,
	description="learning bot",
	license="MIT",
	url="http://scoundrels.github.io/scrib",
	platforms=['any'],
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Topic :: Artificial Intelligence",
		"Licese :: OSI Approvied :: MIT License",
	],
)

