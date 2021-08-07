"""
:Author: Marcel Simader
:Date: 13.07.2021

..	versionadded:: 1.3.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import abc
import enum
import os
import random
import time
from inspect import Traceback
from itertools import permutations
from subprocess import run, CalledProcessError, PIPE, TimeoutExpired
from typing import Optional, Final, Tuple, Callable, final, FrozenSet, Dict, Set, AnyStr, ClassVar, \
	Protocol, runtime_checkable, Sequence, Mapping, Type, TypeVar, Iterable, _ProtocolMeta, List, Union
from warnings import warn

from SEPModules.SEPPrinting import repr_str, time_str
from SEPModules.SEPUtils import abstract_not_implemented, Singleton, SingletonMeta, SEPSyntaxError, SingleStackFrameInfo

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ EXCEPTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LogicError(Exception):
	"""
	:py:class:`LogicError` is an exception class for errors in the :py:mod:`SEPLogic` module.

	:param msg: the message of the error
	:param proposition: the string representation of the proposition which is related to the error
	"""

	def __init__(self, msg: AnyStr, proposition: AnyStr):
		super(LogicError, self).__init__(msg)
		self.msg = msg
		self.proposition = proposition

	def __str__(self) -> str:
		return f"{super(LogicError, self).__str__()} (raised for {self.proposition!r})"

class LogicSyntaxError(SEPSyntaxError, LogicError):
	"""
	:py:class:`LogicSyntaxError` is an exception class for syntax errors in the :py:mod:`SEPLogic` module.

	:param msg: the message of the error
	:param proposition: the string representation of the proposition which is related to the error
	:param file_path: the path to the file where the error occurred
	:param lineno: the line number at which the error occurred in the file
	:param offset: the offset in characters for the syntax error 'cursor'
	:param code_context: the code context of where the error occurred (i.e. the source code)
	"""

	def __init__(self,
				 msg: AnyStr,
				 proposition: AnyStr,
				 file_path: Union[AnyStr, os.PathLike],
				 lineno: int,
				 offset: int,
				 code_context: List[AnyStr]):
		LogicError.__init__(self, msg, proposition)
		SEPSyntaxError.__init__(self, f"{msg} (raised for {proposition!r})", file_path, lineno, offset, code_context)

	@staticmethod
	def from_traceback(msg: AnyStr, proposition: AnyStr, tb: Traceback, offset: int = 0) -> SEPSyntaxError:
		"""
		Creates a :py:class:`SEPSyntaxError` object from a message, traceback, and an optional offset.

		:param msg: the message of the error
		:param proposition: the string representation of the proposition which is related to the error
		:param tb: the traceback to use as basis for the error
		:param offset: the offset in characters for the syntax error 'cursor'
		:return: a new :py:class:`SEPSyntaxError` instance
		"""
		return LogicSyntaxError(msg, proposition, tb.filename, tb.lineno, offset, tb.code_context)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CONNECTIVE BASES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class _Connective(enum.Enum):
	"""
	:py:class:`_Connective` is the base class for connective enumerations. Each enumeration member must contain the method
	that this connective is associated with. It also stores an arity (see :py:class:`ConnectiveArity`), and a "strength".

	The relational operators ``<``, ``>``, ``<=``, ``>=`` of this instance compare the :py:attr:`strength` attribute, and
	the equivalency operators ``==`` and ``!=`` compare strict object identity.

	:param method: the method corresponding to this connective
	:param arity: the arity of this connective (see :py:class:`ConnectiveArity`)
	:param strength: an integer value defining this connective's relative strength to the other connectives (for instance,
		negation is stronger than material implication)
	"""

	def __init__(self,
				 method: Callable,
				 arity: ConnectiveArity,
				 strength: int):
		self._method = method
		self._arity = arity
		self._strength = strength

	@property
	def method(self) -> Callable:
		""" :return: the method implementing the behavior of this connective """
		return self._method

	@property
	def arity(self) -> ConnectiveArity:
		""" :return: the arity of this connective """
		return self._arity

	@property
	def strength(self) -> int:
		""" :return: the relative strength of this connective """
		return self._strength

	def __hash__(self) -> int:
		return super(_Connective, self).__hash__()

	def __eq__(self, other) -> bool:
		return self is other

	def __ne__(self, other) -> bool:
		return self is not other

	def __lt__(self, other) -> bool:
		return isinstance(other, _Connective) and self._strength < other._strength

	def __le__(self, other) -> bool:
		return isinstance(other, _Connective) and self._strength <= other._strength

	def __gt__(self, other) -> bool:
		return isinstance(other, _Connective) and self._strength > other._strength

	def __ge__(self, other) -> bool:
		return isinstance(other, _Connective) and self._strength >= other._strength

	def __repr__(self) -> str:
		return f"<Connective {self._name_}>"

@final
class ConnectiveFormat:
	"""
	:py:class:`ConnectiveFormat` is a class which holds a mapping of :py:class:`_Connective` objects to their respective
	:py:class:`ConnectiveFormat.Entry` objects.

	:param enumeration: which :py:class:`_Connective` enumeration to define in this format
	:param entries: a mapping of :py:class:`_Connective` objects to their respective
		:py:class:`ConnectiveFormat.Entry` objects.
	"""

	class Entry:
		"""
		:py:class:`ConnectiveFormat.Entry` holds one entry of the mapping of :py:class:`ConnectiveFormat`.

		:param prefix: the string to prepend to the operands
		:param joiner: the string to use to join the operands (see ``str.join``)
		:param suffix: the string o append to the operands
		"""

		def __init__(self, prefix: str, joiner: str, suffix: str):
			self._prefix, self._joiner, self._suffix = prefix, joiner, suffix

		@property
		def prefix(self) -> str:
			""" The string to prepend to the operands. """
			return self._prefix

		@property
		def joiner(self) -> str:
			""" The string to use to join the operands (see ``str.join``). """
			return self._joiner

		@property
		def suffix(self) -> str:
			""" The string to append to the operands. """
			return self._suffix

	_ConnectiveEnum: Final[TypeVar] = TypeVar("_ConnectiveEnum", bound=_Connective)

	def __init__(self, enumeration: Type[_ConnectiveEnum], entries: Mapping[_ConnectiveEnum, ConnectiveFormat.Entry]):
		# check that all connectives have an entry
		for conn in enumeration:
			if conn not in entries:
				raise KeyError(f"Missing connective {conn!r} from entries (class uses "
							   f"{enumeration.__name__!r} enumeration)")
		self._enumeration = enumeration
		self._entries = entries

	@property
	def enumeration(self) -> Type[_ConnectiveEnum]:
		""" The :py:class:`_Connective` enumeration this format defines. """
		return self._enumeration

	def format(self, *operands: str, connective: _ConnectiveEnum) -> str:
		"""
		Formats the operands with the given connective based on the format specified by the mapping in this class.

		:param operands: an arbitrary number of operands as strings
		:param connective: the connective from the specified :py:attr:`enumeration` enum class
		:return: the formatted string
		"""
		try:
			entry = self._entries[connective]
		except KeyError as e:
			raise KeyError(f"Missing connective {connective!r} from entries (class uses "
						   f"{self._enumeration.__name__!r} enumeration)") from e
		return f"{entry.prefix}{entry.joiner.join(operands)}{entry.suffix}"

@final
class ConnectiveArity(enum.Enum):
	"""
	:py:class:`ConnectiveArity` is an enum representing the arity of a :py:class:`_Connective` object. It contains an
	operand checking function which takes in the number of operands and returns whether this number is valid with the
	operator, and a description string.

	The available members are as follows:

	* :py:attr:`NILARY`: exactly 0 operands (name is derived from word nil)
	* :py:attr:`UNARY`: exactly 1 operand
	* :py:attr:`BINARY`: exactly 2 operands
	* :py:attr:`NARY`: 2 or more operands (n-ary)

	:param: a function which checks with the supplied number of operands whether the operator can be applied or not
	:param description: a short description of this arity for use in error and log output
	"""

	def __init__(self,
				 operand_check: Callable[[int], bool],
				 description: AnyStr):
		self._operand_check = operand_check
		self._description = str(description)

	NILARY: Final = lambda x: x == 0, "exactly 0 operands"
	UNARY: Final = lambda x: x == 1, "exactly 1 operand"
	BINARY: Final = lambda x: x == 2, "exactly 2 operands"
	NARY: Final = lambda x: x >= 2, "2 or more operands"

	@property
	def operand_check(self) -> Callable[[int], bool]:
		""" :return: a function which checks if the supplied number of operands is valid """
		return self._operand_check

	@property
	def description(self) -> str:
		""" :return: a short description of this arity for use in log or error output """
		return self._description

	def __repr__(self) -> str:
		return f"<Arity {self._name_} (for {self._description})>"

	def __str__(self) -> str:
		return self._description

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CONNECTIVE ENUMS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@runtime_checkable
class SupportsLogicalConnective(Protocol):
	"""
	A simple protocol for indicating that the standard logical connective methods are supported by a class.
	"""

	@abc.abstractmethod
	def __invert__(self):
		raise abstract_not_implemented(SupportsLogicalConnective, "__invert__")

	@abc.abstractmethod
	def __truediv__(self, other):
		raise abstract_not_implemented(SupportsLogicalConnective, "__truediv__")

	@abc.abstractmethod
	def __floordiv__(self, other):
		raise abstract_not_implemented(SupportsLogicalConnective, "__floordiv__")

	@abc.abstractmethod
	def __rshift__(self, other):
		raise abstract_not_implemented(SupportsLogicalConnective, "__rshift__")

	@abc.abstractmethod
	def __lshift__(self, other):
		raise abstract_not_implemented(SupportsLogicalConnective, "__lshift__")

	@abc.abstractmethod
	def __pow__(self, power):
		raise abstract_not_implemented(SupportsLogicalConnective, "__pow__")

	@abc.abstractmethod
	def __and__(self, other):
		raise abstract_not_implemented(SupportsLogicalConnective, "__and__")

	@abc.abstractmethod
	def __or__(self, other):
		raise abstract_not_implemented(SupportsLogicalConnective, "__or__")

@final
class LogicalConnective(_Connective):
	"""
	:py:class:`LogicalConnective` is an enum deriving from :py:class:`_Connective`. it contains the basic logical
	connectives:

	* :py:attr:`EMPTY`: no operator, empty (nilary)
	* :py:attr:`NONE`: no operator, identity (unary)
	* :py:attr:`NEG`: negation (unary)
	* :py:attr:`EXIST`: existential quantification (unary)
	* :py:attr:`UNIV`: universal quantification (unary)
	* :py:attr:`AND`: logical and (n-ary)
	* :py:attr:`OR`: logical or (n-ary)
	* :py:attr:`R_IMPL`: material "left-implies-right" implication (binary)
	* :py:attr:`L_IMPL`: material "right-implies-left" implication (binary)
	* :py:attr:`IFF`: material equivalence, biconditional "if-and-only-if" (binary)
	"""
	EMPTY: Final = lambda self: self, ConnectiveArity.NILARY, 100

	NONE: Final = lambda self: self, ConnectiveArity.UNARY, 100
	NEG: Final = SupportsLogicalConnective.__invert__, ConnectiveArity.UNARY, 80

	EXIST: Final = SupportsLogicalConnective.__truediv__, ConnectiveArity.BINARY, 80
	UNIV: Final = SupportsLogicalConnective.__floordiv__, ConnectiveArity.BINARY, 80
	R_IMPL: Final = SupportsLogicalConnective.__rshift__, ConnectiveArity.BINARY, 30
	L_IMPL: Final = SupportsLogicalConnective.__lshift__, ConnectiveArity.BINARY, 30
	IFF: Final = SupportsLogicalConnective.__pow__, ConnectiveArity.BINARY, 20

	AND: Final = SupportsLogicalConnective.__and__, ConnectiveArity.NARY, 50
	OR: Final = SupportsLogicalConnective.__or__, ConnectiveArity.NARY, 40

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ PROTOCOLS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@runtime_checkable
class SupportsConnectiveFormat(Protocol):
	""" Protocol to check whether or not a class supports formatting by :py:class:`ConnectiveFormat`. """

	@abc.abstractmethod
	def connective_format(self, *, conn_format: ConnectiveFormat, **kwargs) -> str:
		raise abstract_not_implemented(SupportsConnectiveFormat, "conn_format")

class SupportsToPrettyPrint(SupportsConnectiveFormat, abc.ABC):
	""" Abstract base class for subclasses that can convert themselves to a pretty printed string. """

	_pretty_print_format: Final[ConnectiveFormat] = \
		ConnectiveFormat(LogicalConnective, {
				LogicalConnective.EMPTY : ConnectiveFormat.Entry("", "", ""),
				LogicalConnective.NONE  : ConnectiveFormat.Entry("", "", ""),
				LogicalConnective.NEG   : ConnectiveFormat.Entry("\u00AC", "", ""),
				LogicalConnective.EXIST : ConnectiveFormat.Entry("\u2203", ". ", ""),
				LogicalConnective.UNIV  : ConnectiveFormat.Entry("\u2200", ". ", ""),
				LogicalConnective.R_IMPL: ConnectiveFormat.Entry("", " \u2192 ", ""),
				LogicalConnective.L_IMPL: ConnectiveFormat.Entry("", " \u2190 ", ""),
				LogicalConnective.IFF   : ConnectiveFormat.Entry("", " \u2194 ", ""),
				LogicalConnective.AND   : ConnectiveFormat.Entry("", " \u2227 ", ""),
				LogicalConnective.OR    : ConnectiveFormat.Entry("", " \u2228 ", "")
				})

	def to_pretty_print(self) -> str:
		"""
		Converts this object to a pretty-printed string.

		:return: a pretty-printed string representation of this object
		"""
		return self.connective_format(conn_format=self._pretty_print_format)

class SupportsToLimboole(SupportsConnectiveFormat, abc.ABC):
	""" Abstract base class for subclasses that can convert themselves to the limboole syntax as string. """

	_limboole_format: Final[ConnectiveFormat] = \
		ConnectiveFormat(LogicalConnective, {
				LogicalConnective.EMPTY : ConnectiveFormat.Entry("", "", ""),
				LogicalConnective.NONE  : ConnectiveFormat.Entry("", "", ""),
				LogicalConnective.NEG   : ConnectiveFormat.Entry("!", "", ""),
				LogicalConnective.EXIST : ConnectiveFormat.Entry("?", " ", ""),
				LogicalConnective.UNIV  : ConnectiveFormat.Entry("#", " ", ""),
				LogicalConnective.R_IMPL: ConnectiveFormat.Entry("", " -> ", ""),
				LogicalConnective.L_IMPL: ConnectiveFormat.Entry("", " <- ", ""),
				LogicalConnective.IFF   : ConnectiveFormat.Entry("", " <-> ", ""),
				LogicalConnective.AND   : ConnectiveFormat.Entry("", " & ", ""),
				LogicalConnective.OR    : ConnectiveFormat.Entry("", " | ", "")
				})

	def to_limboole(self) -> str:
		"""
		Converts this object to a limboole-compatible string.

		:return: a limboole-compatible string representation of this object
		"""
		return self.connective_format(conn_format=self._limboole_format)

class SupportsToLaTeX(SupportsConnectiveFormat, abc.ABC):
	""" Abstract base class for subclasses that can convert themselves to LaTeX as string. """

	_latex_format: Final[ConnectiveFormat] = \
		ConnectiveFormat(LogicalConnective, {
				LogicalConnective.EMPTY : ConnectiveFormat.Entry("", "", ""),
				LogicalConnective.NONE  : ConnectiveFormat.Entry("", "", ""),
				LogicalConnective.NEG   : ConnectiveFormat.Entry(r"\neg{", "", "}"),
				LogicalConnective.EXIST : ConnectiveFormat.Entry(r"\exists ", "\colon ", ""),
				LogicalConnective.UNIV  : ConnectiveFormat.Entry(r"\forall ", "\colon ", ""),
				LogicalConnective.R_IMPL: ConnectiveFormat.Entry("", r" \rightarrow ", ""),
				LogicalConnective.L_IMPL: ConnectiveFormat.Entry("", r" \leftarrow ", ""),
				LogicalConnective.IFF   : ConnectiveFormat.Entry("", r" \leftrightarrow ", ""),
				LogicalConnective.AND   : ConnectiveFormat.Entry("", r" \land ", ""),
				LogicalConnective.OR    : ConnectiveFormat.Entry("", r" \lor ", "")
				})

	def to_latex(self) -> str:
		"""
		Converts this object to a LaTeX-compatible string.

		:return: a LaTeX-compatible string representation of this object
		"""
		return f"${self.connective_format(conn_format=self._latex_format)}$"

@runtime_checkable
class SupportsEval(Protocol):
	""" Protocol to check whether or not an object can be evaluated using an assignment. """

	@abc.abstractmethod
	def eval(self, assignment: Assignment) -> bool:
		"""
		Evaluates this object using assignment ``assignment`` and returns its truth value.

		:param assignment: the mapping (assignment) of truth values to :py:class:`AtomicProposition` objects
		:return: the truth value of this object under assignment ``assignment``
		"""
		raise abstract_not_implemented(SupportsEval, "eval")

class SupportsLimbooleEval(SupportsToLimboole, abc.ABC):
	""" Abstract base class for an object that can be converted to limboole syntax and then evaluated by limboole. """

	def limboole_eval(self, *option: str, timeout: Optional[float] = 1.0) -> str:
		"""
		Passes the value generated by :py:meth:`to_limboole` to the ``STDIN`` of a Python ``subprocess`` call to the program
		``limboole`` with arguments ``option``. Additionally, a timeout is specified to abort waiting for the program to
		return.

		:param option: an arbitrary amount of strings which will be added to the called limboole command
		:param timeout: a timeout in seconds after which the execution of the subprocess will be halted and a
			``RuntimeError`` raised
		:return: the ``STDOUT`` of the program

		:raise LogicError: if there was an error while running the program, if the process timed out after the seconds
			specified by the ``timeout`` argument
		"""
		try:
			out = run(("limboole",) + option,
					  input=self.to_limboole(), text=True, stdout=PIPE, stderr=PIPE,
					  timeout=timeout, check=True)
			return out.stdout
		except CalledProcessError as e:
			raise LogicError(f"Error while trying to pass formula to limboole:\n{e.stderr}", self.to_limboole()) from e
		except TimeoutExpired as e:
			raise LogicError(f"Process timed out after {time_str(e.timeout)} while trying to pass formula "
							 f"to limboole", self.to_limboole()) from e

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ PROPOSITION ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Proposition(SupportsLogicalConnective,
				  SupportsToPrettyPrint, SupportsToLaTeX,
				  SupportsEval, SupportsLimbooleEval):
	"""
	:py:class:`Proposition` is the base class for representing a general propositional object. A general proposition
	consists of an arbitrary amount of composite :py:class:`Proposition` objects connected by a :py:class:`_Connective`.
	Upon creation of a proposition, the connective's arity operand check function is called to ensure the correct number
	of composite propositions.

	Aside from the propositions and connective, this class also keeps track of all of the seen connectives in its child
	proposition objects. It also keeps track of all the atomic propositions that have been seen in its child proposition
	objects (see :py:class:`AtomicProposition`).

	The class provides the following attributes for checking various characteristics of the structure of the proposition:
	:py:attr:`empty`, :py:attr:`atomic`, :py:attr:`literal`, :py:attr:`quantifier`, :py:attr:`quantified`.

	The operations defined by :py:class:`LogicalConnective` have been implemented in this class, which means that all
	propositions can be arbitrarily combined, with the mapping from operator to method being outlined in each member
	object of :py:class:`LogicalConnective`. It is noteworthy to say that ``__mul__`` (``*``) is mapped to ``__and__``
	(``&``), and ``__add__`` (``+``) is mapped to ``__or__`` (``|``) by default.

	..	note::

		All new instances of :py:class:`Proposition` are normalized according to the static method :py:meth:`normalize`,
		so that redundant constructions like nested :py:attr:`LogicalConnective.NONE` connectives can be avoided.

	..	warning::

		The boolean value of all :py:class:`Proposition` objects is ``False`` by default and issues a syntax warning. If
		one desires to check the truth value of a proposition, the :py:meth:`eval` method should be used with an
		assignment.

	:param proposition: an arbitrary number of :py:class:`Proposition` objects
	:param connective: a :py:class:`_Connective` for defining the combining behavior of all passed propositions, usually
		a member of :py:class:`LogicalConnective`, if ``None`` is given the constructor will try to use the correct
		connective when possible
	:raise ValueError: if no connective is given and the connective cannot be deduced from the other arguments, if the
		number of operands is incompatible with the given connective
	"""

	def __init__(self, *proposition: Proposition, connective: Optional[_Connective] = None):
		# try to guess right connective if not given
		if connective is None or connective.arity == ConnectiveArity.NARY:
			if len(proposition) == 0:
				connective = LogicalConnective.EMPTY
			elif len(proposition) == 1:
				connective = LogicalConnective.NONE
			elif connective is None:
				raise ValueError("_Connective missing from constructor of Proposition")

		# check if num of operands is compatible with connective
		if not connective.arity.operand_check(len(proposition)):
			raise ValueError(f"Incompatible number of operands for connective {connective.name}, "
							 f"received {len(proposition)} but expected {connective.arity.description}")

		# apply normalization step
		proposition, connective = self.normalize(proposition, connective)

		# remove duplicates from nary operation
		if connective.arity == ConnectiveArity.NARY:
			proposition = tuple(dict.fromkeys(proposition))

		self._connective: _Connective = connective
		self._propositions: Tuple[Proposition] = tuple(proposition)

		# keep list of contained atomic props
		self._seen_atomic_propositions = {p for p in proposition if p.atomic}
		self._seen_atomic_propositions.update(*(p._seen_atomic_propositions for p in proposition if p is not self))
		self._seen_atomic_propositions: FrozenSet[AtomicProposition] = frozenset(self._seen_atomic_propositions)

		# keep list of contained connectives
		self._seen_connectives = {connective}
		self._seen_connectives.update(*(p._seen_connectives for p in proposition if p is not self))
		self._seen_connectives: FrozenSet[_Connective] = frozenset(self._seen_connectives)

	@staticmethod
	def normalize(propositions: Sequence[Proposition],
				  connective: _Connective) -> Tuple[Sequence[Proposition], _Connective]:
		r"""
		Normalizes the input to the initializer of a :py:class:`Proposition` instance. The arguments to this function are
		the same arguments passed to :py:meth:`__init__` but note that this function will not try to check or correct these
		inputs. The following rules are applied for :math:`a \in \mathcal{P}`, and :math:`P \in \mathcal{L}`:

		..	math::

			\neg \top 					&{}\Rightarrow \bot \\
			\neg \bot					&{}\Rightarrow \top \\
			\neg \neg a					&{}\Rightarrow a \\
			(a)							&{}\Rightarrow a \\
			P \land (a \land \cdots)	&{}\Rightarrow P \land a \land \cdots \\
			P \lor (a \lor \cdots)		&{}\Rightarrow P \lor a \lor \cdots

		Note that in this notation, the parentheses :math:`(\cdots)` refer to a :py:class:`Proposition` object which is
		nested within the unary :py:attr:`LogicalConnective.NONE` connective.

		"""
		# unary
		if connective.arity == ConnectiveArity.UNARY:
			p = propositions[0]

			# handle negation
			if connective == LogicalConnective.NEG:
				# top/bottom
				if p == Top:
					return (Bottom,), LogicalConnective.NONE
				elif p == Bottom:
					return (Top,), LogicalConnective.NONE
				# nested neg
				elif p._connective == LogicalConnective.NEG:
					q = p._propositions[0]
					return q.normalize(q._propositions, q._connective)
			# handle NONEs
			elif connective == LogicalConnective.NONE:
				return p.normalize(p._propositions, p._connective)
		# nary
		elif connective in (LogicalConnective.AND, LogicalConnective.OR):
			# combine nary props
			for p in propositions:
				if connective == p._connective:
					return p.normalize((*(q for q in propositions if q is not p), *p._propositions), connective)

		# no negation, simply apply to all children now
		# default exit
		new_props = list()
		for p in propositions:
			if p.atomic:
				new_props.append(p._propositions[0])
			else:
				tmp = p.normalize(p._propositions, p._connective)
				new_props.append(Proposition(*tmp[0], connective=tmp[1]))
		return new_props, connective

	@staticmethod
	def _check_assignment(assignment: Assignment) -> None:
		"""
		Checks whether an assignment is legal or not.

		:raise ValueError: if the assignment contains :py:data:`Top` or :py:data:`Bottom`
		"""
		if Top in assignment or Bottom in assignment:
			raise ValueError(f"Cannot assign to Top or Bottom in assignment: {_assignment_to_str(assignment)}")

	@final
	def _require_non_empty(self, p: Proposition, action_name: str) -> Proposition:
		"""
		:return: the proposition if it is not empty (see :py:meth:`empty`)
		:raise LogicError: if the proposition is empty
		"""
		if self.empty:
			raise LogicError(f"Cannot {action_name} empty proposition", str(self))
		return p

	# attributes and properties
	@property
	def propositions(self) -> Tuple[Proposition]:
		""" :return: the child proposition instances of this class """
		return self._propositions

	@property
	def connective(self) -> _Connective:
		""" :return: the connective of this class, or :py:attr:`LogicalConnective.NONE` if no connective was defined """
		return LogicalConnective.NONE if self._connective is None else self._connective

	@property
	def seen_atomic_propositions(self) -> Set[AtomicProposition]:
		"""
		Gathers a set of all the atomic propositions that have been defined in any of the child proposition objects of
		this class.

		:return: a set of atomic propositions found in any of the child propositions of this class
		"""
		return set(self._seen_atomic_propositions)

	@property
	def seen_connectives(self) -> Set[_Connective]:
		"""
		Gathers a set of all the connectives that have been defined in any of the child proposition objects of
		this class.

		:return: a set of connectives found in any of the child propositions of this class
		"""
		return set(self._seen_connectives)

	@property
	def empty(self) -> bool:
		""" :return: whether or not this proposition contains child propositions """
		return len(self) == 0

	@final
	@property
	def atomic(self) -> bool:
		""" :return: whether or not this proposition is atomic """
		return isinstance(self, AtomicProposition) or (self._connective == LogicalConnective.NONE
													   and self._propositions[0].atomic)

	@property
	def literal(self) -> bool:
		""" :return: whether or not this proposition is a literal (i.e. atomic or a negation of an atomic proposition) """
		# either one or arbitrarily negated atomic proposition
		return self.atomic or (self._connective in (LogicalConnective.NONE, LogicalConnective.NEG)
							   and self._propositions[0].literal)

	@property
	def quantifier(self) -> bool:
		"""
		:return: whether or not this proposition is a quantifier (i.e. a :py:attr:`literal` proposition which is
			existentially or universally quantified)
		"""
		# quantifier
		quantifier = (self._connective == LogicalConnective.EXIST or self._connective == LogicalConnective.UNIV) and \
					 self._propositions[0].atomic
		# or arbitrarily negated quantifier
		quantifier |= self._connective == LogicalConnective.NEG and self._propositions[0].quantifier
		return quantifier

	@property
	def quantified(self) -> bool:
		"""
		:return: whether or not this proposition contains any quantifiers (i.e. a proposition where any of the child
			propositions fulfill :py:attr:`quantifier`)
		"""
		return LogicalConnective.EXIST in self._seen_connectives or LogicalConnective.UNIV in self._seen_connectives

	# formula methods
	def CNF(self) -> bool:
		"""
		Checks whether or not this formulas is in conjunctive normal form (counterpart to :py:meth:`DNF`).

		:return: whether or not this formula is in CNF
		"""
		# parent is AND
		valid = self._connective == LogicalConnective.AND
		# all direct children are literals, or OR of literals
		for p in self._propositions:
			if not valid: break
			valid &= p.literal or (p._connective == LogicalConnective.OR and all(q.literal for q in p._propositions))
		return valid

	def DNF(self) -> bool:
		"""
		Checks whether or not this formulas is in disjunctive normal form (counterpart to :py:meth:`CNF`).

		:return: whether or not this formula is in DNF
		"""
		# parent is OR
		valid = self._connective == LogicalConnective.OR
		# all direct children are literals, or AND of literals
		for p in self._propositions:
			if not valid: break
			valid &= p.literal or (p._connective == LogicalConnective.AND and all(q.literal for q in p._propositions))
		return valid

	def valid(self) -> bool:
		"""
		Checks whether or not this formula is valid using ``limboole``.

		:return: whether or not this formula is valid
		:raise LogicError: if the proposition is quantified
		"""
		if self.quantified:
			raise LogicError("No support for evaluating quantified formulas, see SEPPQBF instead", str(self))
		return "% VALID formula" in self.limboole_eval()

	def sat(self) -> bool:
		"""
		Checks whether or not this formula is satisfiable using ``limboole``.

		:return: whether or not this formula is satisfiable
		:raise LogicError: if the proposition is quantified
		"""
		if self.quantified:
			raise LogicError("No support for evaluating quantified formulas, see SEPPQBF instead", str(self))
		return "% SATISFIABLE formula" in self.limboole_eval("-s")

	def model(self) -> Assignment:
		"""
		Looks for a satisfying assignment (model) of this formula using ``limboole``. If no such model is found and the
		formula is unsatisfiable, the empty dictionary is returned. The dictionary maps each :py:class:`AtomicProposition`
		object of this class to a boolean truth value.

		:return: either a satisfying assignment as dictionary or the empty dictionary, if no such assignment exists
		:raise LogicError: if there was an error parsing the output model
		"""
		out: Dict[AtomicProposition, bool] = dict()

		atomic_props = [(p, p.to_limboole()) for p in self.seen_atomic_propositions]
		name: str
		val: str
		# each line of form [<identifier>] = (1|0)
		for name, val in [l.split("=") for l in self.limboole_eval("-s").splitlines()[1:]]:
			name, val = name.strip(), val.strip()
			for i in range(len(atomic_props)):
				# we do not assignments for top and bottom
				if not name in ("top", "bottom") and name == atomic_props[i][1]:
					try:
						out[atomic_props[i][0]] = bool(int(val))
						del atomic_props[i]
						break
					except ValueError as e:
						raise LogicError(f"Error while parsing limboole output model, failed to convert {val} to a "
										 f"boolean value", str(self)) from e
		return out

	def eval(self, assignment: Assignment) -> bool:
		self._check_assignment(assignment)
		if self.quantified:
			raise LogicError("No support for evaluating quantified formulas, see SEPPQBF instead", str(self))

		# nilary
		if self._connective.arity == ConnectiveArity.NILARY:
			raise LogicError("Cannot determine truth value of empty proposition without context", str(self))
		# unary
		elif self._connective.arity == ConnectiveArity.UNARY:
			p = self._propositions[0]

			if self._connective == LogicalConnective.NEG:
				return not p.eval(assignment)
			elif self._connective == LogicalConnective.NONE:
				return p.eval(assignment)
		# binary
		elif self._connective.arity == ConnectiveArity.BINARY:
			p, q = self._propositions[0:2]

			if self._connective == LogicalConnective.R_IMPL:
				return not p.eval(assignment) or q.eval(assignment)
			elif self._connective == LogicalConnective.L_IMPL:
				return p.eval(assignment) or not q.eval(assignment)
			elif self._connective == LogicalConnective.IFF:
				return p.eval(assignment) == q.eval(assignment)
		# nary
		elif self._connective.arity == ConnectiveArity.NARY:
			if self._connective == LogicalConnective.OR:
				return any(p.eval(assignment) for p in self._propositions)
			elif self._connective == LogicalConnective.AND:
				return all(p.eval(assignment) for p in self._propositions)

		raise ValueError(f"No implemented evaluation case for _Connective {self._connective}")

	def _rec_partial_eval(self, assignment: Assignment) -> Proposition:
		return Proposition(*(p._rec_partial_eval(assignment) for p in self._propositions), connective=self._connective)

	def partial_eval(self, assignment: Assignment, *, simplify: bool = False) -> Proposition:
		"""
		Partially evaluate this proposition by replacing atomic propositions by the truth constants :py:data:`Top`, or
		:py:data:`Bottom` according to the given assignment.

		..	seealso:: :py:meth:`Proposition.eval`

		:param assignment: the (partial) assignment to apply to this proposition
		:param simplify: whether or not to apply simplification rules to the proposition after applying the assignment
		:return: the partially evaluated proposition
		:raise LogicError: if the proposition is quantified
		"""
		self._check_assignment(assignment)
		if self.quantified:
			raise LogicError("No support for evaluating quantified formulas, see SEPPQBF instead", str(self))

		prop = self._rec_partial_eval(assignment)
		if simplify:
			prop = prop.expand().reduce()
		return prop

	def simplify_neg(self) -> Proposition:
		r"""
		Perform simplification steps regarding the negations in this proposition. The following rules are applied for
		:math:`a, b \in \mathcal{P}`, and a proposition :math:`P \in \mathcal{L}`:

		..	math::

			\neg \neg a 					&{}\Longrightarrow a \\
			\neg (a \rightarrow b) 			&{}\Longrightarrow a \lor \neg b \\
			\neg (a \leftarrow b) 			&{}\Longrightarrow \neg a \lor b \\
			\neg (a \leftrightarrow b) 		&{}\Longrightarrow (a \lor b) \land (\neg a \lor \neg b) \\
			\neg \exists a : P				&{}\Longrightarrow \forall a : \neg P \\
			\neg \forall a : P				&{}\Longrightarrow \exists a : \neg P \\
			\neg (a \land b \land \cdots) 	&{}\Longrightarrow \neg a \lor \neg b \lor \cdots \\
			\neg (a \lor b \lor \cdots) 	&{}\Longrightarrow \neg a \land \neg b \land \cdots

		:return: the simplified proposition
		"""
		if self.atomic:
			return self

		# shorthand for recursive call
		_s = Proposition.simplify_neg

		# handle negation cases
		if self._connective == LogicalConnective.NEG:
			p = self._propositions[0]

			# unary connectives
			if p._connective.arity == ConnectiveArity.UNARY:
				q = p._propositions[0]

				if p._connective == LogicalConnective.NEG:
					return _s(q)
			# binary connectives
			if p._connective.arity == ConnectiveArity.BINARY:
				u, v = p._propositions[0:2]
				if p._connective == LogicalConnective.R_IMPL:
					return _s(u) & _s(~v)
				elif p._connective == LogicalConnective.L_IMPL:
					return _s(~u) & _s(v)
				elif p._connective == LogicalConnective.IFF:
					return (_s(u) | _s(v)) & (_s(~u) | _s(~v))
				elif p._connective == LogicalConnective.UNIV:
					return u / _s(~v)
				elif p._connective == LogicalConnective.EXIST:
					return u // _s(~v)
			# nary connectives
			elif p._connective.arity == ConnectiveArity.NARY:
				if p._connective == LogicalConnective.AND:
					return Proposition(*(_s(~u) for u in p._propositions), connective=LogicalConnective.OR)
				elif p._connective == LogicalConnective.OR:
					return Proposition(*(_s(~u) for u in p._propositions), connective=LogicalConnective.AND)

		# no negation, simply apply to all children now
		# default exit
		return Proposition(*(_s(u) for u in self._propositions), connective=self._connective)

	def _rec_reduce(self, depth: int) -> Proposition:
		if self.literal:
			return self

		# binary
		if self._connective.arity == ConnectiveArity.BINARY:
			p, q = self._propositions[0], self._propositions[1]

			if self._connective in (LogicalConnective.R_IMPL, LogicalConnective.L_IMPL):
				# flip in this case
				if self._connective == LogicalConnective.L_IMPL:
					p, q = q, p
				if (p == Bottom) or (q == Top) or (p == q) \
						or ((p._connective == LogicalConnective.AND) and (q in p)) \
						or ((q._connective == LogicalConnective.OR) and (p in q)):
					return Top
				elif (q == Bottom) \
						or ((q._connective == LogicalConnective.AND) and (~p in q)):
					return ~p
				elif (p == Top) \
						or ((p._connective == LogicalConnective.OR) and (~q in p)):
					return q
			elif self._connective == LogicalConnective.IFF:
				if p == Top:
					return q
				elif q == Top:
					return p
				elif p == Bottom:
					return ~q
				elif q == Bottom:
					return ~p
				elif p == q:
					return Top
				elif p == (~q):
					return Bottom
		# AND/OR
		elif self._connective in (LogicalConnective.AND, LogicalConnective.OR):
			prop_set: Set[Proposition] = set(self._propositions)

			# check for contradictions and tautologies
			if self._connective == LogicalConnective.AND and Top in prop_set:
				return Proposition(*prop_set.difference({Top}), connective=self._connective)._rec_reduce(0)
			elif self._connective == LogicalConnective.AND and Bottom in prop_set:
				return Bottom
			elif self._connective == LogicalConnective.OR and Top in prop_set:
				return Top
			elif self._connective == LogicalConnective.OR and Bottom in prop_set:
				return Proposition(*prop_set.difference({Bottom}), connective=self._connective)._rec_reduce(0)
			else:
				# iterate over pairs of propositions
				for p, q in permutations(prop_set, r=2):
					# a with ~a
					if p == (~q):
						return Bottom if self._connective == LogicalConnective.AND else Top

					# absorption
					elif p.literal ^ q.literal:
						prop, lit = (p, q) if q.literal else (q, p)

						if (prop._connective in (LogicalConnective.AND, LogicalConnective.OR)) \
								and (prop._connective != self._connective) \
								and (lit in prop):
							others = prop_set.difference({prop})
							return Proposition(*others, connective=self._connective)._rec_reduce(0)

					# distributivity
					elif (not p.literal and not q.literal) and (p._connective == q._connective) \
							and (p._connective in (LogicalConnective.AND, LogicalConnective.OR)) \
							and (p._connective != self._connective):
						_p, _q = set(p._propositions), set(q._propositions)
						factor_a = _p.intersection(_q)
						factor_b = (Proposition(*_p.difference(factor_a), connective=p._connective),
									Proposition(*_q.difference(factor_a), connective=q._connective))

						if 1 <= len(factor_a) < len(_p) + len(_q):
							others = prop_set.difference({p, q})
							res = Proposition(*factor_a, Proposition(*factor_b, connective=self._connective),
											  connective=p._connective)
							return Proposition(res, *others, connective=self._connective)._rec_reduce(0)

					# detect impl
					if self._connective == LogicalConnective.OR \
							and ((p._connective == LogicalConnective.NEG) ^ (q._connective == LogicalConnective.NEG)):
						others = prop_set.difference({p, q})
						if p._connective == LogicalConnective.NEG:
							return Proposition(p._propositions[0] >> q, *others,
											   connective=self._connective)._rec_reduce(0)
						elif q._connective == LogicalConnective.NEG:
							return Proposition(q._propositions[0] >> p, *others,
											   connective=self._connective)._rec_reduce(0)

					# detect iff
					elif self._connective == LogicalConnective.AND \
							and p._connective in (LogicalConnective.R_IMPL, LogicalConnective.L_IMPL) \
							and q._connective in (LogicalConnective.R_IMPL, LogicalConnective.L_IMPL):
						a, b = p._propositions[0:2]
						c, d = q._propositions[0:2]
						if p._connective == LogicalConnective.L_IMPL:
							b, a = a, b
						if q._connective == LogicalConnective.L_IMPL:
							d, c = c, d

						if a == d and b == c:
							others = prop_set.difference({p, q})
							return Proposition(Proposition(a, b, connective=LogicalConnective.IFF), *others,
											   connective=self._connective)._rec_reduce(0)

		# reduce recursively, default exit
		new = Proposition(*(p._rec_reduce(0) for p in self._propositions), connective=self._connective)
		return new._rec_reduce(depth + 1) if depth < 1 else new

	def reduce(self) -> Proposition:
		r"""
		Reduce this proposition, so that its syntactic representation is more compact. The following rules are applied
		for :math:`a, b \in \mathcal{P}`, and propositions :math:`P, Q, R, S \in \mathcal{L}`:

		..	math:: a \leftarrow b :\Longleftrightarrow b \rightarrow a

		..	math::

			\bot \rightarrow a 							&{}\Longrightarrow \top \\
			a \rightarrow \top							&{}\Longrightarrow \top \\
			a \rightarrow a 							&{}\Longrightarrow \top \\
			a \land b \land \cdots \rightarrow a 		&{}\Longrightarrow \top \\
			a \rightarrow a \lor b \lor \dots			&{}\Longrightarrow \top \\
			a \rightarrow \bot 							&{}\Longrightarrow \neg a \\
			\top \rightarrow a 							&{}\Longrightarrow a \\
			a \rightarrow \neg a \land b \land \cdots	&{}\Longrightarrow \neg a \\
			\neg a \rightarrow a \land b \land \cdots	&{}\Longrightarrow a \\
			a \lor b \lor \cdots \rightarrow \neg a		&{}\Longrightarrow \neg a \\
			\neg a \lor b \lor \cdots \rightarrow a		&{}\Longrightarrow a

		..	math::

			a \leftrightarrow \top		&{}\Longrightarrow a \\
			\top \leftrightarrow a		&{}\Longrightarrow a \\
			a \leftrightarrow \bot		&{}\Longrightarrow \neg a \\
			\bot \leftrightarrow a		&{}\Longrightarrow \neg a \\
			a \leftrightarrow a			&{}\Longrightarrow \top \\
			\neg a \leftrightarrow a	&{}\Longrightarrow \bot \\
			a \leftrightarrow \neg a	&{}\Longrightarrow \bot

		..	math::

			\top \land P										&{}\Longrightarrow P \\
			\bot \land \cdots									&{}\Longrightarrow \bot \\
			\top \lor \cdots									&{}\Longrightarrow \top \\
			\bot \lor P											&{}\Longrightarrow P \\
			a \lor \neg a \lor \cdots							&{}\Longrightarrow \top \\
			a \land \neg a \land \cdots							&{}\Longrightarrow \bot \\
			a \land (a \lor \cdots) \land P 					&{}\Longrightarrow a \land P \\
			a \lor (a \land \cdots) \lor P						&{}\Longrightarrow a \lor P \\
			(P \land Q) \lor (P \land R) \lor S					&{}\Longrightarrow \big(P \land (Q \lor R)\big) \lor S \\
			(P \lor Q) \land (P \lor R) \land S					&{}\Longrightarrow \big(P \lor (Q \land R)\big) \land S \\
			\neg P \lor Q \lor R								&{}\Longrightarrow (P \rightarrow Q) \lor R \\
			P \lor \neg Q \lor R								&{}\Longrightarrow (Q \rightarrow P) \lor R \\
			(P \rightarrow Q) \land (Q \rightarrow P) \land R 	&{}\Longrightarrow (P \leftrightarrow Q) \land R

		:return: the reduced proposition
		"""
		return self._rec_reduce(0)

	def expand(self) -> Proposition:
		r"""
		Expand this proposition, so that its syntactic representation is less compact. The following rules are applied
		for :math:`a, b, c \in \mathcal{P}`, and a proposition :math:`P \in \mathcal{L}`:

		..	math::

			a \rightarrow b 						&{}\Longrightarrow \neg a \lor b \\
			a \leftarrow b 							&{}\Longrightarrow a \lor \neg b \\
			a \leftrightarrow b 					&{}\Longrightarrow (a \land b) \lor (\neg a \land \neg b) \\
			a \land (b \lor c \lor \cdots) \land P 	&{}\Longrightarrow
			\big((a \land b) \lor (a \land c) \lor \cdots\big) \land P \\
			a \lor (b \land c \land \cdots) \lor P  &{}\Longrightarrow
			\big((a \lor b) \land (a \lor c) \land \cdots\big) \lor P

		:return: the expanded proposition
		"""
		if self.literal:
			return self

		# binary
		if self._connective.arity == ConnectiveArity.BINARY:
			p, q = self._propositions[0].expand(), self._propositions[1].expand()

			if self._connective == LogicalConnective.R_IMPL:
				return (~p | q).expand()
			elif self._connective == LogicalConnective.L_IMPL:
				return (p | ~q).expand()
			elif self._connective == LogicalConnective.IFF:
				return ((p & q) | (~p & ~q)).expand()
		# nary
		elif self._connective.arity in (LogicalConnective.AND, LogicalConnective.OR):
			prop_set: Set[Proposition] = {p.expand() for p in self._propositions}
			# distributivity
			for p, q in permutations(prop_set, r=2):
				# exactly one is literal
				if p.literal ^ q.literal:
					# set up prop and lit and do more checks
					prop, lit = (p, q) if q.literal else (q, p)
					if prop._connective not in (LogicalConnective.AND, LogicalConnective.OR) \
							or self._connective == prop._connective:
						continue

					others = prop_set.difference({lit, prop})
					expanded = Proposition(*(Proposition(lit, r, connective=self._connective)
											 for r in prop._propositions),
										   connective=prop._connective)
					# recursive expand
					return Proposition(expanded, *others, connective=self._connective).expand()

		# expand children, default exit
		return Proposition(*(p.expand() for p in self._propositions), connective=self._connective)

	def is_sub_proposition(self, other: Proposition) -> bool:
		return self == other \
			   or (self._connective.arity == ConnectiveArity.NARY
				   and self._connective == other._connective
				   and all(q in other for q in self._propositions)) \
			   or any((self == p) or (not p.atomic and self.is_sub_proposition(p))
					  for p in other._propositions)

	# operators
	def __binary_operator(self, other, connective: _Connective, connective_name: str) -> Proposition:
		"""
		Connect two propositions by a connective and either return the proposition or a :py:class:`Formula`. N-ary
		operators are automatically combined, and unilary operators are merged into one proposition if possible.
		"""
		# convert int to bool if possible
		if isinstance(other, int):
			if not (other == 0 or other == 1):
				raise ValueError(f"Cannot {connective_name} int of value {other}, must be 1 or 0, or True or False")
			other = bool(other)

		# check types now
		if not isinstance(other, (Proposition, bool)):
			raise TypeError(f"Cannot {connective_name} object of type {other.__class__.__name__}, expected "
							f"Proposition, bool, or int")

		# convert bool to Top or Bottom
		if isinstance(other, bool):
			other = Top if other else Bottom

		# check if either is empty
		if self.empty:
			return other
		if other.empty:
			return self

		# default
		self_props = (self,)
		other_props = (other,)
		# either connectives match
		if connective.arity == ConnectiveArity.NARY:
			if self._connective == connective:
				self_props = self._propositions
			if other._connective == connective:
				other_props = other._propositions

		return Proposition(*self_props, *other_props, connective=connective)

	def __binary_quantifier(self, other, connective: _Connective, connective_name: str) -> Proposition:
		if not isinstance(other, Proposition):
			raise TypeError(f"Cannot {connective_name} object of type {other.__class__.__name__}, expected "
							f"Proposition")
		if not self.atomic:
			raise LogicSyntaxError.from_traceback(f"Quantified proposition must be atomic",
												  str(self), SingleStackFrameInfo()[2], offset=1)
		return Proposition(self, other, connective=connective)

	def __r_binary_quantifier(self, other, connective: _Connective, connective_name: str) -> Proposition:
		if not isinstance(other, (Proposition, Iterable)):
			raise TypeError(f"Cannot {connective_name} object of type {other.__class__.__name__}, expected "
							f"Proposition or Iterable")
		# always make iterable
		if isinstance(other, Proposition):
			other = (other,)

		# incrementally build up new proposition
		p = self
		for atom in reversed(other):
			if not isinstance(atom, Proposition):
				raise TypeError(f"Cannot {connective_name} object of type {atom.__class__.__name__}, expected "
								f"Proposition")
			p = atom.__binary_quantifier(p, connective, connective_name)
		return p

	def __and__(self, other) -> Proposition:
		return self.__binary_operator(other, LogicalConnective.AND, "AND")

	def __mul__(self, other) -> Proposition:
		return self.__and__(other)

	def __or__(self, other) -> Proposition:
		return self.__binary_operator(other, LogicalConnective.OR, "OR")

	def __add__(self, other) -> Proposition:
		return self.__or__(other)

	def __rshift__(self, other) -> Proposition:
		return self.__binary_operator(other, LogicalConnective.R_IMPL, "RIGHT IMPLY")

	def __lshift__(self, other) -> Proposition:
		return self.__binary_operator(other, LogicalConnective.L_IMPL, "LEFT IMPLY")

	def __pow__(self, other) -> Proposition:
		return self.__binary_operator(other, LogicalConnective.IFF, "BICONDITIONAL")

	def __truediv__(self, other) -> Proposition:
		return self.__binary_quantifier(other, LogicalConnective.EXIST, "EXISTENTIALLY QUANTIFY")

	def __floordiv__(self, other) -> Proposition:
		return self.__binary_quantifier(other, LogicalConnective.UNIV, "UNIVERSALLY QUANTIFY")

	def __rtruediv__(self, other) -> Proposition:
		return self.__r_binary_quantifier(other, LogicalConnective.EXIST, "EXISTENTIALLY QUANTIFY")

	def __rfloordiv__(self, other) -> Proposition:
		return self.__r_binary_quantifier(other, LogicalConnective.UNIV, "UNIVERSALLY QUANTIFY")

	def __invert__(self) -> Proposition:
		return Proposition(self, connective=LogicalConnective.NEG)

	# misc methods
	def copy(self) -> Proposition:
		"""
		Copies this proposition into a new proposition object. This is a deep copy of all containing propositions.

		:return: a deep copy of this proposition object
		"""
		atomic_props = {p: p.copy() for p in self._seen_atomic_propositions}

		def __copy__(prop: Proposition) -> Proposition:
			return Proposition(*(atomic_props[p] if p in atomic_props else __copy__(p) for p in prop._propositions),
							   connective=prop._connective)

		return __copy__(self)

	@final
	def __bool__(self) -> False:
		warn(f"bool(Proposition) should not be used, Proposition objects cannot be used in if or while statements "
			 f"or expressions and will always return False", SyntaxWarning, stacklevel=2)
		return False

	def __len__(self) -> int:
		return len(self._propositions)

	def __contains__(self, item):
		return any(item == p for p in self._propositions)

	# comparison methods
	def __hash__(self) -> int:
		if self._connective == LogicalConnective.NONE:
			return hash(self._propositions[0])
		else:
			return hash((*(hash(p) for p in self._propositions), self._connective))

	def syntactically_equal(self, other) -> bool:
		"""
		Compare two propositions syntactically based on their computed hash.

		:param other: the proposition to compare against
		:return: whether or not ``cls`` is syntactically equivalent to ``other``
		"""
		return isinstance(other, Proposition) and (hash(other) == hash(self))

	@final
	def __eq__(self, other) -> bool:
		return self.syntactically_equal(other)

	# str methods
	def connective_format(self, *,
						  conn_format: ConnectiveFormat,
						  parent: Optional[Proposition] = None) -> str:
		ignore_pars = parent is None \
					  or self._connective.arity == ConnectiveArity.UNARY \
					  or (parent._connective in (LogicalConnective.UNIV, LogicalConnective.EXIST)
						  and self is parent._propositions[1])

		props = (p.connective_format(conn_format=conn_format, parent=self)
				 for p in self._propositions)
		out = conn_format.format(*props, connective=self._connective)

		return out if ignore_pars else f"({out})"

	@final
	def __str__(self) -> str:
		return self.to_pretty_print()

	def __repr__(self) -> str:
		return repr_str(self, Proposition.propositions, Proposition.connective, value_function=str)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ ATOMIC PROPOSITIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AtomicProposition(Proposition):
	"""
	:py:class:`AtomicProposition` represents the smallest unit of a :py:class:`Proposition`, aside from the empty formula.
	Each new instance of :py:class:`AtomicProposition` is uniquely assigned an :py:attr:`id` defined by the system's current
	time in nanoseconds and a random __offset. The class registers this id in a set to avoid the slim chance of a duplicate.
	All subclasses should, if they desire a custom implementation of the id system, register it like so:
	``AtomicProposition._id_set.add(id)``.

	Each :py:class:`AtomicProposition` object, besides the :py:attr:`id`, also has a unique :py:attr:`volatile_name`. As
	the name suggests, this name does not guarantee to be unique over multiple runtimes and is subject to change at any
	point. It is used when generating the :py:meth:`to_limboole` and :py:meth:`__str__` format outputs. The naming convention
	is given as regular expression ``^[a-z](')*$`` for pretty-printed, and ``^[a-z](-prime)*$`` for limboole output.

	This class, as well as each class subclassing :py:class:`AtomicProposition` will contain the class attributes defining
	how the :py:attr:`volatile_name` of an object should behave. Each new subclass will start the name back at the lowest
	character at the lowest "prime characters" count. To keep names unique, each name will be prefixed with the subclass'
	name. This behaviour may be changed but with caution.

	To get the next volatile name for a new object, use the class method :py:meth:`_next_volatile_name`. To get the next
	id for a new object, use the static method :py:meth:`_next_id`.

	The exception are the special :py:data:`Top` and :py:data:`Bottom` singleton objects. :py:data:`Top` will always be
	assigned id ``1`` and volatile name ``top``, and :py:data:`Bottom` will always be assigned id ``0`` and volatile name
	``bottom``. The pretty-printed outputs of ``top`` and ``bottom`` are the down-tick and up-tick symbols respectively,
	and the limboole outputs are ``(top | !top)`` and ``(bottom & !bottom)`` since limboole does not support these truth
	values natively.
	"""

	_id_set: ClassVar[Set[int]] = set()

	_curr_name: ClassVar[Optional[str]] = None
	_prime: ClassVar[str] = "\u2032"
	_curr_name_primes: ClassVar[int] = 0
	_curr_name_prefix: ClassVar[str] = ""

	def __init__(self):
		self._id = self._next_id()
		self._volatile_name = self._next_volatile_name()
		super(AtomicProposition, self).__init__(self, connective=LogicalConnective.NONE)

	def __init_subclass__(cls, *args, **kwargs):
		super(AtomicProposition, cls).__init_subclass__(*args, **kwargs)
		cls._curr_name = None
		cls._curr_name_primes = 0
		cls._curr_name_prefix = f"{cls.__name__}_"

	@staticmethod
	def normalize(propositions: Sequence[Proposition],
				  connective: _Connective) -> Tuple[Sequence[Proposition], _Connective]:
		return propositions, connective

	@staticmethod
	@final
	def _next_id(requested_id: int = None) -> int:
		"""
		Get the next available id. If ``requested_id`` is passed, then that id will be returned if it is valid and has not
		been used by another object.

		:param requested_id: optional, the requested id
		:return: the requested id or the next valid id if no requested id was passed or if the requested id was taken already
		"""
		new_id = requested_id
		while (new_id is None) or (new_id in AtomicProposition._id_set):
			new_id = time.monotonic_ns() + random.randint(0, 10 ** 6)
		AtomicProposition._id_set.add(new_id)
		return new_id

	@classmethod
	def _next_volatile_name(cls) -> str:
		"""
		Get the next available volatile name.

		:return: the next volatile name as string
		"""
		if cls._curr_name is None:
			cls._curr_name = "a"
		else:
			if ord(cls._curr_name) < ord("z"):
				cls._curr_name = chr(ord(cls._curr_name) + 1)
			else:
				cls._curr_name = "a"
				cls._curr_name_primes += 1
		return cls._curr_name_prefix + cls._curr_name + (cls._prime * cls._curr_name_primes)

	@property
	def id(self) -> int:
		""" :return: the id of this atomic proposition object """
		return self._id

	@property
	def volatile_name(self) -> str:
		""" :return: the volatile name of this atomic proposition object """
		return self._volatile_name

	def eval(self, assignment: Assignment) -> bool:
		self._check_assignment(assignment)
		if not self in assignment:
			raise LogicError(f"No matching truth value for proposition in assignment {_assignment_to_str(assignment)}",
							 str(self))
		return assignment[self]

	def _rec_partial_eval(self, assignment: Assignment) -> AtomicProposition:
		if self in assignment:
			return Top if assignment[self] else Bottom
		else:
			return self

	def is_sub_proposition(self, other: Proposition) -> bool:
		return self is other

	def copy(self) -> AtomicProposition:
		return AtomicProposition()

	def __hash__(self) -> int:
		return hash((self._id, self._connective))

	def connective_format(self, *,
						  conn_format: ConnectiveFormat,
						  parent: Optional[Proposition] = None) -> str:
		if conn_format == self._limboole_format:
			name = self._volatile_name.replace(self._prime, "-prime")
		elif conn_format == self._latex_format:
			name = self._volatile_name.replace(self._prime, r"\prime")
		else:
			name = self._volatile_name
		return conn_format.format(name, connective=self._connective)

	def __repr__(self) -> str:
		return repr_str(self, AtomicProposition.volatile_name, AtomicProposition.id)

class __SingletonPropositionMeta(SingletonMeta, _ProtocolMeta, abc.ABCMeta):
	"""
	:py:class:`__SingleTonPropositionMeta` is a meta class for the truth constant propositions :py:class:`_Top`, and
	:py:class:`_Bottom`.
	"""
	pass

@final
class _Top(AtomicProposition, Singleton, metaclass=__SingletonPropositionMeta):

	def __init__(self):
		self._id = self._next_id(1)
		self._volatile_name = "top"
		super(AtomicProposition, self).__init__(self, connective=LogicalConnective.NONE)

	def eval(self, assignment: Assignment) -> True:
		self._check_assignment(assignment)
		return True

	def _rec_partial_eval(self, assignment: Assignment) -> AtomicProposition:
		return Top

	def connective_format(self, *,
						  conn_format: ConnectiveFormat,
						  parent: Optional[Proposition] = None) -> str:
		if conn_format == self._limboole_format:
			name = "(top | !top)"
		elif conn_format == self._pretty_print_format:
			name = "\u22A4"
		elif conn_format == self._latex_format:
			name = r"\top"
		else:
			name = self._volatile_name
		return conn_format.format(name, connective=self._connective)

	def __repr__(self) -> str:
		return "Top"

@final
class _Bottom(AtomicProposition, Singleton, metaclass=__SingletonPropositionMeta):

	def __init__(self):
		self._id = self._next_id(0)
		self._volatile_name = "bottom"
		super(AtomicProposition, self).__init__(self, connective=LogicalConnective.NONE)

	def eval(self, assignment: Assignment) -> False:
		self._check_assignment(assignment)
		return False

	def _rec_partial_eval(self, assignment: Assignment) -> AtomicProposition:
		return Bottom

	def connective_format(self, *,
						  conn_format: ConnectiveFormat,
						  parent: Optional[Proposition] = None) -> str:
		if conn_format == self._limboole_format:
			name = "(bottom & !bottom)"
		elif conn_format == self._pretty_print_format:
			name = "\u22A5"
		elif conn_format == self._latex_format:
			name = r"\bot"
		else:
			name = self._volatile_name
		return conn_format.format(name, connective=self._connective)

	def __repr__(self) -> str:
		return "Bottom"

# special Top and Bottom objects
Top: Final[_Top] = _Top()
""" The singleton object representing the truth value ``True``. """
Bottom: Final[_Bottom] = _Bottom()
""" The singleton object representing the truth value ``False``. """

# type aliases
Assignment: Final = Mapping[AtomicProposition, bool]
""" A type alias for a mapping of :py:class:`AtomicProposition` objects to a ``bool`` truth value. """

_PropositionType: Final = TypeVar("_PropositionType", Proposition, SupportsToPrettyPrint, SupportsToLimboole)
""" A generic type variable for a proposition which can be turned into a string for e.g. error printing. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def _assignment_to_str(assignment: Assignment):
	return f"{{{', '.join(f'{key!s}: {val!s}' for key, val in assignment.items())}}}"
