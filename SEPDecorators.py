#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++
import time
from inspect import signature, Parameter, _empty
from itertools import zip_longest
import concurrent.futures
from concurrent.futures import ProcessPoolExecutor

import unittest

import SEPPrinting
from SEPPrinting import cl_p, get_time_str, NAME, NUMBER, ERROR, WARNING, RESET_ALL, CYAN

fillChar = "~"
maxLineLength = 80
__wrapName__ = "__wrap__"

#+++++++++++++++++++++++++++++++
#++++++++++MODULE CODE++++++++++
#+++++++++++++++++++++++++++++++

#++++++++++FUNCTIONS++++++++++

def timedReturn(func):
	"""
	Same functionality as SEPTiming.timed decorator but returns the time and return-value as dictionary.
	"""
	def __wrap__(*args, **kwargs):
		sTime = time.perf_counter()
		r = func(*args, **kwargs)
		tTime = time.perf_counter() - sTime
		return {"return": r, "time": tTime}
	return __wrap__

def timed(func):
	"""
	Times the decorated function and prints the amount of time it took to execute. Returns the return-value of provided function.
	"""
	def __wrap__(*args, **kwargs):
		timedFunc = timedReturn(func)
		r = timedFunc(*args, **kwargs)
		print("{} took {} to execute.".format(cl_p(func.__name__, NAME), cl_p(get_time_str(r["time"]))))
		return r["return"]
	return __wrap__

def check_type(iterable=None, enable=True):
	"""
	Automate the checking of argument types for a function.
	'enable' value toggles type checking on or off. 
	'iterable' value of form {'arg_name': [typ1, typ2, ...], ...} tells typer checker which values an iterable is permitted to hold.
	"""
	if not (type(iterable) is dict or iterable is None and type(enable) is bool):
		raise TypeError("Decorator 'check_type' expects arguments 'iterable' and 'enable' to be of types 'dict' and 'bool' respectively.")
	
	#clean up iterable dict
	if iterable is not None:
		iterable = {k: tuple(v) if type(v) is list else tuple([v]) for k, v in iterable.items()}
		iterable_name = {k: tuple([i.__name__ for i in v]) for k, v in iterable.items() if v is not None}
	
	def __sup_wrapper__(func):
		_check_range_flag = False
		
		func_signature = signature(func)
		
		#filter return annotation
		func_signature_return_annotation = tuple(func_signature.return_annotation) if type(func_signature.return_annotation) is list else \
																			 tuple([func_signature.return_annotation])
		func_signature_return_annotation_name = tuple(n.__name__ for n in func_signature_return_annotation)
		
		#filter parameter input a bit
		func_pars = {k: (tuple(v.annotation) if type(v.annotation) is list else \
								tuple([v.annotation])) for k, v in dict(func_signature.parameters).items()}
		for k, v in func_pars.items():
			if len(v) == 1 and type(v[0]) is range: 
				func_pars[k] = tuple([v[0], int])
				_check_range_flag = True
		
		func_par_names = {k: tuple([type(a).__name__ for a in v]) for k, v in func_pars.items() if v is not None}
		
		#internal function to abstract raising error
		def raise_TypeError(f, i, an, pn, val, types):
			if type(val) not in types:
				raise TypeError("Function '{}' expected type of {}argument '{}' to be in {}, but received '{}'.".format(\
															f, i, an, pn, val.__class__.__name__))
		
		def __wrapper__(*args, **kwargs):
			if enable:
				func_binding = func_signature.bind(*args, **kwargs)
				func_binding.apply_defaults()
				
				#test for type matching in ---
				for name, val in func_binding.arguments.items():
					#iterable match case
					if iterable is not None and name in iterable.keys():
						[None for el in val if raise_TypeError(func.__name__, "elements of ", name, iterable_name[name], el, iterable[name])]
					#annotation match case
					if _empty not in func_pars[name]:
						raise_TypeError(func.__name__, "", name, func_par_names[name], val, func_pars[name])
					
					#check for int ranges
					if _check_range_flag and type(func_pars[name][0]) is range:
						if val not in func_pars[name][0]:
							raise ValueError("Value '{}' for argument '{}' outside of range (expected range '{} to {} with step {}').".format(\
											val, name, func_pars[name][0].start, func_pars[name][0].stop, func_pars[name][0].step))
					
			#call func and save result
			result = func(*args, **kwargs)
			
			if enable and _empty not in func_signature_return_annotation:
				#check output of function
				if type(result) not in func_signature_return_annotation:
					raise TypeError("Return value type of function '{}' is expected to be in {}, but received '{}'.".format(\
										func.__name__, func_signature_return_annotation_name, result.__class__.__name__))
				
			return result
			
		#set the correct name for sub_wrapper
		__wrapper__.__name__ = "check_type_{}".format(func.__name__)
		return __wrapper__
	return __sup_wrapper__

