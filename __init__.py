#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree
Provides a simple tree functionality, mainly for enigmage."""

__ALL__ = [ 'directory' ]

from errors import *

import abc
import collections

FollowingInformation = collections.namedtuple("FollowingInformation", "node tag")

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
		self._following = FollowingInformation(node=node, key=key)
	def unfollow(self, node):
		node._followers.remove(self)
		self._following = None
	@property
	def parent(self):
		return self._get_parent()
	@parent.setter
	def parent(self, parent):
		if self.readonly:
			raise EnigtreeReadOnlyError
		else:
			old_parent = self.parent # cache to prevent multiple, potentially expensive calculation
			if old_parent != parent:
				self._set_parent(parent)
				for key in self._followers:
					self._followers[key]._set_parent(parent._followers[key])
				try:
					if old_parent:
						old_parent._remove_child_notification(self)
				finally:
					if parent:
						parent._add_child_notification(self)
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
	def _add_child(self, child):
		self._children.add(child)
	def _remove_child(self, child):
		self._children.remove(child)

class DataNode(Node):
	def __init__(self, data):
		self.data = data
		super().__init__()
	def __str__(self):
		return self.data

class NoFormatter:
	def __call__(self, node):
		return node
	def deeper(self):
		return self

class PrettyFormatter:
	def __init__(self, indentation=0):
		self.indentation = indentation
	def deeper(self):
		return type(self)(self.indentation+1)
	def __call__(self, node):
		return " " * self.indentation + "{0}{1}".format(node._has_children() and "+" or "|", node)

class GenerationwiseFormatter:
	def __init__(self, generation=0, announce_string="Generation {0}:", announced_generations=None):
		self.generation = generation
		self.announce_string = announce_string
		if not announced_generations:
			announced_generations = set()
		self.announced_generations = announced_generations
	def deeper(self):
		return type(self)(generation=self.generation+1, announce_string=self.announce_string, announced_generations=self.announced_generations)
	def __call__(self, node):
		if self.generation not in self.announced_generations:
			self.announced_generations.add(self.generation)
			return self.announce_string.format(self.generation) + "\n{0}".format(node)
		else:
			return str(node)

def progeny_depth(node, generations=-1, formatter=NoFormatter()):
	if generations:
		for child in node.children:
			yield formatter(child)
			for childchild in progeny_depth(child, generations-1, formatter.deeper()):
				yield childchild

def progeny_width(node, generations=-1, formatter=NoFormatter()):
	if generations:
		for child in node.children:
			yield formatter(child)
		for child in node.children:
			for childchild in progeny_width(child, generations-1, formatter.deeper()):
				yield childchild

if __name__ == "__main__":
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
	print("The progeny of {0}".format(a))
	print("Depth first")
	for ahne in progeny_depth(a, formatter = PrettyFormatter()):
		print(ahne)
	print("Width first")
	for ahne in progeny_width(a, formatter = GenerationwiseFormatter()):
		print(ahne)
	print("Width first, only two generations")
	for ahne in progeny_width(a, generations=2, formatter = GenerationwiseFormatter()):
		print(ahne)
	print("Width first, NoFormatter")
	for ahne in progeny_width(a):
		print(ahne)
