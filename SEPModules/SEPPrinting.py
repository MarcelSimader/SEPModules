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
from math import ceil
from numbers import Real
from typing import Any, Collection, Tuple, Callable, Union, Final, Literal, Dict, Optional, TypeVar

from colorama import Cursor, init as cl_init
from colorama.ansi import AnsiFore, AnsiStyle, code_to_chars

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ GLOBALS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

__PRINT_COLORS__ = True

def _get_print_color() -> bool:
	return __PRINT_COLORS__

def _set_print_color(val: bool):
	global __PRINT_COLORS__
	if type(val) is not bool:
		raise TypeError("Expected type of 'print_colors' to be 'bool' but received '{}'".format(val.__class__.__name__))
	__PRINT_COLORS__ = val

print_colors = property(_get_print_color, _set_print_color,
						doc="""Property to globally enable or disable color printing for module :py:mod:`SEPPrinting`. Defaults to `True`.""")

# initialize colorama and set up constants
cl_init()

POS: Final = lambda x=0, y=0: Cursor.POS(x, y)
REL_POS: Final = lambda x=0, y=0: (Cursor.FORWARD(x) if x >= 0 else Cursor.BACK(-x)) + (
		Cursor.DOWN(y) if y >= 0 else Cursor.UP(-y))
SAVE_POS: Final = "\033[s"
LOAD_POS: Final = "\033[u"

UP: Final = Cursor.UP
DOWN: Final = Cursor.DOWN
FORWARD: Final = Cursor.FORWARD
BACK: Final = Cursor.BACK

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Style:
	r"""
	A helper class to represent style and colors and which actions can be performed on them. New :py:class:`Style` objects
	may be instantiated using ``int`` ANSI style codes, or the :py:mod:`colorama.ansi` classes of `Colorama`. Furthermore,
	style can be combined into composite style by the bitwise ``&`` and ``|`` and the ``+`` operator. Inplace operations
	are **not** supported as the instances of this class are immutable by design.
	"""

	def __init__(self, *styles: Union[int, AnsiStyle, AnsiFore]):
		if any([isinstance(x, tuple) for x in styles]):
			raise TypeError("style parameter contained a nested tuple, but must be a flat tuple")
		self._styles = styles

	@property
	def styles(self) -> Tuple[Union[int, AnsiStyle, AnsiFore]]:
		r""" :return: the style tuple of this instance """
		return self._styles

	def __len__(self) -> int:
		r""" :return: the amount of different style contained in this instance """
		return len(self._styles)

	def __and__(self, other: STYLE_CONCAT) -> STYLE_CONCAT:
		r"""
		Combines two style or strings into one.

		:param other: a different style to combine with this one
		:return: a new style combining both given style, if a string is given as ``other`` the return value will be the
			application of the :py:meth:`__str__` function to the style concatenated with the other operand
		"""
		if isinstance(other, Style):
			return Style(*self._styles, *other._styles)
		elif isinstance(other, str):
			return str(self) + other
		elif isinstance(other, bytes):
			return bytes(str(self), "UTF-8") + other
		else:
			raise TypeError(
					f"other is of type {other.__class__.__name__}, but expected type 'Style', 'str', or 'bytes'")

	def __or__(self, other: STYLE_CONCAT) -> STYLE_CONCAT:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __add__(self, other: STYLE_CONCAT) -> STYLE_CONCAT:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __rand__(self, other: STYLE_CONCAT) -> STYLE_CONCAT:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __ror__(self, other: STYLE_CONCAT) -> STYLE_CONCAT:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __radd__(self, other: STYLE_CONCAT) -> STYLE_CONCAT:
		r""" See :py:meth:`__and__` for details. """
		return self.__and__(other)

	def __eq__(self, other: Style) -> bool:
		if not isinstance(other, Style):
			raise TypeError(f"other is of type {other.__class__.__name__}, but expected type 'Style'")
		return self._styles == other._styles

	def __repr__(self) -> str:
		return f"Style({', '.join(repr(x) for x in self._styles)})"

	def __str__(self) -> str:
		return str().join(code_to_chars(x) for x in self._styles)

STYLE_CONCAT: Final = TypeVar("STYLE_CONCAT", Style, str, bytes)
""" Generic type variable for the :py:class:`Style` class. """

SUPPRESS: Final = Style()
r""" 
Default style to import into a project.

..	deprecated:: 0.1.2

	Deprecated because of the introduction of :py:class:`Style`. These values are kept for backwards compatibility but
	will have the empty style associated with them.

"""
ERROR = LIGHT_ERROR = WARNING = NUMBER = NAME = SUPPRESS

RED: Final = Style(AnsiFore.RED)
YELLOW: Final = Style(AnsiFore.YELLOW)
GREEN: Final = Style(AnsiFore.GREEN)
BLUE: Final = Style(AnsiFore.BLUE)
CYAN: Final = Style(AnsiFore.CYAN)
MAGENTA: Final = Style(AnsiFore.MAGENTA)