#deprecated
def compare(funcs, repetitions=1, *args, **kwargs):
	raise DeprecationWarning("'Compare' function will be removed or rewritten.")
	"""
	Compare the execution times of an array of functions.
	Functions need to share the same variable input, but can each have unique or shared optional arguments.
	The Time differences, return values and individual timings are printed to the console.

	Takes:
		-funcs, array of functions
		-*args and **kwargs, arguments for function calls

	Returns:
		-Return values of the individual functions.

	TODO: Just rewrite this whole damn mess -- It's bad.
	"""
	#++++++++++sanitize input++++++++++
	# detect if function is already wrapped
	for i, f in enumerate(funcs):
		if f.__name__ == __wrapName__:
			raise ValueError("Function no. {} is already decorated.".format(i+1))
	
	def __getOptional__(funcPars):
		"""
		Helper function for detecting optional kwargs.
		"""
		return len([a for a in funcPars.values() if a.default is not Parameter.empty])
	
	#++++check compatible args and kwargs
	funcPars = [signature(f).parameters for f in funcs]
	#find longest list of pars
	baseParIndex, maxPars, totalOptPars = 0, 0, 0
	for i,funcPar in enumerate(funcPars):
		if len(funcPar) - __getOptional__(funcPar) > maxPars: maxPars, baseParIndex = len(funcPar) - __getOptional__(funcPar), i
		totalOptPars += __getOptional__(funcPar)
	maxOptPars = __getOptional__(funcPars[baseParIndex])
	
	#define # of args
	expected = maxPars
	received = {"args":len(args),"kwargs":len(kwargs)}
	
	#detect missing expected args
	for funcPar, f in zip(funcPars, funcs):
		has = len(funcPar) - __getOptional__(funcPar)
		if has > expected:
			raise TypeError("Invalid number of arguments (expected {}, has {} in function {}).".format(expected, has, f.__name__))
			
	#check if provided args match expected args
	if received["kwargs"] > totalOptPars:
		raise TypeError("Invalid number of shared optional arguments (expected no more than {}, received {}).".format(totalOptPars, received["kwargs"]))
	if received["args"] != expected:
		raise TypeError("Invalid number of shared arguments (expected {}, received {}).".format(expected, received["args"]))
	
	#++++++++++time functions++++++++++
	_timedReturn = {}
	for f, fPs in zip(funcs, funcPars):
		#set which arguments apply to this function
		argsFiltered = args[:len(fPs) - __getOptional__(fPs)]
		kwargsFiltered = dict((k, v) for k, v in kwargs.items() if k in fPs)
		if __getOptional__(fPs) > 0:
			timer = time.perf_counter()
			for _ in range(repetitions - 1): f(*argsFiltered, **kwargsFiltered)
			r = f(*argsFiltered, **kwargsFiltered)
			_timedReturn[f]= {"return": r, "time": (time.perf_counter() - timer) / repetitions}
		else:
			timer = time.perf_counter()
			for _ in range(repetitions - 1): f(*argsFiltered)
			r = f(*argsFiltered)
			_timedReturn[f]= {"return": r, "time": (time.perf_counter() - timer) / repetitions}
	
	#++++++++++print output++++++++++
	longestName = max([len(keys.__name__) for keys in _timedReturn.keys()])
	out = {"return": ["",""], "time": ["",""], "diff": ["",""]}
	
	#temporary function for cutting off lines
	def cut_save_line_wFormat(strs, section):
		out[section][0] += strs[0] if len(strs[1]) <= maxLineLength else \
														strs[0][:maxLineLength + (len(strs[0]) - len(strs[1]) - 7)] + RESET_ALL + "...\n"
		out[section][1] += strs[1] if len(strs[1]) <= maxLineLength else \
														strs[1][:maxLineLength] + "...\n"
		
	#loop through output
	for f, kv in _timedReturn.items():
		name = f.__name__.ljust(longestName)

		cut_save_line_wFormat(["{} returned: {}\n".format(cl_p(name, NAME), cl_p(kv["return"], NUMBER)), \
													 "{} returned: {}\n".format(name, kv["return"])], \
													 "return")
		
		cut_save_line_wFormat(["{} took: {}\n".format(cl_p(name, NAME), cl_p(get_time_str(kv["time"]), NUMBER)), \
													 "{} took: {}\n".format(name, get_time_str(kv["time"]))], \
													 "time")
		
		for f1, kv1 in _timedReturn.items():
			name1 = f1.__name__.ljust(longestName)
			tDiff = kv["time"]-kv1["time"]
			
			if f is not f1 and tDiff >= 0:
				cut_save_line_wFormat(["Diff. {} and {}: {}\n".format(cl_p(name, NAME), cl_p(name1, NAME), cl_p(get_time_str(tDiff), NUMBER)), \
															 "Diff. {} and {}: {}\n".format(name, name1, get_time_str(tDiff))], \
															 "diff")
	
	longestLine = min([max(map(lambda l: max(map(lambda s: len(s), l[1].split("\n"))), out.values())), maxLineLength])
	_ret = str().ljust(longestLine, fillChar) + "\n"
	for line, _ in out.values():
		_ret += line + "\n"
	return _ret

