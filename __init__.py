#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree
Provides a simple tree functionality, mainly for enigmage."""

__ALL__ = [ 'directory' ]

class BaseNode(object):
	"""You will have to implement:
		_get_parent(self)
		_set_parent(self, parent)
		_has_children(self)
		_get_children(self)
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
	def _has_children(self):
		return len(self._children)
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
	def __str__(self):
		return self.data

class ProgenyFormatter(object):
	def __call__(self, node):
		return node
	@property
	def deeper(self):
		return self

class PrettyFormatter(object):
	def __init__(self, indentation=0):
		self.indentation = indentation
	@property
	def deeper(self):
		return type(self)(self.indentation+1)
	def __call__(self, node):
		return " " * self.indentation + "{0}{1}".format(node._has_children() and "+" or "|", node)

def progeny(node, generations=-1, formatter=ProgenyFormatter()):
	if generations:
		for child in node.children:
			yield formatter(child)
			for childchild in progeny(child, generations-1):
				yield formatter.deeper(childchild)

#~ class NiceFormatter(object):

def elaborate_str(node, generations=-1):
	"""See progeny.__doc__."""
	returnstring = str(self)
	if generations:
		if self.childs:
			returnstring = '\n|-'.join( ["+" + returnstring] + ['\n  '.join(child.elaborate_str(generations=generations-1).split("\n")) for child in self.childs ] )
	return returnstring
def oprogeny(self, generations=-1):
	"""Recursive! Handle with care! Right now, it doesn't check any loops and duplicates! If generations is not a nonnegative integer, it will return the complete progeny."""
	progeny = [self]
	if generations:
		if generations > 0: generations -= 1
		for child in self.childs:
			try:
				progeny += child.progeny(generations)
			except RuntimeError:
				pass
	return progeny

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
	for ahne in progeny(a, formatter = PrettyFormatter()):
		print(ahne)
