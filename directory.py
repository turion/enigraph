#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree.directory"""

import enigtree
import os

class DirNode(enigtree.Node):
	"""An active enigtree.Node that represents a directory tree. Has init_data as a hook for handling the actual data."""
	_dir = ''
	def __init__(self, path, *args, **kwargs):
		self._isdir = None
		self._isfile = None
		self.path = path
		enigtree.Node.__init__(self, data=self.init_data(*args, **kwargs), *args, **kwargs)
		self._childs_done = False
	def init_data(self, *args, **kwargs):
		"""Inherit this method to change the data according to what you want it to do"""
		return self.path
	@property
	def path(self):
		return self._path
	@path.setter
	def path(self, path):
		if os.path.isdir(path) or os.path.isfile(path):
			self._path = path
		else:
			raise ValueError('Not a valid path: ' + str(path))
	@property
	def isfile(self):
		if self._isfile == None:
			self._isfile = os.path.isfile(self.path)
		return self._isfile
	@property
	def isdir(self):
		if self._isdir == None:
			self._isdir = os.path.isdir(self.path)
		return self._isdir
	@property
	def childs(self):
		"""Returns all subdirectories and scans the first time. Maybe this behaviour will be changed one day to increase performance and functionality. Right now this crashes if you inherit __init__ with different required arguments."""
		if not self._childs_done:
			self_type = type(self)
			if self.isdir:
				self._childs = [self_type(os.path.join(self.path, child_path), parent=self) for child_path in os.listdir(self.path) if self.child_accepted(child_path)] # Hopefully ensures that the children will be instances of the same class, if inherited
			else:
				self._childs = []
			self.sort_childs()
			self._childs_done = True
		return self._childs
	def child_accepted(self, child_path):
		"""Here it is possible to perform tests on the file specified by child allow only special files/directories"""
		return True
	def sort_childs(self):
		"""Here you can implement future sorting algorithms which are performed at each directory scan."""
		pass
