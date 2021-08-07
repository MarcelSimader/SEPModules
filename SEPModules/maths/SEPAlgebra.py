"""
:Author: Marcel Simader
:Date: 11.04.2021

.. versionadded:: v0.1.1.dev0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

from itertools import permutations, islice
from typing import Callable, TypeVar, List, final, Union, Final, Set, Tuple, Literal, Iterable, \
	Iterator

from SEPModules.SEPPrinting import repr_str
from SEPModules.SEPUtils import Singleton

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@final
class _NoElement(Singleton):
	""" A final and private class used to generate the singleton :py:data:`NoElement`. """

	def __bool__(self):
		return False

	def __str__(self):
		return "NoElement"

	def __repr__(self):
		return f"<{str(self)}>"

	def __eq__(self, other):
		return other is NoElement

NoElement: Final = _NoElement()
""" Singleton used to indicate that an algebraic structure does not have an element under a method or operator. """
NoElementType: Final = _NoElement

Element: Final = TypeVar("Element")
""" Generic type ``Element`` for use in statically typing :py:class:`AlgebraicStructure`. """
Operator: Final = Callable[[Element, Element], Element]
""" Type alias ``Operator`` for use in typing :py:class:`AlgebraicStructure`. Represents a ``Callable`` taking two arguments 
of type :py:data:`Element` and returning an object of type :py:data:`Element`. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AlgebraicStructure:
	r"""
	:py:class:`AlgebraicStructure` is a class designed to represent a structure :math:`(G, \circ_1, \circ_2, \ldots, \circ_n)`
	with one collection containing any number of elements of type ``Element`` and another collection of callable objects which
	represent the binary operators applied to the elements of :math:`G`.

	The usual relational operators can be performed on this class:

	+-------------------+-------------------+------------------+-------------------+-------------------+-------------------+
	| :math:`\leq`      |  :math:`<`        | :math:`>`        | :math:`\geq`      | :math:`=`         | :math:`\neq`      |
	+-------------------+-------------------+------------------+-------------------+-------------------+-------------------+
	| :py:meth:`__le__` | :py:meth:`__lt__` | :py:meth:`__gt__`| :py:meth:`__ge__` | :py:meth:`__eq__` | :py:meth:`__ne__` |
	+-------------------+-------------------+------------------+-------------------+-------------------+-------------------+

	Performing a boolean test using ``bool(algebraic_struct)`` (see :py:meth:`__bool__`) will intenrally call the function
	:py:meth:`is_valid` of the respective class instance.

	An example usage of :py:class:`AlgebraicStructure` could look as follows, where we define an algebraic structure over
	the set :math:`\mathbb{Z}_3 = \{ 0, 1, 2 \}` along with the binary operator :math:`f\colon \mathbb{Z}_3 \times \mathbb{Z}_3
	\to \mathbb{Z}_3`, :math:`f(a, b) = a + b \mod 3`.

	>>> struct = AlgebraicStructure({0, 1, 2}, lambda a, b: (a + b) % 3)
	>>> assert bool(struct) == struct.is_valid() == True # since struct is valid
	>>> print(struct.neutral_elements()) # only one neutral el for our one operator
	[0]
	>>> print(struct.find_inverses_per_operator(0, 1)) # finds one inverse of element 1 for operator 0
	2

	:param elements: a collection containing n elements of any but the same type ``Element``, where the type given must
		be honored in all other uses of this instance
	:param binary_operators: a collection of callable objects taking two arguments of type ``Element`` and returning one
		single object of type ``Element`` representing the application of the given operator onto the objects given as
		arguments
	:param test_for_closure: a keyword-only argument that defaults to False, see :py:attr:`test_for_closure` for details

	..	note::

		Parameter ``elements`` will internally be stored as a :py:class:`set` object and parameter ``binary_operators``
		will internally be stored as a :py:class:`tuple` object.

		This class implements most methods by exhaustively iterating over all elements over the set, at times even in up
		to three nested loops, leading to very bad time complexity. More efficient and tailored solutions for these problems
		may be implemented as subclasses that are less general than this one.
	"""

	def __init__(self,
				 elements: Iterable[Element],
				 *binary_operators: Operator,
				 test_for_closure: bool = False):
		self._elements = frozenset(elements)
		self._binary_operators = tuple(binary_operators)
		self._test_for_closure = test_for_closure

	@property
	def elements(self) -> Set[Element]:
		r"""A collection representing set :math:`G` in this algebraic structure."""
		return set(self._elements)

	@property
	def binary_operators(self) -> Tuple[Operator, ...]:
		r"""
		A collection of binary operators representing the operators :math:`\circ_1, \circ_2, \ldots, \circ_n` of
		this algebraic structure.
		"""
		return tuple(self._binary_operators)

	@property
	def test_for_closure(self) -> bool:
		r"""
		Determines whether this algebraic structure will test for closure or not. Turning this value off can be useful for
		testing infinite sets using a finite selection of elements from it. Because of this property, :py:attr:`test_for_closure`
		is set to ``False`` by default. It may be set to ``True`` if an exact mathematical definition of an algebraic
		structure is desired.
		"""
		return self._test_for_closure

	def is_valid(self) -> bool:
		r"""
		Test whether or not this algebraic structure is considered as valid. In this case this means that
		:math:`(G, \circ_1, \circ_2, \ldots, \circ_n)` must be closed under all operators :math:`\circ_n` if the property
		:py:attr:`test_for_closure` is set to ``True``. Otherwise, this function will always return True.

		:return: a boolean value determining the validity of this algebraic structure
		"""
		return not self.test_for_closure or all(AlgebraicStructure.is_closed(self))

	def is_associative(self) -> Iterator[bool]:
		r"""
		Test whether this algebraic structure is associative for every operator :math:`\circ_n` in :py:attr:`binary_operators`
		over set :math:`G`.

		:return: an iterator of booleans describing for every operator whether it is associative with set :math:`G` or
			not in order
		"""
		for operator in self.binary_operators:
			is_associative = True  # assume that new operator is associative
			for el_tuple in permutations(self.elements, 3):
				if not (operator(operator(el_tuple[0], el_tuple[1]), el_tuple[2])
						== operator(el_tuple[0], operator(el_tuple[1], el_tuple[2]))):
					is_associative = False
					break

			yield is_associative

	def neutral_elements(self) -> Iterator[Union[List[Element], Element, NoElementType]]:
		r"""
		Try to find the neutral element for every operator :math:`\circ_n` in :py:attr:`binary_operators` over set :math:`G`.
		This function matches an arbitrary amount of neutral elements per operator.

		:return: an iterator of neutral elements or a list of lists of neutral elements of type ``Element`` for every
			operator in order, if no such neutral element is found the literal :py:data:`NoElement` is returned
		"""
		for operator in self.binary_operators:
			neutral_el_count = 0
			temp_neutral_list = list()

			# test all elements
			for el_test in self.elements:

				is_neutral = True
				for el_other in self.elements:
					if not (operator(el_test, el_other) == operator(el_other, el_test) == el_other):
						is_neutral = False
						break

				# we found one neutral element for operator
				if is_neutral:
					temp_neutral_list.append(el_test)
					neutral_el_count = neutral_el_count + 1

			# add results to result list
			if neutral_el_count == 0:
				yield NoElement
			elif neutral_el_count == 1:
				yield temp_neutral_list[0]
			else:
				yield temp_neutral_list

	def find_inverses_per_operator(self, operator_num: int, element: Element) \
			-> Union[List[Element], Element, NoElementType]:
		r"""
		Finds the inverses of an element ``element`` under operator :math:`\circ_{operator\_num}` stored in this instance
		at position ``operator_num``. This function will return a list of possible inverses for each operator and each
		neutral element of said operator. Note that any neutral element may match an inverse and there is no distinction
		made between these cases.

		:param operator_num: the position of operator :math:`\circ_{\text{operator\_num}}` in this structure :math:`G`
		:param element: the element to find inverses under operator :math:`\circ_{operator\_num}` of

		:raises ValueError: if ``operator_num < 0`` or no operator exists in this instance at position ``operator_num``
		:return: either a list of objects of type ``Element``, an ``Element`` object or the :py:data:`NoElement` literal
			if no inverses exists
		"""
		if operator_num < 0 or operator_num >= len(self.binary_operators):
			raise ValueError(f"no such operator or negative value (received '{operator_num}', "
							 f"expected no more than '{len(self.binary_operators)}'")

		operator = self.binary_operators[operator_num]
		neutral_elements = next(islice(AlgebraicStructure.neutral_elements(self), operator_num, operator_num + 1))
		result_list = list()

		# check if neutral elements exists
		if neutral_elements is NoElement:
			return NoElement

		# create a list out of neutral_elements if it is only one element
		if not isinstance(neutral_elements, list):
			neutral_elements = (neutral_elements,)

		# find inverse
		for el_other in self.elements:
			# check against all neutral elements, if any match we have an inverse
			if any(operator(element, el_other) == operator(el_other, element) == neutral
				   for neutral in neutral_elements):
				result_list.append(el_other)

		# return
		if len(result_list) == 0:
			return NoElement
		elif len(result_list) == 1:
			return result_list[0]

		return result_list

	def has_inverses(self) -> Iterator[bool]:
		r"""
		Test every element of :math:`G` on every operator :math:`\circ_n` to see if inverses exist for each element for
		any neutral element of said operator. This function calls :py:meth:`neutral_elements` to test for inverses and
		aborts if the substructure trivially has no inverses.

		:return: an iterator of boolean values for each operator in order, corresponding to whether all objects have an
			inverse under said operator or not
		"""

		for operator, neutral_els in zip(self.binary_operators, AlgebraicStructure.neutral_elements(self)):

			# check if neutral element even exists for this operator
			if neutral_els is NoElement:
				yield False
			else:
				# create list if not already
				if not isinstance(neutral_els, list):
					neutral_els = (neutral_els,)

				# test for inverses
				operator_has_inverses = True
				for el_test in self.elements:
					found_inverse = False

					for el_other in self.elements:
						# if any neutral element matches we have an inverse
						if any(operator(el_test, el_other) == operator(el_other, el_test) == neutral_el
							   for neutral_el in neutral_els):
							found_inverse = True
							break

					# one element does not have an inverse so break
					if not found_inverse:
						operator_has_inverses = False
						break

				yield operator_has_inverses

	def is_commutative(self) -> Iterator[bool]:
		r"""
		Test every element in :math:`G` on every operator :math:`\circ_n` to see if it is commutative or not. This function
		keeps track of any tuple :math:`(a, b)` it has seen to speed up computation. Since for commutativity we need to test
		:math:`\forall a, b: a \circ_n b = b \circ_n a`, once we have seen :math:`(a, b)` we do not need to also test
		:math:`(b, a)`.

		:return: an iterator of boolean values corresponding to whether each operator is commutative or not in order
		"""
		# list to keep track of pairs of elements we've seen
		# since we are testing for commutativity we do not
		# need to test both (a, b) and (b, a)
		seen_element_pairs = list()

		for operator in self.binary_operators:
			is_commutative = True

			for el_test in self.elements:

				# break out of loop if not commutative
				if not is_commutative:
					break
				for el_other in self.elements:
					# continue if this tuple has been tested
					if (el_test, el_other) in seen_element_pairs:
						continue
					# update cache
					seen_element_pairs.append((el_other, el_test))

					if not operator(el_test, el_other) == operator(el_other, el_test):
						is_commutative = False
						break

			yield is_commutative

	def is_closed(self) -> Iterator[bool]:
		"""
		Test whether or not set :math:`G` is closed under :math:`\circ_n`.

		:return: an iterator of boolean values corresponding to whether or not every operator is closed or not in order
		"""
		for operator in self.binary_operators:

			is_closed = True
			# loop through all permutations
			for el_test, el_other in permutations(self.elements, 2):
				if operator(el_test, el_other) not in self.elements:
					is_closed = False
					break

			yield is_closed

	def __hash__(self) -> int:
		return hash((self.elements, self.binary_operators))

	def __eq__(self, other) -> bool:
		r"""
		Returns ``True`` if all of the following criteria are met:

		1. ``cls`` and ``other`` are an instance of :py:class:`AlgebraicStructure`
		2. :math:`G_{cls} \triangle G_{other} = \emptyset`, ie. the sets are equal in elements
		3. :math:`\forall i \in \{0,\ldots,|G|-1\} \;\forall a, b \in G: a \circ^i_{cls} b = a \circ^i_{other} b`, ie.
			all operators of ``cls`` and ``other`` return the same value if they are passed the same arguments

		:returns: a boolean value describing whether ``cls`` and ``other`` are algebraically equal or not
		:meta public:
		"""
		if self is other:
			return True

		if not isinstance(other, AlgebraicStructure):
			return False

		# compare elements
		if len(self.elements.symmetric_difference(other.elements)) != 0:
			return False

		# test how many operators there are
		if len(self.binary_operators) != len(other.binary_operators):
			return False

		# compare operators
		for self_operator, other_operator in zip(self.binary_operators, other.binary_operators):

			# all permutations of elements (only cls.elements since they are equal anyway)
			for el_test, el_other in permutations(self.elements, 2):
				if self_operator(el_test, el_other) != other_operator(el_test, el_other):
					return False

		# passed all checks
		return True

	def __ne__(self, other) -> bool:
		r"""
		See negation of :py:meth:`__eq__`.
		"""
		return not self == other

	def __lt__(self, other) -> bool:
		r"""
		Test whether or not this algebraic structure is a true substructure of algebraic structure ``other`` or not.

		:return: a boolean value describing whether or not ``cls`` is a true substructure of ``other`` or not
		:meta public:
		"""
		if not isinstance(other, AlgebraicStructure):
			return False

		# els_self subset els_other
		if not self.elements.issubset(other.elements):
			return False

		# make sure it's real subset
		if len(self.elements.symmetric_difference(other.elements)) == 0:
			return False

		# test amount of operators
		if len(self.binary_operators) > len(other.binary_operators):
			return False

		# test that we really are a valid algebraic structure
		if not self.is_valid():
			return False

		# passed all checks
		return True

	def __le__(self, other) -> bool:
		r"""
		Test whether or not this algebraic structure is a substructure of algebraic structure ``other`` or not.

		:return: a boolean value describing whether or not ``cls`` is a substructure of ``other`` or not
		:meta public:
		"""
		return self < other or self == other

	def __gt__(self, other) -> bool:
		r"""
		Test whether or not algebraic structure ``other`` is a true substructure of this algebraic structure or not.

		:return: a boolean value describing whether or not ``other`` is a true substructure of ``cls`` or not
		"""
		return not self <= other

	def __ge__(self, other) -> bool:
		r"""
		Test whether or not algebraic structure ``other`` is a substructure of this algebraic structure or not.

		:return: a boolean value describing whether or not ``other`` is a substructure of ``cls`` or not
		"""
		return not self < other

	def __bool__(self) -> bool:
		"""
		Returns whether this algebraic structure is valid or not (see :py:meth:`is_valid`).

		:return: boolean value describing whether this algebraic structure is valid or not
		:meta public:
		"""
		return self.is_valid()

	def __repr_general(self) -> str:
		"""
		Create a repr string for this instance.
		:return: a repr string
		"""
		return repr_str(self, self.__class__.elements, self.__class__.binary_operators)

	def __repr__(self) -> str:
		return self.__repr_general()

	def __str__(self) -> str:
		return f"(Els={self.elements}, {', '.join(op.__qualname__ for op in self.binary_operators)})"

