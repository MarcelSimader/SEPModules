#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++

import sys
from getopt import getopt

from SEPModules.SEPPrinting import cl_p, CYAN

#+++++++++++++++++++++++++++++++
#++++++++++MODULE CODE++++++++++
#+++++++++++++++++++++++++++++++

#++++++++++CLASSES++++++++++

class ConsoleArguments:
	
	#constants
	__SET__ = "set"
	__ARGS__ = "args"
	__KWARGS__ = "kwargs"
	__REQUIRED__ = "required"
	__REQUIRED_AND_SET__ = "required and set"
	
	#vars
	_argnames, _kwargnames = None, None
	requires_arg = {}
	_args, _kwargs = {}, {}
	
	def __init__(self, argnames, kwargnames, noLoad=False):		
		#check if arg-names and kwarg-names are of type list
		if not (type(argnames) is list and type(kwargnames) is list):
			raise TypeError("Parameters 'arg-names' and 'kwarg-names' must be of type list (received {} and {}).".format(\
														argnames.__class__.__name__, kwargnames.__class__.__name__))
		#check that arg-names and kwarg-names don't overlap
		overlap = [(a, b) for a in argnames for b in kwargnames if a.replace(":", "") == b.replace("=", "")]
		if len(overlap):
			raise ValueError("Arguments and keyword arguments can not share the same name (args and kwargs {} overlap).".format(overlap))
			
		#load argument names into string
		self._argnames = str()
		for argname in argnames: self._argnames += argname
		#load kwarg names into list
		self._kwargnames = kwargnames
		
		#set which options require an argument
		for argname, kwargname in zip(argnames, kwargnames):
			self.requires_arg[argname.replace(":", "")] 	=   argname[-1:] == ":"
			self.requires_arg[kwargname.replace("=", "")]	= kwargname[-1:] == "="
		
		#load arguments into class
		if not noLoad: self.__load_arguments__(argnames, kwargnames)
	
	def __load_arguments__(self, argnames, kwargnames):
		"""	
		private function to load all arguments based on the names into dictionaries
		takes arg-names and kwarg-names in the form of lists and *NOT* in the form of getopt.getopt
		"""
		_args_in = getopt(sys.argv[1:], self._argnames, self._kwargnames)
		
		#check if parsing started with an argument
		if len(_args_in[0]) < 1:
			if len(_args_in[1]) < 1:
				raise RuntimeError("Missing arguments: {} and {}.".format(argnames, kwargnames)) #all args missing
			raise RuntimeError("Unexpected terminal argument '{}'.".format(_args_in[1][0])) #got unexpected argument
		#check if parsing produced an error by having an argument after -options that did not expect one
		if len(_args_in[1]) > 0:
			raise RuntimeError("Expected no argument after '{}' but received '{}'.".format(_args_in[0][-1][0], _args_in[1][0]))
			
		#iterate over and save the valid arguments and split them into args and kwargs
		for arg, val in _args_in[0]:
			if arg[:2] == "--":
				self._kwargs[arg[2:]] = val
			elif arg[:1] == "-":
				self._args[arg[1:]]		= val
			else:
				raise Exception("'getopt.getopt' returned an invalid argument-pair while parsing: {}. (This should not occur.)".format((arg, val)))
	
	def requires(self, options):
		"""
		Function decorator that only executions the function if the desired 'options' are detected using 'ConsoleArguments.__contains__(self, options)'.
		"""
		def __wrapper__(func):
			def __subwrapper__(*args, **kwargs):
				if options in self:
					return func(*args, **kwargs)
				else:
					return
			return __subwrapper__
		return __wrapper__
	
	@property
	def args(self):
		for key in self._args.keys():
			yield (key, self[key])
			
	@property
	def kwargs(self):
		for key in self._kwargs.keys():
			yield (key, self[key])
	
	@property
	def size(self):
		"""
		Return either the amount of set args + keyword args, the amount of set args, the amount of set keyword args, the amount of required args,
		or the amount of required and set args.
		"""
		result = {self.__SET__: len(self._args) + len(self._kwargs), \
							self.__ARGS__: len(self._args), \
							self.__KWARGS__: len(self._kwargs), \
							self.__REQUIRED__: len([a for a in self.requires_arg.values() if a]), \
							self.__REQUIRED_AND_SET__: len([a for a in self.requires_arg.items() if a[1] and a[0] in self])}
		
		result.update({ "assigned": result[self.__SET__], \
										"arg": result[self.__ARGS__], \
										"kwarg": result[self.__KWARGS__], \
										"req": result[self.__REQUIRED__], \
										"required and assigned": result[self.__REQUIRED_AND_SET__], "req assigned": result[self.__REQUIRED_AND_SET__], "req set": result[self.__REQUIRED_AND_SET__]})
		return result
	
	def __contains__(self, options, all=True):
		"""
		Returns True if the options is found in args or kwargs.
		'all' can be set to True for checking against all values of "type(options) == list/set" or to False for only checking if any match.
		"""
		isStr, isList, isDict = type(options) is str, type(options) is list, type(options) is dict
		if not (isStr or isList or isDict):
			raise TypeError("Illegal type '{}' for argument 'options' ('list', 'str' or 'dict' expected).".format(options.__class__.__name__))
		
		intersection_min = int(all) * (len(options) - 1) #type checking guarantees options has a length dunder-method implemented
		if isStr:
			return options in self._args.keys() or options in self._kwargs.keys() #check if key exists
		elif isList:
			return len(set(options) & set(self._args.keys())) + len(set(options) & set(self._kwargs.keys())) > intersection_min #check if all keys exist
		elif isDict:
			return len([None for b in options.items() if b in self._args.items() or b in self._kwargs.items()]) > intersection_min #check if all keys exist and all values match
	
	def __repr__(self):
		return "ConsoleArguments<(%s, %s)>" % ([a if b != ":" else a + ":" for a, b in zip(self._argnames, self._argnames[1:] + " ") if a != ":"], self._kwargnames)
	
	def __str__(self):
		return "ConsoleArguments: {args: %s, kwargs: %s}" % (cl_p(self._args, CYAN), cl_p(self._kwargs, CYAN))

	def __getitem__(self, key):
		#check type
		if type(key) is not str:
			raise TypeError("Key is of the wrong type (expected 'str', received '{}').".format(key.__class__.__name__))
		
		if key in self._args.keys():
			return True if self._args[key] == "" else self._args[key] #return true if arg option (i.e. flag) is set
		elif key in self._kwargs.keys():
			return self._kwargs[key]
		else:
			raise KeyError("'{}' was not found as argument or keyword argument.".format(key)) #throw key error if not in args or kwargs
			
	def __iter__(self):
		#combine args and kwargs
		for key in list(self._args.keys()) + list(self._kwargs.keys()):
			yield (key, self[key])
	

