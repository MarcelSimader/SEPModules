"""
:Author: Marcel Simader
:Date: 01.04.2021

.. versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import sys
from itertools import product
from math import copysign, gcd, floor, ceil
from numbers import Real, Number
from typing import Tuple, Callable, Union, Set, Optional, Iterable, TypeVar, Final

from SEPModules.SEPPrinting import cl_s, WARNING

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

T : Final = TypeVar("T")
""" Type variable for the :py:mod:`SEPMaths` module. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def __prepare_int_binary_op__(func: Callable) -> Callable:
	"""Do type checking of arithmetic binary operations on Rationals and auto-convert int or float to Rational type."""

	def __wrapper__(self, other: Union[int, float, Rational]) -> Rational:
		if not isinstance(other, (int, float, Rational)):
			raise TypeError(
					f"Illegal binary operation '{func.__name__}' of type 'Rational' and '{other.__class__.__name__}' "
					f"(expected 'int', 'Rational' or 'float').")

		if isinstance(other, (int, float)):
			other = Rational(other)  # convert c to (c / 1) (or (a / b) = c if float)
		return func(self, other)

	# replace docstring and name
	try:
		__wrapper__.doc__ = func.__doc__
		__wrapper__.__name__ = func.__name__
	finally:
		return __wrapper__

