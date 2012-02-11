#! /usr/bin/python
# -*- coding: utf-8 -*-


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

class DebugFormatter(NoFormatter):
	def __call__(self, node):
		input("Returning node {}".format(node))
		return node

class AvoidCircles:
	def __init__(self):
		self.visited = set() # let's hope that the class is hashable
	def _redefine_add(self):
		self.visited = list(self.visited)
		self.add = self.visited.append
	def add(self, node):
		try:
			self.visited.add(node)
		except TypeError: # the node or some node in the progeny was not hashable, recast set as slower list and proceed
			self._redefine_add()
			self.add(node)
	def __call__(self, node):
		try:
			if node not in self.visited:
				self.add(node)
				return True
			else:
				return False
		except TypeError: # the node or some node in the progeny was not hashable, recast set as slower list and proceed
			self._redefine_add()
			return True # since it's not hashable, it couldn't be in there


def progeny_depth(node, generations=-1, formatter=NoFormatter(), circle_checker=lambda child: True):
	if generations:
		allowed_children = filter(circle_checker, node.children)
		for child in allowed_children:
			yield formatter(child)
			for childchild in progeny_depth(child, generations-1, formatter.deeper(), circle_checker):
				yield childchild

def progeny_width(node, generations=-1, formatter=NoFormatter(), circle_checker=lambda child: True):
	if generations:
		allowed_children = tuple(filter(circle_checker, node.children))
		for child in allowed_children:
			#print("Erste Runde {}".format(child))
			yield formatter(child)
		for child in allowed_children:
			for childchild in progeny_width(child, generations-1, formatter.deeper(), circle_checker):
				#print("Zweite Runde {}".format(child))
				yield childchild
