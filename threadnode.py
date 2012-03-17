#! /usr/bin/python
# -*- coding: utf-8 -*-

"""Threatnought
Kann man sicher mit Dekoratoren direkt an den Funktionen besser bewerkstelligen"""

import threading
import enigraph

class ThreadNode(enigtree.Node):
	def __init__(self, timeout = None):
		self.thread = threading.Thread(target = self.set_data)
		self.timeout = timeout
		self.thread.start()
	def set_data(self):
		self._data = None
	@property
	def data(self):
		try:
			self._data
		except AttributeError:
			self.thread.join(self.timeout)
			if self.thread.is_alive():
				raise RuntimeError("Thread {self.thread} of {self} timed out after {self.timeout} seconds.".format(self=self))
		return self._data
	@data.setter
	def data(self, data):
		self._data = data
	
# Damit noch was machen, was ein ähnliches Verhalten bei childs zeigt
