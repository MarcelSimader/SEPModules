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
from numbers import Number
from typing import Union, AnyStr, Optional, Collection, Tuple, Final, Dict, Iterator, Literal, TypeVar, Mapping, \
	Callable, Iterable, Sequence, Any, NoReturn

from SEPModules.TeX.SEPTeX import LaTeXEnvironment, LaTeXDocument, LaTeXHandler

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZColor:
	"""
	:py:class:`TikZColor` represents an RGB color definition. Each color has a name, either 3 or 4 values and a mode. These
	color instances need to be registered with the TikZPicture instance before they can be used. Multiple colors can share
	the same name but they will be overridden by one another, with the color registered at the most recent time being the
	used version.

	The mode can be one of two values:
		* ``rgb`` for int or float values in the interval [0;1], or
		* ``RGB`` for int values in the interval [0;255]

	Colors of length 3 represent ``RED``, ``GREEN`` and ``BLUE``, while colors with length 4 add an addition ``ALPHA``
	channel at the end.

	Various arithmetic operations are implemented for this class. The syntax # TODO finish this

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

	T = TypeVar("T", int, float)
	""" The type variable used for channels of the color value. Must be int or float. """
	ColorValue = Union[Tuple[T, T, T], Tuple[T, T, T, T]]
	""" Shorthand for a tuple of either 3 or 4 :py:attr:`T`. """

	def __init__(self,
				 name: AnyStr,
				 value: ColorValue,
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

	def __validate_color_value__(self, value: ColorValue) -> None:
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
	def value(self) -> ColorValue:
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

	def __binary_operation__(self, other: Union[T, TikZColor, ColorValue], operator: Callable[[T, T], T]) -> TikZColor:
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
	def __add__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a + b)

	def __sub__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a - b)

	def __mul__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a * b)

	def __truediv__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a / b)

	def __floordiv__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a // b)

	def __mod__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: a % b)

	# "right" arithmetic operations
	def __radd__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b + a)

	def __rsub__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b - a)

	def __rmul__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b * a)

	def __rtruediv__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b / a)

	def __rfloordiv__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b // a)

	def __rmod__(self, other: Union[T, TikZColor, ColorValue]) -> TikZColor:
		return self.__binary_operation__(other, lambda a, b: b % a)

	def __len__(self) -> int:
		return len(self._value)

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

	def full_name(self) -> str:
		""" :return: a string containing the ``xcolor`` name to be used in a LaTeX document, alias for :py:meth:`__str__` """
		return str(self)

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

	:param required_packages: variable length argument, the names of the packages which are required to use the subclass
		of this class
	"""

	def __init__(self, *required_packages: AnyStr):
		self._required_packages = required_packages

	@property
	def required_packages(self) -> Tuple[AnyStr]:
		""" :return: the packages required to use this class in a document """
		return tuple(self._required_packages)

	@abc.abstractmethod
	def __str__(self) -> str:
		pass

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
	STR_NUM: Final = Union[AnyStr, int, float]
	""" The type of a value which accepts either a string, int, or float value. """

	# This tuple is purely used to define the style properties so that IDEs and other tools can find and suggest them
	__slots__ = ("width", "height", "x_scale", "y_scale", "scale", "shift", "draw", "dashed",
				 "dotted", "line_width", "color", "fill", "draw_opacity", "fill_opacity",
				 "__dict__")

	def __init__(self,
				 custom_entries: Optional[Mapping[DICT_ENTRY]] = None,
				 *,
				 width: Optional[STR_NUM] = None,
				 height: Optional[STR_NUM] = None,
				 x_scale: Optional[STR_NUM] = None,
				 y_scale: Optional[STR_NUM] = None,
				 scale: Optional[STR_NUM] = None,
				 shift: Optional[Tuple[STR_NUM, STR_NUM]] = None,

				 draw: Optional[bool] = None,
				 dashed: Optional[bool] = None,
				 dotted: Optional[bool] = None,
				 line_width: Optional[STR_NUM] = None,
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

				"draw"        : draw,
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

	:param required_packages: variable length argument, the names of the packages which are required to use the subclass
		of this class
	:param style: the style to be attached to the instance of this class
	"""

	def __init__(self, *required_packages: AnyStr, style: TikZStyle):
		super(TikZStyled, self).__init__(*required_packages, "xcolor")
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

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CONCRETE TIKZ OBJECTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZPath(TikZStyled):
	r"""
	:py:class:`TikZPath` represents a collection of coordinates drawn using the ``\draw`` command of TikZ.

	:param coordinates: a collection of coordinates for the path
	:param coord_unit: a unit which will be placed after every coordinate value when the final string is constructed
	:param cycle: whether or not to end the final path string with ``-- cycle``, which will join the ending to the beginning
	:param style: the style to apply to this path
	"""

	Coordinate: Final = Tuple[Number, Number]
	""" The type of a coordinate of the path. """

	COORDINATE_FORMAT: Final = r"({:.2f}{}, {:.2f}{})"
	""" The format of a single coordinate.  """
	COORDINATE_JOINER: Final = r" -- "
	r""" The symbol to use between the coordinates in the ``\draw`` command. """

	def __init__(self,
				 coordinates: Collection[Coordinate],
				 coord_unit: AnyStr = "",
				 cycle: bool = False,
				 style: TikZStyle = TikZStyle(draw=True)):
		super(TikZPath, self).__init__(style=style)

		self._coordinates = tuple(coordinates)
		self._coordinates_string = None
		self._coord_unit = coord_unit
		self._cycle = cycle
		self._style = style

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
				self._coordinates_string = self.COORDINATE_JOINER.join([
						self.COORDINATE_FORMAT.format(c[0], self._coord_unit, c[1], self._coord_unit) for c in
						self._coordinates
						])
		return self._coordinates_string

	@property
	def coordinates(self) -> Tuple[Coordinate]:
		return self._coordinates

	@property
	def coord_unit(self):
		return self._coord_unit

	@property
	def cycle(self) -> bool:
		return self._cycle

	@property
	def style(self) -> TikZStyle:
		return self._style

	def __str__(self) -> str:
		return f"\\draw[{str(self._style)}] {self.coordinates_string} {'-- cycle' if self.cycle else ''}"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ MAIN TIKZ ENV ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class TikZPicture(LaTeXEnvironment):
	r"""
	:py:class:`TikZPicture` represents the standard TikZ ``tikzpicture`` environment.

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
		self._defined_colors = list(defined_colors)
		self._color_handler = LaTeXHandler(indent_level)

	@property
	def defined_colors(self) -> Tuple[TikZColor]:
		"""
		:return: the colors which have so far been defined by this environment, or have been passed to this environment
			at construction
		"""
		return tuple(self._defined_colors)

	def define_color(self, color: Union[TikZColor, Iterable[TikZColor]]) -> None:
		"""
		Register one or multiple colors with this instance. This will define the color at the beginning of the environment.

		:param color: the color or colors to define
		"""
		if not isinstance(color, Iterable):
			color = (color,)
		# define color and register as seen
		for c in color:
			if c not in self._defined_colors:
				self._color_handler.write(c.definition())
				self._defined_colors.append(c)

	def write(self, s: Union[TikZWriteable, AnyStr]) -> None:
		"""
		Write ``s`` to the handler of this instance. If ``s`` is a string this method will simply write it, if ``s`` is
		a :py:class:`TikZWriteable` object this method will first register the required packages, then the required
		colors, call the ``__str__`` method of the object, and finally add ``;`` to the end if it is missing

		:param s: the object to write to the handler
		"""
		if isinstance(s, TikZWriteable):
			# get required packages of object and register as seen
			if not type(s) in self._seen_tikz_writeable_types:
				for package in s.required_packages:
					self.document.use_package(package)
				self._seen_tikz_writeable_types.append(type(s))

			# register colors if styled
			if isinstance(s, TikZStyled):
				for color in s.colors:
					self.define_color(color)

			# draw call
			s = str(s)
			if not s.endswith(";"):
				s += ";"

		super(TikZPicture, self).write(s)

	def __exit__(self, exc_type, exc_val, exc_tb):
		# write color handler to parent
		if len(self._color_handler) > 0:
			self.parent_handler.write(str(self._color_handler))
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
