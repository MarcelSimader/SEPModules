"""
Author: Marcel Simader
Data: 01.04.2021

..	versionadded:: 1.4.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import unittest
from itertools import combinations
from typing import Type

from SEPModules.maths.SEPLogic import AtomicProposition, Top, Bottom, LogicalConnective, _Top, _Bottom

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TestAtomicProposition(unittest.TestCase):

	class TestImplementationAtomicProposition(AtomicProposition):
		pass

	@staticmethod
	def reset_atomic_proposition(cls: Type[AtomicProposition] = AtomicProposition):
		if cls is AtomicProposition:
			cls._id_set = set()
			cls._curr_name = None
			cls._curr_name_primes = 0
			cls._curr_name_prefix = ""
		else:
			cls.__init_subclass__()

	def setUp(self) -> None:
		self.reset_atomic_proposition()

		at = AtomicProposition
		self.prime = at._prime
		self.a, self.b, self.c, self.d = at(), at(), at(), at()

	def tearDown(self) -> None:
		del self.a, self.b, self.c, self.d

	def test_id_gen(self):
		self.reset_atomic_proposition()
		self.assertSetEqual(set(), AtomicProposition._id_set)
		self.assertEqual(3, AtomicProposition._next_id(3))
		self.assertSetEqual({3}, AtomicProposition._id_set)
		self.assertEqual(621, AtomicProposition._next_id(621))
		self.assertSetEqual({3, 621}, AtomicProposition._id_set)
		new_id = AtomicProposition._next_id(3)
		self.assertNotEqual(3, new_id)
		self.assertSetEqual({3, 621, new_id}, AtomicProposition._id_set)

		_at = TestAtomicProposition.TestImplementationAtomicProposition
		self.reset_atomic_proposition(_at)
		_a = _at()
		self.assertSetEqual({3, 621, new_id, _a._id}, AtomicProposition._id_set)
		self.assertSetEqual({3, 621, new_id, _a._id}, _at._id_set)
		_b = _at()
		self.assertSetEqual({3, 621, new_id, _a._id, _b.id}, AtomicProposition._id_set)
		self.assertSetEqual({3, 621, new_id, _a._id, _b.id}, _at._id_set)

	def test_volatile_name(self):
		self.reset_atomic_proposition()
		self.assertEqual("a", AtomicProposition._next_volatile_name())
		self.assertEqual("b", AtomicProposition._next_volatile_name())
		self.assertEqual("c", AtomicProposition._next_volatile_name())
		[AtomicProposition._next_volatile_name() for _ in range(22)]
		self.assertEqual("z", AtomicProposition._next_volatile_name())
		self.assertEqual(f"a{self.prime}", AtomicProposition._next_volatile_name())
		[AtomicProposition._next_volatile_name() for _ in range(25)]
		self.assertEqual(f"a{self.prime}{self.prime}", AtomicProposition._next_volatile_name())
		self.assertEqual(f"b{self.prime}{self.prime}", AtomicProposition._next_volatile_name())

		_at = TestAtomicProposition.TestImplementationAtomicProposition
		self.reset_atomic_proposition(_at)
		self.assertEqual(None, _at._curr_name)
		self.assertEqual(0, _at._curr_name_primes)
		self.assertEqual("TestImplementationAtomicProposition_", _at._curr_name_prefix)
		_a = _at()
		self.assertEqual("TestImplementationAtomicProposition_a", _a._volatile_name)
		_b = _at()
		self.assertEqual("TestImplementationAtomicProposition_b", _b._volatile_name)

	def test_id_not_equal(self):
		for first, second in combinations((self.a, self.b, self.c, self.d), r=2):
			self.assertNotEqual(first._id, second._id)

	def test_volatile_name_not_equal(self):
		for first, second in combinations((self.a, self.b, self.c, self.d), r=2):
			self.assertNotEqual(first._volatile_name, second._volatile_name)

	def test_to_limboole(self):
		self.reset_atomic_proposition()
		self.assertEqual("a", AtomicProposition().to_limboole())
		[AtomicProposition() for _ in range(25)]
		self.assertEqual("a-prime", AtomicProposition().to_limboole())
		[AtomicProposition() for _ in range(25)]
		self.assertEqual("a-prime-prime", AtomicProposition().to_limboole())
		self.assertEqual("b-prime-prime", AtomicProposition().to_limboole())

	def test_eval(self):
		self.assertTrue(self.a.eval({self.a: True}))
		self.assertTrue(self.b.eval({self.b: True}))
		self.assertFalse(self.a.eval({self.a: False}))
		self.assertFalse(self.b.eval({self.b: False}))
		self.assertRaises(KeyError, lambda: self.a.eval({}))
		self.assertRaises(KeyError, lambda: self.b.eval({self.a: True}))

	def test_partial_eval(self):
		self.assertEqual(Top, self.a.partial_eval({self.a: True}))
		self.assertEqual(Top, self.b.partial_eval({self.b: True}))
		self.assertEqual(Bottom, self.a.partial_eval({self.a: False}))
		self.assertEqual(Bottom, self.b.partial_eval({self.b: False}))
		self.assertEqual(self.a, self.a.partial_eval({}))
		self.assertEqual(self.b, self.b.partial_eval({self.a: False}))

	def test_copy(self):
		self.assertNotEqual(self.a, self.a.copy())
		self.assertNotEqual(self.b, self.b.copy())
		self.assertNotEqual(self.c, self.c.copy())

	def test_hash(self):
		self.assertEqual(hash((self.a._id, self.a._connective)), hash(self.a))
		self.assertEqual(hash((self.b._id, LogicalConnective.NONE)), hash(self.b))
		self.assertEqual(hash((self.c._id, self.c._connective)), hash(self.c))
		self.assertEqual(hash((self.d._id, LogicalConnective.NONE)), hash(self.d))

	def test_top(self):
		self.assertEqual(1, Top._id)
		self.assertTrue(Top.eval({}))
		self.assertEqual("top", Top._volatile_name)
		self.assertEqual("(top | !top)", Top.to_limboole())
		self.assertEqual(Top, _Top())

	def test_bottom(self):
		self.assertEqual(0, Bottom._id)
		self.assertFalse(Bottom.eval({}))
		self.assertEqual("bottom", Bottom._volatile_name)
		self.assertEqual("(bottom & !bottom)", Bottom.to_limboole())
		self.assertEqual(Bottom, _Bottom())

if __name__ == "__main__":
	raise NotImplementedError()
