"""
Author: Marcel Simader

Date: 11.04.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from itertools import permutations
from typing import Collection, Callable, TypeVar, List, final, Union, Final, Set, Tuple

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _lock_element(name: str, msg: str):
	"""Private function to lock attributes and methods of :py:class:`_NoElement`."""
	def lock_element(*args): raise SyntaxError(f"cannot {msg} NoElement (passed {args})")
	lock_element.__name__ = name
	return lock_element

@final
class _NoElement(object):
	"""A final and private class used to generate the singleton :py:data:`NoElement`."""

	def __bool__(self):
		return False

	def __str__(self):
		return "NoElement"

	def __repr__(self):
		return f"<{str(self)}>"

	def __eq__(self, other):
		return other is NoElement

	# clean up for NoNeutralElement
	__init_subclass__ = _lock_element("__init_subclasses__", "init subclasses of")
	__delattr__ = _lock_element("__delattr__", "delete attribute for")

Element : Final = TypeVar("Element")
"""Generic type `Element` for use in statically typing :py:class:`AlgebraicStructure`."""
Operator : Final = Callable[[Element, Element], Element]
"""Type alias `Operator` for use in typing :py:class:`AlgebraicStructure`. Represents a `Callable` taking two arguments 
of type :py:data:`Element` and returning an object of type :py:data:`Element`."""

NoElement : Final = _NoElement()
"""Singleton used to indicate that an algebraic structure does not have an element under a method or operator."""
# stop new instances from being created and lock setting
_NoElement.__new__ = _lock_element("__new__", "instantiate")
_NoElement.__setattr__ = _lock_element("__setattr__", "set attribute for")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AlgebraicStructure:
	r"""
	:py:class:`AlgebraicStructure` is a class designed to represent a structure :math:`(G, \circ_1, \circ_2, \ldots, \circ_n)`
	with one collection containing any number of elements of type `Element` and another collection of callable objects which
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

	:param elements: a collection containing n elements of any but the same type `Element`, where the type given must
		be honored in all other uses of this instance
	:param binary_operators: a collection of callable objects taking two arguments of type `Element` and returning one
		single object of type `Element` representing the application of the given operator onto the objects given as
		arguments

	..	note::

		Parameter `elements` will internally be stored as a :py:class:`set` object and parameter `binary_operators` will
		internally be stored as a :py:class:`tuple` object.

		This class implements most methods by exhaustively iterating over all elements over the set, at times even in up
		to three nested loops, leading to very bad time complexity. More efficient and tailored solutions for these problems
		may be implemented as subclasses that are less general than this one.
	"""

	def __init__(self,
				 elements : Collection[Element],
				 *binary_operators : Operator):
		self._elements = set(elements)
		self._binary_operators = tuple(binary_operators)

	@property
	def elements(self) -> Set[Element]:
		r"""A collection representing set :math:`G` in this algebraic structure."""
		return self._elements

	@property
	def binary_operators(self) -> Tuple[Operator, ...]:
		r"""
		A collection of binary operators representing the operators :math:`\circ_1, \circ_2, \ldots, \circ_n` of
		this algebraic structure.
		"""
		return self._binary_operators

	def is_valid(self) -> bool:
		r"""
		Test whether or not this algebraic structure is considered as valid. In this case this means that
		:math:`(G, \circ_1, \circ_2, \ldots, \circ_n)` must be closed under all operators :math:`\circ_n`.

		:return: a boolean value determining the validity of this algebraic structure
		"""
		return all(self.is_closed())

	def is_associative(self) -> List[bool]:
		r"""
		Test whether this algebraic structure is associative for every operator :math:`\circ_n` in :py:attr:`binary_operators`
		over set :math:`G`.

		:return: a list of booleans describing for every operator whether it is associative with set :math:`G` or not in order
		"""
		result_list = list()

		for operator in self.binary_operators:
			is_commutative = True # assume that new operator is commutative
			for el_tuple in permutations(self.elements, 3):
				if not (operator(operator(el_tuple[0], el_tuple[1]), el_tuple[2]) ==
						operator(el_tuple[0], operator(el_tuple[1], el_tuple[2]))):
					is_commutative = False
					break

			result_list.append(is_commutative)

		return result_list

	def neutral_elements(self) -> List[Union[List[Element], Element, _NoElement]]:
		r"""
		Try to find the neutral element for every operator :math:`\circ_n` in :py:attr:`binary_operators` over set :math:`G`.
		This function matches an arbitrary amount of neutral elements per operator.

		:return: a list of neutral elements or a list of lists of neutral elements of type `Element` for every operator in order,
			if no such neutral element is found the literal :py:data:`NoElement` is returned
		"""
		result_list = list()

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
				result_list.append(NoElement)
			elif neutral_el_count == 1:
				result_list.append(temp_neutral_list[0])
			else:
				result_list.append(temp_neutral_list)

		return result_list

	def find_inverses_per_operator(self, operator_num : int, element : Element) -> Union[List[Element], Element, _NoElement]:
		r"""
		Finds the inverses of an element `element` under operator :math:`\circ_{operator\_num}` stored in this instance
		at position `operator_num`. This function will return a list of possible inverses for each operator and each
		neutral element of said operator. Note that any neutral element may match an inverse and there is no distinction
		made between these cases.

		:param operator_num: the position of operator :math:`\circ_{operator\_num}` in this structure :math:`G`
		:param element: the element to find inverses under operator :math:`\circ_{operator\_num}` of

		:raises ValueError: if `operator_num < 0` or no operator exists in this instance at position `operator_num`
		:return: either a list of objects of type `Element`, an `Element` object or the :py:data:`NoElement` literal if
			no inverses exists
		"""
		if operator_num < 0 or operator_num >= len(self.binary_operators):
			raise ValueError(f"no such operator or negative value (received '{operator_num}', "
							 f"expected no more than '{len(self.binary_operators)}'")

		operator = self.binary_operators[operator_num]
		neutral_elements = self.neutral_elements()[operator_num]
		result_list = list()

		# check if neutral elements exists
		if neutral_elements is NoElement:
			return NoElement

		# create a list out of neutral_elements if it is only one element
		if not type(neutral_elements) is list:
			neutral_elements = (neutral_elements,)

		# find inverse
		for el_other in self.elements:
			# check against all neutral elements, if any match we have an inverse
			if any([operator(element, el_other) == operator(el_other, element) == neutral for neutral in neutral_elements]):
				result_list.append(el_other)

		# return
		if len(result_list) == 0:
			return NoElement
		elif len(result_list) == 1:
			return result_list[0]

		return result_list

	def has_inverses(self) -> List[bool]:
		r"""
		Test every element of :math:`G` on every operator :math:`\circ_n` to see if inverses exist for each element for
		any neutral element of said operator. This function calls :py:meth:`neutral_elements` to test for inverses and
		abort if the substructure trivially has no inverses.

		:return: a list of boolean values for each operator in order, corresponding to whether all objects have an inverse
			under said operator or not
		"""
		result_list = list()

		for i, operator in enumerate(self.binary_operators):

			# create a list out of neutral_elements
			neutral_els = self.neutral_elements()[i]

			# check if neutral element even exists for this operator
			if neutral_els is NoElement:
				result_list.append(False)
				continue

			# create list if not already
			if not type(neutral_els) is list:
				neutral_els = (neutral_els,)

			# test for inverses
			operator_has_inverses = True
			for el_test in self.elements:
				found_inverse = False

				for el_other in self.elements:
					# if any neutral element matches we have an inverse
					if any([operator(el_test, el_other) == operator(el_other, el_test) == neutral_el for neutral_el in neutral_els]):
						found_inverse = True
						break

				# one element does not have an inverse so break
				if not found_inverse:
					operator_has_inverses = False
					break

			# we found an inverse
			result_list.append(operator_has_inverses)

		return result_list

	def is_commutative(self) -> List[bool]:
		r"""
		Test every element in :math:`G` on every operator :math:`\circ_n` to see if it is commutative or not. This function
		keeps track of any tuple :math:`(a, b)` it has seen to speed up computation. Since for commutativity we need to test
		:math:`\forall a, b: a \circ_n b = b \circ_n a`, once we have seen :math:`(a, b)` we do not need to also test
		:math:`(b, a)`.

		:return: a list of boolean values corresponding to whether each operator is commutative or not in order
		"""
		result_list = list()

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

			result_list.append(is_commutative)

		return result_list

	def is_closed(self) -> List[bool]:
		"""
		Test whether or not set :math:`G` is closed under :math:`\circ_n`.

		:return: a list of boolean values corresponding to whether or not every operator is closed or not in order
		"""
		result_list = list()

		for operator in self.binary_operators:

			is_closed = True
			# loop through all permutations
			for el_test, el_other in permutations(self.elements, 2):
				if operator(el_test, el_other) not in self.elements:
					is_closed = False
					break

			result_list.append(is_closed)

		return result_list

	def __hash__(self):
		return hash((self.elements, self.binary_operators))

	def __eq__(self, other) -> bool:
		r"""
		Returns true if all of the following criteria are met:

		1. `self` and `other` are an instance of :py:class:`AlgebraicStructure`
		2. :math:`G_{self} \triangle G_{other} = \emptyset`, ie. the sets are equal in elements
		3. :math:`\forall i \in \{0,\ldots,|G|-1\} \;\forall a, b \in G: a \circ^i_{self} b = a \circ^i_{other} b`, ie. all operators of `self` and `other` return the same value if they are passed the same arguments

		:returns: a boolean value describing whether `self` and `other` are algebraically equal or not
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

			# all permutations of elements (only self.elements since they are equal anyway)
			for el_test, el_other in permutations(self.elements, 2):
				if self_operator(el_test, el_other) != other_operator(el_test, el_other):
					return False

		# passed all checks
		return True

	def __ne__(self, other):
		r"""
		See negation of :py:meth:`__eq__`.
		"""
		return self != other

	def __lt__(self, other) -> bool:
		r"""
		Test whether or not this algebraic structure is a true substructure of algebraic structure `other` or not.

		:return: a boolean value describing whether or not `self` is a true substructure of `other` or not
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

	def __le__(self, other):
		r"""
		Test whether or not this algebraic structure is a substructure of algebraic structure `other` or not.

		:return: a boolean value describing whether or not `self` is a substructure of `other` or not
		"""
		return self < other or self == other

	def __gt__(self, other):
		r"""
		Test whether or not algebraic structure `other` is a true substructure of this algebraic structure or not.

		:return: a boolean value describing whether or not `other` is a true substructure of `self` or not
		"""
		return not self <= other

	def __ge__(self, other):
		r"""
		Test whether or not algebraic structure `other` is a substructure of this algebraic structure or not.

		:return: a boolean value describing whether or not `other` is a substructure of `self` or not
		"""
		return not self < other

	def __bool__(self):
		"""
		Returns whether this algebraic structure is valid or not (see :py:meth:`is_valid`).

		:return: boolean value describing whether this algebraic structure is valid or not
		"""
		return self.is_valid()

	def __repr__(self) -> str:
		return f"<AlgebraicStructure({self.elements}, {self.binary_operators}>"

	def __str__(self) -> str:
		return f"(G={self.elements}, {str([op.__qualname__ for op in self.binary_operators])[1:-1]})"

class Monoid(AlgebraicStructure):
	r"""
	:py:class:`Monoid` is a subclass of :py:class:`AlgebraicStructure` and represents an algebraic structure of form
	:math:`(G, \circ)`. To test whether or not this instance is a valid monoid in the mathematical sense this class
	implements :py:meth:`is_valid` and :py:meth:`__bool__` (see :py:class:`AlgebraicStructure`).

	Unlike :py:class:`AlgebraicStructure`, this class is can only be instantiated with one operator (e.g.
	``monoid = Monoid({...}, add)`` is allowed but ``monoid = Monoid({...}, add, subtract)`` is not since it
	can never be a valid monoid).
	"""

	def __init__(self,
				 elements: Collection[Element],
				 binary_operator: Operator):
		super().__init__(elements, binary_operator)

	def is_valid(self) -> bool:
		r"""
		Test whether or not this :py:class:`Monoid` instance is a valid mathematical monoid or not. For this to be true,
		two conditions must be met:

			* `self` is a valid :py:class:`AlgebraicStructure` (ie. is closed)
			* `self` is commutative with :math:`\circ` over :math:`G`

		:return: a boolean representing whether this instance is a valid monoid or not
		"""
		return super().is_valid() and self.is_commutative()

	def is_associative(self) -> bool:
		r"""
		Test whether this algebraic structure is associative for operator :math:`\circ` over set :math:`G`.

		:return: a boolean value describing whether this :py:class:`Monoid` instance is associative or not
		"""
		return super().is_associative()[0]

	def neutral_elements(self) -> Union[List[Element], Element, _NoElement]:
		r"""
		Try to find the neutral element for operator :math:`\circ` over set :math:`G`. This function matches an arbitrary
		amount of neutral elements but will almost always simply return one object of type `Element`.

		:return: a list of neutral elements or a single neutral elements of type `Element`, if no such neutral element
			is found the literal :py:data:`NoElement` is returned
		"""
		return super().neutral_elements()[0]

	def find_inverses(self, element : Element) -> Union[List[Element], Element, _NoElement]:
		return super().find_inverses_per_operator(0, element)

	# TODO: write docstrings here
	def has_inverses(self) -> bool:
		return super().has_inverses()[0]

	def is_commutative(self) -> bool:
		return super().is_commutative()[0]

	def is_closed(self) -> bool:
		return super().is_closed()[0]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~