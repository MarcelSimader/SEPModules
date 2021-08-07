"""
:Author: Marcel Simader
:Date: 01.04.2021

..	versionadded:: v0.1.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import math
from typing import Any, Callable, Union, Final, Literal, Optional, TypeVar, AnyStr, Sequence, \
	SupportsFloat, Iterable
from warnings import warn

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

_T: Final = TypeVar("_T")
""" A generic type variable for use in :py:mod:`SEPPrinting`. """

# color print property
_PRINT_COLORS = True

def _set_print_color(val: bool):
	global _PRINT_COLORS
	if not isinstance(val, bool):
		raise TypeError(f"Expected type of 'print_colors' to be 'bool' but received {val.__class__.__name__}")
	_PRINT_COLORS = val

print_colors = property(lambda: _PRINT_COLORS, _set_print_color, None,
						doc=""" Property to globally enable or disable color printing for module :py:mod:`SEPPrinting`. 
Defaults to ``True``.""")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ ANSI CONTROL SEQUENCES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AnsiControl:
	r"""
	:py:class:`AnsiControl` represents ANSI control sequences and which actions can be performed on them. New AnsiControl
	objects may be instantiated using ``int`` ANSI CSI codes which will be combined as ``CSI int``; or sequences of ``int``,
	and ``str``, which will be combined as ``CSI int0;int1;...;int_n str0``. Furthermore, style can be combined into
	composite style by the bitwise ``&`` and ``|`` and the ``+`` operator. Strings (or bytes) can also be combined with
	styles, in which case strings (or bytes) concatenated with the entire control sequence will be returned.

	:param style: an arbitrary amount of ANSI style codes
	"""

	# escape sequence constants
	ESC: Final[str] = chr(0x1B)
	CSI: Final[str] = ESC + chr(0x9B)
	OSC: Final[str] = ESC + chr(0x9D)

	def __init__(self, *style: Union[int, Sequence[Union[int, str]]]):
		for x in (o for o in style if not isinstance(o, (int, Sequence))):
			raise TypeError(f"style must be an int, or sequence of ints and strings, "
							f"but received {x.__class__.__name__!r}")
		# sequence checks
		for x in (o for o in style if isinstance(o, Sequence)):
			if not (all(isinstance(xs, int) for xs in x[:-1]) and isinstance(x[-1], str)):
				raise ValueError(f"Sequence arguments for AnsiControl must be of form (int0, int1, ..., int_n, str), "
								 f"but received {tuple(xs.__class__.__name__ for xs in x)!r}")
		self._styles = style

	@property
	def styles(self) -> Union[int, Sequence[Union[int, str]]]:
		r""" :return: the style tuple of this instance """
		return self._styles

	def __len__(self) -> int:
		r""" :return: the amount of different style contained in this instance """
		return len(self._styles)

	def __and__(self, other: _AnsiControlConcat) -> _AnsiControlConcat:
		r"""
		Combines two style or strings into one.

		:param other: a different style to combine with this one
		:return: a new style combining both given style, if a string is given as ``other`` the return value will be the
			application of the :py:meth:`__str__` function to the style concatenated with the other operand
		"""
		if isinstance(other, AnsiControl):
			return AnsiControl(*self._styles, *other._styles)
		elif isinstance(other, str):
			return str(self) + other
		elif isinstance(other, bytes):
			return bytes(str(self), "UTF-8") + other
		else:
			raise TypeError(f"other is of type {other.__class__.__name__}, but expected type 'AnsiControl', 'str', "
							f"or 'bytes'")

	def __or__(self, other: _AnsiControlConcat) -> _AnsiControlConcat:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __add__(self, other: _AnsiControlConcat) -> _AnsiControlConcat:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __rand__(self, other: _AnsiControlConcat) -> _AnsiControlConcat:
		r""" See :py:meth:`__and__` for details. """
		# reverse concatenation or call original left hand side AND
		if isinstance(other, str):
			return other + str(self)
		elif isinstance(other, bytes):
			return other + bytes(str(self), "UTF-8")
		else:
			return self.__and__(other)

	def __ror__(self, other: _AnsiControlConcat) -> _AnsiControlConcat:
		r""" See :py:meth:`__and__` for details. """
		return self.__rand__(other)

	def __radd__(self, other: _AnsiControlConcat) -> _AnsiControlConcat:
		r""" See :py:meth:`__and__` for details. """
		return self.__rand__(other)

	def __hash__(self) -> int:
		return hash(self._styles)

	def __eq__(self, other: AnsiControl) -> bool:
		return isinstance(other, AnsiControl) and self._styles == other._styles

	def __repr__(self) -> str:
		return f"AnsiControl({', '.join(repr(x) for x in self._styles)})"

	def __str__(self) -> str:
		return str().join(self.CSI + ";".join(str(xs) for xs in x[:-1]) + x[-1]
						  if isinstance(x, Sequence) else
						  self.CSI + str(x)
						  for x in self._styles)

_AnsiControlConcat: Final = TypeVar("_AnsiControlConcat", AnsiControl, str, bytes)
""" Generic type variable for the :py:class:`AnsiControl` class. """

SUPPRESS: Final[AnsiControl] = AnsiControl()
r""" 
Default style to import into a project.

