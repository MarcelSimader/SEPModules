"""
:Author: Marcel Simader
:Date: 01.04.2021

.. versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys
from getopt import getopt, GetoptError
from typing import List, Callable, Dict, Union, Tuple, Final, Iterable, Iterator, Collection, TypeVar

from SEPModules.SEPDecorators import copy_func_attrs
from SEPModules.SEPPrinting import repr_str

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_R: Final = TypeVar("_R")
""" The generic type variable to use for function returns in the :py:mod:`SEPIO` module. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class ConsoleArgsError(Exception):
	""" Error class used to catch exceptions while parsing the ``sys.argv`` input for :py:class:`ConsoleManager`. """

	def __init__(self, msg: str, arguments: Collection[str]):
		super(ConsoleArgsError, self).__init__()
		self.msg = msg
		self.arguments = arguments

	def __str__(self) -> str:
		return f"{self.msg} (fault in arguments {self.arguments})"

# TODO: typed arguments idea

class ConsoleArguments:
	"""
	A console arguments manager that holds information about and offers API functionality for the console options and
	flags passed into the program. It immediately tries to read from ``sys.argv`` if the ``no_load`` option is not set
	upon creation of an instance.

	:param argnames: a list of single-letter strings defining the options, adding ``:`` to the end of a letter indicates
	 	that a value must be passed to this flag
	:param kwargnames: a list of multi-letter string defining long options, adding ``=`` to the end of a string indicates
	 	that a value must be passed to this flag
	:param no_load: keyword-only argument, prohibits the console manager from automatically reading ``sys.argv`` upon
		creation of the console arguments manager object

	:raises ValueError: if any option or long option share the same name
	:raise ConsoleArgsError: if there was an error while parsing the ``sys.argv`` input
	"""

	# constants
	_SET_TOTAL: Final = "set"
	_SET_ARGS: Final = "args"
	_SET_KWARGS: Final = "kwargs"
	_SET_PARS: Final = "parameters"
	_REQUIRED: Final = "required"
	_REQUIRED_AND_SET: Final = "required and set"

	def __init__(self, argnames: Iterable[str], kwargnames: Iterable[str], *, no_load: bool = False):
		# check that arg-names and kwarg-names don't overlap
		overlap = [(a, b) for a in argnames for b in kwargnames if a.replace(":", "") == b.replace("=", "")]
		if len(overlap) > 0:
			raise ValueError(f"Arguments and keyword arguments can not share the same name (args and kwargs "
							 f"{overlap!r} overlap).")

		# init vars in case noLoad is set
		self._requires_arg = {}
		self._args, self._kwargs, self._pars = {}, {}, []

		# load argument names into string
		self._argnames = str()
		for argname in argnames:
			self._argnames += argname
		# load kwarg names into list
		self._kwargnames = kwargnames

		# set which options require an argument
		for argname in argnames:
			self._requires_arg[argname.replace(":", "").strip()] = argname[-1] == ":"
		for kwargname in kwargnames:
			self._requires_arg[kwargname.replace("=", "").strip()] = kwargname[-1] == "="

		# load arguments into class
		if not no_load:
			self._load_arguments()

	def _load_arguments(self) -> None:
		"""	
		Load all arguments defined by the passed arg and kwarg names into :py:class:`ConsoleArguments` by reading from
		`sys.argv`.

		:raise ConsoleArgsError: if there was an error while parsing
		"""
		try:
			_args_in = getopt(sys.argv[1:], self._argnames, self._kwargnames)
		except GetoptError as e:
			raise ConsoleArgsError("Error while running getopt", sys.argv[1:]) from e

		# check if _args_in order has potentially been read incorrectly by seeing if any parameter is
		# also named in the args or kwargs
		if any(arg[1:] in self._argnames.replace(":", "")
			   or arg[2:] in [x.replace("=", "") for x in self._kwargnames]
			   for arg in _args_in[1]):
			raise ConsoleArgsError("Parameter found in arguments, maybe you put them in the wrong order?", _args_in[1])

		# save parameters into cls, preserving order
		self._pars = _args_in[1]

		# iterate over and save the valid arguments and split them into args and kwargs
		for arg, val in _args_in[0]:
			if arg.startswith("--"):
				self._kwargs[arg[2:].strip()] = val
			elif arg.startswith("-"):
				self._args[arg[1:].strip()] = val
			else:
				raise ConsoleArgsError(f"'getopt.getopt' returned an invalid argument-pair while parsing: "
									   f"{(arg, val)!r}. (This should not occur.)", _args_in[0])

	@property
	def args(self) -> Iterator[Tuple[str, str]]:
		""" Returns all flags passed in ``sys.argv`` as iterator. """
		for key in self._args.keys():
			yield key, self[key]

	@property
	def kwargs(self) -> Iterator[Tuple[str, str]]:
		""" Returns all long flags passed in ``sys.argv`` as iterator. """
		for key in self._kwargs.keys():
			yield key, self[key]

	@property
	def pars(self) -> Iterator[str]:
		""" Returns all parameters passed in ``sys.argv`` as iterator. """
		for par in self._pars:
			yield par

	@property
	def requires_arg(self) -> Dict[str, bool]:
		return dict(self._requires_arg)

	@property
	def set_total(self) -> int:
		"""
		See other size_dict properties:

		:returns: the amount of set args, keyword args, and parameters.
		"""
		return self.size_dict[self._SET_TOTAL]

	@property
	def set_args(self) -> int:
		"""
		See other size_dict properties:

		:returns: the amount of set args.
		"""
		return self.size_dict[self._SET_ARGS]

	@property
	def set_kwargs(self) -> int:
		"""
		See other size_dict properties:

		:returns: the amount of set keyword args.
		"""
		return self.size_dict[self._SET_KWARGS]

	@property
	def set_pars(self) -> int:
		"""
		See other size_dict properties:

		:returns: the amount of set parameters.
		"""
		return self.size_dict[self._SET_PARS]

	@property
	def required(self) -> int:
		"""
		See other size_dict properties:

		:returns: the amount of required args (e.g. a flag ``a:``).
		"""
		return self.size_dict[self._REQUIRED]

	@property
	def required_and_set(self) -> int:
		"""
		See other size_dict properties:

		:returns: the amount of required and set args (i.e. same as :py:attr:`required` but only counts ``a:`` if it
			was also set).
		"""
		return self.size_dict[self._REQUIRED_AND_SET]

	@property
	def size_dict(self) -> Dict[str, int]:
		"""
		Returns a dictionary containing:
			* the amount of set args + keyword args (:py:const:`_SET_TOTAL`),
			* the amount of set args (:py:const:`_SET_ARGS`),
			* the amount of set keyword args (:py:const:`_SET_KWARGS`),
			* the amount of set parameters (:py:const:`_SET_PARS`),
			* the amount of required args (:py:const:`_REQUIRED`),
			* the amount of required and set args (:py:const:`_REQUIRED_AND_SET`).

		:return: a dictionary containing the keys held as constant static variables in the :py:class:`ConsoleArguments`
			class
		"""
		result: Dict[str, int] = {self._SET_TOTAL       : len(self._args) + len(self._kwargs) + len(self._pars),
								  self._SET_ARGS        : len(self._args),
								  self._SET_KWARGS      : len(self._kwargs),
								  self._SET_PARS        : len(self._pars),
								  self._REQUIRED        : len([a for a in self._requires_arg.values()
															   if a]),
								  self._REQUIRED_AND_SET: len([a for a in self._requires_arg.items()
															   if a[1] and a[0] in self])}
		return result

	def requires(self, options: Union[int, str, List[str], Dict[str, str]]) \
			-> Callable[[Callable[..., _R]], Callable[..., _R]]:
		"""
		Function decorator that only executes the function if the desired options are detected using the same mechanism
		by which :py:meth:`__contains__` operates.
		"""

		def __decorator__(func: Callable[..., _R]) -> Callable[..., _R]:
			def __wrapper__(*args, **kwargs):
				if options in self:
					return func(*args, **kwargs)

			return copy_func_attrs(__wrapper__, func, "requires")

		return __decorator__

	def __contains__(self, options: Union[int, str, List[str], Dict[str, str]], *, _all: bool = True) -> bool:
		"""
		:param _all: can be set to ``True`` for checking against all values of ``type(options) == list/set`` or to
			``False`` for only checking if any match
		:return: ``True`` if the options is found in ``args`` or ``kwargs``.
		"""
		is_int, is_str, is_list, is_dict = isinstance(options, int), isinstance(options, str), \
										   isinstance(options, list), isinstance(options, dict)
		if not any((is_int, is_str, is_list, is_dict)):
			raise TypeError(f"Illegal type '{options.__class__.__name__}' for argument 'options' ('int', 'str', "
							f"'list' or 'dict' expected).")

		intersection_min = 0
		if (is_list or is_dict) and _all:
			intersection_min = len(options) - 1

		if is_int:
			return 0 <= options < len(self._pars)
		elif is_str:
			return options in self._args or options in self._kwargs  # check if key exists
		elif is_list:
			options = set(options)
			return len(options & set(self._args.keys())) \
				   + len(options & set(self._kwargs.keys())) \
				   + len(options & set(range(len(self._pars)))) \
				   > intersection_min  # check if all or any keys exist
		elif is_dict:
			count = 0
			for b in options.items():
				if b in self._args.items() or b in self._kwargs.items() or b in enumerate(self._pars):
					count += 1
				# check if all or any keys exist and the corresponding values match
				if count > intersection_min:
					return True
			return False

	def __getitem__(self, key: Union[int, str]) -> str:
		"""
		Returns an argument/keyword argument if the supplied key is a ``str`` object. If the supplied key is of type
		``int``, the corresponding parameter is returned.
		"""
		if isinstance(key, str):
			if key in self._args:
				return self._args[key]
			elif key in self._kwargs:
				return self._kwargs[key]
		elif isinstance(key, int):
			if (0 <= key < len(self._pars)) or (0 > key >= - len(self._pars)):
				return self._pars[key]
		else:
			raise TypeError(f"Key is of the wrong type (expected 'str' or 'int', received '{key.__class__.__name__}')")

		# key not found
		raise KeyError(f"key {key!r} not found in {self!r}")

	def __len__(self) -> int:
		return self.set_total

	def __iter__(self) -> Iterator[Tuple[Union[str, int], str]]:
		"""
		Iterate over :py:attr:`args`, then :py:attr:`kwargs`, and finally enumerate all :py:attr:`pars` entries.
		"""
		for key in self._args.keys():
			yield key, self[key]
		for key in self._kwargs.keys():
			yield key, self[key]
		for key in range(len(self._pars)):
			yield key, self[key]

	def __repr__(self) -> str:
		return repr_str(self, ConsoleArguments.args, ConsoleArguments.kwargs, ConsoleArguments.pars)

	def __str__(self) -> str:
		return repr_str(self, ConsoleArguments.args, ConsoleArguments.kwargs, ConsoleArguments.pars,
						ConsoleArguments.set_args, ConsoleArguments.set_kwargs, ConsoleArguments.set_pars)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: Work on binary IO variable saving system
