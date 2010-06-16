#! /usr/bin/python
# -*- coding: utf-8 -*-

# enigtree package to provide a simple tree functionality, mainly for enigmage

__ALL__ = [ 'directory' ]

class Node(object):
	data = None
	_parent = None
	parents = []
	_childs = []
	_favourite_child = None
	_successor = None
	_predecessor = None
	def __init__(self, data=None, parent=None, successor=None, predecessor=None):
		self.data = data
		self.parents = []
		self.parent = parent
		self.successor, self.predecessor = successor, predecessor
		self._childs = []
	def adopt(self, node, favourite=False):
		"""Only does the links on the parent side. Consider the parent property if you want links on both sides."""
		#print self, " had the following childs:"
		#for child in self.childs: print child
		#print self, " is adopting ", node
		if node and (not node in self.childs): self.childs.append(node)
		#print self, " has the following childs now:"
		#for child in self.childs: print child
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
		try:
			self.childs.remove(node)
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
	def become_predecessor(self, node):
		self._successor = node
		try:
			node._predecessor = self
		except AttributeError:
			pass
	def become_successor(self, node):
		self._predecessor = node
		try:
			node._successor = self
		except AttributeError:
			pass
	@property
	def successor(self):
		return self._successor
	@successor.setter
	def successor(self, successor):
		self.become_predecessor(successor)
	@property
	def predecessor(self):
		return self._predecessor
	@predecessor.setter
	def predecessor(self, predecessor):
		self.become_successor(predecessor)
	@property
	def parent(self):
		return self._parent
	@parent.setter
	def parent(self, parent):
		self._parent = parent
		if parent:
			self.parents.append(parent)
			parent.adopt(self)
	def __str__(self):
		return str(self.data)
		#return str(self.data) + str([str(child.data) for child in self.childs])
	def __repr__(self):
		return "enigtree.Node containing ", str(self.data)
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
	def align_childs(self, enforce=True):
		success = True
		for child_index in range(len(self.childs)-1): # If no childs, range will return an empty set
			if enforce or not (self.childs[child_index].successor or self.childs[child_index+1].predecessor):
				self.childs[child_index].successor = self.childs[child_index+1]
			else:
				success = False
		return success #
	@property
	def childs(self):
		"""Read-only so far, may be with writing access in subclasses."""
		return self._childs