..	deprecated:: 0.1.2

	Deprecated because of the introduction of :py:class:`AnsiControl`. These values are kept for backwards compatibility 
	but will have the empty style associated with them.

"""
ERROR = LIGHT_ERROR = WARNING = NUMBER = NAME = SUPPRESS

# cursor modifiers
def UP(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor ``n`` cells up. """
	return AnsiControl((n, "A"))

def DOWN(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor ``n`` cells down. """
	return AnsiControl((n, "B"))

def FORWARD(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor ``n`` cells forward. """
	return AnsiControl((n, "C"))

def BACKWARD(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor ``n`` cells backward. """
	return AnsiControl((n, "D"))

def NEXT_LINE(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor to the first column ``n`` lines down. """
	return AnsiControl((n, "E"))

def PREV_LINE(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor to the first column ``n`` lines up. """
	return AnsiControl((n, "F"))

def HORIZ(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which moves the cursor to column ``n`` of the current line. """
	return AnsiControl((n, "G"))

def POS(x: int = 1, y: int = 1) -> AnsiControl:
	"""
	Creates an ANSI control sequence which moves the cursor to the absolute position ``x, y`` with the top
	left corner being ``1, 1``.
	"""
	return AnsiControl((x, y, "H"))

def REL_POS(x: int = 0, y: int = 0) -> AnsiControl:
	"""
	Creates an ANSI control sequence which move the cursor ``x`` cells horizontally, and ``y`` cells vertically
	relative to its current position.
	"""
	_x, _y = abs(x), abs(y)
	return (FORWARD(_x) if x >= 0 else BACKWARD(_x)) + (DOWN(_y) if y >= 0 else UP(_y))

def ERASE_DISPLAY(n: Literal[0, 1, 2, 3] = 2) -> AnsiControl:
	"""
	Creates an ANSI control sequence which does one of the following:

	+----+-----------------------------------------------------------+
	| n  | Behaviour                                                 |
	+====+===========================================================+
	| 0  | Clear from the cursor to the end of the screen.           |
	+----+-----------------------------------------------------------+
	| 1  | Clear from the cursor to the beginning of the screen.     |
	+----+-----------------------------------------------------------+
	| 2  | Clear the entire screen.                                  |
	+----+-----------------------------------------------------------+
	| 3  | Clear the entire screen and delete the scrollback buffer. |
	+----+-----------------------------------------------------------+
	"""
	return AnsiControl((n, "J"))

def ERASE_LINE(n: Literal[0, 1, 2] = 2) -> AnsiControl:
	"""
	Creates an ANSI control sequence which does one of the following:

	+----+---------------------------------------------------------+
	| n  | Behaviour                                               |
	+====+=========================================================+
	| 0  | Clear from the cursor to the end of the line.           |
	+----+---------------------------------------------------------+
	| 1  | Clear from the cursor to the beginning of the line.     |
	+----+---------------------------------------------------------+
	| 2  | Clear the entire line.                                  |
	+----+---------------------------------------------------------+
	"""
	return AnsiControl((n, "K"))

def SCROLL_UP(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which scrolls up the whole screen by ``n`` lines. New lines are added at the bottom. """
	return AnsiControl((n, "S"))

def SCROLL_DOWN(n: int = 1) -> AnsiControl:
	""" Creates an ANSI control sequence which scrolls down the whole screen by ``n`` lines. New lines are added at the top. """
	return AnsiControl((n, "T"))

# text and color modifies
RESET_ALL: Final[AnsiControl] = AnsiControl((0, "m"))
NORMAL: Final[AnsiControl] = RESET_ALL
BOLD: Final[AnsiControl] = AnsiControl((1, "m"))
BRIGHT: Final[AnsiControl] = BOLD
DIM: Final[AnsiControl] = AnsiControl((2, "m"))
INVERT: Final[AnsiControl] = AnsiControl((7, "m"))

ITALIC: Final[AnsiControl] = AnsiControl((3, "m"))
UNDERLINE: Final[AnsiControl] = AnsiControl((4, "m"))
DOUBLE_UNDERLINE: Final[AnsiControl] = AnsiControl((21, "m"))
BLINK: Final[AnsiControl] = AnsiControl((5, "m"))
STRIKETHROUGH: Final[AnsiControl] = AnsiControl((9, "m"))
BORDER: Final[AnsiControl] = AnsiControl((51, "m"))
OVERLINE: Final[AnsiControl] = AnsiControl((53, "m"))

# foreground
BLACK: Final[AnsiControl] = AnsiControl((30, "m"))
RED: Final[AnsiControl] = AnsiControl((31, "m"))
GREEN: Final[AnsiControl] = AnsiControl((32, "m"))
YELLOW: Final[AnsiControl] = AnsiControl((33, "m"))
BLUE: Final[AnsiControl] = AnsiControl((34, "m"))
MAGENTA: Final[AnsiControl] = AnsiControl((35, "m"))
CYAN: Final[AnsiControl] = AnsiControl((36, "m"))
LIGHT_GRAY: Final[AnsiControl] = AnsiControl((37, "m"))

GRAY: Final[AnsiControl] = AnsiControl((90, "m"))
LIGHT_RED: Final[AnsiControl] = AnsiControl((91, "m"))
LIGHT_GREEN: Final[AnsiControl] = AnsiControl((92, "m"))
LIGHT_YELLOW: Final[AnsiControl] = AnsiControl((93, "m"))
LIGHT_BLUE: Final[AnsiControl] = AnsiControl((94, "m"))
LIGHT_MAGENTA: Final[AnsiControl] = AnsiControl((95, "m"))
LIGHT_CYAN: Final[AnsiControl] = AnsiControl((96, "m"))
WHITE: Final[AnsiControl] = AnsiControl((97, "m"))

# background
BACK_BLACK: Final[AnsiControl] = AnsiControl((40, "m"))
BACK_RED: Final[AnsiControl] = AnsiControl((41, "m"))
BACK_GREEN: Final[AnsiControl] = AnsiControl((42, "m"))
BACK_YELLOW: Final[AnsiControl] = AnsiControl((43, "m"))
BACK_BLUE: Final[AnsiControl] = AnsiControl((44, "m"))
BACK_MAGENTA: Final[AnsiControl] = AnsiControl((45, "m"))
BACK_CYAN: Final[AnsiControl] = AnsiControl((46, "m"))
BACK_LIGHT_GRAY: Final[AnsiControl] = AnsiControl((47, "m"))

BACK_GRAY: Final[AnsiControl] = AnsiControl((100, "m"))
BACK_LIGHT_RED: Final[AnsiControl] = AnsiControl((101, "m"))
BACK_LIGHT_GREEN: Final[AnsiControl] = AnsiControl((102, "m"))
BACK_LIGHT_YELLOW: Final[AnsiControl] = AnsiControl((103, "m"))
BACK_LIGHT_BLUE: Final[AnsiControl] = AnsiControl((104, "m"))
BACK_LIGHT_MAGENTA: Final[AnsiControl] = AnsiControl((105, "m"))
BACK_LIGHT_CYAN: Final[AnsiControl] = AnsiControl((106, "m"))
BACK_WHITE: Final[AnsiControl] = AnsiControl((107, "m"))

# rgb
def RGB(r: int, g: int, b: int) -> AnsiControl:
	""" Creates an ANSI control sequence which displays text with the specified RGB value as foreground color. """
	return AnsiControl((38, 2, r, g, b, "m"))

def BACK_RGB(r: int, g: int, b: int) -> AnsiControl:
	""" Creates an ANSI control sequence which displays text with the specified RGB value as background color. """
	return AnsiControl((48, 2, r, g, b, "m"))

# misc
BELL: Final[str] = chr(7)
CURSOR_VISIBLE: Final[str] = AnsiControl.CSI + "?25h"
CURSOR_INVISIBLE: Final[str] = AnsiControl.CSI + "?25l"
SAVE_SCREEN: Final[str] = AnsiControl.CSI + "?47h"
LOAD_SCREEN: Final[str] = AnsiControl.CSI + "?47l"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ COLOR STRING ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def color_string(s: Any, style: AnsiControl = NORMAL, *, boolean: bool = False) -> str:
	"""
	Add color ANSI escape sequences to a string. Longer name version of :py:func:`cl_s`.

	.. seealso:: Function :py:func:`cl_s` for documentation.
	"""
	return cl_s(s, style, boolean=boolean)

def cl_s(s: Any, style: AnsiControl = NORMAL, *, boolean: bool = False) -> str:
	"""
	Add color ANSI escape sequences to a string. Shorter name version of :py:func:`color_string`.

	:param s: object to convert to string (any type, but must implement ``__bool__`` if ``boolean`` argument is set to
	 	``True``)
	:param style: a :py:class:`AnsiControl` instance
	:param boolean: keyword only parameter, when set to ``True`` automatically formats the input as green or red string
		based on its boolean value

	:returns: ANSI escape sequences of defined style(s) concatenated with ``str(s)``, where s may be of any type

	.. 	note::

		Color printing is globally enabled or disabled by :py:data:`print_colors`. If this value is set to ``False`` this
		function will simply return ``str(s)`` so it can still be printed.
	"""
	if print_colors:
		# set boolean style
		if boolean:
			style = style + GREEN if bool(s) else style + RED

		return style + str(s) + RESET_ALL
	else:
		return str(s)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ TIME STRING ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def time_str(secs: SupportsFloat,
			 n_digits: int = 3,
			 force_unit: Optional[Literal["ns", "µs", "ms", "s", "m", "h"]] = None) -> str:
	"""
	Helper function to format durations of times.

	:param secs: seconds as number
	:param n_digits: the number of digits for floating point values in the output string
	:param force_unit: can be str of value ``ns``, ``µs``, ``ms``, ``s``, ``m``, or ``h`` to force a specific unit to
		display
	:returns: formatted string with adequately chosen units

	:raises ValueError: if secs is negative
	:raises ValueError: if type of force_unit is not one of the specified literals

	..	seealso:: :py:func:`get_appropriate_time_unit`
	"""
	# input sanitation
	if not isinstance(secs, SupportsFloat):
		raise TypeError(f"secs must support __float__, but received type {secs.__class__.__name__} which does not")
	secs = float(secs)
	if secs < 0 or math.copysign(1, secs) == -1:
		raise ValueError(f"value 'secs' must be positive, but received {secs!r}")

	if not isinstance(n_digits, int):
		raise TypeError(f"n_digits must be of type int, but received {n_digits.__class__.__name__}")
	if force_unit is not None and not isinstance(force_unit, str):
		raise TypeError(f"forceUnit must be of type 'str', but received {force_unit.__class__.__name__}")

	float_format = lambda s, suffix: r"{{:.{}f}}".format(int(n_digits)).format(s) + suffix

	# force unit
	if force_unit is not None:
		if force_unit == "ns":
			factor = 1.0e9
		elif force_unit == "µs" or force_unit == "us":
			factor = 1.0e6
		elif force_unit == "ms":
			factor = 1.0e3
		elif force_unit == "s":
			factor = 1
		elif force_unit == "m":
			factor = 1 / 60
		elif force_unit == "h":
			factor = 1 / (60 ** 2)
		else:
			raise ValueError(f"'forceUnit' must be one of 'ns', 'µs', 'ms', 's', 'm', or 'h', but "
							 f"received {force_unit}")
		return float_format(secs * factor, force_unit)

	# regular formatting
	if secs <= 1.0e-7:
		return float_format(secs * 1.0e9, "ns")
	elif secs <= 1.0e-4:
		return float_format(secs * 1.0e6, "µs")
	elif secs <= 1.0e-1:
		return float_format(secs * 1.0e3, "ms")
	elif secs < 60:
		if round(60 - secs, n_digits) == 0:
			secs = math.floor(secs * (10 ** n_digits)) / (10 ** n_digits)
		return float_format(secs, "s")
	else:
		return f"{secs // 60:n}m {float_format(secs % 60, 's')}"

def get_appropriate_time_unit(secs: SupportsFloat) -> Literal["ns", "µs", "ms", "s", "m", "h"]:
	"""
	Turns a second value into a string of the appropriate unit.

	..	seealso:: The literals returned by this function are compatible with :py:func:`time_str`.

	:param secs: seconds as integer or float
	:return: the unit-string determining the most appropriate unit for this seconds count
	"""
	if not isinstance(secs, SupportsFloat):
		raise TypeError(f"secs must support __float__, but received type {secs.__class__.__name__} which does not")
	secs = float(secs)

	if secs <= 1.0e-7:
		return "ns"
	elif secs <= 1.0e-4:
		return "µs"
	elif secs <= 1.0e-1:
		return "ms"
	elif secs < 60:
		return "s"
	elif secs < 60 ** 2:
		return "m"
	else:
		return "h"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ MISC HELP FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def repr_str(obj: Any,
			 *properties: property[_T],
			 value_function: Callable[[_T], str] = repr,
			 include_none: bool = False,
			 include_empty_str: bool = False,
			 joiner: AnyStr = ", ") -> str:
	"""
	repr_str(obj, *properties, value_function=repr, include_none=False, include_empty_str=False, joiner=', ')
	Provides a ``__repr__`` string for any class of type ``obj``.

	:param obj: the object to create this repr string from
	:param properties: the values which should be displayed in this repr string
	:param value_function: which function to apply to each element of ``values``
	:param include_none: whether or not to include ``None`` values or to omit them
	:param include_empty_str: whether or not to include empty string ``str()`` values or to omit them
	:param joiner: which string to use to join the values together (see :py:meth:`str.join`)
	:return: a repr string for ``cls``
	"""
	strings = list()
	for prop, val in map(lambda _p: (_p, _p.fget(obj)), properties):
		if not include_none and val is None:
			continue
		if isinstance(val, str) and not include_empty_str and val == str():
			continue

		# iterable to list conversion
		if isinstance(val, Iterable) and not isinstance(val, (str, bytes)):
			_val = list()
			for i, v in enumerate(val):
				if i >= 50:
					warn(RuntimeWarning(f"repr_string iterable {obj.__class__.__name__} for contains more than "
										f"50 objects, so broke off early"))
					_val.append("...")
					break
				_val.append(value_function(v))
			val = f"[{', '.join(_val)}]"
		else:
			val = value_function(val)

		# construct key=val string
		strings.append(f"{prop.fget.__name__}={val}")
	return f"{obj.__class__.__name__}({joiner.join(strings)})"

def error_str(original: AnyStr,
			  error_from: int,
			  error_to: int,
			  error_msg: Optional[AnyStr] = None,
			  *,
			  error_style: AnsiControl = RED,
			  enable_color: bool = True) -> str:
	# input sanitation
	if len(original) == 0:
		return str()
	if "\n" in original:
		raise ValueError("original string cannot contain newline '\\n' character, but "
						 "found one at position {}".format(original.find("\n")))
	if error_from < 0 or error_to < 0 \
			or error_from > len(original) or error_to > len(original) \
			or error_from > error_to:
		raise ValueError(f"error_from and error_to must be in range [0;{len(original)}], and "
						 f"error_from <= error_to, but received [{error_from};{error_to}]")

	_cl_s = cl_s if enable_color else lambda x, *y: x
	# add color and hint
	out_str = original[:error_from] + _cl_s(original[error_from:error_to], error_style) + original[error_to:]
	# consider newlines
	out_str += "\n" + (" " * error_from) + _cl_s("^" * max(1, error_to - error_from), error_style)

	if error_msg is None:
		return out_str
	else:
		return f"{out_str}\n\nError at position {error_from}: {error_msg}"