#+++++++++++++++++++++++++++
#++++++++++TESTING++++++++++
#+++++++++++++++++++++++++++

class TestRequireType(unittest.TestCase):
	
	def setUp(self):
		def add(a :int, b :int) -> float:
			return a + b
		self.add = add
		
		def addLists(list1 :list, list2 :list, list3 :list):
			result = []
			for el in [list1, list2, list3]:
				result = result + el
			return result
		self.addLists = addLists
		
		def nothing():
			return
		self.nothing = nothing
		
		def rangeAdd(a :range(0,10), b :range(0, 20, 2)):
			return a + b
		self.rangeAdd = rangeAdd
		
	def tearDown(self):
		del self.add, self.addLists, self.nothing, self.rangeAdd
	
	def test_check_type_TypeError(self):
		with self.assertRaises(TypeError):
			_func = check_type(enable=3)(self.add)
			_func(2, 2)
			
		with self.assertRaises(TypeError):
			_func = check_type(enable=True, iterable=[int, float])(self.add)
			_func(2, 2)
			
	def test_check_type_simple(self):
		with self.assertRaises(TypeError):
			_func = check_type()(self.add)
			_func(2, 2.3)
			
		with self.assertRaises(TypeError):
			_func = check_type()(self.add)
			_func("test", 3)
		
	def test_check_type_iter(self):
		with self.assertRaises(TypeError):
			_func = check_type(iterable={"list1": int, "list2": float, "list3": str})(self.addLists)
			_func([2, 3], [3.3, True], ["test"])
			
	def test_check_type_result(self):
		with self.assertRaises(TypeError):
			_func = check_type()(self.add)
			_func(2, 2)
			
	def test_check_type_range(self):
		with self.assertRaises(ValueError):
			_func = check_type()(self.rangeAdd)
			_func(2, 11)
	
def test_performance_check_type(n=1_000):
	def add(a :int, b:float) -> type(None):
		return None
		
	add_norm = add
	add_type = check_type()(add)
	
	_range = range(n)
	
	@timedReturn
	def __test_performance_check_type__(func, *args, **kwargs):
		for _ in _range:
			func(*args, **kwargs)
			
	times = {func.__name__: __test_performance_check_type__(func, 3, 5.5)["time"] for func in [add_norm, add_type]}
	
	for k, v in times.items():
		print("{} took {}.".format(cl_p(k, NAME), cl_p(get_time_str(v), NUMBER)))
	
if __name__ == "__main__":
	test_performance_check_type()
	
	unittest.main()