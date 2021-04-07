"""
Author: Marcel Simader

Date: 01.04.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
from __future__ import annotations

import types
from numbers import Real
from typing import Tuple, Callable, Any, Union, Set

import sys
from itertools import product, combinations
from math import copysign, gcd, floor, ceil, isclose

from SEPModules.SEPPrinting import cl_p, WARNING

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Rational:
	"""
	Rational number of the form :math:`a/b \\text{ with } a, b \\in \\mathbb{Z}`. Used for symbolic computations in :mod:`SEPMaths`
	module. Values are automatically simplified. The following forms are accepted, where option 1 and 3 are exact and
	option 2 will approximate the float input as integer ratio:

		1. `Rational(int, int)`
		2. `Rational(float, 1)` or `Rational(float)`
		3. `Rational(rational_instance, 1)` or `Rational(rational_instance)`

	:param a: may be an int, float or Rational
	:param b: may be an int if a is an int, otherwise should be 1 or left out

	:raises ValueError: if the denominator `b` is set to 0
	"""
	
	#Decorator
	def _prepare_int_binary_op(func : Callable[..., Any]) -> Callable[..., Any]:
		"""
		Do type checking of arithmetic binary operations on Rationals and auto-convert int or float to Rational type.
		"""
		def __wrapper__(self, other):
			if not (type(other) in (int, float) or type(other) is Rational):
				raise TypeError("Illegal binary operation '{}' of type 'Rational' and '{}' (expected 'int', 'Rational' or 'float')."\
				.format(func.__name__, other.__class__.__name__))
		
			if type(other) in (int, float): 
				other = Rational(other) #convert c to (c / 1) (or (a / b) = c if float)
			return func(self, other)

		# replace docstring and name
		__wrapper__.doc__ = func.__doc__
		__wrapper__.__name__ = func.__name__
		return __wrapper__

	@staticmethod
	def __simplify__(a : int, b : int) -> Tuple[int, int]:
		"""
		Takes in a tuple :math:`(a, b)` for integers a and b and returns a simplified tuple :math:`(c, d)` where :math:`a/b\\equiv c/d`.
		"""
		_gcd = gcd(a, b) #divide a and b by gcd(a, b). When gcd is 1, already fully simplified 
		return a // _gcd, b // _gcd
	
	@property
	def sign(self) -> int:
		return (self._sign[0] ^ self._sign[1]) + 1 #xor hack, amounts to sign[0] * sign[1]
	
	@property
	def a(self) -> int:
		return self.sign * self._a
	
	@property
	def b(self) -> int:
		return self._b

	def __init__(self, a : Union[int, float, Rational]=1, b : int=1):
		if not ((type(a) is int and type(b) is int) or (type(a) is float and b == 1) or (type(a) is Rational and b == 1)):
			raise TypeError("Values 'a' and 'b' must be of type 'int' (received {}, {}). \
						Alternatively 'a' can be of type 'float' or 'Rational' when \
						'b' is set to 1 or left blank.".format(a.__class__.__name__, b.__class__.__name__))
		
		#TODO: write tests for input type Rational
		if type(a) in (Rational, float) and b == 1: #handle Rational or float input
			if type(a) is float:
				a = find_rational_approximation(a)
			self._a, self._b, self._sign = a._a, a._b, a._sign
			return #return since all the calculations must have already been done for these inputs
		
		if not b: #if b == 0
			raise ValueError("Denominator of Rational fraction can not be 0.")
			
		if not a: #filter out -0 (if a == 0)
			self._sign = (1, 1)
		else:
			self._sign = (sign(a, zero=1), sign(b, zero=1)) #set sign of fraction
				
		self._a, self._b = Rational.__simplify__(abs(a), abs(b)) #simplify tuple of absolute values
	
	def __repr__(self) -> str:
		return "<Rational(a={}, b={})>".format(self.a, self._b)
		
	def __str__(self) -> str:
		if self._a == 0 or self._b == 1:
			return str(self.a) #handle (+-0 / x)and (+-y / 1)
		else:
			return "{}/{}".format(self.a, self._b)
		
	def __getitem__(self, key : Union[str, int]) -> int:
		if not type(key) in (str, int):
			raise TypeError("Key must be of type 'str' or 'int' (received '{}').".format(key.__class__.__name__))
		# not (key is string -> key is a or b) and (key is int -> key is 0 or 1)
		if not (((not type(key) is str) or key == "a" or key == "b") and ((not type(key) is int) or key == 0 or key == 1)):
			raise IndexError("Key must be either '0', '1', 'a' or 'b' for type Rational (received '{}').".format(key))
			
		return self.a if key == "a" or key == 0 else self.b
		
	def __hash__(self):
		return hash(tuple([self.sign, self._a, self._b]))
	
	@_prepare_int_binary_op
	def __compare__(self, other) -> int:
		"""
		Function that returns -1 if :math:`a < b`, 0 if :math:`a = b`, or 1 if :math:`a > b` for Rationals a and b.
		"""
		if self.sign != other.sign:
			return self.sign #either (1, -1) or (-1, 1) so we can return self.sign
		else: # either (1, 1) or (-1, -1) so we check
			# abs(a / b) - abs(c / d)
			# abs(ad / bd) - abs(cb / db)
			# abs(ad) - abs(cb)
			return sign(self._a * other._b - other._a * self._b)
				
	def __eq__(self, other) -> bool:
		return not bool(self.__compare__(other)) #not bool(-1, 1) -> False
		
	def __neq__(self, other) -> bool:
		return bool(self.__compare__(other)) #not bool(0) -> True
		
	def __lt__(self, other) -> bool:
		return self.__compare__(other) == -1
		
	def __le__(self, other) -> bool:
		return self.__compare__(other) <= 0
		
	def __gt__(self, other) -> bool:
		return self.__compare__(other) == 1
		
	def __ge__(self, other) -> bool:
		return self.__compare__(other) >= 0
	
	@_prepare_int_binary_op
	def __add__(self, other) -> Rational:
		"""
		:math:`(a1 / b1) + (a2 / b2) = (a1 * b2 + a2 * b1) / ( b1 * b2)`
		"""
		a = (self.a * other._b + other.a * self._b)
		b = self._b * other._b
		return Rational(a, b)
	
	@_prepare_int_binary_op
	def __sub__(self, other) -> Rational:
		"""
		:math:`(a1 / b1) - (a2 / b2) = (a1 * b2 - a2 * b1) / ( b1 * b2)`
		"""
		a = (self.a * other._b - other.a * self._b)
		b = self._b * other._b
		return Rational(a, b)
	
	@_prepare_int_binary_op
	def __mul__(self, other) -> Rational:
		"""
		:math:`(a1 * a2) / (b1 * b2)`
		"""
		a = self.a * other.a
		b = self._b * other._b
		return Rational(a, b)
	
	@_prepare_int_binary_op
	def __truediv__(self, other) -> Rational:
		"""
		:math:`(a1 * b2) / (b1 * a2)`
		"""
		if not other._a: #not bool(0) -> True
			raise ValueError("Cannot divide by zero.")
		a = self.a * other._b
		b = self._b * other.a
		return Rational(a, b)
	
	def __pow__(self, other) -> Rational:
		if not type(other) is int:
			raise TypeError("Illegal binary operation '{}' of type 'Rational' and '{}' (expected 'int').".format("**", other.__class__.__name__))
		
		if sign(other) + 1: #bool(2) -> True
			a = self.a ** other
			b = self._b ** other
		else: #bool(0) -> False
			a = self._b ** -other
			b = self.a ** -other
		return Rational(a, b)
	
	@_prepare_int_binary_op
	def __mod__(self, other) -> Rational:
		"""
		:math:`((a * d) - (c * b * floor((a * d) / (b * c))) / (b * d)`
		"""
		# (sign0 ^ sign1) + 1 xor bit-hack amounts to sign0 * sign1 but ~~F A S T E R
		a = ((other.sign ^ self.sign) + 1) * ((self._a * other._b) - (self._b * other._a * floor((self._a * other._b) / (self._b * other._a))))
		b = self._b * other._b
		return Rational(a, b)
	
	@_prepare_int_binary_op
	def __and__(self, other) -> Rational:
		"""
		:math:`(a1 + a2) / (b1 + b2)`
		"""
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
		
	def __round__(self, n_digits : int=None) -> float:
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

def find_rational_approximation(num : Real, precision :int=4) -> Rational:
	"""
	Returns a Rational x with numerator and denominator a, b where :math:`\\text{float}(x) = a/b \\approx \\text{num}`.

	:param num: the number to approximate as float or int
	:param precision: the number of decimal digits of precision, if this exceeds the limits of the floating point
		architecture of the system, this value is truncated to this maximum

	:raises ValueError: if precision is negative
	"""
	if type(num) not in (float, int):
		raise TypeError("Type of 'num' must be 'int' or 'float' (received '{}').".format(num.__class__.__name__))
	if type(precision) is not int:
		raise TypeError("Type of 'precision' must be 'int' (received type '{}').".format(precision.__class__.__name__))
	if precision < 0:
		raise ValueError("Value of 'precision' must be non-negative (received '{}').".format(precision))

	_mantissa = abs(num) % 1 #returns digits after decimal place of num
	if _mantissa == 0: return Rational(int(num)) #return num/1 if there are no decimal places
		
	try:
		#handle precision values that are too large
		if precision > sys.float_info.dig - 1:
			print(cl_p("Warning: The precision of findRationalApproximation was set to {}, but the maximum system specification is {} (precision has been automatically set to the system maximum).".format(precision, sys.float_info.dig - 1), WARNING))
			precision = sys.float_info.dig
	except Exception as e:
		print(cl_p("Warning: Something went wrong while getting sys.float_info!\n\t{}".format(e), WARNING))

	# starting, left_bound, right_bound
	iteration_vars = (1, 2, 0, 1, 1, 1)
	while abs((iteration_vars[0] / iteration_vars[1]) - _mantissa) >= 10 ** -(1 + precision):
		geq = int((iteration_vars[0] / iteration_vars[1]) >= _mantissa) # 0 or 1
		iteration_vars = (iteration_vars[0] + geq * (iteration_vars[2]) + ((1 - geq) * (iteration_vars[4])),
						  iteration_vars[1] + geq * (iteration_vars[3]) + ((1 - geq) * (iteration_vars[5])),
						  geq * (iteration_vars[2]) + ((1 - geq) * (iteration_vars[0])),
						  geq * (iteration_vars[3]) + ((1 - geq) * (iteration_vars[1])),
						  geq * (iteration_vars[0]) + ((1 - geq) * (iteration_vars[4])),
						  geq * (iteration_vars[1]) + ((1 - geq) * (iteration_vars[5])))
	
	return Rational(int(copysign(iteration_vars[0] + int(abs(num)) * iteration_vars[1], num)), iteration_vars[1])

def get_possible_rationals(_set : Union[list, set]) -> Set[Rational]:
	"""
	Returns unique Rationals in a set with :math:`a/b \\quad \\forall a, b \\in \\text{_set}`.

	:param _set: all elements of `_set` must be integers.

	:raises ValueError: if elements of `_set` are not all integers
	"""
	if not type(_set) in (list, set):
		raise TypeError("Argument must be of type 'list' or 'set' (received '{}').".format(_set.__class__.__name__))
	if [None for el in _set if type(el) is not int]:
		raise ValueError("All elements of input set must be integers.")
	
	# all rationals (a, b) over Cartesian product length 2 of _set
	return {Rational(*a) for a in product(_set, repeat=2) if a[1] != 0}

def is_group(_set : Union[list, set], operator : Callable[[Any, Any], Any], tolerance :int=0, abelian :bool=False) -> bool:
	"""
	Test if a set and an operator form a group.

	:param operator: described by a function of form `(a, b) -> (c)`
	:param tolerance: a value from 0 to 10, where 0 is the least and 10 is the most tolerance in floating point precision
	:param abelian: test for a regular or an abelian group

	:raises ValueError: if tolerance is not between 0 and 10
	"""
	#input sanitation
	if type(_set) not in (list, set):
		raise TypeError("'_set' must be of type 'list' or 'set' (received '{}').".format(_set.__class__.__name__))
	
	try:
		_arg_count = operator.__code__.co_argcount - operator.__code__.co_kwonlyargcount #count positional arguments of operator function
	except Exception:
		_arg_count = 0
	if (not type(operator) is types.FunctionType) or _arg_count != 2: 
		raise TypeError("'operator' must be of type 'function' and receive two positional arguments (has {}).".format(_arg_count))
	
	if not type(tolerance) is int:
		raise TypeError("'tolerance' must be of type 'int' (received '{}').".format(tolerance.__class__.__name__))
	if tolerance < 0 or tolerance > 10:
		raise ValueError("'tolerance' must be between 0 (least) and 10 (most) (received {}).".format(tolerance))
	
	#TODO: figure out what to do with these properties
	# hasNeutral, isAssociative, hasInverses, isCommutative = False, True, True, True
	neutral_element = None
	
	#define custom equal to test if values are approximately equal according to 'tolerance' value
	if tolerance == 0:
		equal = lambda a, b: a == b
	else:
		_tol = 10**(12-tolerance)
		equal = lambda a, b: isclose(a, b, rel_tol=_tol)
	
	#list so we do not recompute the same values
	_computed = {}
	
	def add_or_get_computed(a, b):
		"""
		Retrieve already computed values or compute and then store them in _computed.
		"""
		_ab = (a, b)
		try:
			return _computed[_ab]
		except KeyError:
			_computed[_ab] = operator(a, b)
			return _computed[_ab]
	
	#++++test associativity++++
	for a, b, c in combinations(_set, 3):
		if not equal(operator(a, add_or_get_computed(b, c)), operator(add_or_get_computed(a, b), c)):
			# isAssociative = False
			return False #cannot be a group
	
	#++++test for commutativity++++
	if abelian:
		for a, b in combinations(_set, 2):
			if not equal(add_or_get_computed(a, b), add_or_get_computed(b, a)):
				# isCommutative = False
				return False
	
	#++++find neutral element++++
	for a in _set:
		_neutralFlag = True
		for b in _set:
			if not equal(add_or_get_computed(a, b), b):
				_neutralFlag = False
				break
		if _neutralFlag:
			neutral_element = a
			# hasNeutral = True
			break
	
	if neutral_element is None: return False #cannot be a group
	
	#++++test for inverses++++
	for a in _set:
		_hasInverseFlag = False
		for b in _set:
			if equal(add_or_get_computed(a, b), neutral_element):
				_hasInverseFlag = True
				break
		if not _hasInverseFlag: 
			# hasInverses = False
			return False #cannot be group
	
	return True

def is_abelian_group(_set : Union[list, set], operator : Callable[[Any, Any], Any], tolerance :int=0) -> bool:
	"""
	Works the same way as :py:func:`is_group` but tests for Abelian groups.
	"""
	return is_group(_set, operator, tolerance=tolerance, abelian=True)

def fibonacci(n : int, fib_list=None) -> int:
	n = abs(n) if n < 0 else n
	if fib_list is None:
		fib_list = {-2:0, -1:0, 0:0, 1:1}
	def __fast_fib__(n, fibList):
		if not n in fibList:
			fibList[n] = __fast_fib__(n - 1, fibList) + __fast_fib__(n - 2, fibList)
		return fibList[n]
	return __fast_fib__(n, fib_list)

def slow_fibonacci(n : int) -> int:
	n = abs(n) if n < 0 else n
	def __slow_fib__(n):
		if n < 1:
			return 0
		elif n == 1:
			return 1
		return __slow_fib__(n - 1) + __slow_fib__(n - 2)
	return __slow_fib__(n)
	
def sign(x : int, zero : int=0) -> int:
	"""
	Returns the sign of x, where sign(0) = `zero`.

	:param zero: defaults to 0, but 1 may be useful in certain applications
	"""
	return -1 if x < 0 else (1 if x > 0 else zero)