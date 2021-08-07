"""
:Author: Marcel Simader
:Date: 12.05.2021

.. versionadded:: v0.1.2
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import enum
import sys
from time import strftime, time
from typing import Container, final, Optional, TypeVar, Any, AnyStr, Collection, Callable, Final, Type, Dict, List, \
	Tuple, ClassVar

from SEPModules.SEPDecorators import copy_func_attrs
from SEPModules.SEPPrinting import AnsiControl, cl_s, LIGHT_BLUE, BRIGHT, LIGHT_RED, RED, YELLOW, GREEN, GRAY
from SEPModules.SEPUtils import StackFrameInfo

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LevelType(enum.Enum):
	"""
	Enum for indicating which type of Level an enum entry in a :py:class:`Level` subclass is. Possible values are:

	* ``NORMAL``
	* ``ERROR``
	* ``DEBUG``
	"""
	NORMAL = 0
	ERROR = 1
	DEBUG = 2

class Level(enum.Enum):
	"""
	Abstract base class for all :py:class:`Logger` level enums. :py:class:`Logger` values are comparable using the standard
	compare operators and additionally must be instantiated with a tuple of form ``(level, prefix, style, level_type)``
	with types ``int``, ``AnyStr``, :py:class:`SEPModules.SEPPrinting.AnsiControl`, and :py:class:`LevelType` which can
	be accessed as properties of the instances of this class.
	"""

	def __init_subclass__(cls, **kwargs):
		super(Level, cls).__init_subclass__(**kwargs)
		cls.__level_types: ClassVar[Dict[LevelType, List[Level]]] = {l: list() for l in LevelType}

	def __init__(self, level: int, prefix: str, style: AnsiControl, level_type: LevelType):
		if not (isinstance(level, int)
				and isinstance(prefix, str)
				and isinstance(style, AnsiControl)
				and isinstance(level_type, LevelType)):
			raise ValueError(f"enums values of subclass of Level must be initialized with a tuple of form (level_num, "
							 f"prefix, style, level_type), but received tuple ({level.__class__.__name__!r}, "
							 f"{prefix.__class__.__name__!r}, {style.__class__.__name__!r}, "
							 f"{level_type.__class__.__name__!r})")
		self._level = level
		self._prefix = prefix
		self._style = style
		self._level_type = level_type

		# update level type mapping
		self.__level_types[level_type].append(self)

	@final
	def __eq__(self, other) -> bool:
		return isinstance(other, Level) and self._level == other._level

	@final
	def __ne__(self, other) -> bool:
		return isinstance(other, Level) and self._level != other._level

	@final
	def __lt__(self, other) -> bool:
		return isinstance(other, Level) and self._level < other._level

	@final
	def __gt__(self, other) -> bool:
		return isinstance(other, Level) and self._level > other._level

	@final
	def __le__(self, other) -> bool:
		return isinstance(other, Level) and self._level <= other._level

	@final
	def __ge__(self, other) -> bool:
		return isinstance(other, Level) and self._level >= other._level

	@property
	def level(self) -> int:
		return self._level

	@property
	def prefix(self) -> str:
		return self._prefix

	@property
	def style(self) -> AnsiControl:
		return self._style

	@property
	def level_type(self) -> LevelType:
		return self._level_type

	@classmethod
	@final
	def get_errors(cls) -> Tuple[Level, ...]:
		"""
		This function provides those levels which represent an error so that the :py:class:`Logger` class can discern
		between normal outputs and error outputs.

		:return: an iterator of :py:class:`Level` enum entry which represent the error levels
		"""
		return tuple(cls.__level_types[LevelType.ERROR])

	@classmethod
	@final
	def get_debug(cls) -> Tuple[Level, ...]:
		"""
		This function provides the debug enum for use in the :py:class:`Logger` class. This function is needed to provide
		the logger class with a debug level.

		:return: an iterator of :py:class:`Level` enum entry which represents the debug levels
		"""
		return tuple(cls.__level_types[LevelType.DEBUG])

class DefaultLevel(Level):
	"""
	Default set of levels to pass to a :py:class:`Logger` instance.
	"""
	VERBOSE = (0, "[Verbose] ", GRAY, LevelType.NORMAL)
	INFO = (1, "[Info] ", BRIGHT, LevelType.NORMAL)
	OK = (2, "[OK] ", GREEN, LevelType.NORMAL)
	WARNING = (3, "[Warning] ", YELLOW, LevelType.NORMAL)
	ERROR = (4, "[Error] ", BRIGHT + LIGHT_RED, LevelType.ERROR)
	FATAL_ERROR = (10, "[Fatal Error] ", RED, LevelType.ERROR)
	DEBUG = (999, "[Debug] ", LIGHT_BLUE, LevelType.DEBUG)

# convenience aliases for the default enum
VERBOSE = DefaultLevel.VERBOSE
INFO = DefaultLevel.INFO
OK = DefaultLevel.OK
WARNING = DefaultLevel.WARNING
ERROR = DefaultLevel.ERROR
FATAL_ERROR = DefaultLevel.FATAL_ERROR

_Level = TypeVar("_Level", bound=Level)
""" The generic type parameter for which :py:class:`Level` subclass to use in a :py:class:`Logger` instance. """
_Func = TypeVar("_Func", Callable, staticmethod, classmethod)
""" The generic type variable constrained by Callable, static, or classmethod for typing usage in :py:mod:`SEPLogger`. """
_C = TypeVar("_C")
""" The ``cls`` type variable typing usage in :py:mod:`SEPLogger`. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Logger:
	r"""
	Logger(level_class=DefaultLevel, min_level=DefaultLevel.VERBOSE, level_mask=None, print_function=None, use_timestamp=False, use_date=False, ignore_level_restrictions=False, use_color=True)
	:py:class:`Logger` provides a convenient way to handle printing to the console, or to another stream or file.

	A logger instance holds configurations on how to print data and what additional meta-data to include. The :py:class:`Level`
	enum can be used to configure different levels of verbosity (e.g. WARNING, ERROR, etc.) with default levels already
	implemented in :py:class:`DefaultLevels`, which are also accessible through their aliases :py:data:`VERBOSE`,
	:py:data:`INFO`, :py:data:`WARNING`, :py:data:`ERROR`, :py:data:`FATAL_ERROR`. Logger also includes a convenience
	method :py:meth:`debug` which can be used to debug and includes additional meta-data such as the file name and line
	number.

	For convenience, one might want to set up the logger as a constant, or use the provided :py:data:`DEFAULT_LOGGER`
	instance in the following fashion:

	>>> from SEPModules.SEPLogger import DEFAULT_LOGGER
	>>> from SEPModules import log # alias to the log method is already provided!
	>>> from SEPModules import debug # and so is an alias to the debug method!
	>>> fatal_error = lambda *msg: DEFAULT_LOGGER.log(*msg, level=FATAL_ERROR) # alias to an error output of the log function

	Now we can simply use the aliases to access the logger: ::

		log("this is an error", level=ERROR)
		[Error] [<Timestamp>] this is an error

		debug(("_test", "tuple"), 123)
		[Debug] [<Timestamp>] [<input>::<function>:<lineno>] ('_test', 'tuple') 123

		fatal_error("halting problem is not decidable!")
		[Fatal Error] [<Timestamp>] halting problem is not decidable!

	:param level_class: which :py:class:`Level` subclass to use as enum for the verbosity levels of this instance
	:param min_level: the minimum level an entry must have to be printed or written to the log
	:param level_mask: a container of levels to ignore when printing or writing to the log
	:param print_function: a callable taking in one string (the message itself) and one level (the level of this message),
		the print_function is expected to write this message to a buffer or output with optional formatting or changes
		based on the supplied level, and then to flush the buffer to write the change immediately if the level is at error
		threshold
	:param use_timestamp: whether or not to print a timestamp with each log entry (see :py:meth:`_provide_timestamp`)
	:param use_date: whether or not to add the current date to each timestamp
	:param ignore_level_restrictions: if set to True, this will ignore the values of the ``min_level`` and ``level_mask``
	 	parameters
	:param use_color: whether or not to use color when printing or writing to the log
	"""

	def __init__(self,
				 level_class: Type[_Level] = DefaultLevel,
				 min_level: _Level = DefaultLevel.VERBOSE,
				 level_mask: Optional[Container[_Level]] = None,
				 print_function: Optional[Callable[[AnyStr, _Level], None]] = None,
				 use_timestamp: bool = False,
				 use_date: bool = False,
				 ignore_level_restrictions: bool = False,
				 use_color: bool = True):
		# unchecked attrs
		self._level_class = level_class
		self.print_function = self.default_print_function if print_function is None else print_function
		self.use_timestamp = use_timestamp
		self.use_date = use_date
		self.ignore_level_restrictions = ignore_level_restrictions
		self.use_color = use_color

		# checked attr setters
		self.min_level = min_level
		self.level_mask = level_mask

	# ~~~~~~~~~~~~~~~ helpers and properties ~~~~~~~~~~~~~~~

	@staticmethod
	def __process_any_input(*msg: Any, joiner: AnyStr = " ") -> str:
		""" Returns the arguments as a space separated string, applying the ``__str__`` method of each argument. """
		return joiner.join([str(m) for m in msg])

	@final
	def __validate_level(self, level: _Level) -> None:
		""" Checks if the given level is valid on this instance. """
		if level not in self._level_class:
			raise TypeError(f"level must be an item of the {self._level_class} enum, but received "
							f"type {level.__class__} (Did you forget to change the level_class parameter in "
							f"the constructor of this Logger?)")

	@final
	def __level_condition(self, level: _Level) -> bool:
		""" :return: whether or not the given level warrants action under the instance's settings """
		return self.ignore_level_restrictions or (level >= self.min_level and level not in self._level_mask)

	def _provide_timestamp(self) -> str:
		"""
		Provides the current time as timestamp.

		:return: a timestamp in the format ``DAY.MONTH.YEAR HOUR:MINUTE:SECOND.MILLISECOND`` with the date only appearing
			if :py:attr:`use_date` is True, if :py:attr:`use_timestamp` is False this method will simply return the empty
			string
		"""
		if self.use_timestamp or self.use_date:
			_time, _date = f"{strftime('%H:%M:%S')}.{int((time() % 1) * 1E3):03d}", f"{strftime('%d.%m.%y')}"
			return f"[{_date if self.use_date else ''}{_time if self.use_timestamp else ''}] "
		else:
			return str()

	@final
	def _local_print(self, msg: str, level: _Level) -> None:
		"""
		The print helper function that passes on specific data to the defined :py:attr:`print_function` of this instance.
		It also first checks if the input should be printed in the first place.
		"""
		if self.__level_condition(level):
			self.print_function(cl_s(msg, level.style) if self.use_color else msg, level)

	def default_print_function(self, message: AnyStr, level: _Level) -> None:
		"""
		The default function used for printing. This will print to ``STDOUT`` for levels below or equal to :py:obj:`.WARNING`,
		and to ``STDERR`` for anything above, excluding the debug output.

		..	note::

			The level provided by the :py:meth:`Level.get_debug` method will never be considered an error by this function,
			even if it is provided by the :py:meth:`Level.get_errors` method.
		"""
		if (level in self._level_class.get_debug()) or (level not in self._level_class.get_errors()):
			sys.stdout.write(message)
		else:
			sys.stderr.write(message)
		sys.stderr.flush()

	@property
	def min_level(self) -> _Level:
		""" :return: the minimum level to be logged by this instance """
		return self._min_level

	@min_level.setter
	def min_level(self, level: _Level) -> None:
		"""
		Sets the minimum level to be logged by this instance.

		:param level: the level to set the minimum to
		:raise TypeError: if level is not part of the enum specified by `level_class` (see :py:class:`Logger`
			constructor)
		"""
		self.__validate_level(level)
		self._min_level = level

	@property
	def level_mask(self) -> Optional[Collection[_Level]]:
		""" :return: the level mask blocking specific levels from being logged """
		return self._level_mask

	@level_mask.setter
	def level_mask(self, mask: Optional[Collection[_Level]]) -> None:
		"""
		Sets a new level mask for blocking specific levels from being logged in this instance.

		:param mask: the new level mask, may be None to reset the level mask to an empty collection
		:raise TypeError: if any passed level in the new mask is not part of the enum specified by `level_class` (see
			:py:class:`Logger` constructor)
		"""
		if mask is None:
			self._level_mask = ()
		else:
			self._level_mask = mask
			[self.__validate_level(l) for l in mask]

	@property
	def level_class(self) -> Type[_Level]:
		""" :return: the enum of which all levels used by this instance must be a part of """
		return self._level_class

	# ~~~~~~~~~~~~~~~ methods ~~~~~~~~~~~~~~~

	def log(self, *msg: Any,
			level: _Level = DefaultLevel.INFO,
			start: AnyStr = "",
			joiner: AnyStr = " ",
			end: AnyStr = "\n") -> None:
		"""
		log(*msg, level=DefaultLevel.INFO, start='', joiner=' ', end='\\n')
		Registers a log entry with this instance.

		:param msg: the message to log, can be any number of objects
		:param level: which level to mark this entry as (see :py:class:`Logger` and :py:class:`Level`)
		:param start: the starting character of the message of the log entry (inserted after prefix and timestamp)
		:param joiner: the character used to join multiple input objects together (akin to ``str.join``)
		:param end: the ending character of the log entry, similar to the end keyword argument of the ``print`` builtin
		:raise TypeError: if level is not part of the enum specified by `level_class` (see :py:class:`Logger`
			constructor)
		"""
		self.__validate_level(level)
		self._local_print(f"{level.prefix}{self._provide_timestamp()}"
						  f"{start}{self.__process_any_input(*msg, joiner=joiner)}{end}",
						  level)

	def newline(self, level: _Level = DefaultLevel.INFO) -> None:
		"""
		newline(level=DefaultLevel.INFO)
		Registers an empty line with this instance.

		:param level: the level to mark this blank line as, this does not print a style or prefix and simply exists so
			that newlines can be printed conditionally based on what the level requirements of this instance are
		:raise TypeError: if level is not part of the enum specified by `level_class` (see :py:class:`Logger`
			constructor)
		"""
		self.__validate_level(level)
		self._local_print("", level)

	def debug(self,
			  *msg: Any,
			  stack_depth: int = 1,
			  include_function_name: bool = True,
			  start: AnyStr = "",
			  joiner: AnyStr = " ",
			  end: AnyStr = "\n") -> None:
		"""
		Registers a debug log entry with this instance.

		:param msg: the message to log, can be any number of objects
		:param stack_depth: how far back into the stack to trace the origin of this call
		:param include_function_name: whether to include the name of the function scope of the call or not
		:param start: the starting character of the message of the log entry (inserted after prefix and timestamp)
		:param joiner: the character used to join multiple input objects together (akin to ``str.join``)
		:param end: the ending character of the log entry, similar to the end keyword argument of the ``print`` builtin
		"""
		# get stack info
		caller_texts = reversed(tuple(f"{caller.filename}"
									  f"{f'::{caller.function}' if include_function_name else ''}"
									  f":{caller.lineno}"
									  for caller in StackFrameInfo()[1:(stack_depth + 1)]))

		_debug = tuple(self._level_class.get_debug())
		if len(_debug) > 0:
			_debug = _debug[0]
		else:
			raise ValueError(f"Enum {self._level_class.__name__!r} does not define any 'debug' levels")
		# newline + (spacing * prefix + open square bracket)
		offset_join_text = "\n" + (" " * (len(_debug.prefix) + 1))

		# log
		self.log(f"[{offset_join_text.join(caller_texts)}] {start}{self.__process_any_input(*msg, joiner=joiner)}",
				 level=_debug, start="", joiner=joiner, end=end)

	# ~~~~~~~~~~~~~~~ decorators ~~~~~~~~~~~~~~~

	def log_call(self,
				 *msg: Any,
				 level: _Level = DefaultLevel.INFO,
				 use_qualified_name: bool = True,
				 include_arguments: bool = False,
				 exclude_self: bool = True,
				 start: AnyStr = "",
				 joiner: AnyStr = " ",
				 end: AnyStr = "\n") -> Callable[[_Func], _Func]:
		"""
		log_call(*msg, level=DefaultLevel.INFO, use_qualified_name=True, include_arguments=False, exclude_self=True, start='', joiner=' ', end='\\n')
		Customizable decorator for logging a function call with a message and a level. This log call will automatically
		include the function name in the output.

		:param msg: the message to log, can be any number of objects
		:param level: which level to mark this entry as (see :py:class:`Logger` and :py:class:`Level`)
		:param use_qualified_name: whether or not to use the fully qualified name of the function in the log output
		:param include_arguments: whether or not to include the arguments passed to the function in the log output
		:param exclude_self: whether or not to exclude the ``cls`` argument for methods
		:param start: the starting character of the message of the log entry (inserted after prefix and timestamp)
		:param joiner: the character used to join multiple input objects together (akin to ``str.join``)
		:param end: the ending character of the log entry, similar to the end keyword argument of the ``print`` builtin
		:return: the customized decorator function
		"""

		def __decorator__(raw_func: _Func) -> _Func:
			is_static, is_class = isinstance(raw_func, staticmethod), isinstance(raw_func, classmethod)
			func = raw_func.__func__ if is_static or is_class else raw_func
			name = func.__qualname__ if use_qualified_name else func.__name__

			def __wrapper__(*args, **kwargs):
				# process args passed to func
				arg_str = str()
				if include_arguments:
					_args = [repr(v) for v in args] + [f'{n}={v!r}' for n, v in kwargs.items()]
					# remove "cls" for instance methods
					if len(_args) > 0 and exclude_self and func.__code__.co_varnames[0] == "cls":
						del _args[0]
					if len(_args) > 0:
						arg_str = f" <- {', '.join(_args)}"

				# log func
				self.log(f"[{name}{arg_str}] {start}{self.__process_any_input(*msg, joiner=joiner)}",
						 level=level, start="", joiner=joiner, end=end)

				# call func
				return func(*args, **kwargs)

			_decorated = copy_func_attrs(__wrapper__, func, "logged")
			if is_static:
				return staticmethod(_decorated)
			elif is_class:
				return classmethod(_decorated)
			else:
				return _decorated

		return __decorator__

	# ~~~~~~~~~~~~~~~ base classes ~~~~~~~~~~~~~~~

	def log_class(self,
				  *msg: Any,
				  level: _Level = DefaultLevel.INFO,
				  allow_public: bool = True,
				  allow_private: bool = True,
				  include_arguments: bool = False,
				  exclude_self: bool = True,
				  start: AnyStr = "",
				  joiner: AnyStr = " ",
				  end: AnyStr = "\n") -> Callable[[Type[_C]], Type[_C]]:
		"""
		log_class(*msg, level=DefaultLevel.INFO, allow_public=True, allow_private=True, include_arguments=False, exclude_self=True, start='', joiner=' ', end='\\n')
		Customizable decorator for logging a function call with a message and a level. This log call will automatically
		include the function name in the output.  DOCS change this docstring

		..	note::

			The ``__str__`` and ``__repr__`` methods cannot be logged, since they maybe be used to generate the log
			output. The ``__new__`` method is also not logged.

		:param msg: the message to log, can be any number of objects
		:param level: which level to mark this entry as (see :py:class:`Logger` and :py:class:`Level`)
		:param allow_public: whether or not to allow public methods (all methods with names not starting with any
			underscores), for example ``message``
		:param allow_private: whether or not to allow "sunder" or "dunder" methods (all methods with names starting with
		 	underscores), for example ``_calc_runtime``
		:param include_arguments: whether or not to include the arguments passed to the function in the log output
		:param exclude_self: whether or not to exclude the ``cls`` argument for methods
		:param start: the starting character of the message of the log entry (inserted after prefix and timestamp)
		:param joiner: the character used to join multiple input objects together (akin to ``str.join``)
		:param end: the ending character of the log entry, similar to the end keyword argument of the ``print`` builtin
		:return: the customized decorator function
		"""
		_decorator = self.log_call(*msg, level=level, use_qualified_name=True, include_arguments=include_arguments,
								   exclude_self=exclude_self, start=start, joiner=joiner, end=end)

		def __wrapper__(cls: Type[_C]) -> Type[_C]:
			# iterate over members of class, copy so we can loop over once
			for name in cls.__dict__:
				# exclude str and repr
				if name in ("__str__", "__repr__", "__new__", "__class__", "__dict__", "__module__",
							"__main__", "__doc__", "__weakref__", "__slots__"):
					continue
				# filter based on name
				if name.startswith("_"):
					if not allow_private: continue
				else:
					if not allow_public: continue

				obj = getattr(cls, name)

				# differentiate between property and function types
				new_func = None
				if isinstance(obj, property):
					new_func = property(*[_decorator(_f) for _f in (obj.fget, obj.fset, obj.fdel) if _f is not None],
										doc=obj.__doc__)
				elif isinstance(obj, _Func.__constraints__):
					new_func = _decorator(obj)

				if new_func is not None:
					setattr(cls, name, new_func)
			return cls

		return __wrapper__

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ DEFAULT LOGGER INSTANCE ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

DEFAULT_LOGGER: Final = Logger(ignore_level_restrictions=True)
""" 
This instance is provided for convenient logging and debugging. This logger has all of the default arguments, except that
the ``ignore_level_restrictions`` option, which will disable the level features, is set to True (see :py:class:`Logger`). 
"""
log: Final = DEFAULT_LOGGER.log
debug: Final = DEFAULT_LOGGER.debug
