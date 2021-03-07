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
	SET_TOTAL        = "set"
	SET_ARGS         = "args"
	SET_KWARGS       = "kwargs"
	SET_PARS         = "parameters"
	REQUIRED         = "required"
	REQUIRED_AND_SET = "required and set"
	
	#vars
	_argnames, _kwargnames = None, None
	requires_arg = {}
	_args, _kwargs, _pars = {}, {}, []
	
	def __init__(self, argnames, kwargnames, noLoad=False):		
		#check if arg-names and kwarg-names are of type list
		if not (type(argnames) is list and type(kwargnames) is list):
			raise TypeError("Parameters 'arg-names' and 'kwarg-names' must be of type list (received {} and {}).".format(\
														argnames.__class__.__name__, kwargnames.__class__.__name__))
		
		#check that arg-names and kwarg-names don't overlap
		overlap = [(a, b) for a in argnames for b in kwargnames if a.replace(":", "") == b.replace("=", "")]
		if len(overlap):
			raise ValueError("Arguments and keyword arguments can not share the same name (args and kwargs {} overlap).".format(overlap))
		
		#init vars in case noLoad is set
		self.requires_arg = {}
		self._args, self._kwargs, self._pars = {}, {}, []
		
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
		
		#check if _args_in order is fishy by seeing if any parameter has a dash
		if any(["-" in arg for arg in _args_in[1]]):
			raise Exception("Argument or keyword argument '{}' not recognized. (Maybe the arguments are in the wrong order?)".format(\
													_args_in[1][0]))
		
		#save parameters into self, preserving order
		self._pars = _args_in[1]
		
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
	def pars(self):
		for par in self._pars:
			yield par
	
	@property
	def size(self):
		"""
		Return either the amount of set args + keyword args, the amount of set args, the amount of set keyword args, the amount of required args,
		or the amount of required and set args.
		"""
		result = {self.SET_TOTAL: len(self._args) + len(self._kwargs), \
							self.SET_ARGS: len(self._args), \
							self.SET_KWARGS: len(self._kwargs), \
							self.SET_PARS: len(self._pars), \
							self.REQUIRED: len([a for a in self.requires_arg.values() if a]), \
							self.REQUIRED_AND_SET: len([a for a in self.requires_arg.items() if a[1] and a[0] in self])}
		
		#add aliases
		result.update({ "assigned": result[self.SET_TOTAL], \
										"arg": result[self.SET_ARGS], \
										"kwarg": result[self.SET_KWARGS], \
										"pars": result[self.SET_PARS], \
										"req": result[self.REQUIRED], \
										"required and assigned": result[self.REQUIRED_AND_SET], "req assigned": result[self.REQUIRED_AND_SET], "req set": result[self.REQUIRED_AND_SET]})
		return result
	
	def __contains__(self, options, all=True):
		"""
		Returns True if the options is found in args or kwargs.
		'all' can be set to True for checking against all values of "type(options) == list/set" or to False for only checking if any match.
		"""
		isInt, isStr, isList, isDict = type(options) is int, type(options) is str, type(options) is list, type(options) is dict
		if not (isInt or isStr or isList or isDict):
			raise TypeError("Illegal type '{}' for argument 'options' ('int', 'str', 'list' or 'dict' expected).".format(options.__class__.__name__))
		
		if not isInt: intersection_min = int(all) * (len(options) - 1) #type checking guarantees options has a length dunder-method implemented
		
		if isInt:
			return options >= 0 and options < len(self._pars)
		elif isStr:
			return options in self._args.keys() or options in self._kwargs.keys() #check if key exists
		elif isList:
			return len(set(options) & set(self._args.keys())) + len(set(options) & set(self._kwargs.keys())) + len(set(options) & set(range(len(self._pars)))) > intersection_min #check if all keys exist
		elif isDict:
			return len([None for b in options.items() if b in self._args.items() or b in self._kwargs.items() or b in [(i, par) for i, par in enumerate(self._pars)]]) > intersection_min #check if all keys exist and all values match
	
	def __repr__(self):
		return "ConsoleArguments<(%s, %s)>" % ([a if b != ":" else a + ":" for a, b in zip(self._argnames, self._argnames[1:] + " ") if a != ":"], self._kwargnames)
	
	def __str__(self):
		return "ConsoleArguments: (args: %s, kwargs: %s, pars: %s)" % (self._args, self._kwargs, self._pars)

	def __getitem__(self, key):
		"""
		Returns an argument/keyword argument if the supplied key is a 'str' object. If the supplied key is of type 'int', the
		corresponding parameter is returned. If the key is not found, 'None' is returned.
		"""
		#check type
		if not (type(key) is str or type(key) is int):
			raise TypeError("Key is of the wrong type (expected 'str' or 'int', received '{}').".format(key.__class__.__name__))
		
		if type(key) is str:
			if key in self._args.keys():
				return True if self._args[key] 		== "" else self._args[key] #return true if arg option (i.e. flag) is set
			elif key in self._kwargs.keys():
				return True if self._kwargs[key] 	== "" else self._kwargs[key] #return true if kwarg option (i.e. flag) is set
			else:
				return None
		else: #must be int
			if (key >= 0 and key < len(self._pars)) or (key < 0 and key >= - len(self._pars)):
				return self._pars[key]
			else:
				return None
		
	def __iter__(self):
		"""
		Enumerate args, then kwargs, then pars (in the form '(#order, par value, )').
		"""
		#combine args and kwargs
		for key in list(self._args.keys()) + list(self._kwargs.keys()) + list(range(len(self._pars))):
			yield (key, self[key])
	

