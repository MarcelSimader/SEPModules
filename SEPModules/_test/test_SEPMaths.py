import unittest

from itertools import combinations
import random
from math import fmod

from maths.SEPMaths import is_group, is_abelian_group, Rational, find_rational_approximation, get_possible_rationals
from SEPModules.SEPDecorators import timed

# noinspection PyTypeChecker
def test_performance_is_group(n=4):
	print("".rjust(20, "~"))
	z0 = get_possible_rationals(set(range(-n, n + 1)))
	print("(n={}) ".format(len(z0)), end="")
	_isGroup = timed(is_group)
	print("Result: {}".format(_isGroup(z0, lambda a, b: a + b)))

# noinspection PyTypeChecker
def test_performance_is_abelian_group(n=4):
	print("".rjust(20, "~"))
	z0 = get_possible_rationals(set(range(-n, n + 1)))
	print("(n={}) ".format(len(z0)), end="")
	_isAbelianGroup = timed(is_abelian_group)
	print("Result: {}".format(_isAbelianGroup(z0, lambda a, b: a + b)))

# noinspection PyTypeChecker
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
			In case a lot of data should be thrown at the class to _test it.
			"""
			# r = op(Rational(k, j), Rational(i, l))
			# t = op_int(k/j, i/l)
			# if float(r) - t >= 10**-14:
				# print(cl_s("{},{}: {} is not equal to {}!".format((k, j), (i, l), float(r), t), RED))

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

# noinspection PyTypeChecker
def test_performance_find_rational_approximation(n=100_000, precision=6):
	print("{}\n(n={:f_}, precision={}) ".format(str().rjust(20, "~"), n, precision), end="")

	rands = [random.random() for _ in range(n)]

	@timed
	def __test_performance_find_rational_approximation__():
		for k in rands:
			find_rational_approximation(k, precision=precision)
	__test_performance_find_rational_approximation__()

# noinspection PyTypeChecker
class TestRationalMethods(unittest.TestCase):
	
	def setUp(self):
		self.zero 		= Rational(0, 1)
		self.neg_zero 	= Rational(0, -1)
		self.one_third 	= Rational(1, 3)
		self.two_fifth 	= Rational(2, 5)
		
		self.invalidCases = [(0, 0), (1, 0), (-1, 0), (0, -0), (-0, 0), (-0, -0)]
		self.cases = {(0, 1): (0, 1), (1, 1): (1, 1), (2, 1): (2, 1), (-3, 1): (-3, 1), (0, 2): (0, 1), (-0, 3): (-0, 1), (1, 2): (1, 2), (2, -2): (-1, 1),
		(3, 2): (3, 2), (-0, -3): (0, 1), (1, 3): (1, 3), (2, 3): (2, 3), (-6, 3): (-2, 1), (2, 4): (1, 2), (6, -4): (-3, 2), (35, 45): (7, 9),
		(-64, -16): (4, 1), (27, 33): (9, 11), (18, 108): (1, 6)}
	
	def tearDown(self):
		del self.zero, self.neg_zero, self.one_third, self.two_fifth, self.invalidCases, self.cases
	
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
	
	def test_hash_reflexive(self):
		self.assertTrue(hash(self.one_third) == hash(self.one_third))
		
	def test_hash_representation(self):
		for el in [(2, 6), (3, 9), (-3, -9)]:
			with self.subTest(val=el):
				self.assertTrue(hash(self.one_third) == hash(Rational(*el)))
	
	def test_eq_reflexive(self):
		self.assertTrue(self.one_third == self.one_third)
	
	def test_eq_representation(self):
		for el in [(2, 6), (3, 9), (-3, -9)]:
			with self.subTest(val=el):
				self.assertTrue(self.one_third == Rational(*el))
	
	def test_neq_representation(self):
		for el in [(3, 1), (2, -6), (-3, 9), (-3, 9), (1, 5), (0, 3), (0.5, 1)]:
			with self.subTest(val=el):
				self.assertTrue(self.one_third != Rational(*el))
	
	def test_lt_representation(self):
		for el in [(3, 1), (2, 3), (-10, -29), (1, 2), (0.672, 1)]:
			with self.subTest(val=el):
				self.assertTrue(self.one_third < Rational(*el))
	
	def test_le_representation(self):
		for el in [(3, 1), (2, 3), (-10, -29), (1, 2), (0.672, 1), (1, 3), (-2, -6)]:
			with self.subTest(val=el):
				self.assertTrue(self.one_third <= Rational(*el))
				
	def test_add(self):
		#((a, b), (c, d))  -->  (1, 3) + (a, b) = (c, d)
		for el in [((2, 3), (1, 1)), ((-2, 3), (-1, 3)), ((7, 9), (10, 9))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third + Rational(*el[0]), Rational(*el[1]))
				
	def test_sub(self):
		#((a, b), (c, d))  -->  (1, 3) - (a, b) = (c, d)
		for el in [((2, 3), (-1, 3)), ((-2, 3), (1, 1)), ((7, 9), (-4, 9))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third - Rational(*el[0]), Rational(*el[1]))
				
	def test_mul(self):
		#((a, b), (c, d))  -->  (1, 3) * (a, b) = (c, d)
		for el in [((2, 3), (2, 9)), ((-2, 3), (-2, 9)), ((5, 7), (5, 21))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third * Rational(*el[0]), Rational(*el[1]))
				
	def test_truediv(self):
		#((a, b), (c, d))  -->  (1, 3) * (a, b) = (c, d)
		for el in [((2, 3), (3, 6)), ((-2, 3), (-3, 6)), ((5, 7), (7, 15))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third / Rational(*el[0]), Rational(*el[1]))
				
	def test_pow(self):
		#(a, (b, c))  -->  (1, 3) ** a = (b, c)
		for el in [(2, (1, 9)), (-1, (3, 1)), (0, (1, 1))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third ** el[0], Rational(*el[1]))
				
	def test_mod(self):
		#((a, b), (c, d))  -->  (1, 3) mod (a, b) = (c, d)
		for el in [((2, 3), (1, 3)), ((-2, 3), (-1, 3)), ((1, 6), (0, 1))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third % Rational(*el[0]), Rational(*el[1]))
				
	def test_and(self):
		#((a, b), (c, d))  -->  (1, 3) & (a, b) = (c, d)
		for el in [((2, 3), (3, 6)), ((7, 15), (8, 18))]:
			with self.subTest(val=el):
				self.assertEqual(self.one_third & Rational(*el[0]), Rational(*el[1]))
				
	def test_and_ValueError(self):
		# (a, b)  -->  (1, 3) & (a, b)
		for el in [(17, -23), (18, -20)]:
			with self.subTest(val=el):
				with self.assertRaises(ValueError):
					self.one_third & Rational(*el)
					
	def test_neg(self):
		# (a, b)  -->  -(a, b)
		for el in [((2, 3), (-2, 3)), ((3, 6), (-3, 6)), ((-7, 15), (7, 15)), ((-8, -18), (-8, 18))]:
			with self.subTest(val=el):
				self.assertEqual(-Rational(*el[0]), Rational(*el[1]))
				
	def test_findRationalApproximation_return(self):
		_set = {random.random() for _ in range(5)}
		for precision in range(14 + 1):
			for rand in _set:
				with self.subTest(value=rand, precision=precision):
					self.assertAlmostEqual(rand, float(find_rational_approximation(rand, precision=precision)), precision - 1)

if __name__ == "__main__":
	test_performance_rational()
	test_performance_find_rational_approximation()
	