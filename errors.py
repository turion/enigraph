#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree.errors"""

class EnigtreeException(Exception):
	pass

class EnigtreeValueError(EnigtreeException, ValueError):
	pass

class EnigtreeReadOnlyError(EnigtreeValueError):
	pass

class EnigtreeInitialisationError(EnigtreeValueError):
	pass

class EnigtreeNoParent(EnigtreeValueError):
	pass
