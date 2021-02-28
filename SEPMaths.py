#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++

import sys
from itertools import product, combinations
from math import copysign, gcd, floor, ceil, fmod, isclose, pi
import types
import random

import unittest

import SEPDecorators
from SEPDecorators import timed, check_type
from SEPPrinting import cl_p, RED, GREEN, WARNING
from SEPCMaths import iterateRationalApproximation, intSign

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
			self._sign = (intSign(a, zero=1), intSign(b, zero=1)) #set sign of fraction
				
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
			return intSign(self._a * other._b - other._a * self._b)
				
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
		
		if intSign(other) + 1: #bool(2) -> True
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
	a, b = iterateRationalApproximation(1, 2, 0, 1, 1, 1, _mantissa, 10**(-precision), microIterations)
	
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
	
#+++++++++++++++++++++++++++
#++++++++++TESTING++++++++++
#+++++++++++++++++++++++++++

def test_performance_isGroup(n=4):
	print("".rjust(20, "~"))
	z0 = getPossibleRationals(set(range(-n, n+1)))
	print("(n={}) ".format(len(z0)), end="")
	_isGroup = SEPTiming.timed(isGroup)
	print("Result: {}".format(_isGroup(z0, lambda a, b: a + b)))

def test_performance_isAbelianGroup(n=4):
	print("".rjust(20, "~"))
	z0 = getPossibleRationals(set(range(-n, n+1)))
	print("(n={}) ".format(len(z0)), end="")
	_isAbelianGroup = SEPTiming.timed(isAbelianGroup)
	print("Result: {}".format(_isAbelianGroup(z0, lambda a, b: a + b)))

