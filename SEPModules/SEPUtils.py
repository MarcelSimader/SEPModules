"""
:Author: Marcel Simader
:Date: 01.08.2021

..	versionadded:: v2.0.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import abc
import os
import sys
from inspect import stack, getframeinfo, Traceback
from os import path
from typing import Type, ClassVar, TypeVar, Final, Callable, Optional, Union, final, Tuple, AnyStr, \
	List

from SEPModules.SEPDecorators import copy_func_attrs, lock

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_T: Final = TypeVar("_T")
""" Generic type variable for use in the :py:mod:`SEPUtils` module. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ EXCEPTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SEPSyntaxError(SyntaxError):
	"""
	:py:class:`SEPSyntaxError` is an error for general syntax errors raised by custom implementations in :py:mod:`SEPModules`.

	:param msg: the message of the error
	:param file_path: the path to the file where the error occurred
	:param lineno: the line number at which the error occurred in the file
	:param offset: the offset in characters for the syntax error 'cursor'
	:param code_context: the code context of where the error occurred (i.e. the source code)
	"""

	def __init__(self,
				 msg: AnyStr,
				 file_path: Union[AnyStr, os.PathLike],
				 lineno: int,
				 offset: int,
				 code_context: List[AnyStr]):
		super(SEPSyntaxError, self).__init__(msg, (file_path, lineno, offset, code_context))

	@staticmethod
	def from_traceback(msg: AnyStr, tb: Traceback, offset: int = 0) -> SEPSyntaxError:
		"""
		Creates a :py:class:`SEPSyntaxError` object from a message, traceback, and an optional offset.

		:param msg: the message of the error
		:param tb: the traceback to use as basis for the error
		:param offset: the offset in characters for the syntax error 'cursor'
		:return: a new :py:class:`SEPSyntaxError` instance
		"""
		return SEPSyntaxError(msg, tb.filename, tb.lineno, offset, tb.code_context)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMMUTABLE ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ImmutableMeta(abc.ABCMeta, type):
	"""
	:py:class:`ImmutableMeta` is the meta class behind the mechanism of the :py:class:`Immutable` abstract base class.
	"""

	def __new__(cls, *args, **kwargs):
		new_cls = super(ImmutableMeta, cls).__new__(cls, *args, **kwargs)

		new_cls.__setattr__ = new_cls._lock_method(new_cls, new_cls.__setattr__, "set attribute for", 0)
		new_cls.__delattr__ = new_cls._lock_method(new_cls, new_cls.__delattr__, "delete attribute of", 0)

		return new_cls

	@staticmethod
	def _lock_method(cls: Type, func: Callable[..., _T], action: AnyStr, stack_depth: int) -> Callable[..., _T]:
		def __lock__(self, *args, **kwargs) -> _T:
			if getattr(self, "_locked", False):
				raise SEPSyntaxError.from_traceback(f"Cannot {action} immutable class {cls.__name__!r}",
													SingleStackFrameInfo()[stack_depth + 1])
			else:
				return func(self, *args, **kwargs)

		return copy_func_attrs(__lock__, func, "locked")

	def __call__(cls, *args, **kwargs):
		new = super(ImmutableMeta, cls).__call__(*args, **kwargs)
		new._locked = True
		return new

