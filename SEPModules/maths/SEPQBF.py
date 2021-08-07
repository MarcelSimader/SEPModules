"""
:Author: Marcel Simader
:Date: 18.07.2021

..	versionadded:: 1.4.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

from typing import Tuple, Set, Optional, FrozenSet, Sequence

from SEPModules.SEPPrinting import repr_str
from SEPModules.SEPUtils import SingleStackFrameInfo
from SEPModules.maths.SEPLogic import AtomicProposition, SupportsLimbooleEval, Proposition, LogicalConnective, \
	_Connective, SupportsToLimboole, Top, SupportsToPrettyPrint, ConnectiveFormat, SupportsToLaTeX, LogicSyntaxError, \
	LogicError

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class PQBF(SupportsToPrettyPrint, SupportsLimbooleEval):
	"""
	:py:class:`PQBF` represents a quantified boolean formula in "prenex" form. The class contains a prefix, which consists
	of the quantifiers, and a matrix which consists of the formula itself.
	"""

	# inner classes
	class Node(SupportsToPrettyPrint, SupportsToLimboole, SupportsToLaTeX):

		def __init__(self,
					 pqbf: PQBF,
					 connective: Optional[_Connective] = None,
					 assignment_value: Optional[bool] = None,
					 left: Optional[PQBF.Node] = None,
					 right: Optional[PQBF.Node] = None):
			self.left: Optional[PQBF.Node] = left
			self.right: Optional[PQBF.Node] = right
			self.pqbf: Optional[PQBF] = pqbf
			self.connective: Optional[_Connective] = connective
			self.assignment_value: bool = assignment_value

		@property
		def num_children(self) -> int:
			return len([None for n in self.children if n is not None])

		@property
		def children(self) -> Tuple[Optional[PQBF.Node], Optional[PQBF.Node]]:
			return self.left, self.right

		@property
		def root(self) -> bool:
			return (self.connective is None) and (self.assignment_value is None)

		@property
		def leaf(self) -> bool:
			return (self.left is None) and (self.right is None)

		def eval_node(self) -> bool:
			if self.leaf or self.connective is None:
				return self.pqbf.matrix == Top
			elif self.connective not in (LogicalConnective.EXIST, LogicalConnective.UNIV):
				return False
			elif self.connective == LogicalConnective.EXIST:
				return self.left.eval_node() or self.right.eval_node()
			elif self.connective == LogicalConnective.UNIV:
				res = self.left.eval_node() and self.right.eval_node()
				return res

		def connective_format(self, *, conn_format: ConnectiveFormat, **kwargs) -> str:
			return self.pqbf.connective_format(conn_format=conn_format, **kwargs)

		def __repr__(self) -> str:
			return repr_str(self, PQBF.Node.root, PQBF.Node.leaf, PQBF.Node.num_children)

		def __str__(self) -> str:
			return self.to_pretty_print()

	# PQBF class
	def __init__(self, prefix: Sequence[Tuple[_Connective, AtomicProposition]], matrix: Proposition):
		# check that there are no quantifiers in matrix
		if matrix.quantified:
			raise LogicSyntaxError.from_traceback(f"'matrix' is not in prenex form",
												  str(matrix), SingleStackFrameInfo()[1])

		# trick to remove duplicates in order
		self._prefix: Tuple[Tuple[_Connective, AtomicProposition], ...] = tuple(dict.fromkeys(prefix))
		self._matrix: Proposition = matrix

		# construct formula
		formula = matrix
		for q, a in reversed(prefix):
			formula = Proposition(a, formula, connective=q)
		self._formula = formula

		# determine other props
		self._quantified_vars: FrozenSet[AtomicProposition] = frozenset(t[1] for t in prefix)
		self._free_vars: FrozenSet[AtomicProposition] = frozenset(matrix.seen_atomic_propositions
																  .difference(self._quantified_vars))
		self._outermost_quantifier: Optional[_Connective] = None if len(self._prefix) < 1 else self._prefix[0][0]

	@staticmethod
	def from_formula(formula: Proposition) -> PQBF:
		# split formula into prefix and matrix
		prefix = list()
		curr = formula
		while curr.connective in (LogicalConnective.EXIST, LogicalConnective.UNIV):
			atomic_props = curr.propositions[0].seen_atomic_propositions
			if len(atomic_props) > 1:
				raise LogicSyntaxError.from_traceback(f"Quantifier contains more than one atomic "
													  f"proposition: {atomic_props!r}", str(curr),
													  SingleStackFrameInfo()[1])
			prefix.append((curr.connective, atomic_props.pop()))
			curr = curr.propositions[1]

		# check that there are no more quantifiers after the first non-quantifier
		if curr.quantified:
			_formula, _curr = str(formula), str(curr)
			raise LogicSyntaxError.from_traceback(f"Formula is not in prenex form, expected no more quantifiers "
												  f"in {_curr!r}", _formula, SingleStackFrameInfo()[1],
												  offset=_formula.find(_curr))

		return PQBF(prefix, curr)

	# attributes
	@property
	def formula(self) -> Proposition:
		return self._formula

	@property
	def prefix(self) -> Tuple[Tuple[_Connective, AtomicProposition], ...]:
		return self._prefix

	@property
	def matrix(self) -> Proposition:
		return self._matrix

	@property
	def quantified_vars(self) -> Set[AtomicProposition]:
		return set(self._quantified_vars)

	@property
	def free_vars(self) -> Set[AtomicProposition]:
		return set(self._free_vars)

	@property
	def outermost_quantifier(self) -> Optional[_Connective]:
		return self._outermost_quantifier

	def limboole_eval(self, *option: str, timeout: Optional[float] = 1.0) -> str:
		# add --depqbf to options
		return super(PQBF, self).limboole_eval(*(("--depqbf",) + option), timeout=timeout)

	# formula methods
	def partial_eval_outermost(self) -> Tuple[PQBF, PQBF]:
		if len(self._prefix) < 1:
			raise LogicError(f"Prefix contains 0 variables", str(self))

		outermost, new_prefix = self._prefix[0], self._prefix[1:]
		new_matrices = [self._matrix.partial_eval({outermost[1]: truth_val}, simplify=True)
						for truth_val in (True, False)]

		return PQBF(new_prefix, new_matrices[0]), PQBF(new_prefix, new_matrices[1])

	def assignment_tree(self) -> PQBF.Node:
		root = PQBF.Node(self)

		def __build_tree__(parent: PQBF.Node) -> Optional[PQBF.Node]:
			if len(parent.pqbf.prefix) > 0:
				pqbf1, pqbf2 = parent.pqbf.partial_eval_outermost()
				parent.left = __build_tree__(PQBF.Node(pqbf1, pqbf1._outermost_quantifier, True))
				parent.right = __build_tree__(PQBF.Node(pqbf2, pqbf2._outermost_quantifier, False))
			return parent

		return __build_tree__(root)

	# misc methods
	def connective_format(self, *, conn_format: ConnectiveFormat, **kwargs) -> str:
		return self._formula.connective_format(conn_format=conn_format, **kwargs)

	def __str__(self) -> str:
		return self.to_pretty_print()

	def __repr__(self) -> str:
		return repr_str(self, PQBF.prefix, PQBF.matrix)

# class PCNF(PQBF):
#
# 	def __init__(cls, prefix: Sequence[Tuple[AtomicProposition, _Connective]], matrix: Proposition):
# 		if not matrix.CNF():
# 			raise ValueError(f"Proposition {str(matrix)} is not in CNF")
# 		super(PCNF, cls).__init__(prefix, matrix)
