#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigraph.fsnode"""

import enigraph
from . import contextmanagers

import os
import os.path

import shutil

import time

import threading



class EnigraphFSError(enigraph.EnigraphValueError):
	pass

class EnigraphNotADirectory(EnigraphFSError):
	pass

class EnigraphExists(EnigraphFSError):
	pass

class EnigraphInvalidPath(EnigraphFSError):
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

class CheckedCachedNode(enigraph.CachedNode):
	def __new__(cls, path):
		instance = super().__new__(path)
		if instance.path != path: # Since path is mutable
			del cls.cache[path]
			instance = super().__new__(path)
		return instance

class BaseFSNode(enigraph.CachedNode): # TODO: threadsafety only works if the locks aquire all the locks of the parents
	def __new__(cls, path, new=False, new_fail_if_exists=True, parent=None):
		path = expandpath(path)
		name = os.path.split(path)[1]
		if parent:
			if os.path.isabs(path):
				raise enigraph.EnigraphValueError("If appending to an existing parent, path must be relative")
			path = os.path.join(parent.path, path)
		instance = super().__new__(cls, path)
		if parent:
			instance._parent = parent
		elif os.path.split(path)[0] == path: # reached the root of the filesystem
			instance._parent = None
			name = path
		else:
			instance._parent = cls(os.path.split(path)[0], new=new, new_fail_if_exists=False)
			instance._parent._add_child_notification(instance)
		if new:
			if os.path.exists(path):
				if new_fail_if_exists:
					raise EnigraphExists(instance)
			else:
				if new in ("directory", "dir"):
					os.mkdir(path)
				elif new == "file":
					with open(path, "w"):
						pass
				elif callable(new):
					new(path)
			if not os.path.exists(path):
				raise EnigraphInitialisationError("Couldn't create new file at {} with recipe {}".format(instance.path, new))
		instance.lock = threading.RLock()
		instance.locks = lambda: contextmanagers.iter_nested((node.lock for node in instance.ancestors(return_self=True)))
		with instance.lock:
			instance._name = name
		return instance
	def __init__(self, path, new=False, new_fail_if_exists=True, parent=None):
		super().__init__()
	@property
	def path(self):
		try:
			return os.path.join(self.parent.path, self.name)
		except enigraph.EnigraphNoParent:
			return self.name
	@property
	def name(self):
		return self._name
	@name.setter
	def name(self, name):
		if os.path.split(name)[0]:
			raise EnigraphInvalidPath("Can't set name to {}, since it is compound")
		with self.locks():
			old_name = self._name
			old_path = self.path
			self._name = name
			try:
				os.rename(old_path, self.path)
			except OSError:
				self._name = old_name
				raise
	@property
	def isdir(self):
		return os.path.isdir(self.path)
	@property
	def isfile(self):
		return os.path.isfile(self.path)
	@property
	def exists(self):
		return os.path.exists(self.path)
	
	def _get_children(self):
		with self.locks():
			if self.isdir:
				return tuple(type(self)(child_name, parent=self) for child_name in os.listdir(self.path))
			elif self.exists: # rather perform the test a few times too often, the file might have been deleted in the meantime
				return ()
			else:
				raise EnigraphInvalidPath(self)

	def _get_parent(self):
		return self._parent

	def _set_parent(self, parent):
		with self.locks(), parent.locks(): # If this deadlocks because parent in self.ancestors(), I didn't understand RLocks
			if not parent.exists:
				raise EnigraphInvalidPath(parent)
			elif not parent.isdir:
				raise EnigraphNotADirectoryError(parent)
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
#TODO: For efficiency, _add_child_notification should save the child

class FSNode(enigraph.CachedChildrenNode, BaseFSNode):
	pass

def test():
	try:
		test = FSNode("~/et/Enigraphtest", new="directory")
		test == None
		print("We have a new node at {}.\nIt's ancestors:".format(test.path))
		for node in test.ancestors():
			print(node)
		
		child = FSNode("bla", new="file", parent=test)
		print("A child: {}".format(child.path))
		print("A lot of nodes are now already in the cache:")
		for path in type(child).cache:
			print(path)
		child2 = FSNode("~/et/Enigraphtest/bla")
		print("Create a child2 with the same path as child. Let's check the value of 'child is child2': {}".format(child is child2))
		child2.name = "blub"
		print("Changed the name of child2 to {}, now child is: {}".format(child2, child))

		test2 = FSNode(os.path.expanduser("~/et/Enigraphtest2"), new="directory")
		test.parent = test2
		child.parent = test2
		print("Let's mess around with the directory. Now it looks like this:")
		for sub in test2.progeny(method="depth", formatter = enigraph.progeny.PrettyFormatter(), return_root=True):
			print(sub)
		print("The ancestry of {}".format(child))
		for p in child.ancestors(True):
			print(p)
	finally:
		for cleanup_path in map(os.path.expanduser, ("~/et/Enigraphtest", "~/et/Enigraphtest2")):
			try:
				shutil.rmtree(cleanup_path)
			except OSError:
				pass
	
