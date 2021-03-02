import unittest

from itertools import combinations
import random

from SEPModules.SEPMaths import isGroup, isAbelianGroup, Rational, findRationalApproximation, getPossibleRationals
from SEPModules.SEPDecorators import timed

def test_performance_isGroup(n=4):
	print("".rjust(20, "~"))
	z0 = getPossibleRationals(set(range(-n, n+1)))
	print("(n={}) ".format(len(z0)), end="")
	_isGroup = timed(isGroup)
	print("Result: {}".format(_isGroup(z0, lambda a, b: a + b)))

def test_performance_isAbelianGroup(n=4):
	print("".rjust(20, "~"))
	z0 = getPossibleRationals(set(range(-n, n+1)))
	print("(n={}) ".format(len(z0)), end="")
	_isAbelianGroup = timed(isAbelianGroup)
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
	