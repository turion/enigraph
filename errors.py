#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree.errors"""

class EnigtreeException(Exception):
	pass

class EnigtreeReadOnlyError(EnigtreeException)):
	pass
