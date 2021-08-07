"""
:Author: Marcel Simader
:Date: 17.07.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import unittest

from SEPMaths import get_possible_rationals, Rational
from maths.SEPAlgebra import NoElement, AlgebraicStructure, Semigroup, Group, AbelianGroup, Ring, Field, Monoid

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ TESTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# noinspection PyTypeChecker
class AlgebraTestBase:

	def setUp(self):
		self.add = lambda a, b: a + b
		self.sub = lambda a, b: a - b
		self.mul = lambda x, y: x * y
		self.add_z3 = lambda el0, el1: (el0 + el1) % 3

		self.nums = list(range(10))
		self.neg_nums = list(range(-9, 10))
		self.rationals_wo_zero = get_possible_rationals([x for x in range(-3, 4) if x != 0])

	def tearDown(self):
		del self.add, self.sub, self.mul, self.add_z3
		del self.nums, self.neg_nums, self.rationals_wo_zero

# noinspection PyTypeChecker
class TestAlgebraicStructure(AlgebraTestBase, unittest.TestCase):

	def setUp(self):
		super().setUp()

		self.add_and_mul_nums = AlgebraicStructure(self.nums, self.add, self.mul)
		self.add_and_mul_neg_nums = AlgebraicStructure(self.neg_nums, self.add, self.mul)
		self.sub_nums = AlgebraicStructure(self.nums, self.sub)
		self.add_nums = AlgebraicStructure(self.nums, self.add)
		self.add_z3_z3 = AlgebraicStructure([0, 1, 2], self.add_z3)
		self.mul_rational_wo_zero = AlgebraicStructure(self.rationals_wo_zero, self.mul)
		self.empty_struct = AlgebraicStructure(())

	def tearDown(self):
		super().tearDown()

		del self.add_and_mul_nums, self.add_and_mul_neg_nums, self.sub_nums, self.mul_rational_wo_zero, \
			self.empty_struct, self.add_z3_z3, self.add_nums

	def test_properties(self):
		test_struct = AlgebraicStructure(self.nums, self.add)

		with self.subTest(property="elements"):
			self.assertSetEqual(set(self.nums), test_struct.elements)

		with self.subTest(property="binary_operators"):
			self.assertTupleEqual((self.add,), test_struct.binary_operators)

		del test_struct

	def test_is_valid(self):
		with self.subTest(type="add and mul pos no-_test"):
			self.assertTrue(self.add_and_mul_nums)
			self.assertTrue(self.add_and_mul_nums.is_valid())

		with self.subTest(type="add and mul pos _test"):
			self.assertTrue(AlgebraicStructure(self.nums, self.add, self.mul, test_for_closure=False))
			self.assertTrue(AlgebraicStructure(self.nums, self.add, self.mul, test_for_closure=False).is_valid())
			self.assertFalse(AlgebraicStructure(self.nums, self.add, self.mul, test_for_closure=True))
			self.assertFalse(AlgebraicStructure(self.nums, self.add, self.mul, test_for_closure=True).is_valid())

		with self.subTest(type="add z3 _test"):
			self.assertTrue(AlgebraicStructure([0, 1, 2], self.add_z3, test_for_closure=True))
			self.assertTrue(AlgebraicStructure([0, 1, 2], self.add_z3, test_for_closure=True).is_valid())

		with self.subTest(type="empty struct"):
			self.assertTrue(AlgebraicStructure([], test_for_closure=True))
			self.assertTrue(AlgebraicStructure([], test_for_closure=True).is_valid())

	def test_is_associative(self):
		with self.subTest(type="add and mul"):
			self.assertListEqual([True, True], list(self.add_and_mul_nums.is_associative()))
			self.assertTrue(all(self.add_and_mul_nums.is_associative()))

		with self.subTest(type="sub"):
			self.assertListEqual([False], list(self.sub_nums.is_associative()))
			self.assertFalse(all(self.sub_nums.is_associative()))

		with self.subTest(type="empty structure"):
			self.assertListEqual([], list(self.empty_struct.is_associative()))
			self.assertTrue(all(self.empty_struct.is_associative()))

	def test_neutral_elements(self):
		with self.subTest(type="add and mul"):
			self.assertListEqual([0, 1], list(self.add_and_mul_nums.neutral_elements()))

		with self.subTest(type="sub"):
			self.assertListEqual([NoElement], list(self.sub_nums.neutral_elements()))

		with self.subTest(type="empty structure"):
			self.assertListEqual([], list(self.empty_struct.neutral_elements()))

	def test_find_inverses_per_operator(self):
		for i in self.neg_nums:
			with self.subTest(type="add and mul op 0", num=i):
				self.assertEqual(-i, self.add_and_mul_neg_nums.find_inverses_per_operator(0, i))

			with self.subTest(type="add and mul op 1", num=i):
				self.assertEqual(i if abs(i) == 1 else NoElement,
								 self.add_and_mul_neg_nums.find_inverses_per_operator(1, i))

	def test_has_inverses(self):
		with self.subTest(type="add and mul neg"):
			self.assertListEqual([True, False], list(self.add_and_mul_neg_nums.has_inverses()))

		with self.subTest(type="add and mul pos"):
			self.assertListEqual([False, False], list(self.add_and_mul_nums.has_inverses()))

		with self.subTest(type="sub pos"):
			self.assertListEqual([False], list(self.sub_nums.has_inverses()))

		with self.subTest(type="mul rational"):
			self.assertTrue(list(self.mul_rational_wo_zero.has_inverses())[0])

		with self.subTest(type="empty structure"):
			self.assertListEqual([], list(self.empty_struct.has_inverses()))
			self.assertTrue(all(self.empty_struct.has_inverses()))

	def test_is_commutative(self):
		with self.subTest(type="add and mul neg"):
			self.assertListEqual([True, True], list(self.add_and_mul_neg_nums.is_commutative()))

		with self.subTest(type="add and mul pos"):
			self.assertListEqual([True, True], list(self.add_and_mul_nums.is_commutative()))

		with self.subTest(type="sub pos"):
			self.assertListEqual([False], list(self.sub_nums.is_commutative()))

		with self.subTest(type="empty structure"):
			self.assertListEqual([], list(self.empty_struct.is_commutative()))
			self.assertTrue(all(self.empty_struct.is_commutative()))

	def test_is_closed(self):
		with self.subTest(type="add pos"):
			self.assertListEqual([False, False], list(self.add_and_mul_nums.is_closed()))

		with self.subTest(type="add z3"):
			self.assertListEqual([True], list(self.add_z3_z3.is_closed()))

		with self.subTest(type="empty structure"):
			self.assertListEqual([], list(self.empty_struct.is_closed()))

	def test_eq(self):
		with self.subTest(type="ident"):
			self.assertEqual(self.add_and_mul_nums, self.add_and_mul_nums)

		with self.subTest(type="equal"):
			self.assertEqual(self.add_and_mul_neg_nums, AlgebraicStructure(self.neg_nums, self.add, self.mul))

		with self.subTest(type="lambda equal"):
			self.assertEqual(self.add_and_mul_nums,
							 AlgebraicStructure(self.nums, lambda a, b: a + b, lambda a, b: a * b))
			self.assertEqual(self.add_and_mul_nums,
							 AlgebraicStructure(list(range(10)), lambda a, b: a + b, lambda a, b: a * b))

		with self.subTest(type="not equal"):
			self.assertNotEqual(self.mul_rational_wo_zero, self.add_and_mul_nums)

		with self.subTest(type="empty structure"):
			self.assertEqual(self.empty_struct, AlgebraicStructure(()))

	def test_lt(self):
		with self.subTest(type="add pos < add and mul pos"):
			self.assertGreaterEqual(self.add_nums, self.add_and_mul_nums)

		with self.subTest(type="dict"):
			self.assertLess(
					AlgebraicStructure([0, 1], lambda a, b: {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0}[(a, b)]),
					AlgebraicStructure([0, 1, 2], lambda a, b: {(0, 0): 0, (0, 1): 1, (1, 0): 1, (1, 1): 0, (0, 2): 1,
																(1, 2): 2, (2, 2): 1, (2, 0): 0, (2, 1): 0}[(a, b)]))

		with self.subTest(type="add z3 < add z7"):
			self.assertLess(self.add_z3_z3, AlgebraicStructure(list(range(7)), lambda a, b: (a + b) % 7))

		with self.subTest(type="many ops z3"):
			self.assertLess(AlgebraicStructure([0, 1, 2], lambda a, b: (a + b) % 3, lambda a, b: (a + b) % 2),
							AlgebraicStructure([0, 1, 2, 3], lambda a, b: (a + b) % 3, lambda a, b: (a + b) % 4))

		with self.subTest(type="empty structure"):
			self.assertLess(self.empty_struct, self.add_and_mul_nums)

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
			self.assertTrue(list(test_struct.is_associative())[0])

		with self.subTest(type="neutral el"):
			self.assertEqual(list(test_struct.neutral_elements())[0], "")

		with self.subTest(type="has inverses"):
			self.assertTrue(list(test_struct.has_inverses())[0])

		with self.subTest(type="find inverses"):
			for test_str in test_struct.elements:
				with self.subTest(index=test_str):
					self.assertEqual(test_struct.find_inverses_per_operator(0, test_str), test_str)

		with self.subTest(type="closed"):
			self.assertFalse(list(test_struct.is_closed())[0])

# noinspection PyTypeChecker
class TestSemigroup(AlgebraTestBase, unittest.TestCase):

	def setUp(self):
		super().setUp()

		self.add_nums = Semigroup(self.nums, self.add)
		self.add_neg_nums = Semigroup(self.neg_nums, self.add)
		self.sub_nums = Semigroup(self.nums, self.sub)
		self.add_z3_z3 = Semigroup([0, 1, 2], self.add_z3)
		self.mul_rational_wo_zero = Semigroup(self.rationals_wo_zero, self.mul)
		self.empty_struct = Semigroup((), lambda a, b: 0)

	def tearDown(self):
		super().tearDown()

		del self.add_neg_nums, self.sub_nums, self.mul_rational_wo_zero, \
			self.empty_struct, self.add_z3_z3, self.add_nums

	def test_property(self):
		self.assertEqual(self.add_nums.binary_operator, self.add)

	def test_is_valid(self):
		with self.subTest(type="add pos"):
			self.assertTrue(self.add_nums)
			self.assertTrue(self.add_nums.is_valid())

		with self.subTest(type="sub pos"):
			self.assertFalse(self.sub_nums)
			self.assertFalse(self.sub_nums.is_valid())

		with self.subTest(type="empty struct"):
			self.assertTrue(self.empty_struct)
			self.assertTrue(self.empty_struct.is_valid())

	def test_is_associative(self):
		with self.subTest(type="add pos"):
			self.assertTrue(self.add_nums.is_associative())

	def test_neutral_elements(self):
		with self.subTest(type="add pos"):
			self.assertEqual(0, self.add_nums.neutral_elements())

		with self.subTest(type="empty structure"):
			self.assertEqual(NoElement, self.empty_struct.neutral_elements())

	def test_find_inverses(self):
		with self.subTest(type="add z3"):
			self.assertEqual(0, self.add_z3_z3.find_inverses(0))
			self.assertEqual(2, self.add_z3_z3.find_inverses(1))
			self.assertEqual(1, self.add_z3_z3.find_inverses(2))

		with self.subTest(type="sub nums"):
			self.assertEqual(NoElement, self.sub_nums.find_inverses(0))
			self.assertEqual(NoElement, self.sub_nums.find_inverses(3))

	def test_has_inverses(self):
		with self.subTest(type="mul rational w/o zero"):
			self.assertTrue(self.mul_rational_wo_zero.has_inverses())

		with self.subTest(type="sub pos"):
			self.assertFalse(self.sub_nums.has_inverses())

	def test_is_commutative(self):
		with self.subTest(type="add neg"):
			self.assertTrue(self.add_neg_nums.is_commutative())

		with self.subTest(type="sub pos"):
			self.assertFalse(self.sub_nums.is_commutative())

	def test_is_closed(self):
		with self.subTest(type="add pos"):
			self.assertFalse(self.add_nums.is_closed())

# noinspection PyTypeChecker
class TestMonoid(AlgebraTestBase, unittest.TestCase):

	def test_is_valid(self):
		with self.subTest(type="sub pos"):
			self.assertFalse(Monoid(self.nums, self.sub))

		with self.subTest(type="add pos"):
			self.assertTrue(Monoid(self.nums, self.add))

		with self.subTest(type="mul rational w/o zero and 1/2"):
			self.assertTrue(Monoid(self.rationals_wo_zero.difference((Rational(1, 2),)), self.mul))

# noinspection PyTypeChecker
class TestGroup(AlgebraTestBase, unittest.TestCase):

	def test_is_valid(self):
		with self.subTest(type="sub pos"):
			self.assertFalse(Group(self.nums, self.sub))

		with self.subTest(type="add pos"):
			self.assertFalse(Group(self.nums, self.add))

		with self.subTest(type="mul rational w/o zero and 1/2"):
			self.assertFalse(Group(self.rationals_wo_zero.difference((Rational(1, 2),)), self.mul))

		with self.subTest(type="add neg"):
			self.assertTrue(Group(self.neg_nums, self.add))

# noinspection PyTypeChecker
class TestAbelianGroup(AlgebraTestBase, unittest.TestCase):

	def test_is_valid(self):
		with self.subTest(type="sub pos"):
			self.assertFalse(AbelianGroup(self.nums, self.sub))

		with self.subTest(type="add neg"):
			self.assertTrue(AbelianGroup(self.neg_nums, self.add))

# noinspection PyTypeChecker
class TestRing(AlgebraTestBase, unittest.TestCase):

	def setUp(self):
		super().setUp()

		self.add_mul_nums = Ring(self.nums, self.add, self.mul)
		self.add_mul_neg_nums = Ring(self.neg_nums, self.add, self.mul)
		self.add_sub_nums = Ring(self.nums, self.add, self.sub)
		self.add_mul_z3 = Ring([0, 1, 2], self.add_z3, lambda a, b: (a * b) % 3, test_for_closure=True)
		self.empty_struct = Ring((), lambda a, b: 0, lambda c, d: 1)

	def tearDown(self):
		super().tearDown()

		del self.add_mul_nums, self.add_mul_neg_nums, self.add_sub_nums, self.add_mul_z3, self.empty_struct

	def test_elements_without_zero(self):
		self.assertSetEqual(set(self.nums) - {0}, self.add_mul_nums.elements_without_zero)

	def test_is_valid(self):
		with self.subTest(type="add mul nums"):
			self.assertFalse(self.add_mul_nums)

		with self.subTest(type="add sub nums"):
			self.assertFalse(self.add_sub_nums)

		with self.subTest(type="add mul neg nums"):
			self.assertTrue(self.add_mul_neg_nums)

		with self.subTest(type="add mul z3"):
			self.assertTrue(self.add_mul_z3)

	def test_is_associative(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual((True, True), self.add_mul_nums.is_associative())

		with self.subTest(type="add sub nums"):
			self.assertTupleEqual((True, False), self.add_sub_nums.is_associative())

		with self.subTest(type="empty struct"):
			self.assertTupleEqual((True, True), self.empty_struct.is_associative())

	def test_neutral_elements(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual((0, 1), self.add_mul_nums.neutral_elements())

		with self.subTest(type="add sub nums"):
			self.assertTupleEqual((0, NoElement), self.add_sub_nums.neutral_elements())

		with self.subTest(type="empty struct"):
			self.assertTupleEqual((NoElement, NoElement), self.empty_struct.neutral_elements())

	def test_find_inverses(self):
		with self.subTest(type="add mul nums"):
			self.assertEqual(NoElement, self.add_mul_nums.find_inverses(0, 5))
			self.assertEqual(NoElement, self.add_mul_nums.find_inverses(1, 0))

		with self.subTest(type="add mul z3"):
			self.assertEqual(1, self.add_mul_z3.find_inverses(0, 2))
			self.assertEqual(2, self.add_mul_z3.find_inverses(1, 2))

	def test_has_inverses(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual((False, False), self.add_mul_nums.has_inverses())

		with self.subTest(type="add mul neg nums"):
			self.assertTupleEqual((True, False), self.add_mul_neg_nums.has_inverses())

	def test_is_commutative(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual((True, True), self.add_mul_nums.is_commutative())

		with self.subTest(type="add sub nums"):
			self.assertTupleEqual((True, False), self.add_sub_nums.is_commutative())

	def test_is_closed(self):
		with self.subTest(type="add sub nums"):
			self.assertTupleEqual((False, False), self.add_sub_nums.is_closed())

		with self.subTest(type="add mul z3"):
			self.assertTupleEqual((True, True), self.add_mul_z3.is_closed())

		with self.subTest(type="empty structure"):
			self.assertTupleEqual((True, True), self.empty_struct.is_closed())

	def test_is_distributive(self):
		with self.subTest(type="add mul"):
			self.assertTrue(self.add_mul_nums.is_distributive())

		with self.subTest(type="add add"):
			self.assertFalse(Ring(self.nums, self.add, self.add).is_distributive())

		with self.subTest(type="empty struct"):
			self.assertTrue(self.empty_struct.is_distributive())

# noinspection PyTypeChecker
class TestField(AlgebraTestBase, unittest.TestCase):

	def test_is_valid(self):
		with self.subTest(type="add mul nums"):
			self.assertFalse(Field(self.nums, self.add, self.mul))

		with self.subTest(type="add mul neg nums"):
			self.assertFalse(Field(self.neg_nums, self.add, self.mul))

		with self.subTest(type="add mul rationals"):
			self.assertTrue(Field(get_possible_rationals(list(range(-3, 4))), self.add, self.mul))

		with self.subTest(type="add mul z3"):
			self.assertTrue(Field({0, 1, 2}, self.add_z3, lambda a, b: (a * b) % 3, test_for_closure=True))

if __name__ == '__main__':
	unittest.main()
