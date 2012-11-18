#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigraph
Provides a simple tree functionality, mainly for enigmage."""

__ALL__ = [ 'directory' ]

from .errors import *
from . import progeny

import abc
import collections

Following = collections.namedtuple("Following", "node tag")

class BaseNode(metaclass=abc.ABCMeta):
	"""You will have to implement:
		_get_parent(self)
		_set_parent(self, parent)
		_get_children(self)
	"""
	_readonly = False

	def __init__(self):
		self._followers = {}
		self._following = None

	@property
	def readonly(self):
		return self._following or self._readonly

	@property
	def following(self):
		return self._following
	def follow(self, node, key=None):
		node._followers[key] = self
		self._following = Following(node=node, key=key)
	def unfollow(self, node):
		node._followers.remove(self)
		self._following = None

	@property
	def parent(self):
		parent = self._get_parent()
		if parent is not None:
			return parent
		else:
			raise EnigraphNoParent
	@parent.setter
	def parent(self, parent):
		if self.readonly:
			raise EnigraphReadOnlyError
		else:
			try:
				old_parent = self.parent # cache to prevent multiple, potentially expensive calculation
			except EnigraphNoParent:
				old_parent = None
			if old_parent != parent:
				self._set_parent(parent)
				try:
					if old_parent:
						old_parent._remove_child_notification(self)
				finally:
					if parent:
						parent._add_child_notification(self) # alternative implementation: do the _add_child_notification first and allow it to raise exceptions that abort setting the parent
				for key, follower in self._followers.items():
					follower.parent = parent._followers[key]

	@property
	def children(self):
		return self._get_children()

	@abc.abstractmethod
	def _get_parent(self):
		pass
	@abc.abstractmethod
	def _set_parent(self, parent):
		pass
	@abc.abstractmethod
	def _get_children(self):
		pass

	def _add_child_notification(self, child):
		pass
	def _remove_child_notification(self, child):
		pass
	def _has_children(self): # intentionally not abstract
		try:
			iter(self.children).__next__()
		except StopIteration:
			return False
		else:
			return True

	def progeny(self, method="width", return_root=False, formatter=progeny.NoFormatter(), circle_checker=lambda node: True, **kwargs):
		"""Performance is much better if the Node class and all its subclasses are hashable"""
		if method in ("w", "width", "width_first"):
			progeny_method = progeny.progeny_width
		elif method in ("d", "depth", "depth_first"):
			progeny_method = progeny.progeny_depth
		else:
			raise ValueError("Unknown method {}".format(method))
		if return_root:
			yield formatter(self)
		formatter = formatter.deeper()
		circle_checker(self)
		for child in progeny_method(self, formatter=formatter, circle_checker=circle_checker, **kwargs):
			yield child
	def __iter__(self):
		return self.progeny(circle_checker=progeny.AvoidCircles())

	def ancestors(self, return_self=False):
		avoid_circles = progeny.AvoidCircles()
		next_node = self
		if return_self:
			yield self
		while avoid_circles(next_node):
			try:
				next_node = next_node.parent
			except EnigraphNoParent:
				break
			yield next_node

class Node(BaseNode):
	def __init__(self):
		self._children = set()
		self._parent = None
		super().__init__()
	def _get_parent(self):
		return self._parent
	def _set_parent(self, parent):
		self._parent = parent
	def _get_children(self):
		return iter(self._children) # Do we need iter?
	def _add_child_notification(self, child):
		self._children.add(child)
	def _remove_child_notification(self, child):
		self._children.remove(child)


class DataNode(Node):
	def __init__(self, data):
		self.data = data
		super().__init__()
	def __str__(self):
		return self.data

# Ähnliches Ergebnis lässt sich erzielen, wenn man eine Klassendefinition mit @functools.lru_cache() dekoriert
class CachedNode(BaseNode):
	cache = {}
	def __new__(cls, index):
		try:
			return cls.cache[index]
		except KeyError:
			cls.cache[index] = result = super().__new__(cls)
			return result

class CachedDataNode(CachedNode, DataNode):
	pass

def test():
	a = DataNode("Opa")
	ab = DataNode("Onkel 1")
	ac = DataNode("Onkel 2")
	acd = DataNode("Kind 1")
	ace = DataNode("Kind 2")
	acdf = DataNode("Enkel 1")
	aceg = DataNode("Enkel 2")
	ab.parent = a
	ac.parent = a
	acd.parent = ac
	ace.parent = ac
	acdf.parent = acd
	aceg.parent = ace
	if not input("The progeny of {} (press any key to abort, press enter to test)".format(a)):
		input("\nWidth first")
		for ahne in a.progeny(formatter = progeny.GenerationwiseFormatter()):
			print(ahne)
		input("\nDepth first, with root of the tree")
		for ahne in a.progeny(method="d", formatter = progeny.PrettyFormatter(), return_root=True):
			print(ahne)
		input("\nWidth first, only two generations, with root of the tree")
		for ahne in a.progeny(generations=2, formatter = progeny.GenerationwiseFormatter(), return_root=True):
			print(ahne)
		a.parent = acdf
		input("""
Changed: {}'s parent is now {}.
The graph is now circular, a regular call to progeny would recurse infinitely.
But it's possible to avoid circles and yield every node exactly once
Call {}'s progeny:""".format(a, acdf, ac))
		#for ahne in ac.progeny(circle_checker=AvoidCircles()):
			#print(ahne)
		for ahne in ac: # short for the above
			print(ahne)
	if not input("""
The ancestors of {}:""".format(acdf)):
		for ancestor in acdf.ancestors():#return_self=True):
			print(ancestor)
	if not input("CachedNodes test"):
		b = CachedDataNode("b")
		b2 = CachedDataNode("b")
		c = CachedDataNode("c")
		print(b is b2)
		print(b is c)
