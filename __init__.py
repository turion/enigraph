#! /usr/bin/python
# -*- coding: utf-8 -*-

"""enigtree
Provides a simple tree functionality, mainly for enigmage."""

__ALL__ = [ 'directory' ]

class Node(object):
	open = False
	def __init__(self, data=None, parent=None):
		self.data = data
		self.parents = []
		self.parent = parent
		self._childs = []
		self._favourite_child = None
	def adopt(self, node, favourite=False):
		"""Only does the links on the parent side. Consider the parent property if you want links on both sides. This routine is very low level because it adresses only ._childs and not .childs! Use at own risk."""
		if node and (not node in self._childs): self._childs.append(node)
		if favourite: self.favourite_child = node
	@property
	def favourite_child(self):
		return self._favourite_child
	@favourite_child.setter
	def favourite_child(self, child):
		if child in self.childs or child == None:
			self._favourite_child = child
		else:
			print self, ' says: "', child, '" is not my child.'
	def disinherit(self, node, next_favourite=None):
		"""Technical"""
		try:
			self._childs.remove(node)
			node.parents.remove(self)
			self.favourite_child = next_favourite # Herzlos
		except:
			pass
		if node._parent == self: node._parent = None # Ganz brutal ;)
	@property
	def successors(self):
		successors = []
		next = self.successor
		while next:
			successors.append(next)
			next = next.successor
		return successors
	@property
	def predecessors(self):
		predecessors = []
		next = self.predecessor
		while next:
			predecessors.append(next)
			next = next.predecessor
		return predecessors
	@property
	def successor(self):
		successor = None
		if self.parent:
			childs = self.parent.childs
			index = childs.index(self)
			if len(childs) > index + 1:
				successor = childs[index+1]
		return successor
	@property
	def predecessor(self):
		predecessor = None
		if self.parent:
			childs = self.parent.childs
			index = childs.index(self)
			if index > 0:
				predecessor = childs[index-1]
		return predecessor
	@property
	def parent(self):
		return self._parent
	@parent.setter
	def parent(self, parent):
		if parent:
			self.parents.append(parent)
			parent.adopt(self)
		self._parent = parent
	def __str__(self):
		return str(self.data)
	def __repr__(self):
		return "enigtree.Node containing " + str(self.data)
	def elaborate_str(self):
		"""See progeny.__doc__."""
		returnstring = str(self)
		if self.childs:
			returnstring = '\n|-'.join( ["+" + returnstring] + ['\n  '.join(child.elaborate_str().split("\n")) for child in self.childs ] )
		return returnstring
	def progeny(self, generations=-1):
		"""Recursive! Handle with care! Right now, it doesn't check any loops and duplicates! If generations is not a nonnegative integer, it will return the complete progeny."""
		progeny = [self]
		if generations:
			if generations > 0: generations -= 1
			for child in self.childs:
				#print child
				try:
					progeny += child.progeny(generations)
				except RuntimeError:
					pass
		return progeny
	@property
	def childs(self):
		"""Read-only so far, may be with writing access in subclasses."""
		return self._childs