class Immutable(abc.ABC, metaclass=ImmutableMeta):
	"""
	:py:class:`Immutable` is an abstract base class for marking the instances of a class to be immutable. This means that
	once an object has been created, no attributes can be deleted from it or set to another value.
	"""
	pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ SINGLETON ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class SingletonMeta(abc.ABCMeta, type):
	"""
	:py:class:`SingletonMeta` is the meta class behind the mechanics of the :py:class:`Singleton` abstract base class.
	"""

	_instance: ClassVar[Singleton] = None
	""" The singleton instance for each class. """

	def __new__(cls, *args, **kwargs):
		new_cls = super(SingletonMeta, cls).__new__(cls, *args, **kwargs)

		# guard some methods of new class
		new_cls.__init__ = new_cls.__guard_method(new_cls.__init__, "initialize more than one", stack_depth=0)
		new_cls.__setattr__ = new_cls.__guard_method(new_cls.__setattr__, "set attribute for", stack_depth=0)
		new_cls.__delattr__ = new_cls.__guard_method(new_cls.__delattr__, "delete attribute of", stack_depth=0)

		return new_cls

	def __call__(cls, *args, **kwargs):
		cls.__singleton_guard("instantiate", stack_depth=1)
		return cls.__get_instance(*args, **kwargs)

	def __singleton_guard(cls, action: str, stack_depth: int) -> None:
		if cls._instance is not None:
			frame = SingleStackFrameInfo()[stack_depth + 1]
			raise SEPSyntaxError.from_traceback(f"Cannot {action} Singleton object of type {cls.__name__!r}, "
												f"already created instance {repr(cls._instance)!r}", frame)

	def __guard_method(cls, func: Callable[..., _T], action: str, stack_depth: int) -> Callable[..., _T]:
		def __wrapper__(*args, **kwargs) -> _T:
			cls.__singleton_guard(action, stack_depth=stack_depth + 1)
			return func(*args, **kwargs)

		return copy_func_attrs(__wrapper__, func, "singleton_guard")

	def __get_instance(cls, *args, **kwargs):
		if cls._instance is None:
			cls._instance = super(SingletonMeta, cls).__call__(*args, **kwargs)
		return cls._instance

class Singleton(abc.ABC, metaclass=SingletonMeta):
	"""
	:py:class:`Singleton` is an abstract base class that can be inherited from in order to indicate that a class should
	be a singleton class. A singleton class can only be instantiated once, and once that instance has been created it is
	immutable.

	The singleton instance can be retrieved from the class object by calling the :py:meth:`get_instance` class method. It
	may be ``None`` if no instance of the class has been created yet.
	"""

	@classmethod
	@final
	def get_instance(cls) -> Optional[Singleton]:
		""" Retrieve the singleton instance of this singleton class, or ``None`` if it has not been instantiated yet. """
		return getattr(cls, "_instance", None)

	@final
	def __init_subclass__(cls, **kwargs) -> None:
		super(Singleton, cls).__init_subclass__(**kwargs)
		cls.__init_subclass__ = classmethod(lock(cls.__init_subclass__,
												 lambda _cls: SEPSyntaxError.from_traceback(
														 f"Cannot subclass singleton class {cls.__name__!r}, "
														 f"offending class is {_cls.__name__!r}",
														 SingleStackFrameInfo()[4])
												 ))

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ STACK FRAME ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class StackFrameInfo:
	"""
	:py:class:`StackFrameInfo` is a convenient way to *safely* retrieve ``Traceback`` objects from the stack. It only
	implements three methods (``__init__``, ``get_tracebacks``, and ``__getitem__``) to retrieve the tracebacks and
	emulate a container type with its syntax. Note that it is **not actually a container type**!

	Its usage is shown in the following example: ::

		for tb in StackFrameInfo()[:2]:
			print(tb.lineno)

	:param __offset: how much to offset the start of the stack, this only affects the container syntax, defaults to 2
	"""

	def __init__(self, __offset: int = 2):
		if not isinstance(__offset, int):
			raise TypeError(f"'__offset' must be an int, but received {__offset.__class__.__name__!r}")
		if __offset < 0:
			raise ValueError(f"'__offset' must be greater than or equal to 0, but received {__offset!r}")
		self._offset = __offset

	@staticmethod
	def get_tracebacks(index: slice) -> Tuple[Traceback]:
		try:
			_tracebacks = list()
			# loop over all stacks
			for st in stack()[index]:
				try:
					tb = getframeinfo(st[0])
					# try to shorten file path
					raw_file_path = path.abspath(path.realpath(tb.filename))
					try:
						file_path = path.relpath(raw_file_path, start=path.abspath(path.realpath(os.getcwd())))
					except ValueError:
						# if Windows then different drive letters will cause an error -> absolute path instead
						file_path = raw_file_path
					# check if new path is actually shorter
					if len(file_path) > len(raw_file_path):
						file_path = raw_file_path

					_tracebacks.append(Traceback(file_path, tb.lineno, tb.function, tb.code_context, tb.index))
				finally:
					# delete stack info for safety reasons
					del tb, st
			return tuple(_tracebacks)
		finally:
			del _tracebacks

	def __getitem__(self, item: Union[int, slice]) -> Tuple[Traceback]:
		if isinstance(item, int):
			item = slice(item, item + 1)
		elif not isinstance(item, slice):
			raise TypeError(f"key for 'StackFrameInfo' must be of type 'int', for 'slice'; but "
							f"received {item.__class__.__name__!r}")
		return self.get_tracebacks(slice(item.start + self._offset, item.stop + self._offset, item.step))

