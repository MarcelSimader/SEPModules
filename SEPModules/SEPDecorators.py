"""
Author: Marcel Simader
Data: 01.04.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import time
from typing import Callable, Dict, Union, Any

from SEPModules.SEPPrinting import cl_p, get_time_str, NAME

WRAPPER_NAME = "wrapped_"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def timed_return(func : Callable) -> Callable:
	"""
	Same functionality as SEPTiming.timed decorator but does not print automatically
	:returns: the time and return-value as dictionary.
	"""
	def __wrapper__(*args, **kwargs) -> Dict[str, Union[Any, int]]:
		s_time = time.perf_counter()
		r = func(*args, **kwargs)
		t_time = time.perf_counter() - s_time

		return {"return": r, "time": t_time}
	
	__wrapper__.__name__ = "{}timedReturn_{}".format(WRAPPER_NAME, func.__name__)
	return __wrapper__

def timed(func : Callable) -> Callable:
	"""
	Times the decorated function and prints the amount of time it took to execute.
	:returns: the return-value of provided function.
	"""
	def __wrapper__(*args, **kwargs):
		timed_func = timed_return(func)
		r = timed_func(*args, **kwargs)
		print("{} took {} to execute.".format(cl_p(func.__name__, NAME), cl_p(get_time_str(r["time"]))))
		return r["return"]
	
	__wrapper__.__name__ = "{}timed_{}".format(WRAPPER_NAME, func.__name__)
	return __wrapper__

def check_type():
	"""
	TODO: rewrite this using function annotations instead of my shitty system or just leave it out cause it definitely exists already
	"""
	raise DeprecationWarning("check_type")