# ~~~~~~~~~~~~~~~ ONE OPERATOR STRUCTURES ~~~~~~~~~~~~~~~

class Semigroup(AlgebraicStructure):
	r"""
	:py:class:`Semigroup` is a subclass of :py:class:`AlgebraicStructure` and represents an algebraic structure of form
	:math:`(S, \circ)`. To test whether or not this instance is a valid monoid in the mathematical sense this class
	implements :py:meth:`is_valid` and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).

	Unlike :py:class:`AlgebraicStructure`, this class is can only be instantiated with one operator (e.g.
	``s = Semigroup({...}, add)`` is allowed but ``s = Semigroup({...}, add, subtract)`` is not since it
	can never be a valid semigroup anyway).
	"""

	def __init__(self,
				 elements: Iterable[Element],
				 binary_operator: Operator,
				 *,
				 test_for_closure: bool = False):
		"""
		:param elements: a collection containing n elements of any but the same type ``Element``, where the type given must
			be honored in all other uses of this instance
		:param binary_operator: a callable object taking two arguments of type ``Element`` and returning one
			single object of type ``Element`` representing the application of the given operator onto the objects given as
			arguments
		:param test_for_closure: a keyword-only argument that defaults to False, see :py:attr:`test_for_closure` for details
		"""
		super(Semigroup, self).__init__(elements, binary_operator, test_for_closure=test_for_closure)

	@property
	def binary_operator(self) -> Operator:
		r""" The single operator :math:`\circ` of this algebraic structure. """
		return self.binary_operators[0]

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`Semigroup` instance is a valid mathematical semigroup or not. For this to be
		true, two conditions must be met:

			* ``cls`` is a valid :py:class:`AlgebraicStructure` (see :py:meth:`AlgebraicStructure.is_valid`)
			* ``cls`` is associative with :math:`\circ` over :math:`G`

		:return: a boolean representing whether this instance is a valid semigroup or not
		"""
		return super(Semigroup, self).is_valid() and self.is_associative()

	def is_associative(self) -> bool:
		r"""
		Test whether this algebraic structure is associative for operator :math:`\circ` over set :math:`G`.

		:return: a boolean value describing whether this :py:class:`Semigroup` instance is associative or not
		"""
		return next(islice(super(Semigroup, self).is_associative(), 0, 1))

	def neutral_elements(self) -> Union[List[Element], Element, NoElementType]:
		r"""
		Try to find the neutral element for operator :math:`\circ` over set :math:`G`. This function matches an arbitrary
		amount of neutral elements but will almost always simply return one object of type ``Element``.

		:return: a list of neutral elements or a single neutral elements of type ``Element``, if no such neutral element
			is found the literal :py:data:`NoElement` is returned
		"""
		return next(islice(super(Semigroup, self).neutral_elements(), 0, 1))

	def find_inverses(self, element: Element) -> Union[List[Element], Element, NoElementType]:
		r"""
		Finds the inverses of an element ``element`` under operator :math:`\circ` stored in this instance. This function
		will return a list of possible inverses for each neutral element of said operator. Note that any neutral element
		may match an inverse and there is no distinction made between these cases.

		:param element: the element to find inverses under operator :math:`\circ` of

		:return: either a list of objects of type ``Element``, an ``Element`` object or the :py:data:`NoElement` literal if
			no inverses exists
		"""
		return super(Semigroup, self).find_inverses_per_operator(0, element)

	def has_inverses(self) -> bool:
		r"""
		Test every element of :math:`G` on operator :math:`\circ` to see if inverses exist for each element for any
		neutral element of said operator. This function calls :py:meth:`neutral_elements` to test for inverses and
		aborts if the substructure trivially has no inverses.

		:return: a boolean value corresponding to whether every element has an inverse or not
		"""
		return next(islice(super(Semigroup, self).has_inverses(), 0, 1))

	def is_commutative(self) -> bool:
		r"""
		Test every element in :math:`G` on operator :math:`\circ` to see if it is commutative or not. See
		:py:meth:`AlgebraicStructure.is_commutative` for implementation details.

		:return: a boolean value corresponding to whether this structure is commutative or not
		"""
		return next(islice(super(Semigroup, self).is_commutative(), 0, 1))

	def is_closed(self) -> bool:
		"""
		Test whether or not set :math:`G` is closed under :math:`\circ`.

		:return: a boolean value corresponding to whether or not this structure is closed or not
		"""
		return next(islice(super(Semigroup, self).is_closed(), 0, 1))

	def __repr_general(self) -> str:
		return repr_str(self, self.__class__.elements, self.__class__.binary_operator)

	def __str__(self) -> str:
		return f"(S={self.elements}, {self.binary_operator.__qualname__})"

class Monoid(Semigroup):
	r"""
	:py:class:`Monoid` is a subclass of :py:class:`Semigroup` and represents an algebraic structure of form
	:math:`(M, \circ)`. To test whether or not this instance is a valid semigroup in the mathematical sense this class
	implements :py:meth:`is_valid` and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).
	"""

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`Monoid` instance is a valid mathematical monoid or not. For this to be true,
		two conditions must be met:

			* ``cls`` is a valid :py:class:`Semigroup` (ie. is associative, see :py:meth:`Semigroup.is_valid`)
			* ``cls`` has a neutral element :math:`e` for ever element in set :math:`G` over operator :math:`\circ`

		:return: a boolean representing whether this instance is a valid monoid or not
		"""
		return super(Monoid, self).is_valid() and self.neutral_elements() is not NoElement

	def __str__(self) -> str:
		return f"(M={self.elements}, {self.binary_operator.__qualname__})"

