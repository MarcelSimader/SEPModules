"""
:Author: Marcel Simader
:Date: 01.04.2021

.. versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import time
from typing import Callable, Final, Tuple, TypeVar

from SEPModules.SEPPrinting import get_time_str

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__WRAPPER_NAME__: Final = "wrapped_"
""" The name to use for wrapped functions. """

R : Final = TypeVar("R")
""" The type variable to use for function returns. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def timed_return(func: Callable[..., R]) -> Callable[..., Tuple[R, float]]:
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

	def __wrapper__(*args, **kwargs) -> Tuple[R, float]:
		s_time = time.perf_counter()
		ret = func(*args, **kwargs)
		dur = time.perf_counter() - s_time
		return ret, dur

	try:
		__wrapper__.__name__ = f"{__WRAPPER_NAME__}timed_return_{func.__name__}"
		__wrapper__.__annotations__ = func.__annotations__
		__wrapper__.__doc__ = func.__doc__
	finally:
		return __wrapper__

def timed(func: Callable[..., R]) -> Callable[..., R]:
	"""
	Times the decorated function and prints the amount of time it took to execute.

	:returns: the return value of provided function
	"""

	def __wrapper__(*args, **kwargs) -> R:
		ret, dur = timed_return(func)(*args, **kwargs)
		print(f"{func.__name__} took {get_time_str(dur)} to execute.")
		return ret

	try:
		__wrapper__.__name__ = f"{__WRAPPER_NAME__}timed_{func.__name__}"
		__wrapper__.__annotations__ = func.__annotations__
		__wrapper__.__doc__ = func.__doc__
	finally:
		return __wrapper__
