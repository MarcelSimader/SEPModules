import unittest

from SEPModules.SEPAlgebra import AlgebraicStructure, NoNeutralElement

# TODO: adapt unit tests for group methods
# class TestGroupMethods(unittest.TestCase):
#
# 	def test_isGroup_isAbelianGroup_TypeError_ValueError(self):
# 		with self.assertRaises(TypeError):
# 			is_group(False, lambda a, b: 0)
#
# 		with self.subTest(type="wrong type"):
# 			with self.assertRaises(TypeError):
# 				is_group([0, 1, 2], 5)
# 		with self.subTest(type="wrong argument count"):
# 			with self.assertRaises(TypeError):
# 				is_group({0, 1, 2, 3}, lambda a, b, c: a + b + c)
#
# 		with self.assertRaises(TypeError):
# 			is_group([0], lambda a, b: a + b, tolerance=None)
#
# 		with self.subTest(type="too high"):
# 			with self.assertRaises(ValueError):
# 				is_group([0], lambda a, b: a + b, tolerance=11)
# 		with self.subTest(type="too low"):
# 			with self.assertRaises(ValueError):
# 				is_group([0], lambda a, b: a + b, tolerance=-1)
#
# 	def test_isGroup_result(self):
# 		with self.subTest(type="integer addition"):
# 			self.assertTrue(is_group([-4, -3, -2, -1, 0, 1, 2, 3, 4], lambda a, b: a + b))
#
# 		with self.subTest(type="integer addition w/o negatives"):
# 			self.assertFalse(is_group([0, 1, 2, 3, 4], lambda a, b: a + b))
#
# 		with self.subTest(type="rational multiplication "):
# 			self.assertTrue(
# 				is_group([Rational(-2), Rational(-1), Rational(-1, 2), Rational(1, 2), Rational(1), Rational(2)],
# 						 lambda a, b: a * b))
#
# 		with self.subTest(type="string capitalization"):
# 			def _string_cap(a, b):
# 				res = list(str(a))
# 				for i, char in enumerate(list(a)):
# 					if char in b:
# 						b = b.replace(char, "")
# 						res[i] = res[i].upper()
# 				res = res + list(b)
# 				res.sort()
# 				if not [None for char in res if char.islower()]: return ""
# 				return str().join(res)
#
# 			self.assertTrue(is_group(["a", "b", "c", "ab", "ac", "bc", ""], _string_cap))
#
# 		with self.subTest(type="lookup table"):
# 			"""
# 			Forms a group but not an Abelian group.
# 			"""
#
# 			def _table_lookup(a, b):
# 				dict = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 0): 0, (1, 1): 0, (1, 2): 2, (2, 0): 0, (2, 1): 2,
# 						(2, 2): 1}
# 				return dict[(a, b)]
#
# 			self.assertTrue(is_group([0, 1, 2], _table_lookup))
#
# 	def test_isAbelianGroup_result(self):
# 		with self.subTest(type="integer addition"):
# 			self.assertTrue(is_abelian_group([-4, -3, -2, -1, 0, 1, 2, 3, 4], lambda a, b: a + b))
#
# 		with self.subTest(type="integer addition w/o negatives"):
# 			self.assertFalse(is_abelian_group([0, 1, 2, 3, 4], lambda a, b: a + b))
#
# 		with self.subTest(type="lookup table"):
# 			"""
# 			Forms a group but not an Abelian group.
# 			"""
#
# 			def _table_lookup(a, b):
# 				dict = {(0, 0): 0, (0, 1): 1, (0, 2): 2, (1, 0): 0, (1, 1): 0, (1, 2): 2, (2, 0): 0, (2, 1): 2,
# 						(2, 2): 1}
# 				return dict[(a, b)]
#
# 			self.assertFalse(is_abelian_group([0, 1, 2], _table_lookup))

class TestAlgebraicStructure(unittest.TestCase):

	def setUp(self):
		self.add = lambda a, b: a + b
		self.sub = lambda a, b: a - b
		self.mul = lambda x, y: x * y
		self.add_z3 = lambda el0, el1: (el0 + el1) % 3

		self.nums = list(range(10))
		self.neg_nums = list(range(-9, 10))

		self.empty_struct = AlgebraicStructure((), ())

	def tearDown(self):
		del self.add, self.mul, self.add_z3
		del self.nums, self.neg_nums
		del self.empty_struct

	def test_properties(self):
		test_struct = AlgebraicStructure(self.nums, (self.add,))

		with self.subTest(property="elements"):
			self.assertSetEqual(test_struct.elements, set(self.nums))

		with self.subTest(property="binary_operators"):
			self.assertTupleEqual(test_struct.binary_operators, (self.add,))

		del test_struct

	def test_is_associative(self):
		with self.subTest(type="add and mul"):
			test_struct = AlgebraicStructure(self.nums, (self.add, self.mul))
			self.assertListEqual(test_struct.is_associative(), [True, True])
			self.assertTrue(all(test_struct.is_associative()))

		with self.subTest(type="sub"):
			test_struct = AlgebraicStructure(self.nums, (self.sub,))
			self.assertListEqual(test_struct.is_associative(), [False])
			self.assertFalse(all(test_struct.is_associative()))

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.is_associative(), [])
			self.assertTrue(all(self.empty_struct.is_associative()))

		del test_struct

	def test_neutral_elements(self):
		with self.subTest(type="add and mul"):
			test_struct = AlgebraicStructure(self.nums, (self.add, self.mul))
			self.assertListEqual(test_struct.neutral_elements(), [0, 1])

		with self.subTest(type="sub"):
			test_struct = AlgebraicStructure(self.nums, (self.sub,))
			self.assertListEqual(test_struct.neutral_elements(), [NoNeutralElement])

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.neutral_elements(), [])

		del test_struct



if __name__ == '__main__':
	unittest.main()