class Group(Monoid):
	r"""
	:py:class:`Group` is a subclass of :py:class:`Monoid` and represents an algebraic structure of form :math:`(G, \circ)`.
	To test whether or not this instance is a valid group in the mathematical sense this class implements :py:meth:`is_valid`
	and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).
	"""

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`Group` instance is a valid mathematical group or not. For this to be true,
		two conditions must be met:

			* ``cls`` is a valid :py:class:`Monoid` (ie. is associative and has a neutral element, see
			  :py:meth:`Monoid.is_valid`)
			* ``cls`` has an inverse element :math:`a^{-1}` for ever element in set :math:`G` over operator :math:`\circ`

		:return: a boolean representing whether this instance is a valid group or not
		"""
		return super(Group, self).is_valid() and self.has_inverses()

	def __str__(self) -> str:
		return f"(G={self.elements}, {self.binary_operator.__qualname__})"

class AbelianGroup(Group):
	r"""
	:py:class:`AbelianGroup` is a subclass of :py:class:`Group` and represents an algebraic structure of form
	:math:`(G, \circ)`. To test whether or not this instance is a valid Abelian group in the mathematical sense this
	class implements :py:meth:`is_valid` and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).
	"""

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`AbelianGroup` instance is a valid mathematical Abelian group or not. For
		this to be true, two conditions must be met:

			* ``cls`` is a valid :py:class:`Group` (ie. is associative, has a neutral element and inverses, see
			  :py:meth:`Group.is_valid`)
			* ``cls`` is commutative under operator :math:`\circ`

		:return: a boolean representing whether this instance is a valid Abelian group or not
		"""
		return super(AbelianGroup, self).is_valid() and self.is_commutative()

	def __str__(self) -> str:
		return f"(G={self.elements}, {self.binary_operator.__qualname__})"

