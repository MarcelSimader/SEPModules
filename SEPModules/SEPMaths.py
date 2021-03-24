#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++

import sys
from itertools import product, combinations
from math import copysign, gcd, floor, ceil, isclose
import types

from SEPModules.SEPPrinting import cl_p, WARNING

# from SEPCMaths import iterateRationalApproximation

#+++++++++++++++++++++++++++++++
#++++++++++MODULE CODE++++++++++
#+++++++++++++++++++++++++++++++

#+++++++++CLASSES++++++++++

class Rational():
	"""
	Rational number of the form a/b (a, b in Z). Used for symbolic computations in SEPMaths module. Values are automatically simplified.
	"""
	
	_sign, _a, _b = (1, 1), 1, 1 #_sign stores as two binary values to exploit xor logic (-1 = -, 1 = +)
	
	#Decorator
	def __prepare_int_binary_op__(func):
		"""
		Do type checking of arithmetic binary operations on Rationals and auto-convert int to Rational type.
		"""
		def __wrapper__(self, other):
			if not (type(other) in (int, float) or type(other) is Rational):
				raise TypeError("Illegal binary operation '{}' of type 'Rational' and '{}' (expected 'int', 'Rational' or 'float')."\
				.format(func.__name__, other.__class__.__name__))
		
			if type(other) in (int, float): 
				other = Rational(other) #convert c to (c / 1) (or (a / b) = c if float)
			
			return func(self, other)
		return __wrapper__

	def __simplify__(a, b):
		"""
		Takes in a tuple (a, b) for integers a and b and returns a simplified tuple (c, d) where a/b == c/d.
		"""
		_gcd = gcd(a, b) #divide a and b by gcd(a, b). When gcd is 1, already fully simplified 
		return (a // _gcd, b // _gcd)
	
	@property
	def sign(self):
		return (self._sign[0] ^ self._sign[1]) + 1 #xor hack, amounts to sign[0] * sign[1]
	
	@property
	def a(self):
		return self.sign * self._a
	
	@property
	def b(self):
		return self._b

	def __init__(self, a=1, b=1):
		if not ((type(a) is int and type(b) is int) or (type(a) is float and b == 1) or (type(a) is Rational and b == 1)):
			raise TypeError("Values 'a' and 'b' must be of type 'int' (received {}, {}). \
						Alternatively 'a' can be of type 'float' or 'Rational' when \
						'b' is set to 1 or left blank.".format(a.__class__.__name__, b.__class__.__name__))
		
		#TODO: write tests for input type Rational
		if type(a) in (Rational, float) and b == 1: #handle Rational or float input
			if type(a) is float:
				a = findRationalApproximation(a)
			self._a, self._b, self._sign = a._a, a._b, a._sign
			return #return since all the calculations must have already been done for these inputs
		
		if not b: #if b == 0
			raise ValueError("Denominator of Rational fraction can not be 0.")
			
		if not a: #filter out -0 (if a == 0)
			self._sign = (1, 1)
		else:
			self._sign = (sign(a, zero=1), sign(b, zero=1)) #set sign of fraction
				
		self._a, self._b = Rational.__simplify__(abs(a), abs(b)) #simplify tuple of absolute values
	
	def __repr__(self):
		return "<Rational(a={}, b={})>".format(self.a, self._b)
		
	def __str__(self):
		if self._a == 0 or self._b == 1: return str(self.a) #handle (+-0 / x)and (+-y / 1)
		else: return "{}/{}".format(self.a, self._b)
		
	def __getitem__(self, key):
		if not type(key) in (str, int):
			raise TypeError("Key must be of type 'str' or 'int' (received '{}').".format(key.__class__.__name__))
		# not (key is string -> key is a or b) and (key is int -> key is 0 or 1)
		if not (((not type(key) is str) or key == "a" or key == "b") and ((not type(key) is int) or key == 0 or key == 1)):
			raise IndexError("Key must be either '0', '1', 'a' or 'b' for type Rational (received '{}').".format(key))
			
		return self.a if key == "a" or key == 0 else self.b
		
	def __hash__(self):
		return hash(tuple([self.sign, self._a, self._b]))
	
	@__prepare_int_binary_op__
	def __compare__(self, other):
		"""
		Function that returns -1 if a < b, 0 if a == b, or 1 if a > b for Rationals a and b.
		"""
		if self.sign != other.sign:
			return self.sign #either (1, -1) or (-1, 1) so we can return self.sign
		else: # either (1, 1) or (-1, -1) so we check
			# abs(a / b) - abs(c / d)
			# abs(ad / bd) - abs(cb / db)
			# abs(ad) - abs(cb)
			return sign(self._a * other._b - other._a * self._b)
				
	def __eq__(self, other):
		return not self.__compare__(other) #not bool(-1, 1) -> False
		
	def __neq__(self, other):
		return self.__compare__(other) #not bool(0) -> True
		
	def __lt__(self, other):
		return self.__compare__(other) == -1
		
	def __le__(self, other):
		return self.__compare__(other) <= 0
		
	def __gt__(self, other):
		return self.__compare__(other) == 1
		
	def __ge__(self, other):
		return self.__compare__(other) >= 0
	
	@__prepare_int_binary_op__
	def __add__(self, other):
		"""
		(a1 / b1) + (a2 / b2) = (a1 * b2 + a2 * b1) / ( b1 * b2)
		"""
		a = (self.a * other._b + other.a * self._b)
		b = self._b * other._b
		return Rational(a, b)
	
	@__prepare_int_binary_op__
	def __sub__(self, other):
		"""
		(a1 / b1) - (a2 / b2) = (a1 * b2 - a2 * b1) / ( b1 * b2)
		"""
		a = (self.a * other._b - other.a * self._b)
		b = self._b * other._b
		return Rational(a, b)
	
	@__prepare_int_binary_op__
	def __mul__(self, other):
		"""
		(a1 * a2) / (b1 * b2)
		"""
		a = self.a * other.a
		b = self._b * other._b
		return Rational(a, b)
	
	@__prepare_int_binary_op__
	def __truediv__(self, other):
		"""
		(a1 * b2) / (b1 * a2)
		"""
		if not other._a: #not bool(0) -> True
			raise ValueError("Cannot divide by zero.")
		a = self.a * other._b
		b = self._b * other.a
		return Rational(a, b)
	
	def __pow__(self, other):
		"""
		(a1 ** c) / (b1 ** c)
		"""
		if not type(other) is int:
			raise TypeError("Illegal binary operation '{}' of type 'Rational' and '{}' (expected 'int').".format("**", other.__class__.__name__))
		
		if sign(other) + 1: #bool(2) -> True
			a = self.a ** other
			b = self._b ** other
		else: #bool(0) -> False
			a = self._b ** -other
			b = self.a ** -other
		return Rational(a, b)
	
	@__prepare_int_binary_op__
	def __mod__(self, other):
		"""
		((a * d) - (c * b * floor((a * d) / (b * c))) / (b * d)
		"""
		# (sign0 ^ sign1) + 1 xor bit-hack amounts to sign0 * sign1 but ~~F A S T E R
		a = ((other.sign ^ self.sign) + 1) * ((self._a * other._b) - (self._b * other._a * floor((self._a * other._b) / (self._b * other._a))))
		b = self._b * other._b
		return Rational(a, b)
	
	@__prepare_int_binary_op__
	def __and__(self, other):
		"""
		(a1 + a2) / (b1 + b2)
		"""
		if self.sign - 1 or other.sign - 1:
			raise ValueError("Values of two Rationals for binary operation '&' must be greater than 0.")
		a = self.a + other.a
		b = self._b + other._b
		return Rational(a, b)
	
	def __neg__(self):
		return Rational(-self.a, self._b)
		
	def __abs__(self):
		return Rational(self._a, self._b)
		
	def __int__(self):
		return int(self.a // self._b)
		
	def __float__(self):
		return float(self.a / self._b)
		
	def __round__(self, nDigits=None):
		if nDigits: 
			return round(float(self), nDigits)
		else: 
			return float(self)
		
	def __floor__(self):
		return Rational(floor(self.a / self._b), 1)
	
	def __ceil__(self):
		return Rational(ceil(self.a / self._b), 1)

#+++++++++FUNCTIONS++++++++++

def findRationalApproximation(num, precision=4, microIterations=1):
	raise DeprecationWarning("Deprecated SEPCMaths")
	"""
	Returns a Rational x with numerator and denominator a, b with float(x) = a / b =~ num.
	Takes:
		- num, the number to approximate as float or int
		- [precision=8], the number of decimal digits of precision
		- [microIterations=1 sets the number of micro iterations to be performed for every macro iteration (ie. 
			every time change and precision are checked).
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

	#																		a,b,(lower),(upper)
	#TODO: fix
	# a, b = iterateRationalApproximation(1, 2, 0, 1, 1, 1, _mantissa, 10**(-precision), microIterations)
	
	return Rational(int(copysign(a + int(abs(num)) * b, num)), int(b))

def getPossibleRationals(_set):
	"""
	Returns all possible Rationals (a / b) for a, b in _set. All elements of _set must be integers.
	"""
	if not type(_set) in (list, set):
		raise TypeError("Argument must be of type 'list' or 'set' (received '{}').".format(_set.__class__.__name__))
	if [None for el in _set if type(el) is not int]:
		raise ValueError("All elements of input set must be integers.")
	
	# all rationals (a, b) over Cartesian product length 2 of _set
	return {Rational(*a) for a in product(_set, repeat=2) if a[1]}

def isGroup(_set, operator, tolerance=0, abelian=False):
	"""
	Test if a set and an operator form a group. The operator is described by a function of form (a, b) -> (c), and the tolerance is a value from 0 to 10, where 0 is the least and 10 is the most tolerance in floating point precision.
	"""
	#input sanitation
	if type(_set) not in (list, set):
		raise TypeError("'_set' must be of type 'list' or 'set' (received '{}').".format(_set.__class__.__name__))
	
	try:
		_arg_count = operator.__code__.co_argcount - operator.__code__.co_kwonlyargcount #count positional arguments of operator function
	except:
		_arg_count = 0
	if (not type(operator) is types.FunctionType) or _arg_count != 2: 
		raise TypeError("'operator' must be of type 'function' and receive two positional arguments (has {}).".format(_arg_count))
	
	if not type(tolerance) is int:
		raise TypeError("'tolerance' must be of type 'int' (received '{}').".format(tolerance.__class__.__name__))
	if tolerance < 0 or tolerance > 10:
		raise ValueError("'tolerance' must be between 0 (least) and 10 (most) (received {}).".format(tolerance))
	
	#TODO: figure out what to do with these properties
	# hasNeutral, isAssociative, hasInverses, isCommutative = False, True, True, True
	neutralEl = None
	
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
			neutralEl = a
			# hasNeutral = True
			break
	
	if neutralEl is None: return False #cannot be a group
	
	#++++test for inverses++++
	for a in _set:
		_hasInverseFlag = False
		for b in _set:
			if equal(add_or_get_computed(a, b), neutralEl):
				_hasInverseFlag = True
				break
		if not _hasInverseFlag: 
			# hasInverses = False
			return False #cannot be group
	
	return True

def isAbelianGroup(_set, operator, tolerance=0):
	"""
	Works the same way as SEPMaths.isGroup but tests for Abelian groups.
	"""
	return isGroup(_set, operator, tolerance=tolerance, abelian=True)

def fibonacci(n, fibList=None):
	n = abs(n) if n < 0 else n
	if fibList is None:
		fibList = {-2:0, -1:0, 0:0, 1:1}
	def __fastFib__(n, fibList):
		if not n in fibList:
			fibList[n] = __fastFib__(n - 1, fibList) + __fastFib__(n - 2, fibList)
		return fibList[n]
	return __fastFib__(n, fibList)

def slowFibonacci(n):
	n = abs(n) if n < 0 else n
	def __slowFib__(n):
		if n < 1:
			return 0
		elif n == 1:
			return 1
		return __slowFib__(n - 1) + __slowFib__(n - 2)
	return __slowFib__(n)
	
def sign(x, zero=0):
	"""
	Returns the sign of x (but sign(0) == zero, defaults to 0).
	"""
	return -1 if x < 0 else (1 if x > 0 else zero)