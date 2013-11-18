#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import setup

def test():
	test_setup()

def test_setup():
	assert setup.name == "scrib"
