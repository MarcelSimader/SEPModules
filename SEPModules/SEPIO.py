"""
:Author: Marcel Simader
:Date: 01.04.2021

.. versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys
from getopt import getopt
from typing import List, Callable, Any, Dict, Union, Tuple, Final, Iterable, Generator, Optional, Iterator

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: typed arguments idea

class ConsoleArguments:
	"""
	A console arguments manager that holds information and offers API functionality regarding the console options and
	flags passed into the program. It immediately tries to read from `sys.argv` if the `no_load` option is not set upon creation.

	:param argnames: a list of single-letter strings defining the options, adding ':'
		to the end of a letter indicates that a value must be passed to this flag
	:param kwargnames: a list of multi-letter string defining long options, adding '='
		to the end of a string indicates that a value must be passed to this flag
	:param no_load: keyword-only argument, prohibits the console manager from automatically reading `sys.argv` upon
		creation of the console arguments manager object

	:raises ValueError: if any option or long option share the same name
	"""

	# constants
	_SET_TOTAL: Final = "set"
	_SET_ARGS: Final = "args"
	_SET_KWARGS: Final = "kwargs"
	_SET_PARS: Final = "parameters"
	_REQUIRED: Final = "required"
	_REQUIRED_AND_SET: Final = "required and set"

	@property
	def set_total(self) -> int:
		"""
		See other size properties:

		:returns: the amount of set args and keyword args.
		"""
		return self.__size__[self._SET_TOTAL]

	@property
	def set_args(self) -> int:
		"""
		See other size properties:

		:returns: the amount of set args.
		"""
		return self.__size__[self._SET_ARGS]

	@property
	def set_kwargs(self) -> int:
		"""
		See other size properties:

		:returns: the amount of set keyword args.
		"""
		return self.__size__[self._SET_KWARGS]

	@property
	def set_pars(self) -> int:
		"""
		See other size properties:

		:returns: the amount of set parameters.
		"""
		return self.__size__[self._SET_PARS]

	@property
	def required(self) -> int:
		"""
		See other size properties:

		:returns: the amount of required args (e.g. a flag `'a:'`).
		"""
		return self.__size__[self._REQUIRED]

	@property
	def required_and_set(self) -> int:
		"""
		See other size properties:

		:returns: the amount of required and set args (i.e. same as :py:attr:`required` but only counts `'a:'` if it
			was also set).
		"""
		return self.__size__[self._REQUIRED_AND_SET]

	def __init__(self, argnames: Iterable[str], kwargnames: Iterable[str], *, no_load: bool = False):
		# check that arg-names and kwarg-names don't overlap
		overlap = [(a, b) for a in argnames for b in kwargnames if a.replace(":", "") == b.replace("=", "")]
		if len(overlap):
			raise ValueError(
					"Arguments and keyword arguments can not share the same name (args and kwargs {} overlap).".format(
						overlap))

		# init vars in case noLoad is set
		self.requires_arg = {}
		self._args, self._kwargs, self._pars = {}, {}, []

		# load argument names into string
		self._argnames = str()
		for argname in argnames: self._argnames += argname
		# load kwarg names into list
		self._kwargnames = kwargnames

		# set which options require an argument
		for argname, kwargname in zip(argnames, kwargnames):
			self.requires_arg[argname.replace(":", "")] = argname[-1:] == ":"
			self.requires_arg[kwargname.replace("=", "")] = kwargname[-1:] == "="

		# load arguments into class
		if not no_load:
			self.__load_arguments__()

	def __load_arguments__(self):
		"""	
		Load all arguments defined by the passed arg and kwarg names into :py:class:`ConsoleArguments` by reading from `sys.argv`.
		"""
		_args_in = getopt(sys.argv[1:], self._argnames, self._kwargnames)

		# check if _args_in order has potentially been read incorrectly by seeing if any parameter is
		# also named in the args or kwargs
		if any([arg in ["-" + a.replace(":", "") for a in self._argnames] or arg in ["--" + a.replace("=", "") for a in
																					 self._kwargnames] for arg in
				_args_in[1]]):
			raise Exception(
					"Argument or keyword argument '{}' not recognized. (Maybe the arguments are in the wrong order?)".format(
							_args_in[1][0]))

		# save parameters into self, preserving order
		self._pars = _args_in[1]

		# iterate over and save the valid arguments and split them into args and kwargs
		for arg, val in _args_in[0]:
			if arg[:2] == "--":
				self._kwargs[arg[2:]] = val
			elif arg[:1] == "-":
				self._args[arg[1:]] = val
			else:
				raise Exception(
						"'getopt.getopt' returned an invalid argument-pair while parsing: {}. (This should not occur.)".format(
								(arg, val)))

	def requires(self, options: Union[int, str, List[str], Dict[str, str]]) -> Callable[..., Any]:
		"""
		Function decorator that only executes the function if the desired options are detected using the same mechanism
		by which :py:meth:`__contains__` operates.
		"""

		def __wrapper__(func):
			def __sub_wrapper__(*args, **kwargs):
				if options in self:
					return func(*args, **kwargs)

			return __sub_wrapper__

		return __wrapper__

	@property
	def args(self) -> Iterator[Tuple[str, str]]:
		"""Returns all flags passed in `sys.argv` as iterator."""
		for key in self._args.keys():
			yield key, self[key]

	@property
	def kwargs(self) -> Iterator[Tuple[str, str]]:
		"""Returns all long flags passed in `sys.argv` as iterator."""
		for key in self._kwargs.keys():
			yield key, self[key]

	@property
	def pars(self) -> Iterator[str]:
		"""Returns all parameters passed in `sys.argv` as iterator."""
		for par in self._pars:
			yield par

	@property
	def __size__(self) -> Dict[str, int]:
		"""
		Returns either:
			* the amount of set args + keyword args (:py:const:`_SET_TOTAL`),
			* the amount of set args (:py:const:`_SET_ARGS`),
			* the amount of set keyword args (:py:const:`_SET_KWARGS`),
			* the amount of set parameters (:py:const:`_SET_PARS`),
			* the amount of required args (:py:const:`_REQUIRED`),
			* the amount of required and set args (:py:const:`_REQUIRED_AND_SET`).

		:return: a dictionary containing the keys held as constant static variables in the ConsoleArguments class
		"""
		result: Dict[str, int] = {self._SET_TOTAL       : len(self._args) + len(self._kwargs),
								  self._SET_ARGS        : len(self._args),
								  self._SET_KWARGS      : len(self._kwargs),
								  self._SET_PARS        : len(self._pars),
								  self._REQUIRED        : len([a for a in self.requires_arg.values() if a]),
								  self._REQUIRED_AND_SET: len(
										  [a for a in self.requires_arg.items() if a[1] and a[0] in self])}

		# add aliases
		result.update({"assigned"             : result[self._SET_TOTAL],
					   "arg"                  : result[self._SET_ARGS],
					   "kwarg"                : result[self._SET_KWARGS],
					   "pars"                 : result[self._SET_PARS],
					   "req"                  : result[self._REQUIRED],
					   "required and assigned": result[self._REQUIRED_AND_SET],
					   "req assigned"         : result[self._REQUIRED_AND_SET],
					   "req set"              : result[self._REQUIRED_AND_SET]})
		return result

	def __contains__(self, options: Union[int, str, List[str], Dict[str, str]], _all: bool = True) -> bool:
		"""
		Returns `True` if the options is found in `args` or `kwargs`.

		:param _all: can be set to `True` for checking against all values of `type(options) == list/set` or to `False` for only checking if any match
		"""
		is_int, is_str, is_list, is_dict = isinstance(options, int), isinstance(options, str), \
										   isinstance(options, list), isinstance(options, dict)
		if not (is_int or is_str or is_list or is_dict):
			raise TypeError(
					"Illegal type '{}' for argument 'options' ('int', 'str', 'list' or 'dict' expected).".format(
							options.__class__.__name__))

		intersection_min = 0
		if not is_int:
			# type checking guarantees options has a length built-in method implemented
			intersection_min = int(_all) * (len(options) - 1)

		if is_int:
			return 0 <= options < len(self._pars)
		elif is_str:
			return options in self._args.keys() or options in self._kwargs.keys()  # check if key exists
		elif is_list:
			return len(set(options) & set(self._args.keys())) \
				   + len(set(options) & set(self._kwargs.keys())) \
				   + len(set(options) & set(range(len(self._pars)))) \
				   > intersection_min  # check if all keys exist
		elif is_dict:
			return len([None for b in options.items()
						if b in self._args.items()
						or b in self._kwargs.items()
						or b in [(i, par) for i, par in enumerate(self._pars)]]) \
				   > intersection_min  # check if all keys exist and all values match

	def __repr__(self) -> str:
		return "ConsoleArguments<({}, {})>".format(
				[a if b != ":" else a + ":" for a, b in zip(self._argnames, self._argnames[1:] + " ") if a != ":"],
				self._kwargnames
				)

	def __str__(self) -> str:
		return f"ConsoleArguments: (args: {self._args}, kwargs: {self._kwargs}, pars: {self._pars})"

	def __getitem__(self, key: Union[int, str]) -> Optional[Union[bool, str]]:
		"""
		Returns an argument/keyword argument if the supplied key is a `str` object. If the supplied key is of type `int`, the
		corresponding parameter is returned. If the key is not found, `None` is returned.
		"""
		# check type
		if not (isinstance(key, str) or isinstance(key, int)):
			raise TypeError(
					"Key is of the wrong type (expected 'str' or 'int', received '{}').".format(key.__class__.__name__))

		if isinstance(key, str):
			if key in self._args.keys():
				# return true if arg option (i.e. flag) is set
				return True if self._args[key] == "" else self._args[key]
			elif key in self._kwargs.keys():
				# return true if kwarg option (i.e. flag) is set
				return True if self._kwargs[key] == "" else self._kwargs[key]
			else:
				return None
		else:  # must be int
			if (0 <= key < len(self._pars)) or (0 > key >= - len(self._pars)):
				return self._pars[key]
			else:
				return None

	def __iter__(self) -> Iterator[Tuple[Union[str, int], str]]:
		"""
		Iterate over :py:attr:`args`, then :py:attr:`kwargs`, and finally enumerate all :py:attr:`pars` entries.
		"""
		# combine args and kwargs
		for key in list(self._args.keys()) + list(self._kwargs.keys()) + list(range(len(self._pars))):
			yield key, self[key]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: Work on binary IO variable saving system
