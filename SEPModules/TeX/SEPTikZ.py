"""
:Author: Marcel Simader
:Date: 30.06.2021

.. versionadded:: v0.1.2.dev2
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import abc
import math
from enum import Enum
from numbers import Number
from typing import Union, AnyStr, Optional, Collection, Tuple, Final, Dict, Iterator, Literal, TypeVar, Mapping, \
	Callable, Iterable, Sequence, Any, NoReturn, Generic, List

from SEPModules.TeX.SEPTeX import LaTeXEnvironment, LaTeXDocument, LaTeXHandler

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

T: Final = TypeVar("T", bound=Number)
""" Constrained type variable for the :py:mod:`SEPTikZ` module. The type of this variable must be a number. """

TIKZ_VALUE: Final = Union[AnyStr, int, float]
""" Type alias for a TikZ key value. """

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZColor(Generic[T]):
	r"""
	:py:class:`TikZColor` represents an RGB color definition. Each color has a name, either 3 or 4 values and a mode. These
	color instances need to be registered with the TikZPicture instance before they can be used. Multiple colors can share
	the same name but they will be overridden by one another, with the color registered at the most recent time being the
	used version.

	The mode can be one of two values:
		* ``rgb`` for int or float values in the interval [0;1], or
		* ``RGB`` for int values in the interval [0;255]

	Colors of length 3 represent ``RED``, ``GREEN`` and ``BLUE``, while colors with length 4 add an addition ``ALPHA``
	channel at the end.

	Comparisons of two colors will compare the names of each color.

	Various arithmetic operations are implemented for this class. The following syntax is used for all binary arithmetic
	operations (the same also applies for the right-handed arithmetic operations, but in reverse):

	..	math:: \circ \in \left\{ +, -, *, /, //, \%, ** \right\}

	..	math::
		\text{color} \circ \lambda &:\Longleftrightarrow
		\left( \text{r} \circ \lambda, \text{g} \circ \lambda, \text{b} \circ \lambda[, \text{a} \circ \lambda] \right) \\
		\text{color} \circ (x, y, z[, w]) &:\Longleftrightarrow
		\left( \text{r} \circ x, \text{g} \circ y, \text{b} \circ z[, \text{a} \circ w]\right) \\
		\text{color1} \circ \text{color2} &:\Longleftrightarrow
		\text{color1} \circ \left(\text{r}, \text{g}, \text{b}[, \text{a}]\right)_{\text{color2}}

	:param name: the name to register this color instance under
	:param value: the ``RGB[A]`` value of this color
	:param mode: the mode of representing the color
	:param generate_unique_name: keyword-only argument that indicates whether or not the class should automatically
		try to make colors unique by adding parts of the hash to the end of the name, this exists mainly to make arithmetic
		operations on colors easier to handle

	:raise ValueError: if the ``value`` tuple is neither 3 nor 4 values long, or the types of the tuple do not match the
		constraints given by ``mode``
	:raise NotImplementedError: if ``mode`` is not one of the listed literals
	"""

	COLOR_VALUE = Union[Tuple[T, T, T], Tuple[T, T, T, T]]
	""" Shorthand for a tuple of either 3 or 4 :py:attr:`T`. """

	def __init__(self,
				 name: AnyStr,
				 value: COLOR_VALUE,
				 mode: Literal["rgb", "RGB"] = "rgb",
				 *,
				 generate_unique_name: bool = False):
		# check constraints
		if mode not in ("rgb", "RGB"):
			raise NotImplementedError(f"Mode {mode} is not known, choose from: rgb, and RGB")

		self._name = str(name)
		self._value = value
		self._mode = mode
		self._generate_unique_name = generate_unique_name

		self.__validate_color_value__(value)

	def __not_implemented__() -> NoReturn:
		raise NotImplementedError("This operation is not supported")

	def __validate_color_value__(self, value: COLOR_VALUE) -> None:
		"""
		Asserts that the input value is either of length 3 or 4, and that the types of all values match the constraints
		of the color mode.
		"""
		if not (len(value) == 3 or len(value) == 4):
			raise ValueError(f"Color value tuple must contain either 3 or 4 values, received {len(value)}")
		type_names = [type(e).__name__ for e in value]
		# check mode adherence
		if self._mode == "rgb" and not all([isinstance(v, (int, float)) for v in value]):
			raise ValueError(f"All color values for mode 'rgb' must be of type int or float, but received {type_names}")
		elif self._mode == "RGB" and not all([isinstance(v, int) for v in value]):
			raise ValueError(f"All color values for mode 'RGB' must be of type int, but received {type_names}")

	@property
	def name(self) -> str:
		""" :return: the name, different from :py:meth:`full_name` and :py:meth:`__str__` since this does not include opacity """
		out = self._name
		if self._generate_unique_name:
			out = out + f"_{abs(hash(self._value))}"[:11]
		return out

	@property
	def value(self) -> COLOR_VALUE:
		return self._value

	@property
	def mode(self) -> str:
		return self._mode

	@property
	def red(self) -> T:
		return self._value[0]

	@property
	def green(self) -> T:
		return self._value[1]

	@property
	def blue(self) -> T:
		return self._value[2]

	@property
	def alpha(self) -> Optional[T]:
		if len(self) <= 3:
			return None
		return self._value[3]

	def add_alpha(self, value: T) -> TikZColor:
		"""
		Adds an alpha channel at opacity ``value`` to this color.

		:param value: the value of the new alpha channel

		:return: the new color with 4 channels, if the color already has 4 channels this function will return the
			original color
		"""
		if not len(self) >= 4:
			new_values = (self.red, self.green, self.blue, value)
			# check if input is legal
			self.__validate_color_value__(new_values)
			# return new color
			return TikZColor(self._name,
							 new_values,
							 self._mode,
							 generate_unique_name=self._generate_unique_name)
		else:
			return self

	def remove_alpha(self) -> TikZColor:
		"""
		Removes the alpha channel of this color.

		:return: the new color with 3 channels, if the color already had 3 channels this function will return the
			original color
		"""
		if not len(self) <= 3:
			return TikZColor(self._name,
							 (self.red, self.green, self.blue),
							 self._mode,
							 generate_unique_name=self._generate_unique_name)
		else:
			return self

	def __binary_operation__(self, other: Union[T, TikZColor, COLOR_VALUE], operator: Callable[[T, T], T]) -> TikZColor:
		"""
		Applies ``operator`` as binary operator to ``self`` and ``other``. If the other input is not a color, then the
		newly generated color will automatically have ``generate_unique_name`` set to ``True``.

		:param other: the value to use on the right hand side of the operator
		:param operator: the operator to apply to the values

		:return: a new :py:class:`TikzColor` instance holding the result of the operation
		:raise ValueError: if the length of ``other`` is not 1 or does not match the length of ``self``, or if the given
			values in ``other`` are not ints or floats greater than or equal to 0
		"""
		# handle other is color
		if isinstance(other, TikZColor):
			generate_unique_name = self._generate_unique_name or other._generate_unique_name
			other = other._value
		else:
			generate_unique_name = True

		# handle other is number
		if not isinstance(other, Sequence):
			other = (other,)
		if len(other) == 1:
			other = other * len(self)
		elif len(other) != len(self):
			raise ValueError(
					f"Other value of binary operator must be a tuple of the same length as {repr(self)} ({len(self)}), "
					f"but received length {len(other)}")
		if not all([isinstance(v, (int, float)) and v >= 0 for v in other]):
			raise ValueError(
					f"All values of other must be a float greater than or equal to 0 but received {other} of types "
					f"{[o.__class__.__name__ for o in other]}")

		# convert to int if needed
		if self._mode == "RGB":
			_operator = lambda a, b: min(max(int(operator(a, b)), 0), 255)
		elif self._mode == "rgb":
			_operator = lambda a, b: min(max(operator(a, b), 0), 1)
		else:
			raise NotImplementedError("This operation is not supported")

		# compute operation and return color
		if len(self) <= 3:
			return TikZColor(self._name,
							 (_operator(self._value[0], other[0]), _operator(self._value[1], other[1]),
							  _operator(self._value[2], other[2])),
							 self._mode,
							 generate_unique_name=generate_unique_name)
		elif len(self) == 4:
			return TikZColor(self._name,
							 (_operator(self._value[0], other[0]), _operator(self._value[1], other[1]),
							  _operator(self._value[2], other[2]), _operator(self._value[3], other[3])),
							 self._mode,
							 generate_unique_name=generate_unique_name)
		else:
			raise NotImplementedError("This operation is not supported")

	# arithmetic operations
	def __add__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a + b)

	def __sub__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a - b)

	def __mul__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a * b)

	def __truediv__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a / b)

	def __floordiv__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a // b)

	def __mod__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a % b)

	def __pow__(self, power: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(power, lambda a, b: a ** b)

	# "right" arithmetic operations
	def __radd__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b + a)

	def __rsub__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b - a)

	def __rmul__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b * a)

	def __rtruediv__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b / a)

	def __rfloordiv__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b // a)

	def __rmod__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b % a)

	def __rpow__(self, other: Union[T, TikZColor, COLOR_VALUE]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b ** a)

	def __len__(self) -> int:
		return len(self._value)

	def __hash__(self):
		return hash(self._name)

	def __eq__(self, other):
		return isinstance(other, TikZColor) and self._name == other._name

	def __str__(self) -> str:
		if len(self) >= 4:
			if self._mode == "rgb":
				alpha = self.alpha
			elif self._mode == "RGB":
				alpha = self.alpha / 255
			else:
				raise NotImplementedError("This operation is not supported")
			return f"{self.name}!{int(alpha * 100)}"
		else:
			return self.name

	def __repr__(self) -> str:
		return f"TikZColor(name={self.name}, value={self._value}, mode={self._mode})"

	@property
	def full_name(self) -> str:
		""" :return: a string containing the ``xcolor`` name to be used in a LaTeX document, alias for :py:meth:`__str__` """
		return str(self)

	@property
	def definition(self) -> str:
		""" :return: a string containing the ``xcolor`` definition of this color for the preamble of a LaTeX document """
		return f"\\definecolor{{{self.name}}}{{{self._mode}}}{{{self.red}, {self.green}, {self.blue}}}"

# ~~~~~~~~~~~~~~~ DEFAULT COLORS ~~~~~~~~~~~~~~~

WHITE: Final = TikZColor("WHITE", (255, 255, 255), "RGB")
LIGHT_GRAY: Final = TikZColor("LIGHT_GRAY", (180, 180, 180), "RGB")
DARK_GRAY: Final = TikZColor("DARK_GRAY", (45, 45, 45), "RGB")
BLACK: Final = TikZColor("BLACK", (0, 0, 0), "RGB")
ALMOST_WHITE: Final = TikZColor("ALMOST_WHITE", (245, 245, 245), "RGB")
ALMOST_BLACK: Final = TikZColor("ALMOST_BLACK", (18, 18, 18), "RGB")
RED: Final = TikZColor("RED", (252, 68, 68), "RGB")
ORANGE: Final = TikZColor("ORANGE", (255, 165, 0), "RGB")
YELLOW: Final = TikZColor("YELLOW", (251, 219, 4), "RGB")
GREEN: Final = TikZColor("GREEN", (139, 195, 74), "RGB")
LIGHT_BLUE: Final = TikZColor("LIGHT_BLUE", (3, 169, 244), "RGB")
DARK_BLUE: Final = TikZColor("DARK_BLUE", (4, 60, 140), "RGB")
PURPLE: Final = TikZColor("PURPLE", (103, 58, 183), "RGB")
MAGENTA: Final = TikZColor("MAGENTA", (156, 39, 176), "RGB")
PINK: Final = TikZColor("PINK", (236, 76, 140), "RGB")
ROSE: Final = TikZColor("ROSE", (252, 140, 132), "RGB")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ WRITEABLE ABC ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZWriteable(abc.ABC):
	"""
	Abstract base class for all TikZ objects which can be written to a :py:class:`.LaTeXHandler`. This class requires all
	subclasses to implement the :py:meth:`__str__` method, because this method will be called when writing this instance
	to a handler.

	:param required_packages: a collection of the names of the packages which are required to use a subclass of this class
	:param required_tikz_libraries: a collection of the names of the TikZ libraries which are required to use a subclass
		of this class
	"""

	def __init__(self,
				 required_packages: Collection[AnyStr],
				 required_tikz_libraries: Collection[AnyStr]):
		self._required_packages = list(required_packages)
		self._required_tikz_libraries = list(required_tikz_libraries)

	def register_required_package(self, *package: AnyStr) -> None:
		""" Register a required package or packages with this instance. """
		if not isinstance(package, Tuple):
			package = (package,)
		self._required_packages.extend(package)

	def register_required_tikz_library(self, *library: AnyStr) -> None:
		""" Register a required TikZ library or libraries with this instance. """
		if not isinstance(library, Tuple):
			library = (library,)
		self._required_tikz_libraries.extend(library)

	@property
	def required_packages(self) -> Tuple[AnyStr]:
		""" :return: the packages required to use this class in a document """
		return tuple(self._required_packages)

	@property
	def required_tikz_libraries(self) -> Tuple[AnyStr]:
		""" :return: the TikZ libraries required to use this class in a document """
		return tuple(self._required_tikz_libraries)

	@abc.abstractmethod
	def __str__(self) -> str:
		pass

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ POINT ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Point(TikZWriteable, Generic[T]):
	r"""
	:py:class:`Point` represented a 2 dimensional coordinate of form :math:`(x, y)`. The class additionally holds information
	on the unit used for the values ``T``. Various arithmetic operations upon two points are supported, but only if they
	share the **same unit**.

	To perform the vector dot product on two points, use the "matrix-mul" operator ``@``.

	:param x: the x-coordinate
	:param y: the y-coordinate
	:param unit: keyword-only argument, denotes the unit to suffix at the end of the :py:class:`Point` instance, is
	 	**automatically converted to all lower case**, for instance ``Point(3, 4, unit="CM")`` will produce the output
	 	 ``( 3.000cm,  4.000cm)``
	"""

	POINT_TEMPLATE: Final = r"({: .3f}{unit}, {: .3f}{unit})"
	""" The format string to use when formatting a point to a string. """

	def __init__(self, x: T, y: T, *, unit: AnyStr = ""):
		super(Point, self).__init__((), ())
		self._x = x
		self._y = y
		self._unit = unit.lower()

	@property
	def x(self) -> T:
		r""" :return: the x coordinate """
		return self._x

	@property
	def y(self) -> T:
		r""" :return: the y coordinate """
		return self._y

	@property
	def point(self) -> Tuple[T, T]:
		r""" :return: the tuple :math:`(x, y)` """
		return self._x, self._y

	@property
	def unit(self) -> AnyStr:
		r""" :return: the all lower-case unit suffix """
		return self._unit

	# arithmetic
	def __other_as_tuple__(self, other: Union[T, Point, Tuple[T, T]], check_unit: bool = False) -> Tuple[T, T]:
		if isinstance(other, Point):
			if check_unit:
				self.__require_same_unit__(other)
			other = other.point
		if not isinstance(other, Tuple):
			other = (other,) * 2
		return other

	def __require_same_unit__(self, other: Point) -> None:
		if not self._unit == other._unit:
			raise ValueError(f"Cannot perform arithmetic operation on points of two different units, "
							 f"given '{self._unit}' and '{other._unit}'")

	def __require_non_zero__(self, other: Union[T, Point, Tuple[T, T]], msg: AnyStr) -> None:
		other = self.__other_as_tuple__(other)
		if any([n == 0 for n in other]):
			raise ZeroDivisionError(f"None of the components of {repr(other)} can be 0 for performing {msg}")

	def __binary_operation__(self, other: Union[T, Point, Tuple[T, T]], operator: Callable[[T, T], T]) -> Point:
		other = self.__other_as_tuple__(other, check_unit=True)
		return Point(operator(self._x, other[0]), operator(self._y, other[1]), unit=self._unit)

	def __add__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: a + b)

	def __sub__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: a - b)

	def __mul__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: a * b)

	def __truediv__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		self.__require_non_zero__(other, "division")
		return self.__binary_operation__(other, lambda a, b: a / b)

	def __floordiv__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		self.__require_non_zero__(other, "floor division")
		return self.__binary_operation__(other, lambda a, b: a // b)

	def __mod__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		self.__require_non_zero__(other, "modulo")
		return self.__binary_operation__(other, lambda a, b: a % b)

	def __pow__(self, power: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(power, lambda a, b: a ** b)

	def __matmul__(self, other: Point) -> float:
		self.__require_same_unit__(other)
		return self._x * other._x + self._y * other._y

	# "right" arithmetic operations
	def __radd__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: b + a)

	def __rsub__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: b - a)

	def __rmul__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: b * a)

	def __rtruediv__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		self.__require_non_zero__(self, "division")
		return self.__binary_operation__(other, lambda a, b: b / a)

	def __rfloordiv__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		self.__require_non_zero__(self, "floor division")
		return self.__binary_operation__(other, lambda a, b: b // a)

	def __rmod__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		self.__require_non_zero__(self, "modulo")
		return self.__binary_operation__(other, lambda a, b: b % a)

	def __rpow__(self, other: Union[T, Point, Tuple[T, T]]) -> Point:
		return self.__binary_operation__(other, lambda a, b: b ** a)

	def __rmatmul__(self, other: Point) -> float:
		self.__require_same_unit__(other)
		return self._x * other._x + self._y * other._y

	# misc operations
	def as_int(self) -> Point[int]:
		r""" :return: a new point :math:`(\text{int}(x), \text{int}(y))` """
		return Point(int(self._x), int(self._y), unit=self.unit)

	def as_float(self) -> Point[float]:
		r""" :return: a new point :math:`(\text{float}(x), \text{float}(y))` """
		return Point(float(self._x), float(self._y), unit=self.unit)

	def __neg__(self) -> Point[T]:
		r""" :return: a new point :math:`((-1) * x, (-1) * y)` """
		return Point(-self._x, -self._y, unit=self.unit)

	def __abs__(self) -> Point[T]:
		r""" :return: a new point :math:`(\text{abs}(x), \text{abs}(y))` """
		return Point(abs(self._x), abs(self._y), unit=self.unit)

	def geometric_length(self) -> float:
		r""" :return: the geometric length of this point to the origin :math:`\vec 0` """
		return math.sqrt(self._x ** 2 + self._y ** 2)

	def __hash__(self) -> int:
		return hash((self._x, self._y, self._unit))

	def __eq__(self, other) -> bool:
		if not isinstance(other, Point):
			return False
		return (self._unit == other._unit) and (self._x == other._x) and (self._y == other._y)

	# str operations
	def __repr__(self) -> str:
		return f"Point({self._x}, {self._y}{'' if self._unit == '' else f', unit={self._unit}'})"

	def __str__(self) -> str:
		return self.POINT_TEMPLATE.format(self._x, self._y, unit=self._unit)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ ARROWS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class _TikZArrow(Enum):
	"""
	:py:class:`_TikZArrow` is the baseclass enumeration for holding TikZ arrow head type data.

	:param key: the TikZ key for this arrow head type (e.g. ``->``)
	"""

	def _generate_next_value_(name, start, count, last_values) -> int:
		if last_values is None:
			return 0
		else:
			return last_values + 1

	def __init__(self, key: str):
		super(_TikZArrow, self).__init__()
		# check types
		if not isinstance(key, str):
			raise TypeError(f"TikZArrow enum entries must be of shape 'TikZ value key' with type 'str', "
							f"found type {key.__class__.__name__}")
		self._key = key

	@property
	def key(self) -> str:
		""" :return: the TikZ key for this arrow head type """
		return self._key

class TikZArrow(_TikZArrow):
	"""
	:py:class:`TikZArrow` is an enumeration of TikZ arrow head types.
	"""

	LINE: Final = "-"

	LEFT: Final = "<-"
	RIGHT: Final = "->"
	LEFT_RIGHT: Final = "<->"
	IN_LEFT: Final = ">-"
	IN_RIGHT: Final = "-<"
	IN_LEFT_RIGHT: Final = ">-<"

	LEFT_STUMP: Final = "|-"
	RIGHT_STUMP: Final = "-|"
	LEFT_RIGHT_STUMP: Final = "|-|"

	LEFT_LATEX: Final = "latex-"
	RIGHT_LATEX: Final = "-latex"
	LEFT_RIGHT_LATEX: Final = "latex-latex"
	LEFT_LATEX_PRIME: Final = "latex'-"
	RIGHT_LATEX_PRIME: Final = "-latex'"
	LEFT_RIGHT_LATEX_PRIME: Final = "latex'-latex'"

	LEFT_CIRC: Final = "o-"
	RIGHT_CIRC: Final = "-o"
	LEFT_RIGHT_CIRC: Final = "o-o"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ STYLE AND STYLED ABC ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZStyle:
	r"""
	:py:class:`TikZStyle` holds information about what styles to apply to a TikZ object. This class implements a container,
	and the :py:meth:`__getitem__` and :py:meth:`__getattribute__` methods. A style can be accessed using the following
	ways:

	>>> scale_style = TikZStyle(x_scale="2cm")
	>>> assert scale_style.x_scale == "2cm"
	>>> assert scale_style["x_scale"] == "2cm"
	>>> assert scale_style["x scale"] == "2cm"
	>>> assert scale_style["x-scale"] == "2cm"
	>>> assert scale_style.style["x scale"] == "2cm" # space is needed here! this use is discouraged

	Additionally, some methods of this instance will ignore None values:

	>>> draw_style = TikZStyle(draw=True)
	>>> assert len(draw_style) == 1 # all other values are None
	>>> assert "y_scale" not in draw_style
	>>> assert "draw" in draw_style

	One can either iterate over the non-None values of this instance, or call the :py:meth:`__str__` method:

	>>> multiple_style = TikZStyle(width="1cm", draw=True)
	>>> for s in multiple_style:
	...		print(s)
	('width', '1cm')
	('draw', True)
	>>> print(str(multiple_style))
	draw, width={1cm}

	:param custom_entries: an optional mapping of any entries not included in the keyword arguments
	"""

	DICT_ENTRY: Final = str, Optional[Union[AnyStr, bool, int, float]]
	""" The types of a dictionary entry of the styles dictionary. """

	# This tuple is purely used to define the style properties so that IDEs and other tools can find and suggest them
	__slots__ = ("width", "height", "x_scale", "y_scale", "scale", "shift", "draw", "dashed",
				 "dotted", "line_width", "color", "fill", "draw_opacity", "fill_opacity",
				 "bend_left", "bend_right", "circle",
				 "__dict__")

	def __init__(self,
				 custom_entries: Optional[Mapping[DICT_ENTRY]] = None,
				 *,
				 width: Optional[TIKZ_VALUE] = None,
				 height: Optional[TIKZ_VALUE] = None,
				 x_scale: Optional[TIKZ_VALUE] = None,
				 y_scale: Optional[TIKZ_VALUE] = None,
				 scale: Optional[TIKZ_VALUE] = None,
				 shift: Optional[Tuple[TIKZ_VALUE, TIKZ_VALUE]] = None,

				 bend_left: Optional[Union[bool, TIKZ_VALUE]] = None,
				 bend_right: Optional[Union[bool, TIKZ_VALUE]] = None,

				 draw: Optional[bool] = True,
				 circle: Optional[bool] = None,

				 dashed: Optional[bool] = None,
				 dotted: Optional[bool] = None,
				 line_width: Optional[TIKZ_VALUE] = None,
				 color: Optional[TikZColor] = None,
				 fill: Optional[TikZColor] = None,

				 draw_opacity: Optional[float] = None,
				 fill_opacity: Optional[float] = None):
		# register styles
		self._style = {
				"width"       : width,
				"height"      : height,
				"x scale"     : x_scale,
				"y scale"     : y_scale,
				"scale"       : scale,
				"shift"       : None if shift is None else f"({shift[0]}, {shift[1]})",

				"bend left"   : bend_left,
				"bend right"  : bend_right,

				"draw"        : draw,
				"circle"      : circle,

				"dashed"      : dashed,
				"dotted"      : dotted,
				"line width"  : line_width,
				"color"       : color,
				"fill"        : fill,

				"draw opacity": draw_opacity,
				"fill opacity": fill_opacity
				}

		# extend registered styles with custom styles
		if custom_entries is not None:
			self._style.update(custom_entries)

		# register all used colors
		self._colors = (color, fill)

	@staticmethod
	def normalize_key(s: str) -> str:
		""" Removes any underscores or hyphens and replaces them with spaces. """
		return s.replace("_", " ").replace("-", " ")

	@property
	def style(self) -> Dict[DICT_ENTRY]:
		""" :return: a deep copy of the styles stored in this instance """
		return dict(self._style)

	@property
	def colors(self) -> Collection[TikZColor]:
		""" :return: a copy of the colors used in this instance, removes ``None`` values """
		return tuple([x for x in self._colors if x is not None])

	def __len__(self) -> int:
		return len([1 for s in self._style.values() if s is not None])

	def __contains__(self, item) -> bool:
		key = self.normalize_key(str(item))
		return key in self._style and self._style[key] is not None

	def __iter__(self) -> Iterator[Tuple[DICT_ENTRY]]:
		for key, value in self._style.items():
			if value is not None:
				yield key, value

	def __setitem__(self, key, value) -> NoReturn:
		raise SyntaxError(f"Cannot assign to attribute {key} of TikZStyle, this class is immutable")

	def __getitem__(self, item) -> DICT_ENTRY[1]:
		return self._style[self.normalize_key(str(item))]

	def __getattr__(self, item) -> Any:
		s_item = self.normalize_key(str(item))
		if s_item in self._style:
			# get style
			return self._style[s_item]

	def __repr__(self) -> str:
		return f"TikZStyle({', '.join([f'{key}={value}' for key, value in self])})"

	def __str__(self) -> str:
		out_string = str()

		# empty string without brackets
		if len(self) <= 0:
			return out_string

		# process normal items and flags (bool) separately
		style_strings = [f"{key}={{{value}}}" for key, value in self if not isinstance(value, bool)]
		style_flags = [f"{key}" for key, value in self if isinstance(value, bool) and value]

		return ", ".join(style_flags + style_strings)

class TikZStyled(TikZWriteable, abc.ABC):
	"""
	Abstract base class adding additional style attributes to :py:class:`TikZWriteable`. This class separately enforces
	a property for the style and for the colors used by an instance. This is done so the colors may be registered by the
	document.

	..	note::

		This baseclass will automatically register ``xcolor`` as required package.

	:param required_packages: a collection of the names of the packages which are required to use a subclass of this class
	:param required_tikz_libraries: a collection of the names of the TikZ libraries which are required to use a subclass
		of this class
	:param style: the style to be attached to the instance of this class
	"""

	def __init__(self,
				 required_packages: Collection[AnyStr],
				 required_tikz_libraries: Collection[AnyStr],
				 style: TikZStyle):
		super(TikZStyled, self).__init__(required_packages, required_tikz_libraries)
		self.register_required_package("xcolor")

		self._style = style
		self._colors = style.colors

	@property
	def colors(self) -> Collection[TikZColor]:
		""" The colors used by the style of this instance. """
		return self._colors

	@property
	def style(self) -> TikZStyle:
		""" The style used by this instance. """
		return self._style

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ NODE AND NODED ABC ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZNode(TikZStyled):
	"""
	:py:class:`TikZNode` represents a standard TikZ node. It holds information about its coordinate, name, label and style.
	A node must first be registered with a :py:class:`TikZPicture` instance by writing it, which happens implicitly if not
	stated explicitly.

	Comparisons of node objects will compare the names of each node.

	:param coordinate: the coordinate at which this node should be placed
	:param label: the label which will be displayed on the document for this node
	:param name: the name which will be used to reference this node
	:param style: the style to apply to this node
	"""

	def __init__(self,
				 coordinate: Point,
				 label: AnyStr = "",
				 name: AnyStr = "",
				 style: TikZStyle = TikZStyle()):
		super(TikZNode, self).__init__((), (), style=style)

		self._coordinate = coordinate
		self._label = str(label)
		self._name = str(name)

	@property
	def coordinate(self) -> Point:
		""" :return: the coordinate of this node """
		return self._coordinate

	@property
	def label(self) -> str:
		""" :return: the label of this node """
		return self._label

	@property
	def name(self) -> str:
		""" :return: the name of this node """
		return self._name

	@property
	def draw_command(self) -> str:
		"""
		The command to draw the node in the document on its own. This is the standard when the node is written directly
		to a :py:class:`TikZPicture` instance. This method is equivalent to :py:meth:`__str__`.

		:return: the draw command for this node
		"""
		return f"\\node[{str(self._style)}]{'' if self._name == '' else f' ({self._name})'}" \
			   f" at {str(self._coordinate)} {{{self._label}}}"

	def __hash__(self):
		return hash(self._name)

	def __eq__(self, other):
		return isinstance(other, TikZNode) and self._name == other._name

	def __str__(self) -> str:
		return self.draw_command

	def __repr__(self) -> str:
		return f"TikZNode(coordinate={repr(self._coordinate)}," \
			   f"{'' if self._name == '' else f' name={self._name},'}" \
			   f" label={self._label})"

class TikZNoded(TikZStyled, abc.ABC):
	"""
	Abstract base class for marking a subclass as using :py:class:`TikZNode` objects. This class must be inherited from
	in order for the :py:class:`TikZPicture` class to be able to register and define the nodes.

	:param required_packages: a collection of the names of the packages which are required to use a subclass of this class
	:param required_tikz_libraries: a collection of the names of the TikZ libraries which are required to use a subclass
		of this class
	:param nodes: the nodes to be attached to the instance of this class
	:param style: the style to be attached to the instance of this class
	"""

	def __init__(self,
				 required_packages: Collection[AnyStr],
				 required_tikz_libraries: Collection[AnyStr],
				 style: TikZStyle,
				 nodes: Collection[TikZNode]):
		super(TikZNoded, self).__init__(required_packages, required_tikz_libraries, style)

		self._nodes = nodes

	@property
	def nodes(self) -> Tuple[TikZNode]:
		""" :retrn: the nodes used by this instance """
		return tuple(self._nodes)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CONCRETE TIKZ OBJECTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZPath(TikZNoded):
	r"""
	:py:class:`TikZPath` represents a collection of coordinates and nodes drawn using the ``\draw`` command of TikZ.

	:param coordinates: a collection of :py:class:`Point` or :py:class:`TikZNode` objects for the path
	:param cycle: whether or not to end the final path string with ``cycle``, which will join the ending to the beginning
	:param style: the style to apply to this path
	"""

	_COORDINATE_JOINER = r" -- "
	r""" The symbol to use between the coordinates in the ``\draw`` command. """

	def __init__(self,
				 coordinates: Collection[Union[Point, TikZNode]],
				 cycle: bool = False,
				 style: TikZStyle = TikZStyle()):
		super(TikZPath, self).__init__((), (),
									   style=style,
									   nodes=[n for n in coordinates if isinstance(n, TikZNode)])

		self._coordinates = tuple(coordinates)
		self._coordinates_string = None
		self._cycle = cycle

	@property
	def coordinates_string(self) -> str:
		"""
		Converts all of the coordinates of this instance to a string. If there are no coordinates then the empty string
		will be returned.
		"""
		if self._coordinates_string is None:
			if len(self._coordinates) <= 0:
				self._coordinates_string = str()
			else:
				coords = [f"({c.name})" if isinstance(c, TikZNode) else str(c) for c in self._coordinates]
				self._coordinates_string = self._COORDINATE_JOINER.join(coords)
		return self._coordinates_string

	@property
	def coordinates(self) -> Tuple[Union[Point, TikZNode]]:
		""" :return: the coordinates and nodes along this path """
		return self._coordinates

	@property
	def cycle(self) -> bool:
		""" :return: whether or not to join the end of this path to its beginning """
		return self._cycle

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}(coordinates={self._coordinates})"

	def __str__(self) -> str:
		return f"\\draw[{str(self._style)}] {self.coordinates_string}" \
			   f"{f'{self._COORDINATE_JOINER}cycle' if self.cycle else ''}"

class TikZDirectionalPath(TikZPath):
	"""
	:py:class:`TikZDirectionalPath` represents a path similarly to :py:class:`TikZPath` but with additional information
	on the arrow type used to join up the coordinates.

	:param coordinates: a collection of :py:class:`Point` or :py:class:`TikZNode` objects for the path
	:param cycle: whether or not to end the final path string with ``cycle``, which will join the ending to the beginning
	:param style: the style to apply to this path
	:param arrow_type: the :py:class:`TikZArrow` to use for the arrow tip of the edge
	"""

	_COORDINATE_JOINER = r" to "
	r""" The symbol to use between the coordinates in the ``\draw`` command. """

	def __init__(self,
				 coordinates: Collection[Union[Point, TikZNode]],
				 cycle: bool = False,
				 style: TikZStyle = TikZStyle(),
				 arrow_type: TikZArrow = TikZArrow.LINE):
		super(TikZDirectionalPath, self).__init__(coordinates, cycle, style)
		self.register_required_tikz_library("arrows")

		self._arrow_type = arrow_type

	@property
	def arrow_type(self) -> TikZArrow:
		""" :return: which arrow head type to use at the end of this path """
		return self._arrow_type

	def __str__(self) -> str:
		style_list = [x for x in (self._arrow_type.key, str(self._style)) if len(x) > 0]
		return f"\\draw[{', '.join(style_list)}] {self.coordinates_string}" \
			   f"{f'{self._COORDINATE_JOINER}cycle' if self.cycle else ''}"

class TikZCircle(TikZStyled):
	"""
	:py:class:`TikZCircle` represents a standard TikZ circle, with a center coordinate, radius and style.

	:param coordinate: the center coordinate of the circle
	:param radius: the radius of the circle
	:param style: the style of the circle
	"""

	def __init__(self,
				 coordinate: Point,
				 radius: TIKZ_VALUE,
				 style: TikZStyle):
		super(TikZCircle, self).__init__((), (), style)

		self._coordinate = coordinate
		self._radius = radius

	@property
	def coordinate(self) -> Point:
		""" :return: the center coordinate of this circle """
		return self._coordinate

	@property
	def radius(self) -> TIKZ_VALUE:
		""" :return: the radius of this circle """
		return self._radius

	def __str__(self) -> str:
		return f"\\draw[{str(self._style)}] {str(self._coordinate)} circle ({self._radius})"

	def __repr__(self) -> str:
		return f"TikZCircle(coordinate={repr(self._coordinate)}, radius={self._radius})"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ MAIN TIKZ ENV ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZPicture(LaTeXEnvironment):
	r"""
	:py:class:`TikZPicture` represents the standard TikZ ``tikzpicture`` environment. This class aids in registering colors,
	and writing special TikZ objects to the document.

	..	warning::

		When a :py:class:`TikZNoded` object registers its used nodes implicitly with this class, the nodes will be reused
		if a node with matching name is found. Furthermore, the saved list of node objects cannot be passed on or inherited
		to other :py:class:`TikZPicture` or :py:class:`TikZScope` environments. This is done so each "namespace" stays free
		of node pollution.

		This is similar to how :py:class:`TikZColor` objects behave with this class, with the key difference being that
		colors **can** be passed on to other :py:class:`TikZPicture` environments, and are implicitly passed on to child
		:py:class:`TikZScope` environments.

	:param parent_env: the parent environment or document to this environment
	:param style: the main style to use for this environment
	:param defined_colors: any colors which have already been defined in the document and are accessible from within this
		environment, this option is useful if there are manually defined colors or multiple tikzpicture environments in
		the document
	:param indent_level: the number of tab characters to indent this environment relative to the parent environment
	"""

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 style: TikZStyle = TikZStyle(),
				 defined_colors: Collection[TikZColor] = (),
				 indent_level: int = 1):
		super(TikZPicture, self).__init__(parent_env,
										  environment_name="tikzpicture",
										  options=str(style),
										  required_packages=("tikz",),
										  indent_level=indent_level)

		self.__tikz_init__(defined_colors, indent_level)

	def __tikz_init__(self, defined_colors: Collection[TikZColor], indent_level: int):
		""" Initialize this environment. This function should be called by subclasses which do not call the super constructor. """
		self._seen_tikz_writeable_types = list()
		self._defined_colors: List[TikZColor] = list(defined_colors)
		self._defined_nodes: List[TikZNode] = list()
		self._definition_handler = LaTeXHandler(indent_level)

	@property
	def defined_colors(self) -> Tuple[TikZColor]:
		"""
		:return: the colors which have so far been defined by this environment, or have been passed to this environment
			at construction
		"""
		return tuple(self._defined_colors)

	@property
	def defined_nodes(self) -> Tuple[TikZNode]:
		""" :return: the nodes which have been written to this environment """
		return tuple(self._defined_nodes)

	def define_color(self, *color: TikZColor) -> None:
		"""
		Register one or multiple colors with this instance. This will define the color at the beginning of the environment.

		:param color: the color or colors to define
		"""
		if not isinstance(color, Iterable):
			color = (color,)
		# define color and register as seen
		for c in color:
			if c not in self._defined_colors:
				self._definition_handler.write(c.definition)
				self._defined_colors.append(c)

	def write(self, s: Union[TikZWriteable, AnyStr]) -> None:
		"""
		Write ``s`` to the handler of this instance.

		The following conditions apply to special obejct types:
			-	If ``s`` is a string this method will simply write it.

			-	If ``s`` is a :py:class:`TikZWriteable` object this method will first register the required packages, then
			 	the required TikZ libraries, then call the ``__str__`` method of the object, and finally add ``;`` to the
			 	end if it is missing.

				-	If ``s`` is additionally a :py:class:`TikZStyled` object this method will register the required colors
				 	if they have not been passed to this instance, or written with the same name before.
				-	If ``s`` is additionally a :py:class:`TikZNoded` object this method will write the required node objects
				 	if they have not been written with the same name before.

		:param s: the object to write to the handler
		"""
		if isinstance(s, TikZWriteable):
			# +++ get required packages of object and register as seen only once per class +++
			if not type(s) in self._seen_tikz_writeable_types:
				# register packages
				self.document.use_package(*s.required_packages)
				# register tikz libraries
				self.document.use_tikz_library(*s.required_tikz_libraries)
				# mark as seen
				self._seen_tikz_writeable_types.append(type(s))

			# +++ we are doing this regardless of if we have seen the class itself before +++
			# register colors if styled
			if isinstance(s, TikZStyled):
				self.define_color(*s.colors)
			# register nodes if noded
			if isinstance(s, TikZNoded):
				for n in s.nodes:
					self.write(n)

			# skip node if this exact object has been seen before
			if isinstance(s, TikZNode):
				if s in self._defined_nodes:
					return
				else:
					self._defined_nodes.append(s)

			# draw call
			s = str(s)
			if not s.endswith(";"):
				s += ";"

		super(TikZPicture, self).write(s)

	def __exit__(self, exc_type, exc_val, exc_tb):
		# write color handler to parent
		if len(self._definition_handler) > 0:
			self.parent_handler.write(self._definition_handler)
		# super call
		return super(TikZPicture, self).__exit__(exc_type, exc_val, exc_tb)

class TikZScope(TikZPicture):
	"""
	:py:class:`TikZScope` represents the standard TikZ ``scope`` environment. It can only be instantiated with a parent
	environment inheriting from :py:class:`TikZPicture`.

	:param parent_env: the parent environment or document to this environment
	:param style: the main style to use for this environment
	:param indent_level: the number of tab characters to indent this environment relative to the parent environment

	:raise TypeError: if the passed ``parent_env`` is not an instance of a :py:class:`TikZPicture` class
	"""

	def __init__(self,
				 parent_env: TikZPicture,
				 style: TikZStyle = TikZStyle(),
				 indent_level: int = 1):
		# make sure we are in a tikz picture env
		if not isinstance(parent_env, TikZPicture):
			raise TypeError(
					f"TikZScope must be nested within the context manager of a TikZPicture environment or a subclass of it, "
					f"but received {parent_env.__class__.__name__}")

		super(TikZPicture, self).__init__(parent_env,
										  environment_name="scope",
										  options=str(style),
										  required_packages=("tikz",),
										  indent_level=indent_level)
		self.__tikz_init__(parent_env.defined_colors, indent_level)
