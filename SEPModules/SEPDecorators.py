#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++

import time
from inspect import signature, Parameter, _empty

from SEPModules.SEPPrinting import cl_p, get_time_str, NAME, NUMBER, RESET_ALL

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
	Automate the checking of argument types for a function using the Python annotation feature.
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