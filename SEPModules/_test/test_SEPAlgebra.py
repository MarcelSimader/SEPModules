import unittest

from maths.SEPAlgebra import  NoElement, AlgebraicStructure, Monoid, Semigroup, Group, AbelianGroup, Ring, Field
from maths.SEPMaths import get_possible_rationals, Rational


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
			self.assertSetEqual(test_struct.elements, set(self.nums))

		with self.subTest(property="binary_operators"):
			self.assertTupleEqual(test_struct.binary_operators, (self.add,))

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

	def test_repr(self):
		self.assertEqual(self.empty_struct.__repr__(), r"<AlgebraicStructure(set(), ())>")

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

# noinspection PyTypeChecker
class TestMonoid(AlgebraTestBase, unittest.TestCase):

	def setUp(self):
		super().setUp()

		self.add_nums = Monoid(self.nums, self.add)
		self.add_neg_nums = Monoid(self.neg_nums, self.add)
		self.sub_nums = Monoid(self.nums, self.sub)
		self.add_z3_z3 = Monoid([0, 1, 2], self.add_z3)
		self.mul_rational_wo_zero = Monoid(self.rationals_wo_zero, self.mul)
		self.empty_struct = Monoid((), lambda a, b: 0)

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
			self.assertEqual(self.add_nums.neutral_elements(), 0)

		with self.subTest(type="empty structure"):
			self.assertEqual(self.empty_struct.neutral_elements(), NoElement)

	def test_find_inverses(self):
		with self.subTest(type="add z3"):
			self.assertEqual(self.add_z3_z3.find_inverses(0), 0)
			self.assertEqual(self.add_z3_z3.find_inverses(1), 2)
			self.assertEqual(self.add_z3_z3.find_inverses(2), 1)

		with self.subTest(type="sub nums"):
			self.assertEqual(self.sub_nums.find_inverses(0), NoElement)
			self.assertEqual(self.sub_nums.find_inverses(3), NoElement)

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
class TestSemigroup(AlgebraTestBase, unittest.TestCase):

	def test_is_valid(self):
		with self.subTest(type="sub pos"):
			self.assertFalse(Semigroup(self.nums, self.sub))

		with self.subTest(type="add pos"):
			self.assertTrue(Semigroup(self.nums, self.add))

		with self.subTest(type="mul rational w/o zero and 1/2"):
			self.assertTrue(Semigroup(self.rationals_wo_zero.difference((Rational(1,2),)), self.mul))

# noinspection PyTypeChecker
class TestGroup(AlgebraTestBase, unittest.TestCase):

	def test_is_valid(self):
		with self.subTest(type="sub pos"):
			self.assertFalse(Group(self.nums, self.sub))

		with self.subTest(type="add pos"):
			self.assertFalse(Group(self.nums, self.add))

		with self.subTest(type="mul rational w/o zero and 1/2"):
			self.assertFalse(Group(self.rationals_wo_zero.difference((Rational(1,2),)), self.mul))

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
		self.assertSetEqual(self.add_mul_nums.elements_without_zero, set(self.nums) - {0})

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
			self.assertTupleEqual(self.add_mul_nums.is_associative(), (True, True))

		with self.subTest(type="add sub nums"):
			self.assertTupleEqual(self.add_sub_nums.is_associative(), (True, False))

		with self.subTest(type="empty struct"):
			self.assertTupleEqual(self.empty_struct.is_associative(), (True, True))

	def test_neutral_elements(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual(self.add_mul_nums.neutral_elements(), (0, 1))

		with self.subTest(type="add sub nums"):
			self.assertTupleEqual(self.add_sub_nums.neutral_elements(), (0, NoElement))

		with self.subTest(type="empty struct"):
			self.assertTupleEqual(self.empty_struct.neutral_elements(), (NoElement, NoElement))

	def test_find_inverses(self):
		with self.subTest(type="add mul nums"):
			self.assertEqual(self.add_mul_nums.find_inverses(0, 5), NoElement)
			self.assertEqual(self.add_mul_nums.find_inverses(1, 0), NoElement)

		with self.subTest(type="add mul z3"):
			self.assertEqual(self.add_mul_z3.find_inverses(0, 2), 1)
			self.assertEqual(self.add_mul_z3.find_inverses(1, 2), 2)

	def test_has_inverses(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual(self.add_mul_nums.has_inverses(), (False, False))

		with self.subTest(type="add mul neg nums"):
			self.assertTupleEqual(self.add_mul_neg_nums.has_inverses(), (True, False))

	def test_is_commutative(self):
		with self.subTest(type="add mul nums"):
			self.assertTupleEqual(self.add_mul_nums.is_commutative(), (True, True))

		with self.subTest(type="add sub nums"):
			self.assertTupleEqual(self.add_sub_nums.is_commutative(), (True, False))

	def test_is_closed(self):
		with self.subTest(type="add sub nums"):
			self.assertTupleEqual(self.add_sub_nums.is_closed(), (False, False))

		with self.subTest(type="add mul z3"):
			self.assertTupleEqual(self.add_mul_z3.is_closed(), (True, True))

		with self.subTest(type="empty structure"):
			self.assertTupleEqual(self.empty_struct.is_closed(), (True, True))

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