class SingleStackFrameInfo(StackFrameInfo):
	"""
	:py:class:`SingleStackFrameInfo` is a special case of :py:class:`StackFrameInfo` which only returns a single traceback
	instead of a tuple. See :py:class:`StackFrameInfo` for more details.
	"""

	def __getitem__(self, item: int) -> Traceback:
		if not isinstance(item, int):
			raise TypeError(f"'SingleStackFrameInfo' only accepts an int index, "
							f"but received {item.__class__.__name__!r}")
		return self.get_tracebacks(slice(item + self._offset, item + self._offset + 1))[0]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ SMART RECURSION LIMITING ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class RecursionDepthLimit:
	""" DOCS recursion depth """

	def __init__(self, recursion_depth: int):
		self._recursion_depth = recursion_depth

		self._linux = sys.platform.startswith("linux")

	def __enter__(self) -> None:
		self._old_recursion_depth = sys.getrecursionlimit()
		sys.setrecursionlimit(self._recursion_depth)

		if self._linux:
			import resource
			self._old_r_stack_limits = resource.getrlimit(resource.RLIMIT_STACK)
			resource.setrlimit(resource.RLIMIT_STACK, (self._recursion_depth * 0x100, resource.RLIM_INFINITY))

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		sys.setrecursionlimit(self._old_recursion_depth)

		if self._linux:
			import resource
			resource.setrlimit(resource.RLIMIT_STACK, self._old_r_stack_limits)
		return exc_val is None

def smart_recursion_limit(initial_recursion_depth: int = sys.getrecursionlimit(),
						  increase_limit_amount_func: Callable[[int], int] = lambda x: x * 2,
						  max_tries: int = 4) \
		-> Callable[[Callable[..., _T]], Callable[..., _T]]:
	# sanitize input
	if initial_recursion_depth <= 0 or max_tries <= 0:
		raise ValueError("arguments supplied to 'smart_recursion_limit' must be positive")

	# decorator construction
	def smart_recursion_limit_decorator(func: Callable[..., _T]) -> Callable[..., _T]:
		def __wrapper__(*args, **kwargs):
			num_tries, r, curr_recursion_limit = 0, None, initial_recursion_depth
			while num_tries < max_tries:
				# actual function calls
				try:
					with RecursionDepthLimit(curr_recursion_limit):
						r = func(*args, **kwargs)
						break
				except RecursionError:
					curr_recursion_limit = increase_limit_amount_func(curr_recursion_limit)
					if curr_recursion_limit <= 0:
						raise ValueError(f"Value returned by 'curr_recursion_limit' must not be negative or 0, but "
										 f"received {curr_recursion_limit!r}")
					num_tries += 1

			if num_tries == max_tries:
				raise RuntimeError(f"Increased recursion limit for {func.__name__!r} to {curr_recursion_limit!r}, but "
								   f"recursive call still failed")

			return r

		return copy_func_attrs(__wrapper__, func, "smart_rec_limit")

	return smart_recursion_limit_decorator

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def abstract_not_implemented(cls: Type, name: str) -> NotImplementedError:
	""" Returns a NotImplementedError to raise for when an abstract method is not implemented for a class. """
	return NotImplementedError(f"Abstract method {name!r} must be implemented for class {cls.__name__!r}")