def test_performance_rational():
	#45 choose 4	=	148995
	#30 choose 4	=	27405
	#25 choose 4	=	12650
	#20 choose 4 	=	4845
	#10 choose 4	=	210
	n = 35
	@timed
	def __test_performance_rational__(op, op_int):
		for k, j, i, l in combinations(range(-n//2, n//2), 4):
			if not j or not l or not k or not i: continue
			op(Rational(k, j), Rational(i, l))
			"""
			In case a lot of data should be thrown at the class to test it.
			"""
			# r = op(Rational(k, j), Rational(i, l))
			# t = op_int(k/j, i/l)
			# if float(r) - t >= 10**-14:
				# print(cl_p("{},{}: {} is not equal to {}!".format((k, j), (i, l), float(r), t), RED))

	_prnt = lambda s, n: print("(n={}) {}: ".format(n, s.ljust(2)), end="")
	_prnt("+", n)
	__test_performance_rational__(op=lambda a, b: a + b, 	op_int=lambda a, b: a + b)
	_prnt("-", n)
	__test_performance_rational__(op=lambda a, b: a - b, 	op_int=lambda a, b: a - b)
	_prnt("*", n)
	__test_performance_rational__(op=lambda a, b: a * b, 	op_int=lambda a, b: a * b)
	_prnt("/", n)
	__test_performance_rational__(op=lambda a, b: a / b, 	op_int=lambda a, b: a / b)
	_prnt("!=", n)
	__test_performance_rational__(op=lambda a, b: a != b, op_int=lambda a, b: a != b)
	_prnt("==", n)
	__test_performance_rational__(op=lambda a, b: a == b, op_int=lambda a, b: a == b)
	_prnt("<", n)
	__test_performance_rational__(op=lambda a, b: a < b, 	op_int=lambda a, b: a < b)
	_prnt(">", n)
	__test_performance_rational__(op=lambda a, b: a > b, 	op_int=lambda a, b: a > b)
	_prnt("<=", n)
	__test_performance_rational__(op=lambda a, b: a <= b, op_int=lambda a, b: a <= b)
	_prnt(">=", n)
	__test_performance_rational__(op=lambda a, b: a >= b, op_int=lambda a, b: a >= b)
	_prnt("%", n)
	__test_performance_rational__(op=lambda a, b: a % b, 	op_int=lambda a, b: fmod(a, b))
	print()
	
def test_performance_findRationalApproximation(n=100_000, precision=6):
	print("{}\n(n={:_}, precision={}) ".format(str().rjust(20, "~"), n, precision), end="")

	rands = [random.random() for _ in range(n)]

	@timed
	def __test_performance_findRationalApproximation__():
		for k in rands:
			findRationalApproximation(k, precision=precision, microIterations=32)
	__test_performance_findRationalApproximation__()

class TestRationalMethods(unittest.TestCase):
	
	def setUp(self):
		self.zero 		= Rational(0, 1)
		self.negzero 	= Rational(0, -1)
		self.onethird = Rational(1, 3)
		self.twofifth = Rational(2, 5)
		
		self.invalidCases = [(0, 0), (1, 0), (-1, 0), (0, -0), (-0, 0), (-0, -0)]
		self.cases = {(0, 1): (0, 1), (1, 1): (1, 1), (2, 1): (2, 1), (-3, 1): (-3, 1), (0, 2): (0, 1), (-0, 3): (-0, 1), (1, 2): (1, 2), (2, -2): (-1, 1), \
		(3, 2): (3, 2), (-0, -3): (0, 1), (1, 3): (1, 3), (2, 3): (2, 3), (-6, 3): (-2, 1), (2, 4): (1, 2), (6, -4): (-3, 2), (35, 45): (7, 9), \
		(-64, -16): (4, 1), (27, 33): (9, 11), (18, 108): (1, 6)}
	
	def tearDown(self):
		del self.zero, self.negzero, self.onethird, self.twofifth, self.invalidCases, self.cases
	
	def test_init_ValueError(self):
		for el in self.invalidCases:
			with self.subTest(val=el):
				with self.assertRaises(ValueError):
					Rational(*el)
	
	def test_simplify_result(self):
		for key, val in self.cases.items():
			with self.subTest(key=key):
				rat = Rational(key[0], key[1])
				self.assertEqual(rat.a, val[0])
				self.assertEqual(rat.b, val[1])
				
		with self.subTest(key="0.376f"):
			self.assertTrue(Rational(0.376), Rational(376, 1000))
			
	def test_getitem_IndexError_TypeError(self):
		with self.assertRaises(IndexError):
			self.zero[2]
		
		with self.assertRaises(TypeError):
			self.zero[[0, 1]]
		
	def test_getitem_result(self):
		for key, val in self.cases.items():
			with self.subTest(val=val):
				rat = Rational(*key)
				self.assertEqual(rat["a"], val[0])
				self.assertEqual(rat["b"], val[1])
				self.assertEqual(rat[0],   val[0])
				self.assertEqual(rat[1],   val[1])
	
	def test_setitem_TypeError_IndexError(self):
		with self.assertRaises(IndexError):
			self.zero["2"]
		with self.assertRaises(TypeError):
			self.zero[[0, 1]]
		with self.assertRaises(TypeError):
			self.zero[0] = 3.3
			
	"""
	Removed item setting from Rational.
	"""
	# def test_setitem_result(self):
		# for key, val in self.cases.items():
			# with self.subTest(key=key, index=int):
				# rat = Rational()
				# rat[0] = key[0]
				# rat[1] = key[1]
				# self.assertEqual(rat[0], val[0])
				# self.assertEqual(rat[1], val[1])
		# with self.subTest(key=key, index=str):
				# rat = Rational()
				# rat["a"] = key[0]
				# rat["b"] = key[1]
				# self.assertEqual(rat[0], val[0])
				# self.assertEqual(rat[1], val[1])
	
	def test_hash_reflexive(self):
		self.assertTrue(hash(self.onethird) == hash(self.onethird))
		
	def test_hash_representation(self):
		for el in [(2, 6), (3, 9), (-3, -9)]:
			with self.subTest(val=el):
				self.assertTrue(hash(self.onethird) == hash(Rational(*el)))
	
	def test_eq_reflexive(self):
		self.assertTrue(self.onethird == self.onethird)
	
	def test_eq_representation(self):
		for el in [(2, 6), (3, 9), (-3, -9)]:
			with self.subTest(val=el):
				self.assertTrue(self.onethird == Rational(*el))
	
	def test_neq_representation(self):
		for el in [(3, 1), (2, -6), (-3, 9), (-3, 9), (1, 5), (0, 3), (0.5, 1)]:
			with self.subTest(val=el):
				self.assertTrue(self.onethird != Rational(*el))
	
	def test_lt_representation(self):
		for el in [(3, 1), (2, 3), (-10, -29), (1, 2), (0.672, 1)]:
			with self.subTest(val=el):
				self.assertTrue(self.onethird < Rational(*el))
	
	def test_le_representation(self):
		for el in [(3, 1), (2, 3), (-10, -29), (1, 2), (0.672, 1), (1, 3), (-2, -6)]:
			with self.subTest(val=el):
				self.assertTrue(self.onethird <= Rational(*el))
				
	def test_add(self):
		#((a, b), (c, d))  -->  (1, 3) + (a, b) = (c, d)
		for el in [((2, 3), (1, 1)), ((-2, 3), (-1, 3)), ((7, 9), (10, 9))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird + Rational(*el[0]), Rational(*el[1]))
				
	def test_sub(self):
		#((a, b), (c, d))  -->  (1, 3) - (a, b) = (c, d)
		for el in [((2, 3), (-1, 3)), ((-2, 3), (1, 1)), ((7, 9), (-4, 9))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird - Rational(*el[0]), Rational(*el[1]))
				
	def test_mul(self):
		#((a, b), (c, d))  -->  (1, 3) * (a, b) = (c, d)
		for el in [((2, 3), (2, 9)), ((-2, 3), (-2, 9)), ((5, 7), (5, 21))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird * Rational(*el[0]), Rational(*el[1]))
				
	def test_truediv(self):
		#((a, b), (c, d))  -->  (1, 3) * (a, b) = (c, d)
		for el in [((2, 3), (3, 6)), ((-2, 3), (-3, 6)), ((5, 7), (7, 15))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird / Rational(*el[0]), Rational(*el[1]))
				
	def test_pow(self):
		#(a, (b, c))  -->  (1, 3) ** a = (b, c)
		for el in [(2, (1, 9)), (-1, (3, 1)), (0, (1, 1))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird ** el[0], Rational(*el[1]))
				
	def test_mod(self):
		#((a, b), (c, d))  -->  (1, 3) mod (a, b) = (c, d)
		for el in [((2, 3), (1, 3)), ((-2, 3), (-1, 3)), ((1, 6), (0, 1))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird % Rational(*el[0]), Rational(*el[1]))
				
	def test_and(self):
		#((a, b), (c, d))  -->  (1, 3) & (a, b) = (c, d)
		for el in [((2, 3), (3, 6)), ((7, 15), (8, 18))]:
			with self.subTest(val=el):
				self.assertEqual(self.onethird & Rational(*el[0]), Rational(*el[1]))
				
	def test_and_ValueError(self):
		#(a, b)  -->  (1, 3) & (a, b)
		for el in [(17, -23), (18, -20)]:
			with self.subTest(val=el):
				with self.assertRaises(ValueError):
					self.onethird & Rational(*el)
					
	def test_neg(self):
		#(a, b)  -->  -(a, b)
		for el in [((2, 3), (-2, 3)), ((3, 6), (-3, 6)), ((-7, 15), (7, 15)), ((-8, -18), (-8, 18))]:
			with self.subTest(val=el):
				self.assertEqual(-Rational(*el[0]), Rational(*el[1]))
				
	def test_findRationalApproximation_return(self):
		_set = {random.random() for _ in range(5)}
		for precision in range(14 + 1):
			for rand in _set:
				with self.subTest(value=rand, precision=precision):
					self.assertAlmostEqual(rand, float(findRationalApproximation(rand, precision=precision, microIterations=32)), precision - 1)

class TestGroupMethods(unittest.TestCase):
	
	def test_isGroup_isAbelianGroup_TypeError_ValueError(self):
		with self.assertRaises(TypeError):
			isGroup(False, lambda a, b: 0)

		with self.subTest(type="wrong type"):
			with self.assertRaises(TypeError):
				isGroup([0,1,2], 5)
		with self.subTest(type="wrong argument count"):
			with self.assertRaises(TypeError):
				isGroup({0,1,2,3}, lambda a, b, c: a + b + c)

		with self.assertRaises(TypeError):
			isGroup([0], lambda a, b: a + b, tolerance=None)	

		with self.subTest(type="too high"):
			with self.assertRaises(ValueError):
				isGroup([0], lambda a, b: a + b, tolerance=11)
		with self.subTest(type="too low"):
			with self.assertRaises(ValueError):
				isGroup([0], lambda a, b: a + b, tolerance=-1)
		
	def test_isGroup_result(self):
		with self.subTest(type="integer addition"):
			self.assertTrue(isGroup([-4,-3,-2,-1,0,1,2,3,4], lambda a, b: a + b))
		
		with self.subTest(type="integer addition w/o negatives"):
			self.assertFalse(isGroup([0,1,2,3,4], lambda a, b: a + b))
		
		with self.subTest(type="rational multiplication "):
			self.assertTrue(isGroup([Rational(-2),Rational(-1),Rational(-1, 2),Rational(1, 2),Rational(1),Rational(2)], lambda a, b: a * b))
			
		with self.subTest(type="string capitalization"):
			def _string_cap(a, b):
				res = list(str(a))
				for i, char in enumerate(list(a)):
					if char in b: 
						b = b.replace(char, "")
						res[i] = res[i].upper()
				res = res + list(b)
				res.sort()
				if not [None for char in res if char.islower()]: return ""
				return str().join(res)
				
			self.assertTrue(isGroup(["a", "b", "c", "ab", "ac", "bc", ""], _string_cap))
			
		with self.subTest(type="lookup table"):
			"""
			Forms a group but not an Abelian group.
			"""
			def _table_lookup(a, b):
				dict = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 0): 0, (1, 1): 0, (1, 2): 2, (2, 0): 0, (2, 1): 2, (2, 2): 1}
				return dict[(a, b)]
			
			self.assertTrue(isGroup([0,1,2], _table_lookup))
			
	def test_isAbelianGroup_result(self):
		with self.subTest(type="integer addition"):
			self.assertTrue(isAbelianGroup([-4,-3,-2,-1,0,1,2,3,4], lambda a, b: a + b))
		
		with self.subTest(type="integer addition w/o negatives"):
			self.assertFalse(isAbelianGroup([0,1,2,3,4], lambda a, b: a + b))
			
		with self.subTest(type="lookup table"):
			"""
			Forms a group but not an Abelian group.
			"""
			def _table_lookup(a, b):
				dict = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 0): 0, (1, 1): 0, (1, 2): 2, (2, 0): 0, (2, 1): 2, (2, 2): 1}
				return dict[(a, b)]
			
			self.assertFalse(isAbelianGroup([0,1,2], _table_lookup))

if __name__ == "__main__":

	test_performance_rational()
	test_performance_isGroup()
	test_performance_isAbelianGroup()
	test_performance_findRationalApproximation()

	unittest.main()
	