# ~~~~~~~~~~~~~~~ TWO OPERATOR STRUCTURES ~~~~~~~~~~~~~~~

class Ring(AlgebraicStructure):
	r"""
	:py:class:`Ring` is a subclass of :py:class:`AlgebraicStructure` and represents an algebraic structure of form
	:math:`(G, +, \cdot)`. To test whether or not this instance is a valid ring in the mathematical sense this class
	implements :py:meth:`is_valid` and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).

	Unlike :py:class:`AlgebraicStructure`, this class is can only be instantiated with exactly two operators (e.g.
	``ring = Ring({...}, add, mul)`` is allowed but ``ring = Ring({...}, add)`` is not since it can never be a valid
	ring anyway).
	"""

	def __init__(self,
				 elements: Iterable[Element],
				 binary_operator_one: Operator,
				 binary_operator_two: Operator,
				 *,
				 test_for_closure: bool = False):
		"""
		:param elements: a collection containing n elements of any but the same type ``Element``, where the type given must
			be honored in all other uses of this instance
		:param binary_operator_one: a callable object taking two arguments of type ``Element`` and returning one
			single object of type ``Element`` representing the application of the given operator onto the objects given as
			arguments
		:param binary_operator_two: the second operator following the same rules as ``binary_operator_one``
		:param test_for_closure: a keyword-only argument that defaults to False, see :py:attr:`test_for_closure` for details
		"""
		super(Ring, self).__init__(elements, binary_operator_one, binary_operator_two,
								   test_for_closure=test_for_closure)

	@staticmethod
	def __tuple_returner(func: Callable[..., Iterator]):
		"""
		Calls ``func`` and passes the returned list value back to the callee as tuple of length ``2``.
		:param func: the function to call
		:return: a tuple of length two with the resulting values
		"""
		result = list(islice(func(), 0, 2))
		return result[0], result[1]

	@property
	def elements_without_zero(self) -> Set[Element]:
		"""
		The same set as :py:attr:`elements` but without the zero element (according to the neutral element of operator
		:math:`+`).
		"""
		zero_elements = self.neutral_elements()[0]

		if zero_elements is NoElement:
			return self.elements

		if not isinstance(zero_elements, list):
			zero_elements = (zero_elements,)

		# now zero_element is iterable and not NoElement
		return self.elements.difference(zero_elements)

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`Ring` instance is a valid mathematical ring or not. For this to be true,
		four conditions must be met:

			* ``cls`` is a valid :py:class:`AlgebraicStructure` (see :py:meth:`AlgebraicStructure.is_valid`)
			* ``cls`` forms a valid Abelian group with :math:`(G, +)` (see :py:meth:`AbelianGroup.is_valid`)
			* ``cls`` forms a valid semigroup with :math:`(G, \cdot)` (see :py:meth:`Semigroup.is_valid`)
			* ``cls`` is distributive over :math:`+` and :math:`\cdot`

		:return: a boolean representing whether this instance is a valid ring or not
		"""
		return super(Ring, self).is_valid() \
			   and AbelianGroup(self.elements, self.binary_operators[0],
								test_for_closure=self.test_for_closure).is_valid() \
			   and Semigroup(self.elements, self.binary_operators[1],
							 test_for_closure=self.test_for_closure).is_valid() \
			   and self.is_distributive()

	def is_associative(self) -> Tuple[bool, bool]:
		r"""
		Test whether this algebraic structure is associative for operator :math:`+` and :math:`\cdot` over set :math:`G`.

		:return: a tuple of two boolean values describing the associativity of either operator
		"""
		return Ring.__tuple_returner(super(Ring, self).is_associative)

	def neutral_elements(self) \
			-> Tuple[Union[List[Element], Element, NoElementType], Union[List[Element], Element, NoElementType]]:
		r"""
		Try to find the neutral element for operator :math:`+` and :math:`\cdot` over set :math:`G`. This function
		matches an arbitrary amount of neutral elements but will almost always simply return one object of type ``Element``.

		:return: a tuple of a list of neutral elements or a single neutral elements of type ``Element``, if no such neutral
			element is found the literal :py:data:`NoElement` is returned
		"""
		return Ring.__tuple_returner(super(Ring, self).neutral_elements)

	def find_inverses(self, operator_num: Literal[0, 1], element: Element) \
			-> Union[List[Element], Element, NoElementType]:
		r"""
		Finds the inverses of an element ``element`` under operator :math:`+` or :math:`\cdot` stored in this instance.
		This function will return a list of possible inverses for each neutral element of said operator. Note that any
		neutral element may match an inverse and there is no distinction made between these cases.

		:param operator_num: which operator to find an inverse for, must be either ``0`` or ``1`` for :math:`+` and
			:math:`\cdot` respectively
		:param element: the element to find inverses under operator :math:`+` or :math:`\cdot` of

		:return: either a list of objects of type ``Element``, an ``Element`` object or the :py:data:`NoElement` literal
			if no inverses exists
		"""
		return super(Ring, self).find_inverses_per_operator(operator_num, element)

	def has_inverses(self) -> Tuple[bool, bool]:
		r"""
		Test every element of :math:`G` on operator :math:`\circ` to see if inverses exist for each element for any
		neutral element of said operator. This function calls :py:meth:`neutral_elements` to test for inverses and
		aborts if the substructure trivially has no inverses.

		:return: a tuple of two boolean values corresponding to whether every element has an inverse under operators
			:math:`+` and :math:`\cdot` or not
		"""
		return Ring.__tuple_returner(super(Ring, self).has_inverses)

	def is_commutative(self) -> Tuple[bool, bool]:
		r"""
		Test every element in :math:`G` on operator :math:`\circ` to see if it is commutative or not. See
		:py:meth:`AlgebraicStructure.is_commutative` for implementation details.

		:return: a tuple of boolean values corresponding to whether this structure is commutative under operators
			:math:`+` and :math:`\cdot` or not
		"""
		return Ring.__tuple_returner(super(Ring, self).is_commutative)

	def is_closed(self) -> Tuple[bool, bool]:
		"""
		Test whether or not set :math:`G` is closed under :math:`\circ`.

		:return: a tuple of boolean values corresponding to whether or not this structure is closed under operators
			:math:`+` and :math:`\cdot` or not
		"""
		return Ring.__tuple_returner(super(Ring, self).is_closed)

	def is_distributive(self) -> bool:
		"""
		Determine whether this algebraic structure is distributive for operators :math:`+` and :math:`\cdot` for every
		element in :math:`G`.

		:return: whether or not this algebraic structure is distributive
		"""
		# save operators into var for easier reading
		add, mul = self.binary_operators

		# iterate over all 3-valued pairs of elements
		for a, b, c in permutations(self.elements, 3):
			if not (mul(a, add(b, c)) == add(mul(a, b), mul(a, c)) and mul(add(a, b), c) == add(mul(a, c), mul(b, c))):
				return False
		return True

	def __str__(self) -> str:
		return f"(R={self.elements}, {', '.join(op.__qualname__ for op in self.binary_operators)})"

class Field(Ring):
	r"""
	:py:class:`Field` is a subclass of :py:class:`Ring` and represents an algebraic structure of form :math:`(G, +, \cdot)`.
	To test whether or not this instance is a valid field in the mathematical sense this class implements :py:meth:`is_valid`
	and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).
	"""

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`Field` instance is a valid mathematical field or not. For this to be true,
		four conditions must be met:

			* ``cls`` is a valid :py:class:`AlgebraicStructure` (see :py:meth:`AlgebraicStructure.is_valid`)
			* ``cls`` forms a valid Abelian group with :math:`(G, +)` (see :py:meth:`AbelianGroup.is_valid`)
			* ``cls`` forms a valid Abelian group with :math:`(G\backslash\{0\}, \cdot)` , where :math:`0` is the zero
			  element of operator :math:`+` (see :py:meth:`Semigroup.is_valid`)
			* ``cls`` is distributive over :math:`+` and :math:`\cdot`

		:return: a boolean representing whether this instance is a valid field or not
		"""
		return super(Ring, self).is_valid() \
			   and AbelianGroup(self.elements, self.binary_operators[0]).is_valid() \
			   and AbelianGroup(self.elements_without_zero, self.binary_operators[1]).is_valid() \
			   and self.is_distributive()

	def __str__(self) -> str:
		return f"(F={self.elements}, {', '.join(op.__qualname__ for op in self.binary_operators)})"
