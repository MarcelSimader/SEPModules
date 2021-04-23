import unittest

from SEPModules.SEPAlgebra import AlgebraicStructure, NoElement
from SEPModules.SEPMaths import get_possible_rationals

# noinspection PyTypeChecker
class TestAlgebraicStructure(unittest.TestCase):

	def setUp(self):
		self.add = lambda a, b: a + b
		self.sub = lambda a, b: a - b
		self.mul = lambda x, y: x * y
		self.add_z3 = lambda el0, el1: (el0 + el1) % 3

		self.nums = list(range(10))
		self.neg_nums = list(range(-9, 10))
		self.rationals_wo_zero = get_possible_rationals([x for x in self.neg_nums if x != 0])

		self.add_and_mul_nums = AlgebraicStructure(self.nums, self.add, self.mul)
		self.add_and_mul_neg_nums = AlgebraicStructure(self.neg_nums, self.add, self.mul)
		self.sub_nums = AlgebraicStructure(self.nums, self.sub)
		self.add_nums = AlgebraicStructure(self.nums, self.add)
		self.add_z3_z3 = AlgebraicStructure([0, 1, 2], self.add_z3)
		self.mul_rational_wo_zero = AlgebraicStructure(self.rationals_wo_zero, self.mul)
		self.empty_struct = AlgebraicStructure(())

	def tearDown(self):
		del self.add, self.sub, self.mul, self.add_z3
		del self.nums, self.neg_nums, self.rationals_wo_zero
		del self.add_and_mul_nums, self.add_and_mul_neg_nums, self.sub_nums, self.mul_rational_wo_zero, \
			self.empty_struct, self.add_z3_z3, self.add_nums

	def test_properties(self):
		test_struct = AlgebraicStructure(self.nums, self.add)

		with self.subTest(property="elements"):
			self.assertSetEqual(test_struct.elements, set(self.nums))

		with self.subTest(property="binary_operators"):
			self.assertTupleEqual(test_struct.binary_operators, (self.add,))

		del test_struct

	def test_is_associative(self):
		with self.subTest(type="add and mul"):
			self.assertListEqual(self.add_and_mul_nums.is_associative(), [True, True])
			self.assertTrue(all(self.add_and_mul_nums.is_associative()))

		with self.subTest(type="sub"):
			self.assertListEqual(self.sub_nums.is_associative(), [False])
			self.assertFalse(all(self.sub_nums.is_associative()))

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.is_associative(), [])
			self.assertTrue(all(self.empty_struct.is_associative()))

	def test_neutral_elements(self):
		with self.subTest(type="add and mul"):
			self.assertListEqual(self.add_and_mul_nums.neutral_elements(), [0, 1])

		with self.subTest(type="sub"):
			self.assertListEqual(self.sub_nums.neutral_elements(), [NoElement])

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.neutral_elements(), [])

	def test_find_inverses_per_operator(self):
		for i in self.neg_nums:
			with self.subTest(type="add and mul op 0", num=i):
				self.assertEqual(self.add_and_mul_neg_nums.find_inverses_per_operator(0, i), -i)

			with self.subTest(type="add and mul op 1", num=i):
				self.assertEqual(self.add_and_mul_neg_nums.find_inverses_per_operator(1, i), i if abs(i) == 1 else NoElement)

	def test_has_inverses(self):
		with self.subTest(type="add and mul neg"):
			self.assertListEqual(self.add_and_mul_neg_nums.has_inverses(), [True, False])

		with self.subTest(type="add and mul pos"):
			self.assertListEqual(self.add_and_mul_nums.has_inverses(), [False, False])

		with self.subTest(type="sub pos"):
			self.assertListEqual(self.sub_nums.has_inverses(), [False])

		with self.subTest(type="mul rational"):
			self.assertTrue(self.mul_rational_wo_zero.has_inverses()[0])

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.has_inverses(), [])
			self.assertTrue(all(self.empty_struct.has_inverses()))

	def test_is_commutative(self):
		with self.subTest(type="add and mul neg"):
			self.assertListEqual(self.add_and_mul_neg_nums.is_commutative(), [True, True])

		with self.subTest(type="add and mul pos"):
			self.assertListEqual(self.add_and_mul_nums.is_commutative(), [True, True])

		with self.subTest(type="sub pos"):
			self.assertListEqual(self.sub_nums.is_commutative(), [False])

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.is_commutative(), [])
			self.assertTrue(all(self.empty_struct.is_commutative()))

	def test_is_closed(self):
		with self.subTest(type="add pos"):
			self.assertListEqual(self.add_and_mul_nums.is_closed(), [False, False])

		with self.subTest(type="add z3"):
			self.assertListEqual(self.add_z3_z3.is_closed(), [True])

		with self.subTest(type="empty structure"):
			self.assertListEqual(self.empty_struct.is_closed(), [])

	def test_eq(self):
		with self.subTest(type="ident"):
			self.assertTrue(self.add_and_mul_nums == self.add_and_mul_nums)

		with self.subTest(type="equal"):
			self.assertTrue(self.add_and_mul_neg_nums == AlgebraicStructure(self.neg_nums, self.add, self.mul))

		with self.subTest(type="lambda equal"):
			self.assertTrue(self.add_and_mul_nums == AlgebraicStructure(self.nums, lambda a, b: a + b, lambda a, b: a * b))
			self.assertTrue(self.add_and_mul_nums == AlgebraicStructure(list(range(10)), lambda a, b: a + b, lambda a, b: a * b))

		with self.subTest(type="not equal"):
			self.assertFalse(self.mul_rational_wo_zero == self.add_and_mul_nums)

		with self.subTest(type="empty structure"):
			self.assertTrue(self.empty_struct == AlgebraicStructure(()))

	def test_lt(self):
		with self.subTest(type="add pos < add and mul pos"):
			self.assertFalse(self.add_nums < self.add_and_mul_nums)

		with self.subTest(type="dict"):
			self.assertTrue(AlgebraicStructure([0, 1], lambda a, b: {(0,0):0,(0,1):1,(1,0):1,(1,1):0}[(a,b)]) <
							AlgebraicStructure([0, 1, 2], lambda a, b: {(0,0):0,(0,1):1,(1,0):1,(1,1):0,(0,2):1,(1,2):2,(2,2):1,(2,0):0,(2,1):0}[(a,b)]))

		with self.subTest(type="add z3 < add z7"):
			self.assertTrue(self.add_z3_z3 < AlgebraicStructure(list(range(7)), lambda a, b: (a + b) % 7))

		with self.subTest(type="many ops z3"):
			self.assertTrue(AlgebraicStructure([0, 1, 2], lambda a, b: (a + b) % 3, lambda a, b: (a + b) % 2) <
							AlgebraicStructure([0, 1, 2, 3], lambda a, b: (a + b) % 3, lambda a, b: (a + b) % 4))

		with self.subTest(type="empty structure"):
			self.assertTrue(self.empty_struct < self.add_and_mul_nums)

	def test_practical_use_case(self):
		def string_cap(a, b):
			res = list(str(a))
			for i, char in enumerate(list(a)):
				if char in b:
					b = b.replace(char, "")
					res[i] = res[i].upper()
			res = res + list(b)
			res.sort()
			if not [None for char in res if char.islower()]: return ""
			return str().join(res)

		test_struct = AlgebraicStructure(["", "a", "b", "c", "ab", "ac", "bc"], string_cap)

		with self.subTest(type="associativity"):
			self.assertTrue(test_struct.is_associative()[0])

		with self.subTest(type="neutral el"):
			self.assertEqual(test_struct.neutral_elements()[0], "")

		with self.subTest(type="has inverses"):
			self.assertTrue(test_struct.has_inverses()[0])

		with self.subTest(type="find inverses"):
			for test_str in test_struct.elements:
				with self.subTest(index=test_str):
					self.assertEqual(test_struct.find_inverses_per_operator(0, test_str), test_str)

		with self.subTest(type="closed"):
			self.assertFalse(test_struct.is_closed()[0])

		print(repr(test_struct))

# TODO: write unit tests for AlgebraicStructure subclasses

if __name__ == '__main__':
	unittest.main()
