#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Threatnought"""

import threading
import enigtree

class ThreadNode(enigtree.Node):
	def __init__(self, *args, timeout = None, **kwargs):
		self.thread = threading.Thread(target = self.set_data)
		self.timeout = timeout
	def set_data(self):
		self._data = None
	@property
	def data(self):
		try:
			self._data
		except AttributeError:
			self.thread.join(self.timeout)
			if self.thread.isAlive():
				raise RuntimeError("Thread " + repr(self.thread) + " of " + repr(self) + " timed out after " + str(self.timeout) + " seconds."
		return self._data
	@data.setter
	def data(self, data):
		self._data = data
	
# Damit noch was machen, was ein ähnliches Verhalten bei childs zeigt
