#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigraph.errors"""

class EnigraphException(Exception):
	pass

class EnigraphValueError(EnigraphException, ValueError):
	pass

class EnigraphReadOnlyError(EnigraphValueError):
	pass

class EnigraphInitialisationError(EnigraphValueError):
	pass

class EnigraphNoParent(EnigraphValueError):
	pass
