#! /usr/bin/python
# -*- coding: utf-8 -*-

import sys
import traceback
import contextlib

@contextlib.contextmanager
def nested(*managers):
	exits = []
	vars = []
	exc = (None, None, None)
	try:
		for mgr in managers:
			exit = mgr.__exit__
			enter = mgr.__enter__
			vars.append(enter())
			exits.append(exit)
		yield vars
	except:
		exc = sys.exc_info()
	finally:
		while exits:
			exit = exits.pop()
			try:
				if exit(*exc):
					exc = (None, None, None)
			except:
				exc = sys.exc_info()
		if exc != (None, None, None):
			# Don't rely on sys.exc_info() still containing
			# the right information. Another exception may
			# have been raised and caught by an exit method
			raise exc[1]



@contextlib.contextmanager
def iter_nested(mgr_iterator):
	exits = []
	vars = []
	exc = None
	try:
		for mgr in mgr_iterator:
			exit = mgr.__exit__
			enter = mgr.__enter__
			vars.append(enter())
			exits.append(exit)
		yield vars
	except Exception as exception:
		exc = exception
		exc_tuple = (type(exc), exc, exc.__traceback__)
	else:
		exc_tuple = (None, None, None)
	finally:
		while exits:
			exit = exits.pop()
			try:
				if exit(*exc_tuple):
					exc = None
					exc_tuple = (None, None, None)
			except Exception as exception:
				exception.__context__ = exc
				exc = exception
				exc_tuple = (type(exc), exc, exc.__traceback__)
		if exc:
			print("Exception {}".format(exc))
			raise exc


class NestContext:
	def __init__(self, *objects):
		self.objects = objects
	def __enter__(self):
		self.contexts = []
		for obj in self.objects:
			if isinstance(obj, tuple):
				try:
					obj = obj[0](*obj[1:])
				except Exception as error:
					self.__exit__(type(error), error, sys.exc_info()[2])
					raise
			try:
				context = obj.__enter__()
			except Exception as error:
				self.__exit__(type(error), error, sys.exc_info()[2])
				raise   
			self.contexts.append(context)
		return self

	def __iter__(self):
		for context in self.contexts:
			yield context

	def __exit__(self, *args):
		for context in reversed(self.contexts):
			try:
				context.__exit__(*args)
			except Exception as error:
				sys.stderr.write(str(error))

if __name__ == "__main__":
	class NamedContext:
		def __init__(self, name):
			self.name = name
		def __enter__(self):
			print("entering context {}".format(self.name))
		def __exit__(self, *args):
			print("exiting context {}".format(self.name))

	class FailContext(NamedContext):
		def fail(self):
			raise Exception("Failing context {}".format(self.name))

	class EnterFailContext(FailContext):
		def __enter__(self):
			print("Halfway entering context {}".format(self.name))
			self.fail()

	class ExitFailContext(FailContext):
		def __exit__(self, *args):
			print("Halfway exiting context {}".format(self.name))
			self.fail()

	class InitFailContext(FailContext):
		def __init__(self, name):
			super().__init__(name)
			print("Halfway initialising {}".format(self.name))
			self.fail()

	class SuppressContext(NamedContext):
		def __exit__(self, exc_type, exc_value, tb):
			super().__exit__(exc_type, exc_value, tb)
			if exc_type != None:
				return True
			else:
				return False

	class ContextManagers: # meins
		def __init__(self, iterator):
			self.contextmanagers = tuple(iterator)
			self.exit_index = 0
		def __enter__(self):
			contextes = []
			try:
				for contextmanager in self.contextmanagers:
					contextes.append(contextmanager.__enter__())
					self.exit_index += 1
			except:#TODO: catch properly
				self.__exit__()
			else:
				return contextes
		def __exit__(self): # argumente
			for contextmanager in reversed(self.contextmanagers[:self.exit_index]):
				pass
	"""			try:
					contextmanager.__exit__
				except: # TODO
					pass"""
			#und dann eval! ist wirklich das beste

	def contexts():
		yield SuppressContext(1)
		yield NamedContext(2)
		yield EnterFailContext(3)


	#with iter_nested(contexts()):
	#with nested(*contexts()):
	#with NestContext(*contexts()):
		#raise Exception("Innen")

	#with SuppressContext(1):
		#with NamedContext(2):
			#with EnterFailContext(3):
				#raise Exception("Innen")
