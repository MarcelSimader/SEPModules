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

Element : Final = TypeVar("Element")
"""Generic type `Element` for use in statically typing :py:class:`AlgebraicStructure`."""

def _lock_neutral_element(name: str, msg: str):
	"""Private function to lock attributes and methods of :py:class:`_NoNeutralElement`."""
	def lock_neutral_element(*args): raise SyntaxError(f"cannot {msg} NoNeutralElement (passed {args})")
	lock_neutral_element.__name__ = name
	return lock_neutral_element

@final
class _NoNeutralElement(object):
	"""A final and private class used to generate the singleton :py:data:`NoNeutralElement`."""

	def __bool__(self):
		return False

	def __str__(self):
		return "NoNeutralElement"

	def __repr__(self):
		return f"<{str(self)}>"

	def __eq__(self, other):
		if type(other) is NoNeutralElement:
			return True
		else:
			raise SyntaxError("cannot compare NoNeutralElement to other types")

	# clean up for NoNeutralElement
	__init_subclass__ = _lock_neutral_element("__init_subclasses__", "init subclasses of")
	__delattr__ = _lock_neutral_element("__delattr__", "delete attribute for")

NoNeutralElement : Final = _NoNeutralElement()
"""Singleton used to indicate that an algebraic structure does not have a neutral element under an operator."""
# stop new instances from being created and lock setting
NoNeutralElement.__new__ = _lock_neutral_element("__new__", "instantiate")
NoNeutralElement.__setattr__ = _lock_neutral_element("__setattr__", "set attribute for")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AlgebraicStructure:
	r"""
	:py:class:`AlgebraicStructure` is a class designed to represent a structure :math:`(G, \circ_1, \circ_2, \ldots, \circ_n)`
	with one collection containing any number of elements of type `Element` and another collection of callable objects which
	represent the binary operators applied to the elements of :math:`G`.

	:param elements: a collection containing n elements of any but the same type `Element`, where the type given must
		be honored in all other uses of this instance
	:param binary_operators: a collection of callable objects taking two arguments of type `Element` and returning one
		single object of type `Element` representing the application of the given operator onto the objects given as
		arguments

	..	note::

		Parameter `elements` will internally be stored as a :py:class:`set` object and parameter `binary_operators` will
		internally be stored as a :py:class:`tuple` object.
	"""

	def __init__(self,
				 elements : Collection[Element],
				 binary_operators : Collection[Callable[[Element, Element], Element]]):
		self._elements = set(elements)
		self._binary_operators = tuple(binary_operators)

	@property
	def elements(self) -> Set[Element]:
		"""A collection representing set :math:`G` in this algebraic structure."""
		return self._elements

	@property
	def binary_operators(self) -> Tuple[Callable[[Element, Element], Element], ...]:
		"""
		A collection of binary operators representing the operators :math:`\circ_1, \circ_2, \ldots, \circ_n` of
		this algebraic structure.
		"""
		return self._binary_operators

	def is_associative(self) -> List[bool]:
		"""
		Test whether this algebraic structure is associative for every operator :math:`\circ_n` in :py:attr:`binary_operators`
		over set :math:`G`.

		:return: a list of booleans describing for every operator whether it is associative with set :math:`G` or not in order
		"""
		result_list = list()

		for operator in self.binary_operators:

			# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
			# ~~~~~~~~~~~~~~~ TODO: POST IN THE AUTISM SUBREDDIT ~~~~~~~~~~~~~~~
			# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


			is_commutative = True # assume that new operator is commutative
			for el_tuple in permutations(self.elements, 3):
				if not (operator(operator(el_tuple[0], el_tuple[1]), el_tuple[2]) ==
						operator(el_tuple[0], operator(el_tuple[1], el_tuple[2]))):
					is_commutative = False
					break

			result_list.append(is_commutative)

		return result_list

	def neutral_elements(self) -> List[Union[Element, _NoNeutralElement]]:
		"""
		Try to find the neutral element for every operator :math:`\circ_n` in :py:attr:`binary_operators` over set :math:`G`.

		:return: a list of neutral elements of type `Element` for every operator in order, if no such neutral element is
			found the literal :py:data:`NoNeutralElement` is returned
		"""
		result_list = list()

		for operator in self.binary_operators:

			found_neutral = False

			# test all elements
			for el_test in self.elements:
				is_neutral = True
				for el_other in self.elements:
					if not (operator(el_test, el_other) == operator(el_other, el_test) == el_other):
						is_neutral = False
						break

				# we found one neutral element for operator
				if is_neutral:
					result_list.append(el_test)
					found_neutral = True
					break

			# add literal if we failed to find a neutral el
			if not found_neutral:
				result_list.append(NoNeutralElement)

		return result_list

	def has_inverses(self) -> List[bool]:
		"""
		Test every element of :math:`G` on every operator :math:`\circ_n` to see if inverses exist.

		:return:
		"""
		result_list = list()
		neutral_els = self.neutral_elements()

		for i, operator in enumerate(self.binary_operators):

			# first check if a neutral element exists
			if neutral_els[i] is NoNeutralElement:
				result_list.append(False)
			# else check if all inverses exist
			else:
				neutral_el = neutral_els[i]
				has_inverses = True

				for el_test in self.elements:
					found_inverse_el = False

					for el_other in self.elements:
						if operator(el_test, el_other) == operator(el_other, el_test) == neutral_el:
							found_inverse_el = True
							break

					# one element has no inverse
					if not found_inverse_el:
						has_inverses = False
						break

				result_list.append(has_inverses)

		return result_list

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~