LIGHT_RED: Final = Style(91)
LIGHT_YELLOW: Final = Style(93)
LIGHT_GREEN: Final = Style(92)
LIGHT_BLUE: Final = Style(94)
LIGHT_CYAN: Final = Style(96)
LIGHT_MAGENTA: Final = Style(95)

BLACK: Final = Style(AnsiFore.BLACK)
DARK_GRAY: Final = Style(90)
GRAY: Final = Style(37)
WHITE: Final = Style(97)

ITALICS: Final = Style(3)
UNDERLINE: Final = Style(4)
BOLD_UNDERLINE: Final = Style(21)
STRIKETHROUGH: Final = Style(9)
BOXED: Final = Style(51)

BRIGHT: Final = Style(AnsiStyle.BRIGHT)
DIM: Final = Style(AnsiStyle.DIM)
NORMAL: Final = Style(AnsiStyle.NORMAL)

RESET_ALL: Final = Style(AnsiStyle.RESET_ALL)

class FillCharacters:
	"""
	Auto-generated (by font/console_glyph_gen.py) and hand-made fill character sets for the :py:func:`console_graph` function.
	"""

	MINIMAL: Final = ({(" ", " "): 0, ("#", "#"): 1},
					  ("|", "|", "|", "-", "|", "|", "`", "+", "#", "|", "|", "|", "|"))
	"""
	::
	
		#
		#
		BD: |||-|| `+# ||||
	
	"""

	SIMPLE: Final = ({(" ", " "): 0, ("_", "‾"): 0.05, (".", "˙"): 0.1, (":", ":"): 0.3,
					  ("+", "+"): 0.5, ("I", "I"): 0.7, ("#", "#"): 1},
					 ("|", "|", "|", "-", "|", "|", "`", "+", "#", "|", "|", "|", "|"))
	"""
	::
	
		_.:+I#
		‾˙:+I#
		BD: |||-|| `+# ||||
	
	"""

	CONSOLAS_MANUAL: Final = ({(" ", " "): 0, ("_", "‾"): 0.02, ("˷", "͂"): 0.1, (",", "˟"): 0.25, ("ᵦ", "ᴵ"): 0.3,
							   ("ı", "ᵝ"): 0.4, (":", "˸"): 0.55, ("I", "!"): 0.70, ("⌠", "⌡"): 0.85, ("ʬ", "ʬ"): 1},
							  ('│', '├', '┝', '╌', '┤', '┥', '░', '▒', '▓', '┐', '┘', '┌', '└'))
	"""
	::
	
		_˷,ᵦı:+Ii⌠ʬ
		‾˜ ˟ᴵᵝ˸+!I⌡ʬ
		BD: │├┝╌┤┥ ░▒▓ ┐┘┌└
	
	"""

	CONSOLAS: Final = (
			{('̱', '̅'): 0.07, ('̫', '͆'): 0.13, ('ꞈ', '҇'): 0.14, ('¸', 'ᵔ'): 0.17, ('.', '҅'): 0.18, ('̡', '˺'): 0.21,
			 ('₌', '⁼'): 0.27, ('ᴗ', '™'): 0.29, ('ᵥ', 'ᵓ'): 0.34, ('ᵣ', 'ᵓ'): 0.35, (',', 'ˤ'): 0.36, ('₊', 'ᶝ'): 0.39,
			 ('₄', 'ꜟ'): 0.43, ('₅', 'ᶾ'): 0.44, ('₀', 'ᶾ'): 0.45, ('˪', 'ᶮ'): 0.48, ('ᵢ', 'ᶮ'): 0.49, ('□', 'º'): 0.52,
			 ('ː', 'º'): 0.53, ('v', 'ᴃ'): 0.55, ('m', 'о'): 0.57, ('ϖ', '⃝'): 0.6, ('⃝', '⑥'): 0.61, ('<', '⑥'): 0.62,
			 ('ɕ', '҉'): 0.65, ('҉', '¤'): 0.66, ('ȼ', 'ⱥ'): 0.68, ('ƈ', 'ⱬ'): 0.69, ('ʭ', 'ⱬ'): 0.7, ('#', 'Ԉ'): 0.72,
			 ('Ϙ', 'Ԉ'): 0.73, ('Ԍ', 'ѣ'): 0.74, ('ῑ', 'ӽ'): 0.76, ('й', 'ụ'): 0.77, ('h', 'ʞ'): 0.78, ('ø', 'ᶏ'): 0.79,
			 ('ΰ', 'ʗ'): 0.8, ('Ľ', 'Ʀ'): 0.81, ('₾', 'ⱦ'): 0.82, ('ẘ', 'ṋ'): 0.83, ('ŉ', 'ợ'): 0.86, ('ỉ', 'Қ'): 0.87,
			 ('Ⱥ', 'Ṳ'): 0.88, ('ѽ', 'Ṳ'): 0.89, ('ǡ', 'Ӆ'): 0.9, ('ƒ', 'Ƒ'): 0.91, ('ẗ', 'Ԛ'): 0.92, ('Ğ', 'Ṃ'): 0.93,
			 ('ĥ', 'Ṃ'): 0.94, ('$', 'Ϛ'): 0.96, ('Ů', 'ᾷ'): 0.97, ('ẳ', 'Ẕ'): 0.98, ('ḟ', 'Ẕ'): 0.99, (' ', ' '): 0.0,
			 ('ʬ', 'ʬ'): 1.0},
			('│', '├', '┝', '╌', '┤', '┥', '░', '▒', '▓', '┐', '┘', '┌', '└'))
	"""
	Auto generated console_graph fill character set by console_glyph_gen.py from 'font/ConsolasMono-Regular.ttf'::
	
		̱̫ꞈ¸.̡₌ᴗᵥᵣ,₊₄₅₀˪ᵢ□ːvmϖ⃝<ɕ҉ȼƈʭ#ϘԌῑйhøΰĽ₾ẘŉỉȺѽǡƒẗĞĥ$Ůẳḟᾴ Ὂ
		̅͆҇ᵔ҅˺⁼™ᵓᵓˤᶝꜟᶾᶾᶮᶮººᴃо⃝⑥⑥҉¤ⱥⱬⱬԈԈѣӽụʞᶏʗƦⱦṋợҚṲṲӅƑԚṂṂϚᾷẔẔṯ Ὂ
		BD: │├┝╌┤┥ ░▒▓ ┐┘┌└
		Error: 184.775
	
	"""

	CASCADIA_MONO: Final = (
			{('.', '⠒'): 0.15, ('⠄', '⠒'): 0.16, ('◞', '◠'): 0.27, ('◛', '▬'): 0.31, ('₄', '▬'): 0.32, ('₁', '═'): 0.33,
			 ('⠆', '⠢'): 0.38, ('◻', '⬧'): 0.47, ('▸', '◂'): 0.49, ('≡', '≡'): 0.5, ('<', '×'): 0.52, ('▲', '▲'): 0.53,
			 ('+', '◓'): 0.54, ('■', '◓'): 0.55, ('я', 'π'): 0.56, ('≣', 'π'): 0.57, ('¤', '⬠'): 0.59, ('†', '⡰'): 0.61,
			 ('℮', '⬛'): 0.62, ('♠', '♣'): 0.63, ('♦', '❧'): 0.66, ('ґ', 'ҷ'): 0.69, ('ơ', 'ơ'): 0.71, ('©', 't'): 0.73,
			 ('ī', '¡'): 0.75, ('ā', '¡'): 0.76, ('ϗ', 'ų'): 0.77, ('h', 'ų'): 0.78, ('ï', 'χ'): 0.79, ('ß', 'g'): 0.81,
			 ('ả', '¢'): 0.89, ('┆', '¢'): 0.9, ('ǿ', 'ợ'): 0.92, ('/', '┮'): 0.94, ('À', '▆'): 0.96, ('Ö', 'ț'): 0.97,
			 ('Å', '╔'): 0.99, (' ', ' '): 0.0, ('◈', '◈'): 1.0},
			('│', '├', '┝', '╌', '┤', '┥', '░', '▒', '▓', '┐', '┘', '┌', '└'))
	"""
	Auto generated console_graph fill character set by console_glyph_gen.py from 'font/CascadiaMono-Regular.ttf'::
	
		.⠄◞◛₄₁⠆◻▸≡<▲+■я≣¤†℮♠♦ґơ©īāϗhïßả┆ǿ/ÀÖÅĥ ◈
		⠒⠒◠▬▬═⠢⬧◂≡×▲◓◓ππ⬠⡰⬛♣❧ҷơt¡¡ųųχg¢¢ợ┮▆ț╔╔ ◈
		BD: │├┝╌┤┥ ░▒▓ ┐┘┌└
		Error: 114.783
	
	"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def color_string(s: Any, style: Style, boolean: bool = False) -> str:
	"""
	Add color ANSI escape sequences to a string. Longer name version of :py:func:`cl_s`.

	.. seealso:: Function :py:func:`cl_s` for documentation.
	"""
	return cl_s(s, style, boolean=boolean)

def cl_s(s: Any, style: Style, *, boolean: bool = False) -> str:
	"""
	Add color ANSI escape sequences to a string. Shorter name version of :py:func:`color_string`.

	:param s: object to convert to string (any type, but must be `bool` if `boolean` is set to `True`)
	:param style: a :py:class:`Style` instance of arbitrary length
	:param boolean: keyword only parameter, when set to `True` automatically formats the input as green or red string based
		on its boolean value

	:returns: styled string with auto-cast input s, which can be of any type

	.. 	note::

		Color printing is globally enabled or disabled by :py:data:`print_colors`. If this value is set to `True` this
		function will simply return the input so it can still be printed.
	"""
	if not print_colors: return s

	# set boolean style
	if boolean:
		style = style + GREEN if bool(s) else style + RED

	# default style
	if len(style) <= 0:
		style = NORMAL

	return "{}{}{}".format(str(style), str(s), str(RESET_ALL))

def get_time_str(secs: Real, force_unit: Optional[Literal["ns", "µs", "ms", "s", "m", "h"]] = None):
	"""
	Helper function to format durations.

	:param secs: seconds as real number
	:param force_unit: can be str of value "ns/µs/ms/s/m/h" to force a specific unit to display

	:returns: Formatted string with adequate units.

	:raises ValueError: if secs is negative
	:raises ValueError: if type of force_unit is not one of the specified literals
	"""
	# input sanitation
	if secs < 0 or math.copysign(1, secs) == -1:
		raise ValueError("Value for 'secs' must be positive (received {}).".format(secs))

	# ++++FORCE UNIT++++
	if force_unit is not None:
		if not isinstance(force_unit, str):
			raise TypeError("'forceUnit' must be of type 'str' (received {}).".format(force_unit.__class__.__name__))
		if force_unit == "ns":
			factor = 1000000000
		elif force_unit == "µs":
			factor = 1000000
		elif force_unit == "ms":
			factor = 1000
		elif force_unit == "s":
			factor = 1
		elif force_unit == "m":
			factor = 1 / 60
		elif force_unit == "h":
			factor = 1 / (60 * 60)
		else:
			raise ValueError("'forceUnit' must be one of 'ns/µs/ms/s/m/h' (received {}).".format(force_unit))
		return "{:.3f}{}".format(secs * factor, force_unit)

	# ++++REGULAR FORMATTING++++
	if secs <= 0.0000001:
		return "{:.3f}ns".format(secs * 1000000000)
	elif secs <= 0.0001:
		return "{:.3f}µs".format(secs * 1000000)
	elif secs <= 0.1:
		return "{:.3f}ms".format(secs * 1000)
	elif secs < 60:
		if round(60 - secs, 3) == 0:
			secs = 60 - 0.001
		return "{:.3f}s".format(secs)
	else:
		return "{:n}m {:.3f}s".format(int(secs / 60), secs % 60)

def get_appropriate_time_unit(secs: Real) -> Literal["ns", "µs", "ms", "s", "m", "h"]:
	"""
	Turns a second value into a string of the appropriate unit (compatible with :py:func:`get_time_str`).

	:param secs: seconds as integer or float
	:return: the unit-string determining the most appropriate unit for this seconds count
	"""
	if secs <= 0.0000001:
		return "ns"
	elif secs <= 0.0001:
		return "µs"
	elif secs <= 0.1:
		return "ms"
	elif secs < 60:
		return "s"
	elif secs < 3600:
		return "m"
	else:
		return "h"

def console_graph(data: Collection,
				  max_height: int = 13,
				  max_width: int = 128,
				  offset: Tuple[int, int] = (0, 5),
				  center: Tuple[int, int, int, int] = (2, 2, 2, 2),
				  show_scale: bool = True,
				  scale_spacing: int = 1,
				  rounding: int = 2,
				  scale_in_front: bool = False,
				  fill_characters=FillCharacters.SIMPLE,
				  color_function: Callable[[int, int, int, int], Tuple[str, ...]] = None,
				  bg_color: Tuple[str, ...] = NORMAL,
				  use_full_width: bool = True,
				  append_zero_value: bool = False,
				  zero_value: Any = 0,
				  unit_format_function: Callable[[float],
												 Union[
													 Tuple[Union[int, float, str]],
													 Tuple[Union[int, float, str], str],
													 Tuple[Union[int, float, str], str, str]
												 ]] = lambda x: (x,),
				  use_middle_for_unit_position: bool = False,
				  relative_cursor_position: bool = False,
				  debug: bool = False) -> str:
	"""
	..	deprecated:: 0.1.2

		This function is currently being rewritten, and will be available again in a later update.
	"""

	"""
	Creates a graph that can be printed to the console or a log file.

	:param data: a collection of real numbers representing the graph's height at each index, which is used as
		horizontal position
	:param max_height: the height of the graph in characters. Includes all labels and scales
	:param max_width: the width of the graph in characters. Includes all labels and scales
	:param offset: a tuple shifting the data collection left (index 0) or up/down (index 1)

		..	warning::
			Index 0 may have unexpected results and index 1 is currently **not supported**.

	:param center: a padding tuple of the form `(left, right, top, bottom)`. Similar to padding in CSS
	:param show_scale: whether or not to show the side and top scales
	:param scale_spacing: the distance between labels on the side scale in characters
	:param rounding: the rounding of floating point values in the side scale
	:param scale_in_front: whether to put the scale to the left (front) or right of the graph
	:param fill_characters: a tuple containing a dictionary containing float keys and character tuple values, and a tuple
		containing certain special characters (e.g. the scale characters). Fill character sets can be found in the class
		:py:class:`FILL_CHARACTERS`. The dictionary holds one float key approximating the height of a character
		in the graph and a tuple of two characters: one for the bottom version of the character and one for the top
		version. These versions are put for positive and negative values in the graph respectively.

		..	note::

			Console graph fill characters can be generated by using the script :download:`console_glyph_gen.py <../../../bin/console_glyph_gen>`,
			although results vary and the script is not well documented.

	:param color_function: a callable receiving properties of a single character in the graph and returning a color value
		for it. The properties are as follows:

			1. height of the character's column
			2. rate of change between the previous column and the next column
			3. relative position from the x-axis in percent
			4. distance from curve in characters.

		The returned color may be a tuple of style and colors.
	:param bg_color: the color tuple to apply to all background characters (spaces will just appear invisible)
	:param use_full_width: whether or not to fill the rest of the data collection with `zero_value` if the graph does not
		fill the entire space provided by `max_height`. Ensures that the graph does not get printed too narrow
	:param append_zero_value: whether or not to append `zero_value` at the end of the data collection or prepend it to
		the start
	:param zero_value: the value to place in empty columns if `use_full_width` is set (may simply be left at 0 in most
		cases)
	:param unit_format_function: a callable receiving the real number value of a graph label of the side scale and returning
		a tuple defining how the label should be formatted. The tuple may be of length 1, 2 or 3:

		* length 1:
			 1.
				* if the given value is a string, simply display this string in the label
				* if the given value is an int or float, round the value according to `rounding` and then display this string
		* length 2:
			1. still applies from length 1
			2. is a string that will be a text appended to the label
		* length 3:
			1. still applies from length 1
			2. still applies from length 2
			3. is a string that will be prepended to the label

	:param use_middle_for_unit_position: whether or not to use the middle of the character as value for a label. Defaults
		to using the baseline of the character
	:param relative_cursor_position: whether to insert traditional newline character or an ANSI escape sequence
		moving the curse back `max_width` columns if `use_full_width` is set or the used width of the graph; and moving
		the cursor down `max_height` characters
	:param debug: whether or not to show debug characters to make adjusting parameters easier

	:return: a string containing the graph to the specified parameters
	"""
	raise DeprecationWarning("This function is being rewritten and is not usable in its current state")
	# ++++sort fillCharacters by descending value and grab 0 values for quicker access++++
	_sorted_characters = sorted(fill_characters[0].items(), key=lambda item: item[1], reverse=True)
	zero_chars = _sorted_characters[-1][
		0]  # get last entry key tuple after sorting, so should be key tuple where val is 0

	# ++++set debug values++++
	spacer_char = " "  # default value for spacer char
	if debug:
		spacer_char = "'"
		bg_color = BLUE  # set zero char/background color to blue
		zero_chars = (
				fill_characters[1][7], fill_characters[1][8])  # set zero chars to something that can always be seen

	# join background color for faster computations later
	bg_color = str().join(bg_color)

	# ++++add rounding and other shenanigans to unitFormat function++++
	def __decorate_unit_format__(func):
		def __unit_format_wrapper__(graph_value):
			func_result, num_format = func(graph_value), "{}{: ." + str(rounding) + "f}{}"

			# round output of unitFormat function int/float value to specified precision
			func_result_rounded = None
			if type(func_result[0]) in [int, float]:
				func_result_rounded = round(func_result[0], rounding) if rounding > 0 else int(func_result[0])

			if len(func_result) == 3:
				# if 3 arguments passed as tuple, display 'PREFIX + ROUNDED_VALUE + SUFFIX'
				return num_format.format(func_result[1], func_result_rounded, func_result[2])
			elif len(func_result) == 2:
				# if 2 arguments passed as tuple, display 					'ROUNDED_VALUE + SUFFIX'
				return num_format.format("", func_result_rounded, func_result[1])
			elif len(func_result) == 1:
				if func_result_rounded is not None:
					# if 1 argument passed as tuple, display 				'ROUNDED_VALUE'
					return num_format.format("", func_result_rounded, "")
				else:
					return str(func_result[0])
			else:
				raise TypeError(
						"unitFormat needs to return either 3, 2 or 1 value(s) of tuple format '(value [, prefix [, suffix]])'")

		return __unit_format_wrapper__

	unit_format_function = __decorate_unit_format__(unit_format_function)

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~ CELL CLASS ~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	class Cell:
		"""
		Used to represent a column of the final graph.
		"""

		def __init__(self, cell_value, last_cell, color_tuple):
			self.height, self.color, self.data, self.lastCell, self.nextCell = \
				cell_value, color_tuple, list(), last_cell, None

		def __call__(self, ratio, minVal):
			"""
			Set the cells character data and set colors using colorFunction
			"""
			# scale height of cell and global minimum height of all cells
			_adjusted_val, minVal = self.height * ratio, minVal * ratio

			if not self.nextCell: self.nextCell = self
			if not self.lastCell: self.lastCell = self

			# colorFunction(height, change in local height, relative position from x-axis in percent, distance from curve in chars)
			if color_function:
				_sign = 1 if _adjusted_val >= 0 else -1

				# set all color vals based on colorFunction, tuple for faster indexing
				# str join is used to concatenate all tuples of form (COLOR1, COLOR2, STYLE1, etc...) from colorFunction output
				self.color = tuple(str().join(
						color_function(_sign * (char_value / ratio),
									   (self.nextCell.height - self.lastCell.height) / 3,
									   (_sign * char_value) / (len(self.color) * ratio),
									   int(_sign * _adjusted_val - char_value)))
								   for char_value in range(0, int(_sign * _adjusted_val) + 1))

			# apply the char algorithm to fill each column effectively with the fill character set
			self.__set_chars__(_adjusted_val, minVal)

		def __set_chars__(self, cell_value, y_offset):
			"""
			Fills one column/cell object with the character from fillCharacters set in order to
			form a smooth curve over the input data. Works by iteratively decreasing height by 1 and
			filling what space is left with the biggest character that fits within said space
			"""

			def __pad__(height, zero_char_index):
				self.data.extend([str(bg_color) + zero_chars[zero_char_index] + str(RESET_ALL)] * int(height))

			# by finding distance between current value (or x-axis if non-negative value) and minimum global value
			__pad__(max(ceil(abs(y_offset)) + min(0, cell_value), 0), 1)

			unsigned_value_loop = abs(cell_value)
			temp_char_list, signed_value, val_sign = list(), unsigned_value_loop, cell_value < 0

			# fill graph to x-axis starting with largest characters and excluding last char (with value 0)
			for char, charValue in _sorted_characters[:-1]:

				# while character fits into height,
				# else move on to next char
				while charValue <= unsigned_value_loop:
					# invert index for color val  (total height - current height)
					temp_char_list.append(
							str(self.color[int(signed_value - unsigned_value_loop)]) + char[val_sign] + str(RESET_ALL))

					# move down one line/row
					unsigned_value_loop = unsigned_value_loop - 1

			# if no character is small enough to fit into the space left, just add a top or bottom char extra
			if unsigned_value_loop > 0:
				temp_char_list.append(bg_color + zero_chars[val_sign] + RESET_ALL)

			# add temp data reversed if we have a negative value or just add
			if cell_value < 0: temp_char_list.reverse()
			self.data.extend(temp_char_list)

			# fill the rest required to have max height
			__pad__(max_height - len(self.data), 0)

		def __getitem__(self, key):
			"""
			:param key: number of row
			:returns: found row or empty string
			"""
			return self.data[key] if key < len(self.data) else str()

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~ MAIN GRAPH BUILDING ~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	# ++++create list of cells++++
	cells = list()

	# trim data to fit graph
	if offset[0] > 0:
		_trimmed_data = data[-(max_width + offset[0]): -offset[0]]
	else:
		_trimmed_data = data[-max_width:]

	# ++++compute extreme values and scaling ratio++++
	# min value if negative, else just 0
	min_val, max_val = min(0, min(_trimmed_data)), max(0, max(_trimmed_data))

	_trimmed_data = [d - 15 for d in _trimmed_data]

	if show_scale:
		max_height = max_height - 2

	ratio = (max_height - 1) / (max_val - min_val)

	# ++++calculate dimensions if scale is enabled++++
	width_side_scale = 0
	if show_scale:
		unit_range_offset = 1 if min_val != 0 else 0
		unit_range = range(int(min_val * ratio) - unit_range_offset, int(max_val * ratio) + 1)

		# the half character offset used for middle-of-char unit
		use_middle_offset = 0.5 if use_middle_for_unit_position else 0

		# find longest word in this current setup by passing all values into the unitFormat function
		unit_format_dict = {char_val:
								unit_format_function((char_val + use_middle_offset) / ratio)
								if not char_val % (scale_spacing + 1)
								else spacer_char
							for char_val in unit_range}

		longest_unit_format = max([len(v) for v in unit_format_dict.values()])

		# length of entire side scale
		width_side_scale = longest_unit_format + 3
		max_width = max_width - width_side_scale

		# trim data so that entire graph fits in max width but only if it would actually exceed bounds
		if len(_trimmed_data) > max_width:
			_trimmed_data = _trimmed_data[width_side_scale:]

	# extend data with zeroValues if we want to always keep the graph at the same width
	if use_full_width:
		if append_zero_value:
			_trimmed_data.extend([zero_value] * (max_width - len(_trimmed_data)))
		else:
			_trimmed_data[0:0] = [zero_value] * (max_width - len(_trimmed_data))

	# set last cell value for first cell
	last_cell = None
	# initialize with all bg color
	color_tuple = (NORMAL,) * max_height

	for value in _trimmed_data:
		new_cell = Cell(value, last_cell, color_tuple)
		cells.append(new_cell)

		if last_cell is not None:
			last_cell.nextCell = new_cell
		last_cell = new_cell

	# call cells to set color and char data
	[cell(ratio, min_val) for cell in cells]

	# ++++add padding cells++++
	# height of graph = (max height of data) + (height of top scale [in this case either 2 * 0 or 2 * 1 since we have a bool])
	graph_struct_height = max_height + (2 * int(show_scale))

	empty_cell = Cell(0, None, None)
	empty_cell.data = [spacer_char] * graph_struct_height
	cells[0:0] = [empty_cell] * center[0]
	cells.extend([empty_cell] * center[1])

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~ SCALES ~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	if show_scale:
		def _side_scale_sym(i):
			"""
			Short private function to find the correct symbol for the unit side scale
			"""
			if i == unit_range.stop - 1:
				return fill_characters[1][11 if scale_in_front else 9]  # _|
			elif i == unit_range.start:
				return fill_characters[1][12 if scale_in_front else 10]  # "|
			elif i % (scale_spacing + 1):
				return fill_characters[1][0]  # |
			elif scale_in_front:
				return fill_characters[1][2]  # |-
			else:
				return fill_characters[1][5]  # -|

		# ++++side scale++++
		# maxHeight + height of the top scale (i.e. 2 chars)
		scale_cell = Cell(max_height + 2, None, None)

		# set which kind of just function to use depending on location of scale
		scale_just = lambda s: s.rjust if scale_in_front else s.ljust

		# {Numbers}_{|}_ or _{|}_{Numbers} if scale not in front
		scale_cell.data.extend([("{num} {sym} " if scale_in_front else " {sym} {num}").format(
				sym=_side_scale_sym(char_val),
				num=cl_s(scale_just(unit_format_dict[char_val])(longest_unit_format, spacer_char), BRIGHT))
				for char_val in unit_range])

		# add 2 extra rows side scale fill characters to match top scale
		scale_cell.data.extend([spacer_char * width_side_scale] * 2)

		# add after left padding, or after (left padding + data width) if scale not in front
		cells.insert(center[0] + (0 if scale_in_front else len(_trimmed_data)), scale_cell)

		# ++++top scale++++
		# pad out all cells by 1 row so that the space below top scale is filled (i.e. an empty line)
		[cell.data.extend(spacer_char) for cell in cells]

		start, stop = max(len(data) - len(_trimmed_data) - offset[0], 0), max(len(data) - offset[0], 0)
		# top scale is inserted into one cell located at the start of data graph (i.e. left padding + 1)
		top_scale_cell = cells[center[0] + 1]
		# length of middle segment is (length of data or maxWidth (whichever is smaller)) - (lengths of start/end strings) - (4 fill characters)
		top_scale_length_middle_segment = min(len(_trimmed_data), max_width) - len(str(start)) - len(str(stop)) - 4

		# {Start}_{|-}{----///----}{-|}_{Stop}
		top_scale_cell.data.extend(["{} {}{}{} {}".format(
				start,
				fill_characters[1][1],
				fill_characters[1][3] * top_scale_length_middle_segment,
				fill_characters[1][4],
				stop)])

	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~ ASSEMBLING PARTS ~~~~~~~~~~~~~~~
	# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

	# set newline to \n for absolute cursor position or set
	# new line to an escape sequence moving cursor to correct
	# location if cursor position is set to relative
	new_line, debug_newline = "\n", "\\n" if debug else ""

	# width: (max width of graph part) + (padding left/right) + (width side scale)
	full_graph_struct_width = max_width + center[0] + center[1] + width_side_scale

	if relative_cursor_position:
		# move cursor back by width of entire graph structure (including length of debug newline chars!)
		new_line = REL_POS(-(full_graph_struct_width + len(debug_newline)), 0)

	# add debug color and character if desired
	if debug:
		new_line = cl_s(debug_newline, CYAN) + new_line

	# one empty line to pre- or append to output
	empty_line = full_graph_struct_width * spacer_char + new_line

	# ++++create the output string++++
	return empty_line * center[2] + \
		   str().join([(str().join([col[row] for col in cells]) + new_line)
					   for row in range(graph_struct_height - 1, -1, -1)]) \
		   + empty_line * center[3]

def console_progress_bar(position: Real,
						 max_position: Real,
						 length: Real,
						 center: Tuple[int, int, int, int] = (3, 0, 0, 0),
						 progress_characters: Dict[float, str] = {1  : "█", 0.875: "▉", 0.75: "▊", 0.625: "▋",
																  0.5: "▌", 0.375: "▍", 0.25: "▎", 0.125: "▏"},
						 end_characters: Tuple[str, str] = ("<", ">"),
						 show_text: bool = True,
						 text_rounding: int = 2,
						 auto_round: bool = True,
						 rate_of_change: Optional[str] = None,
						 relative_cursor_position: bool = False,
						 debug: bool = False) -> str:
	"""
	..	deprecated:: 0.1.2

		This function is currently being rewritten, and will be available again in a later update.
	"""
	"""
	Creates a progress-bar string that is printable to the console or a log file.

	:param position: the position the progress bar should display out of `max_position` (must be smaller than `max_position`
		but may be negative)
	:param max_position: the maximum value that `position` will ever reach
	:param length: the width of the entire progress bar string, including all texts and offsets
	:param center: a padding tuple of the form `(top, bottom , left, right)`, similar to padding in CSS
	:param progress_characters: a dictionary containing float keys and character values, where the float describes the
		apparent width of the character value. Can be in order but is sorted automatically. The key "1" must be present
		for full characters
	:param end_characters: a tuple of the form `(left char, right char)` defining the characters that will be displayed on
		either end of the progress bar
	:param show_text: whether or not to display the `position / max_position` and potentially `rate_of_change` texts next
		to the progress bar. Enabling this does not change the length
	:param text_rounding: the rounding of the `position / max_position` text values
	:param auto_round: whether or not to automatically round the passed `position` and `max_position` parameters based
	 	on the smallest float in progress_characters. Enabling this will prevent characters from being left out due
	 	to floating point precision errors
	:param rate_of_change: a string to display after the `position / max_position` text. Will only be shown if
		show_text is enabled
	:param relative_cursor_position: whether to insert traditional newline character or an ANSI escape sequence
		moving the curse back `length` columns and down one row
	:param debug: whether or not to show debug characters to make adjusting parameters easier

	:return: a string containing the entire progress bar to the specified parameters

	:raises ValueError: if position is bigger than max_position
	"""
	raise DeprecationWarning("This function is being rewritten and is not usable in its current state")
	text_width = 0
	if show_text:
		# ' ( / )' + 2x 'digits . rounding'
		text_width = 6 + (len(str(int(max_position))) + 1 + text_rounding) * 2
		if rate_of_change is not None:
			# ', ' + rate_of_change
			text_width = text_width + 2 + len(rate_of_change)

	# ...<###>   (text)...
	# -2 for start and end bar
	bar_length = length - (2 + center[0] + center[1] + text_width)

	normalized_pos = position / max_position
	char_pos = normalized_pos * bar_length

	if auto_round:
		digits_min_char = abs(round(math.log10(min(progress_characters.keys()))))
		char_pos = round(char_pos, digits_min_char)

	# we check against bar length because that value is potentially rounded and less finicky with floats
	if char_pos > bar_length:
		raise ValueError(
				"position cannot be bigger than max_position (got {}, but expected no more than {})".format(position,
																											max_position))

	char_list = list()

	# append full chars
	char_list.extend((progress_characters[1],) * int(char_pos))

	# append partial char
	for val, char in sorted(progress_characters.items(), key=lambda x: x[0], reverse=True):
		if val <= char_pos % 1:
			char_list.append(char)
			break

	# fill in the rest
	char_list.extend(" " * (bar_length - len(char_list)))

	newline = "\n"
	space = " "
	if relative_cursor_position:
		newline = REL_POS(-(length + (2 if debug else 0)), 1)
	if debug:
		newline = cl_s("\\n", *CYAN) + newline
		space = "'"

	text_format_str_part = "{:." + str(text_rounding) + "f}"
	if rate_of_change is None:
		text_format_str = " ({part} / {part})".format(part=text_format_str_part)
	else:
		text_format_str = " ({part} / {part}, {roc})".format(part=text_format_str_part, roc=rate_of_change)

	return "{top}{left}{e_left}{bar}{e_right}{text}{right}{newline}{bottom}".format(
			left=space * center[0],
			right=space * center[1],
			top=((space * length) + newline) * center[2],
			bottom=((space * length) + newline) * center[3],
			newline=newline,
			e_left=end_characters[0],
			e_right=end_characters[1],
			bar=str().join(char_list),
			text=text_format_str.format(position, max_position).rjust(text_width) if show_text else str())
