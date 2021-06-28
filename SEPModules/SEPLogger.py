"""
:Author: Marcel Simader
:Date: 12.05.2021

.. versionadded:: v0.1.2
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import abc
import os
from enum import Enum, EnumMeta
from inspect import stack, getframeinfo
from time import strftime, time
from typing import Container, final, Optional, TypeVar, Any, AnyStr, Collection, Callable

from SEPModules.SEPPrinting import cl_s, LIGHT_BLUE, BRIGHT, LIGHT_RED, RED, YELLOW, GREEN, GRAY, Style

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class _LevelsMeta(abc.ABCMeta, EnumMeta):
	"""
	A metaclass used to add abstract method functionality to the :py:class:`enum.EnumMeta` metaclass.
	"""
	pass

class Levels(Enum, metaclass=_LevelsMeta):
	"""
	Abstract base class for all :py:class:`Logger` level enums. :py:class:`Logger` values are comparable using the standard
	compare operators and additionally must be instantiated with a tuple of form ``(level, prefix, style)`` with types
	``int``, ``AnyStr``, and :py:class:`SEPModules.SEPPrinting.Style` which can be accessed as properties of the instances
	of this class. The :py:func:`get_debug` function of this class **must** be overwritten and helps to customize the level
	number, prefix, and style of the debug level (see :py:class:`DefaultLevels` as example).
	"""

	@final
	def __init__(self, *args):
		# do some checks on what was passed here
		if len(args) != 3 or not isinstance(args[0], int) or not isinstance(args[1], str) or not isinstance(args[2], Style):
			raise ValueError(f"enums values of subclass of Levels must be initialized with a tuple of form (level_num, prefix, style), "
							 f"but received tuple {args}")

		# set up attrs
		self._level, self._prefix, self._style = args

	@final
	def __len__(self):
		return self.enum_members

	@final
	def __eq__(self, other):
		return isinstance(other, Levels) and self._level == other._level

	@final
	def __ne__(self, other):
		return isinstance(other, Levels) and self._level != other._level

	@final
	def __lt__(self, other):
		return isinstance(other, Levels) and self._level < other._level

	@final
	def __gt__(self, other):
		return isinstance(other, Levels) and self._level > other._level

	@final
	def __le__(self, other):
		return isinstance(other, Levels) and self._level <= other._level

	@final
	def __ge__(self, other):
		return isinstance(other, Levels) and self._level >= other._level

	@classmethod
	@abc.abstractmethod
	def get_debug(cls) -> Optional[Levels]:
		"""
		This function provides the debug enum for use in the :py:class:`Logger` class. It must be overwritten to change
		the value of this enum. This function is needed to provide the logger class with a debug level.

		:return: a :py:class:`Levels` enum entry
		"""
		return None

	@property
	def level(self):
		return self._level

	@property
	def prefix(self):
		return self._prefix

	@property
	def style(self):
		return self._style

class DefaultLevels(Levels):
	"""
	Default set of levels to pass to a :py:class:`Logger` instance.
	"""
	VERBOSE =     (0,   "[Verbose] ",     GRAY)
	INFO =        (1,   "[Info] ",        BRIGHT)
	OK =		  (2,	"[OK] ",		  GREEN)
	WARNING =     (3,   "[Warning] ",     YELLOW)
	ERROR =       (4,   "[Error] ",       RED)
	FATAL_ERROR = (10,  "[Fatal Error] ", BRIGHT + LIGHT_RED)
	DEBUG		= (999, "[Debug] ", 	  LIGHT_BLUE)

	@classmethod
	def get_debug(cls) -> "DefaultLevels":
		return cls.DEBUG

# convenience aliases for the default enum
VERBOSE 	= DefaultLevels.VERBOSE
INFO 		= DefaultLevels.INFO
OK			= DefaultLevels.OK
WARNING 	= DefaultLevels.WARNING
ERROR 		= DefaultLevels.ERROR
FATAL_ERROR = DefaultLevels.FATAL_ERROR

# levels type var for logger
_LEVELS = TypeVar("_LEVELS", covariant=True, bound=Levels)
""" The generic type parameter for which :py:class:`Levels` subclass to use in a :py:class:`Logger` instance. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Logger:
	r"""
	:py:class:`Logger` provides a convenient way to handle printing to the console, or to another stream or file.

	A logger instance holds configurations on how to print data and what additional meta-data to include. The :py:class:`Levels`
	enum can be used to configure different levels of verbosity (e.g. WARNING, ERROR, etc.) with default levels already
	implemented in :py:class:`DefaultLevels`, which are also accessible through their aliases :data:`VERBOSE`,
	:data:`INFO`, :data:`WARNING`, :data:`ERROR`, :data:`FATAL_ERROR`. Logger also includes a convenience method
	:py:meth:`debug` which can be used to debug and includes additional meta-data such as the file name and line number.

	For convenience, one might want to set up the logger as a constant in the following fashion:

	>>> default_logger = Logger(min_level=WARNING, use_timestamp=True)
	>>> log = default_logger.log # alias to the log function
	>>> debug = default_logger.debug # alias to the debug function
	>>> fatal_error = lambda *msg: default_logger.log(*msg, level=FATAL_ERROR) # alias to an error output of the log function

	Now we can simply use the aliases to access the logger:

	>>> log("this is an error", level=ERROR)
	[Error] [<Timestamp>] this is an error
	>>> debug(("test", "tuple"), 123)
	[Debug] [<Timestamp>] [<input>::<function>:<lineno>] ('test', 'tuple') 123
	>>> fatal_error("halting problem is not decidable!")
	[Fatal Error] [<Timestamp>] halting problem is not decidable!

	:param level_class: which :py:class:`Levels` subclass to use as enum for the verbosity levels of this instance
	:param min_level: the minimum level an entry must have to be printed or written to the log
	:param level_mask: a container of levels to ignore when printing or writing to the log
	:param ignore_level_restrictions: if set to True, this will ignore the values of the ``min_level`` and ``level_mask``
	 	parameters
	:param print_function: a callable taking two strings as input and then performing a write or print operation for each
		entry in the log, the two string arguments are: 1. the actual log string, and 2. the end character similar to the
		end keyword argument in the ``print`` builtin
	:param use_timestamp: whether or not to print a timestamp with each log entry (see :py:meth:`__provide_timestamp__`)
	:param use_date: whether or not to add the current date to each timestamp
	:param use_color: whether or not to use color when printing or writing to the log
	"""

	def __init__(self,
				 level_class : EnumMeta=DefaultLevels,
				 min_level : _LEVELS=DefaultLevels.VERBOSE,
				 level_mask : Optional[Container[_LEVELS]]=None,
				 ignore_level_restrictions : bool=False,
				 print_function : Callable[[AnyStr, AnyStr], None]=lambda msg, end: print(msg, end=end),
				 use_timestamp : bool=False,
				 use_date : bool=False,
				 use_color : bool=True):
		# unchecked attrs
		self._level_class = level_class

		self.ignore_level_restrictions = ignore_level_restrictions
		self.use_color = use_color
		self.use_timestamp = use_timestamp
		self.use_date = use_date
		self.print_function = print_function

		# checked attr setters
		self.min_level = min_level
		self.level_mask = level_mask

	@staticmethod
	def __process_any_input__(*msg : Any) -> str:
		""" Returns the arguments as a space separated string, applying the ``__str__`` method of each argument. """
		return " ".join([str(m) for m in msg])

	def __provide_timestamp__(self) -> str:
		"""
		Provides the current time as timestamp.

		:return: a timestamp in the format ``DAY.MONTH.YEAR HOUR:MINUTE:SECOND.MILLISECOND`` with the date only appearing
			if :py:attr:`use_date` is True, if :py:attr:`use_timestamp` is False this method will simply return the empty
			string
		"""
		return (strftime("[%d.%m.%y %H:%M:%S" if self.use_date else "[%H:%M:%S") + f".{int((time() % 1) * 1E3):03d}] ") if self.use_timestamp else str()

	def __validate_level__(self, level : _LEVELS) -> None:
		if not isinstance(level, self._level_class) or level not in self._level_class:
			raise TypeError(f"level must be an item of the {self._level_class} enum, but received type {level.__class__} "
							f"(Did you forget to change the level_class parameter in the constructor of this Logger?)")

	def _local_print(self, msg : str, style : Style, end : AnyStr) -> None:
		self.print_function(cl_s(msg, style) if self.use_color else msg, end)

	@property
	def min_level(self) -> _LEVELS:
		return self._min_level

	@min_level.setter
	def min_level(self, level : _LEVELS) -> None:
		self.__validate_level__(level)
		self._min_level = level

	@property
	def level_mask(self) -> Optional[Collection[_LEVELS]]:
		return self._level_mask

	@level_mask.setter
	def level_mask(self, value : Optional[Collection[_LEVELS]]) -> None:
		if value is None:
			self._level_mask = ()
		else:
			self._level_mask = value
			[self.__validate_level__(l) for l in value]

	@property
	def level_class(self) -> EnumMeta:
		return self._level_class

	def log(self, *msg : Any,
			level : _LEVELS,
			end : AnyStr="\n") -> None:
		"""
		Registers a log entry with this instance.

		:param msg: the message to log, can be any number of objects
		:param level: which level to mark this entry as (see :py:class:`Logger` and :py:class:`Levels`)
		:param end: the ending character of the log entry, similar to the end keyword argument of the ``print`` builtin
		"""
		self.__validate_level__(level)

		if self.ignore_level_restrictions or (level >= self.min_level and level not in self._level_mask):
			self._local_print(f"{level.prefix}{self.__provide_timestamp__()}{self.__process_any_input__(*msg)}",
							  level.style,
							  end=end)

	def debug(self, *msg : Any,
			  stack_depth : int=1,
			  include_function_name : bool=True,
			  end : AnyStr="\n") -> None:
		"""
		Registers a debug log entry with this instance.

		:param msg: the message to log, can be any number of objects
		:param stack_depth: how far back into the stack to trace the origin of this call
		:param include_function_name: whether to include the name of the function scope of the call or not
		:param end: the ending character of the log entry, similar to the end keyword argument of the ``print`` builtin
		"""
		# get stack info
		stacks = stack()[1:(stack_depth + 1)]
		callers = (getframeinfo(st[0]) for st in stacks)
		caller_texts = list()

		# process text of stack info
		for caller in callers:
			try:
				file_path = os.path.relpath(caller.filename)
			except ValueError:
				# if Windows then different drive letters will cause an error -> absolute path instead
				file_path = caller.filename

			# prepend for reverse order
			caller_texts.insert(0, f"{file_path}{f'::{caller.function}' if include_function_name else ''}:{caller.lineno}")

		# newline + (spacing * prefix + open square bracket)
		offset_join_text = "\n" + (" " * (len(self._level_class.get_debug().prefix) + 1))

		# log
		self.log(f"[{offset_join_text.join(caller_texts)}] {self.__process_any_input__(*msg)}",
				 level=self._level_class.get_debug(),
				 end=end)

		# delete stack info for safety reasons
		del stacks, callers
