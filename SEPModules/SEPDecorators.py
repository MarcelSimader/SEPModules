"""
:Author: Marcel Simader
:Date: 01.04.2021

.. versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import time
from typing import Callable, Dict, Union, Any, Final

from SEPModules.SEPPrinting import cl_s, get_time_str, NAME

__WRAPPER_NAME__ : Final = "wrapped_"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def timed_return(func : Callable) -> Callable:
	"""
	Same functionality as :py:func:`timed` decorator but does not print automatically.

	:returns: the time and return value as dictionary
	"""
	def __wrapper__(*args, **kwargs) -> Dict[str, Union[Any, int]]:
		s_time = time.perf_counter()
		r = func(*args, **kwargs)
		t_time = time.perf_counter() - s_time

		return {"return": r, "time": t_time}
	
	__wrapper__.__name__ = "{}timedReturn_{}".format(__WRAPPER_NAME__, func.__name__)
	__wrapper__.__doc__ = func.__doc__
	return __wrapper__

def timed(func : Callable) -> Callable:
	"""
	Times the decorated function and prints the amount of time it took to execute.

	:returns: the return value of provided function.
	"""
	def __wrapper__(*args, **kwargs):
		timed_func = timed_return(func)
		r = timed_func(*args, **kwargs)
		print("{} took {} to execute.".format(cl_s(func.__name__, NAME), cl_s(get_time_str(r["time"]))))
		return r["return"]
	
	__wrapper__.__name__ = "{}timed_{}".format(__WRAPPER_NAME__, func.__name__)
	__wrapper__.__doc__ = func.__doc__
	return __wrapper__
