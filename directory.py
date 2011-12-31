#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree.directory"""

#import enigtree
import os

import time
class TimeoutCached:
	def __init__(self, function, timeout=1):
		self.timeout = timeout
		self.function = function
		self.last_call = time.time() - timeout - 1
		self.cache = None
	def __call__(self, *args, **kwargs):
		if time.time() - self.last_call > self.timeout:
			self.cache = self.function(*args, **kwargs)
			self.last_call = time.time()
		return self.cache

def timeout_cached(function_or_timeout):
	try:
		function_or_timeout.__call__
	except AttributeError:
		def instantiate_TimeoutCached(function):
			return TimeoutCached(function, timeout=function_or_timeout)
		return instantiate_TimeoutCached
	else:
		return TimeoutCached(function_or_timeout)

class OldDirNode:#(enigtree.Node):
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
		"""Here it is possible to perform tests on the file specified by child allow only special files/directories.
		Until now, it excludes hidden directories and symbolic links."""
		return not (child_path[0] == "." or os.path.islink(os.path.join(self.path, child_path)))
	def sort_childs(self):
		"""Here you can implement future sorting algorithms which are performed at each directory scan."""
		pass
	def adopt(self, node, *args, **kwargs):
		if not self.isdir:
			raise ValueError("Only DirNodes pointing to directories can contain other DirNodes!")
		try:
			old_parent = node._parent
		except:
			old_parent = None		
		enigtree.Node.adopt(self, node, *args, **kwargs)
		old_path, new_path = node.path, os.path.join(self.path, os.path.basename(node.path))
		if old_path != new_path:
			os.rename(old_path, new_path)
			node.path = new_path
			if old_parent:
				old_parent._childs_done = False
			self._childs_done = False
			self.disinherit(node)

if __name__ == "__main__":
	@timeout_cached(1.3)
	def calc():
		print("calculating me")
		return 2
	while(True):
		input()
		print(calc())
