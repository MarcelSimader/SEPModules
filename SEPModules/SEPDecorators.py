"""
:Author: Marcel Simader
:Date: 01.04.2021

.. versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import time
from types import FunctionType
from typing import Callable, Final, Tuple, TypeVar, AnyStr, Union, NoReturn

from SEPModules.SEPPrinting import cl_s, time_str, CYAN

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

WRAPPER_PREFIX: Final[str] = "wrapped"
""" The name to use for wrapped functions. """

_R: Final = TypeVar("_R")
""" The generic type variable to use for function returns in the :py:mod:`SEPDecorators` module. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def copy_func_attrs(func: Callable[..., _R], func_from: Callable, wrapper_name: AnyStr) -> Callable[..., _R]:
	"""
	Copies the ``__name__``, ``__doc__``, and if possible ``__annotations__`` attributes of ``func_from`` to ``func``.
	The name will follow the following form: :py:data:`WRAPPER_PREFIX` _ ``wrapper_name`` _ ``func_from's name``.

	:param func: the function whose attributes are to be updated
	:param func_from: the function whose attributes should be copied to ``func``
	:param wrapper_name: together with :py:data:`WRAPPER_PREFIX` this will be prefixed to the output function's name
	:return: the function with copied attributes
	"""
	try:
		func.__name__ = f"{WRAPPER_PREFIX}_{str(wrapper_name)}_{func_from.__name__}"
		func.__doc__ = func_from.__doc__
		if isinstance(func_from, FunctionType):
			func: FunctionType
			func.__annotations__ = func_from.__annotations__
	finally:
		return func

def lock(func: Callable, error: Union[Exception, Callable[..., Exception]]) -> Callable[..., NoReturn]:
	"""
	Lock a function by unconditionally raising the passed error upon it being called.

	:param func: the function to copy attributes from to populate the new locked method
	:param error: can be one of two types:
		* an exception object
		* a callable which received the arguments that were passed to ``func`` which returns an exception
	:return: a new function which always raises the exception defined by ``error`` upon being called
	"""

	def __lock__(*args, **kwargs) -> NoReturn:
		if isinstance(error, Exception):
			raise error
		elif callable(error):
			_err = error(*args, **kwargs)
			if not isinstance(_err, Exception):
				raise TypeError(f"callable 'error' did not return object of type 'Exception', "
								f"but {type(_err).__name__!r}")
			else:
				raise _err
		else:
			raise TypeError(f"'error' argument of lock function must be either of type 'Exception' or "
							f"'Callable[..., Exception], but received {type(error).__name__!r}")

	return copy_func_attrs(__lock__, func, "locked")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ DECORATORS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def timed_return(func: Callable[..., _R]) -> Callable[..., Tuple[_R, float]]:
	"""
	Same functionality as :py:func:`timed` decorator but does not print automatically. Can be used in the following way: ::

		@timed_return
		def advanced_add(a: int, b: int) -> int:
			for _ in range(b):
				a += 1
			return a

	And now calling the function: ::

		result, time = advanced_add(20, 621421)

	:returns: the return value of the function and the time it took to execute in seconds
	"""

	def __wrapper__(*args, **kwargs):
		s_time = time.perf_counter()
		ret = func(*args, **kwargs)
		dur = time.perf_counter() - s_time
		return ret, dur

	return copy_func_attrs(__wrapper__, func, "timed_return")

def timed(func: Callable[..., _R]) -> Callable[..., _R]:
	"""
	Times the decorated function and prints the amount of time it took to execute.

	:returns: the return value of provided function
	"""

	def __wrapper__(*args, **kwargs):
		ret, dur = timed_return(func)(*args, **kwargs)
		print(f"{cl_s(func.__name__, CYAN)} took {cl_s(time_str(dur), CYAN)} to execute")
		return ret

	return copy_func_attrs(__wrapper__, func, "timed")

# def annotation_type_check(func: Callable[..., R]) -> Callable[..., R]:
# 	"""
#
# 	:param func:
# 	:return:
# 	"""
# 	try:
# 		signature = inspect.signature(func, follow_wrapped=True)
# 	except Exception as e:
# 		raise TypeError(f"Cannot decorate function {func.__name__!r} with annotation_type_check") from e
#
# 	# instance check function
# 	def type_error(var_name, var_val, annotation, desc=""):
# 		# abort conditions
# 		if annotation == inspect.Parameter.empty:
# 			return
#
# 		# type check conditions
# 		error_obj = TypeError(f"Invalid type for {desc}argument {var_name!r} of function {func.__name__!r}: received "
# 							  f"{var_val.__class__.__name__!r}, but expected {annotation!s}")
# 		if (type(annotation) is type) or \
# 				(hasattr(annotation, "_is_runtime_protocol") and annotation._is_runtime_protocol):
# 			if not isinstance(var_val, annotation):
# 				raise error_obj
# 		else:
# 			warn(RuntimeWarning(f"Could not type check annotation {annotation!s}"))
#
# 	def __wrapper__(*args, **kwargs):
# 		bound_arguments = signature.bind(*args, **kwargs)
# 		bound_arguments.apply_defaults()
# 		parameters = signature.parameters
# 		# iterate over bound pars
# 		for name, val in bound_arguments.arguments.items():
# 			try:
# 				par = parameters[name]
# 				annotation = par.annotation
# 			except KeyError as ke:
# 				raise KeyError(f"Cannot find argument {name!r} of function {func.__name__!r} for "
# 							   f"annotation_type_check") from ke
# 			# check types
# 			print(name, val, annotation, flush=True)
# 			if par.kind == inspect.Parameter.VAR_POSITIONAL:
# 				for x in val:
# 					type_error(name, x, annotation, "variable positional ")
# 			elif par.kind == inspect.Parameter.VAR_KEYWORD:
# 				for x in val.values():
# 					type_error(name, x, annotation, "variable keyword ")
# 			else:
# 				type_error(name, val, annotation)
#
# 	return copy_func_attrs(__wrapper__, func, "annotation_type_check")

# def bind_free_propositional_vars(func: Callable[..., R]) -> Callable[..., R]:
# 	"""
# 	Binds all keyword-only arguments of function ``func`` which have no default value to a unique :py:class:`AtomicProposition`.
# 	This function decorator works similarly to ``functools.partial``.
#
# 	Example: Notice how ``a``, and ``b`` are never passed to ``test``: ::
#
# 		@bind_free_propositional_vars
# 		def test(*, a, b):
# 			formula = (~b | a) == (b >> a)
#
# 		test()
#
# 	:param func: the function to decorate
# 	:return: the decorated function, where each non-default valued keyword-only argument is bound to a unique atomic
# 		proposition object
# 	"""
#
# 	if isinstance(func, FunctionType):
# 		func: FunctionType
# 		signature = inspect.signature(func, follow_wrapped=True)
# 		props = {name: AtomicProposition() for name, par in signature.parameters.items()
# 				 if par.kind == inspect.Parameter.KEYWORD_ONLY and par.default is par.empty}
#
# 		def __wrapper__(*args, **kwargs):
# 			return func(*args, **props, **kwargs)
#
# 		return copy_func_attrs(__wrapper__, func, "bind_prop_vars")
# 	else:
# 		warn(RuntimeWarning("received function is not of type FunctionType, are you trying to decorate a builtin?",
# 							{"received type": type(func)}))
# 		return func
