#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree.fsnode"""

import enigtree
from . import contextmanagers

import os
import os.path

import shutil

import time

import threading



class EnigtreeDirectoryError(enigtree.EnigtreeValueError):
	pass

class EnigtreeNotADirectory(EnigtreeDirectoryError):
	pass

class EnigtreeExists(EnigtreeDirectoryError):
	pass

class EnigtreeInvalidPath(EnigtreeDirectoryError):
	pass

#timeoutcached is not very clever to use since it can lead to inconsistencies
#better use libnotify and/or detect time of last modification
class TimeoutCached:
	def __init__(self, function, timeout=0.01):
		self.timeout = timeout
		self.function = function
		self.last_call = time.time() - timeout - 1 # ensure cache is filled at the beginning
		self.cache = None
	def __call__(self, self2): #FIXME: self2 is needed because I'm decorating methods. There must be a better way.
		if time.time() - self.last_call > self.timeout:
			self.cache = self.function(self2)
			self.last_call = time.time()
		return self.cache

def timeout_cached(function_or_timeout):
	if callable(function_or_timeout):
		#return TimeoutCached(function_or_timeout)
		return function_or_timeout
	else:
		def instantiate_TimeoutCached(function):
			#return TimeoutCached(function, timeout=function_or_timeout)
			return function
		return instantiate_TimeoutCached

expandpath = lambda path: os.path.normpath(os.path.expandvars(os.path.expanduser(path)))

class DebugCM:
	def __enter__(self):
		pass
	def __exit__(self, *args):
		return False

class FSNode(enigtree.BaseNode): # TODO: threadsafety only works if the locks aquire all the locks of the parents
	def __init__(self, path, new=False, new_fail_if_exists=True, parent=None):
		super().__init__()
		self.lock = threading.RLock()
		self.locks = lambda: contextmanagers.iter_nested((node.lock for node in self.ancestors(return_self=True)))
		#self.locks = DebugCM()
		path = expandpath(path)
		name = os.path.split(path)[1]
		if parent:
			if os.path.isabs(path):
				raise enigtree.EnigtreeValueError("If appending to an existing parent, path must be relative")
			path = os.path.join(parent.path, path)
			self._parent = parent
		elif os.path.split(path)[0] == path: # reached the root of the filesystem
			self._parent = None
			name = path
		else:
			self._parent = type(self)(os.path.split(path)[0], new=new, new_fail_if_exists=False)
		if new:
			if os.path.exists(path):
				if new_fail_if_exists:
					raise EnigtreeExists(self)
			else:
				if new in ("directory", "dir"):
					os.mkdir(path)
				elif new == "file":
					with open(path, "w"):
						pass
				elif callable(new):
					new(path)
			if not os.path.exists(path):
				raise EnigtreeInitialisationError("Couldn't create new file at {} with recipe {}".format(self.path, new))
		with self.lock:
			self._name = name
	@property
	def path(self):
		try:
			return os.path.join(self.parent.path, self.name)
		except enigtree.EnigtreeNoParent:
			return self.name
	@property
	def name(self):
		return self._name
	@name.setter
	def name(self, name):
		if os.path.split(name)[0]:
			raise EnigtreeInvalidPath("Can't set name to {}, since it is compound")
		with self.locks():
			old_name = self._name
			old_path = self.path
			self._name = name
			try:
				os.rename(old_path, self.path)
			except OSError:
				self._name = old_name
	@property
	def isdir(self):
		return os.path.isdir(self.path)
	@property
	def isfile(self):
		return os.path.isfile(self.path)
	@property
	def exists(self):
		return os.path.exists(self.path)
	
	def _get_parent(self):
		return self._parent
	def _get_children(self):
		with self.locks():
			if self.isdir:
				return (type(self)(os.path.join(self.path, child_path)) for child_path in os.listdir(self.path))
			elif self.exists: # rather perform the test a few times too often, the file might have been deleted in the meantime
				return ()
			else:
				raise EnigtreeInvalidPath(self)
	def _set_parent(self, parent):
		with self.locks(), parent.locks(): # If this deadlocks because parent in self.ancestors(), I didn't understand RLocks
			if not parent.exists:
				raise EnigtreeInvalidPath(parent)
			elif not parent.isdir:
				raise EnigtreeNotADirectoryError(parent)
			else:
				shutil.move(self.path, parent.path)
				self._parent = parent
	def __str__(self):
		return self.name
	def __eq__(self, other):
		return isinstance(other, FSNode) and os.path.samefile(self.path, other.path)
	def delete(self): # TODO: That shouldn't stay like that, it produces inconsistencies
		with self.locks():
			if self.isdir:
				shutil.rmtree(self.path)
			else:
				os.remove(self.path)


def test():
	try:
		test = FSNode("~/et/enigtreetest", new="directory")
		test == None
		print(test.path)
		print("ancestors:")
		for node in test.ancestors():
			print(node)
		child = FSNode("bla", new="file", parent=test)
		test2 = FSNode(os.path.expanduser("~/et/enigtreetest2"), new="directory")
		test.parent = test2
		child.parent = test2
		for sub in test2.progeny(method="depth", formatter = enigtree.progeny.PrettyFormatter(), return_root=True):
			print(sub)
		for p in child.ancestors(True):
			print(p)
	finally:
		for cleanup_path in map(os.path.expanduser, ("~/et/enigtreetest", "~/et/enigtreetest2")):
			try:
				shutil.rmtree(cleanup_path)
			except OSError:
				pass
	