class Rational(Number):
	r"""
	Rational number of the form :math:`a/b` with :math:`a, b \in \mathbb{Z}`. Used for symbolic computations in :mod:`SEPMaths`
	module. Values are automatically simplified. The following forms are accepted, where option 1 and 3 are exact and
	option 2 will approximate the float input as integer ratio:

		+----------------------+----------------------+-----------+
		| parameter `a`        | parameter `b`        | exact?    |
		+======================+======================+===========+
		| int                  | int                  | yes       |
		+----------------------+----------------------+-----------+
		| float                | 1 or -               | no        |
		+----------------------+----------------------+-----------+
		| Rational             | 1 or -               | yes       |
		+----------------------+----------------------+-----------+

	:param a: may be an int, float or Rational
	:param b: may be an int if a is an int, otherwise should be 1 or left out

	:raises ValueError: if the denominator `b` is set to 0
	"""

	@staticmethod
	def __simplify__(a: int, b: int) -> Tuple[int, int]:
		r"""
		Takes in a tuple :math:`(a, b)` for integers a and b and returns a simplified tuple :math:`(c, d)` where :math:`a/b\equiv c/d`.
		"""
		_gcd = gcd(a, b)  # divide a and b by gcd(a, b). When gcd is 1, already fully simplified
		return a // _gcd, b // _gcd

	@property
	def sign(self) -> int:
		"""The sign of this fraction. :returns: either 1 or -1"""
		return self._sign[0] * self._sign[1]

	@property
	def a(self) -> int:
		"""The enumerator of this fraction."""
		return self.sign * self._a

	@property
	def b(self) -> int:
		"""The denominator of this fraction."""
		return self._b

	def __init__(self, a: Union[int, float, Rational] = 1, b: int = 1):
		if not ((isinstance(a, int) and isinstance(b, int))
				or (isinstance(a, float) and b == 1)
				or (isinstance(a, Rational) and b == 1)):
			raise TypeError(
				f"Values 'a' and 'b' must be of type 'int' (received {a.__class__.__name__}, {b.__class__.__name__}). "
				f"Alternatively 'a' can be of type 'float' or 'Rational' when 'b' is set to 1 or left blank.")

		if isinstance(a, (Rational, float)) and b == 1:  # handle Rational or float input
			if isinstance(a, float):
				a = find_rational_approximation(a)
			self._a, self._b, self._sign = a._a, a._b, a._sign
			return  # return since all the calculations must have already been done for these inputs

		if not b:  # if b == 0
			raise ValueError("Denominator of Rational fraction can not be 0.")
		if not a:  # filter out -0 (if a == 0)
			self._sign = (1, 1)
		else:
			self._sign = (sign(a, zero=1), sign(b, zero=1))  # set sign of fraction

		self._a, self._b = Rational.__simplify__(abs(a), abs(b))  # simplify tuple of absolute values

	def __repr__(self) -> str:
		return f"Rational(a={self.a}, b={self._b})"

	def __str__(self) -> str:
		if self._a == 0 or self._b == 1:
			return str(self.a)  # handle (+-0 / x)and (+-y / 1)
		else:
			return f"{self.a}/{self._b}"

	def __getitem__(self, key: Union[str, int]) -> int:
		if not type(key) in (str, int):
			raise TypeError("Key must be of type 'str' or 'int' (received '{}').".format(key.__class__.__name__))
		# not (key is string -> key is a or b) and (key is int -> key is 0 or 1)
		if not (((not type(key) is str) or key == "a" or key == "b") and (
				(not type(key) is int) or key == 0 or key == 1)):
			raise IndexError("Key must be either '0', '1', 'a' or 'b' for type Rational (received '{}').".format(key))

		return self.a if key == "a" or key == 0 else self.b

	def __hash__(self):
		return hash((self.a, self.b))

	@__prepare_int_binary_op__
	def __compare__(self, other : Union[int, float, Rational]) -> int:
		"""
		Function that returns -1 if :math:`a < b`, 0 if :math:`a = b`, or 1 if :math:`a > b` for Rationals a and b.
		"""
		other: Rational
		if self.sign != other.sign:
			return self.sign  # either (1, -1) or (-1, 1) so we can return self.sign
		else:  # either (1, 1) or (-1, -1) so we check
			# abs(a / b) - abs(c / d)
			# abs(ad / bd) - abs(cb / db)
			# abs(ad) - abs(cb)
			return sign(self._a * other._b - other._a * self._b)

	def __eq__(self, other: Union[int, float, Rational]) -> bool:
		return not bool(self.__compare__(other))  # not bool(-1, 1) -> False

	def __ne__(self, other: Union[int, float, Rational]) -> bool:
		return bool(self.__compare__(other))  # not bool(0) -> True

	def __lt__(self, other: Union[int, float, Rational]) -> bool:
		return self.__compare__(other) == -1

	def __le__(self, other: Union[int, float, Rational]) -> bool:
		return self.__compare__(other) <= 0

	def __gt__(self, other: Union[int, float, Rational]) -> bool:
		return self.__compare__(other) == 1

	def __ge__(self, other: Union[int, float, Rational]) -> bool:
		return self.__compare__(other) >= 0

	@__prepare_int_binary_op__
	def __add__(self, other: Union[int, float, Rational]) -> Rational:
		"""
		:math:`(a1 / b1) + (a2 / b2) = (a1 * b2 + a2 * b1) / ( b1 * b2)`
		"""
		other: Rational
		a = (self.a * other._b + other.a * self._b)
		b = self._b * other._b
		return Rational(a, b)

	@__prepare_int_binary_op__
	def __sub__(self, other: Union[int, float, Rational]) -> Rational:
		"""
		:math:`(a1 / b1) - (a2 / b2) = (a1 * b2 - a2 * b1) / ( b1 * b2)`
		"""
		other: Rational
		a = (self.a * other._b - other.a * self._b)
		b = self._b * other._b
		return Rational(a, b)

	@__prepare_int_binary_op__
	def __mul__(self, other: Union[int, float, Rational]) -> Rational:
		"""
		:math:`(a1 * a2) / (b1 * b2)`
		"""
		other: Rational
		a = self.a * other.a
		b = self._b * other._b
		return Rational(a, b)

	@__prepare_int_binary_op__
	def __truediv__(self, other: Union[int, float, Rational]) -> Rational:
		"""
		:math:`(a1 * b2) / (b1 * a2)`
		"""
		other: Rational
		if not other._a:  # not bool(0) -> True
			raise ValueError("Cannot divide by zero.")
		a = self.a * other._b
		b = self._b * other.a
		return Rational(a, b)

	def __pow__(self, other: Union[int, float, Rational]) -> Rational:
		if not isinstance(other, (int, float)):
			raise TypeError("Illegal binary operation '{}' of type 'Rational' and '{}' (expected 'int').".format("**",
																												 other.__class__.__name__))
		if sign(other) + 1:  # bool(2) -> True
			a = self.a ** other
			b = self._b ** other
		else:  # bool(0) -> False
			a = self._b ** -other
			b = self.a ** -other
		return Rational(a, b)

	@__prepare_int_binary_op__
	def __mod__(self, other) -> Rational:
		"""
		:math:`((a * d) - (c * b * floor((a * d) / (b * c))) / (b * d)`
		"""
		other: Rational
		# (sign0 ^ sign1) + 1 xor bit-hack amounts to sign0 * sign1 but ~~F A S T E R
		a = ((other.sign ^ self.sign) + 1) * (
				(self._a * other._b) - (self._b * other._a * floor((self._a * other._b) / (self._b * other._a))))
		b = self._b * other._b
		return Rational(a, b)

	@__prepare_int_binary_op__
	def __and__(self, other) -> Rational:
		"""
		:math:`(a1 + a2) / (b1 + b2)`
		"""
		other: Rational
		if self.sign - 1 or other.sign - 1:
			raise ValueError("Values of two Rationals for binary operation '&' must be greater than 0.")
		a = self.a + other.a
		b = self._b + other._b
		return Rational(a, b)

	def __neg__(self) -> Rational:
		return Rational(-self.a, self._b)

	def __abs__(self) -> Rational:
		return Rational(self._a, self._b)

	def __int__(self) -> int:
		return int(self.a // self._b)

	def __float__(self) -> float:
		return float(self.a / self._b)

	def __round__(self, n_digits: Optional[int] = None) -> float:
		if n_digits:
			return round(float(self), n_digits)
		else:
			return float(self)

	def __floor__(self) -> Rational:
		return Rational(floor(self.a / self._b), 1)

	def __ceil__(self) -> Rational:
		return Rational(ceil(self.a / self._b), 1)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def find_rational_approximation(num: Real, precision: int = 4) -> Rational:
	r"""
	Returns a Rational x with numerator and denominator a, b where :math:`\text{float}(x) = a/b \approx \text{num}`.

	:param num: the number to approximate as float or int
	:param precision: the number of decimal digits of precision, if this exceeds the limits of the floating point
		architecture of the system, this value is truncated to this maximum

	:raises ValueError: if precision is negative
	"""
	if precision < 0:
		raise ValueError("Value of 'precision' must be non-negative (received '{}').".format(precision))

	_mantissa = abs(num) % 1  # returns digits after decimal place of num
	if _mantissa == 0: return Rational(int(num))  # return num/1 if there are no decimal places

	try:
		# handle precision values that are too large
		if precision > sys.float_info.dig - 1:
			print(cl_s("Warning: The precision of findRationalApproximation was set to {}, "
					   "but the maximum system specification is {} (precision has been automatically set to the system maximum)."
					   .format(precision, sys.float_info.dig - 1), WARNING))
			precision = sys.float_info.dig
	except Exception as e:
		print(cl_s("Warning: Something went wrong while getting sys.float_info!\n\t{}".format(e), WARNING))

	# starting, left_bound, right_bound
	iteration_vars = (1, 2, 0, 1, 1, 1)
	while abs((iteration_vars[0] / iteration_vars[1]) - _mantissa) >= 10 ** -(1 + precision):
		geq = int((iteration_vars[0] / iteration_vars[1]) >= _mantissa)  # 0 or 1
		iteration_vars = (iteration_vars[0] + geq * (iteration_vars[2]) + ((1 - geq) * (iteration_vars[4])),
						  iteration_vars[1] + geq * (iteration_vars[3]) + ((1 - geq) * (iteration_vars[5])),
						  geq * (iteration_vars[2]) + ((1 - geq) * (iteration_vars[0])),
						  geq * (iteration_vars[3]) + ((1 - geq) * (iteration_vars[1])),
						  geq * (iteration_vars[0]) + ((1 - geq) * (iteration_vars[4])),
						  geq * (iteration_vars[1]) + ((1 - geq) * (iteration_vars[5])))

	return Rational(int(copysign(iteration_vars[0] + int(abs(num)) * iteration_vars[1], num)), iteration_vars[1])

def get_possible_rationals(_set: Iterable[int]) -> Set[Rational]:
	r"""
	Returns unique Rationals in a set with :math:`a/b \quad \forall a, b \in \text{_set}`.

	:param _set: all elements of `_set` must be integers.

	:raises ValueError: if elements of `_set` are not all integers
	"""
	if [None for el in _set if not isinstance(el, int)]:
		raise ValueError("All elements of input set must be integers.")

	# all rationals (a, b) over Cartesian product length 2 of _set
	return {Rational(*a) for a in product(_set, repeat=2) if a[1] != 0}

def sign(x: Real, zero: T = 0) -> Union[int, T]:
	"""
	Returns the sign of x, where sign(0) = `zero`.

	:param x: the value to get the sign of
	:param zero: defaults to 0, but 1 may be useful in certain applications
	"""
	if x < 0:
		return -1
	elif not x < 0 and not x == 0: # looks weird but is to get around operator quirks
		return 1
	else:
		return zero

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ DEPRECATED ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def is_group():
	"""
	..	deprecated:: 0.1.1.dev0

		:py:func:`is_group` functionality was moved to :py:mod:`SEPModules.SEPAlgebra`
	"""
	raise DeprecationWarning("removed in 0.1.1.dev0, functionality was moved to SEPModules.SEPAlgebra")

def is_abelian_group():
	"""
	..	deprecated:: 0.1.1.dev0

		:py:func:`is_abelian_group` functionality was moved to :py:mod:`SEPModules.SEPAlgebra`.
	"""
	is_group()
