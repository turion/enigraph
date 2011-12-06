#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree
Provides a simple tree functionality, mainly for enigmage."""

__ALL__ = [ 'directory' ]

class BaseNode(object):
	"""You will have to implement:
		_get_parent(self)
		_set_parent(self, parent)
		_add_child(self, child)
		_remove_child(self, child)
	"""
	@property
	def parent(self):
		return self._get_parent()
	@parent.setter
	def parent(self, parent):
		old_parent = self.parent
		if old_parent != parent:
			self._set_parent(parent)
			try:
				if old_parent:
					old_parent._remove_child(self)
			finally:
				parent._add_child(self)
	@property
	def children(self):
		return self._get_children()

class Node(BaseNode):
	def __init__(self):
		self._children = set()
		self._parent = None
	def _get_parent(self):
		return self._parent
	def _set_parent(self, parent):
		self._parent = parent
	def _get_children(self):
		return iter(self._children)
	def _add_child(self, child):
		self._children.add(child)
	def _remove_child(self, child):
		self._children.remove(child)

class DataNode(Node):
	def __init__(self, data):
		self.data = data
		Node.__init__(self)

if __name__ == "__main__":
	a = DataNode("Opa")
	ab = DataNode("Onkel 1")
	ac = DataNode("Onkel 2")
	acd = DataNode("Kind")
	ab.parent = a
	ac.parent = a
	acd.parent = ac
	#~ print elaborate_str(a)
	print [node.data for node in a.children]
	acd.parent = a
	#~ print elaborate_str(a)
	print [node.data for node in a.children]
