#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++
from colorama import Fore, Back, Style, Cursor, init as cl_init
from numbers import Number
import math, random, statistics
from math import ceil, floor, log
import os, sys, time
from time import sleep
from unicodedata import normalize

import unittest

#states
__PRINT_COLORS__ = True

#initialize colorama and set up constants
cl_init()

SUPPRESS = (Style.DIM)
ERROR = (Fore.RED)
LIGHT_ERROR = (Fore.RED, Style.BRIGHT)
WARNING = (Fore.YELLOW)
NUMBER = (Style.BRIGHT)
NAME = (Fore.CYAN)

RED, GREEN, BLUE, YELLOW = (Fore.RED), (Fore.GREEN), (Fore.BLUE), (Fore.YELLOW)
CYAN, MAGENTA = (Fore.CYAN), (Fore.MAGENTA)
WHITE, BLACK = (Fore.WHITE), (Fore.BLACK)

BRIGHT, DIM, NORMAL = (Style.BRIGHT), (Style.DIM), (Style.NORMAL)

POS     = lambda x=0,y=0: Cursor.POS(x, y)
REL_POS = lambda x=0,y=0: (Cursor.FORWARD(x) if x >= 0 else Cursor.BACK(-x)) + (Cursor.DOWN(y) if y >= 0 else Cursor.UP(-y))
SAVE_POS, LOAD_POS = "\033[s", "\033[u"
UP, DOWN, FORWARD, BACK = Cursor.UP, Cursor.DOWN, Cursor.FORWARD, Cursor.BACK

RESET_ALL = (Style.RESET_ALL)

class FILL_CHARACTERS:
	"""
	Auto-generated (by font/console_glyph_gen.py) and hand-made fill character sets for the SEPPrinting.console_graph function.
	"""
	
	"""
	#
	#
	BD: |||-|| `+# ||||
	"""
	MINIMAL = (	{	(" ", " "): 0, ("#", "#"): 1}, \
							("|", "|", "|", "-", "|", "|", "`", "+", "#", "|", "|", "|", "|"))

	"""
	_.:+I#
	‾˙:+I#
	BD: |||-|| `+# ||||
	"""
	SIMPLE = (	{	(" ", " "): 0,   ("_", "‾"): 0.05, (".", "˙"): 0.1, (":", ":"): 0.3, \
								("+", "+"): 0.5, ("I", "I"): 0.7,  ("#", "#"): 1}, \
							("|", "|", "|", "-", "|", "|", "`", "+", "#", "|", "|", "|", "|"))

	"""
	_˷,ᵦı:+Ii⌠ʬ
	‾˜ ˟ᴵᵝ˸+!I⌡ʬ
	BD: │├┝╌┤┥ ░▒▓ ┐┘┌└
	"""
	CONSOLAS_MANUAL = (	{	(" ", " "): 0  , ("_", "‾"): 0.02, ("˷", "͂"): 0.1 , (",", "˟"): 0.25, ("ᵦ", "ᴵ"): 0.3, \
													("ı", "ᵝ"): 0.4, (":", "˸"): 0.55, ("I", "!"): 0.70, ("⌠", "⌡"): 0.85, ("ʬ", "ʬ"): 1}, \
											('│', '├', '┝', '╌', '┤', '┥', '░', '▒', '▓', '┐', '┘', '┌', '└'))
	
	"""
	Auto generated console_graph fill character set by console_glyph_gen.py from 'font/ConsolasMono-Regular.ttf'.
	̱̫ꞈ¸.̡₌ᴗᵥᵣ,₊₄₅₀˪ᵢ□ːvmϖ⃝<ɕ҉ȼƈʭ#ϘԌῑйhøΰĽ₾ẘŉỉȺѽǡƒẗĞĥ$Ůẳḟᾴ Ὂ
	̅͆҇ᵔ҅˺⁼™ᵓᵓˤᶝꜟᶾᶾᶮᶮººᴃо⃝⑥⑥҉¤ⱥⱬⱬԈԈѣӽụʞᶏʗƦⱦṋợҚṲṲӅƑԚṂṂϚᾷẔẔṯ Ὂ
	BD: │├┝╌┤┥ ░▒▓ ┐┘┌└
	Error: 184.775
	"""
	CONSOLAS =      (       {('̱', '̅'): 0.07, ('̫', '͆'): 0.13, ('ꞈ', '҇'): 0.14, ('¸', 'ᵔ'): 0.17, ('.', '҅'): 0.18, ('̡', '˺'): 0.21, ('₌', '⁼'): 0.27, ('ᴗ', '™'): 0.29, ('ᵥ', 'ᵓ'): 0.34, ('ᵣ', 'ᵓ'): 0.35, (',', 'ˤ'): 0.36, ('₊', 'ᶝ'): 0.39, ('₄', 'ꜟ'): 0.43, ('₅', 'ᶾ'): 0.44, ('₀', 'ᶾ'): 0.45, ('˪', 'ᶮ'): 0.48, ('ᵢ', 'ᶮ'): 0.49, ('□', 'º'): 0.52, ('ː', 'º'): 0.53, ('v', 'ᴃ'): 0.55, ('m', 'о'): 0.57, ('ϖ', '⃝'): 0.6, ('⃝', '⑥'): 0.61, ('<', '⑥'): 0.62, ('ɕ', '҉'): 0.65, ('҉', '¤'): 0.66, ('ȼ', 'ⱥ'): 0.68, ('ƈ', 'ⱬ'): 0.69, ('ʭ', 'ⱬ'): 0.7, ('#', 'Ԉ'): 0.72, ('Ϙ', 'Ԉ'): 0.73, ('Ԍ', 'ѣ'): 0.74, ('ῑ', 'ӽ'): 0.76, ('й', 'ụ'): 0.77, ('h', 'ʞ'): 0.78, ('ø', 'ᶏ'): 0.79, ('ΰ', 'ʗ'): 0.8, ('Ľ', 'Ʀ'): 0.81, ('₾', 'ⱦ'): 0.82, ('ẘ', 'ṋ'): 0.83, ('ŉ', 'ợ'): 0.86, ('ỉ', 'Қ'): 0.87, ('Ⱥ', 'Ṳ'): 0.88, ('ѽ', 'Ṳ'): 0.89, ('ǡ', 'Ӆ'): 0.9, ('ƒ', 'Ƒ'): 0.91, ('ẗ', 'Ԛ'): 0.92, ('Ğ', 'Ṃ'): 0.93, ('ĥ', 'Ṃ'): 0.94, ('$', 'Ϛ'): 0.96, ('Ů', 'ᾷ'): 0.97, ('ẳ', 'Ẕ'): 0.98, ('ḟ', 'Ẕ'): 0.99, (' ', ' '): 0.0, ('ʬ', 'ʬ'): 1.0},
													('│', '├', '┝', '╌', '┤', '┥', '░', '▒', '▓', '┐', '┘', '┌', '└'))
	
	"""
	Auto generated console_graph fill character set by console_glyph_gen.py from 'font/CascadiaMono-Regular.ttf'.
	.⠄◞◛₄₁⠆◻▸≡<▲+■я≣¤†℮♠♦ґơ©īāϗhïßả┆ǿ/ÀÖÅĥ ◈
	⠒⠒◠▬▬═⠢⬧◂≡×▲◓◓ππ⬠⡰⬛♣❧ҷơt¡¡ųųχg¢¢ợ┮▆ț╔╔ ◈
	BD: │├┝╌┤┥ ░▒▓ ┐┘┌└
	Error: 114.783
	"""
	CASCADIA_MONO =         (       {('.', '⠒'): 0.15, ('⠄', '⠒'): 0.16, ('◞', '◠'): 0.27, ('◛', '▬'): 0.31, ('₄', '▬'): 0.32, ('₁', '═'): 0.33, ('⠆', '⠢'): 0.38, ('◻', '⬧'): 0.47, ('▸', '◂'): 0.49, ('≡', '≡'): 0.5, ('<', '×'): 0.52, ('▲', '▲'): 0.53, ('+', '◓'): 0.54, ('■', '◓'): 0.55, ('я', 'π'): 0.56, ('≣', 'π'): 0.57, ('¤', '⬠'): 0.59, ('†', '⡰'): 0.61, ('℮', '⬛'): 0.62, ('♠', '♣'): 0.63, ('♦', '❧'): 0.66, ('ґ', 'ҷ'): 0.69, ('ơ', 'ơ'): 0.71, ('©', 't'): 0.73, ('ī', '¡'): 0.75, ('ā', '¡'): 0.76, ('ϗ', 'ų'): 0.77, ('h', 'ų'): 0.78, ('ï', 'χ'): 0.79, ('ß', 'g'): 0.81, ('ả', '¢'): 0.89, ('┆', '¢'): 0.9, ('ǿ', 'ợ'): 0.92, ('/', '┮'): 0.94, ('À', '▆'): 0.96, ('Ö', 'ț'): 0.97, ('Å', '╔'): 0.99, (' ', ' '): 0.0, ('◈', '◈'): 1.0},
																	('│', '├', '┝', '╌', '┤', '┥', '░', '▒', '▓', '┐', '┘', '┌', '└'))
	
#+++++++++++++++++++++++++++++++
#++++++++++MODULE CODE++++++++++
#+++++++++++++++++++++++++++++++
def color_print(s, *styles):
	"""
	Use color to print to console. Longer name version of printing.cl_p.
	"""
	return cl_p(s, *styles)

def cl_p(s, *styles, boolean=False):
	"""
	Use color to print to console. Shorter name version of printing.color_print.
	Takes:
		-s, object to print (any type, but must be bool if boolean flag is set)
		-*styles, style variables
		-boolean, flag that automatically formats a boolean input as green or red string 

	Returns:
		-Styled string with auto-converted input s.
	"""
	if not __PRINT_COLORS__: return s
	
	#sanitize input
	if boolean and not type(s) is bool:
		raise TypeError("Keyword-only argument 'boolean' set to 'True', but argument 's' is of type '{}' (expected 'bool').".format(s.__class__.__name__))
	
	#set default style
	if not styles or len(styles) == 0:
		styles = (NORMAL)
	#set boolean style
	if boolean:
		styles = (*styles, Fore.GREEN) if s else (*styles, Fore.RED)
	
	return "{}{}{}".format(str().join(styles), s, RESET_ALL)
	
def get_time_str(secs, forceUnit=None):
	"""
	Helper function to format durations.

	Takes:
		-secs, seconds as numbers
		-forceUnit, can be str of value "ns/µs/ms/s/m/h" to force a specific unit to display

	Returns:
		-Formatted string with adequate units.
	"""
	#input sanitation
	if not type(secs) in (float, int):
		raise TypeError("Expected 'secs' to be of type 'int' or 'float' but received {}.".format(secs.__class__.__name__))
	if secs < 0 or math.copysign(1, secs) == -1:
		raise ValueError("Value for 'secs' must be positive (received {}).".format(secs)) 
	
	#++++FORCE UNIT++++
	if forceUnit:
		if type(forceUnit) is not str:
			raise TypeError("'forceUnit' must be of type 'str' (received {}).".format(forceUnit.__class__.__name__))
		if 		forceUnit == "ns": factor = 1000000000
		elif	forceUnit == "µs": factor = 1000000
		elif	forceUnit == "ms": factor = 1000
		elif	forceUnit == "s":  factor = 1
		elif	forceUnit == "m":  factor = 1/60
		elif	forceUnit == "h":  factor = 1/(60 * 60)
		else:
			raise ValueError("'forceUnit' must be one of 'ns/µs/ms/s/m/h' (received {}).".format(forceUnit))
		return "{:.3f}{}".format(secs * factor, forceUnit)
	
	#++++REGULAR FORMATTING++++
	if secs <= 0.0000001:
		return "{:.3f}ns".format(secs*1000000000)
	elif secs <= 0.0001:
		return "{:.3f}µs".format(secs*1000000)
	elif secs <= 0.1:
		return "{:.3f}ms".format(secs*1000)
	elif secs < 60:
		if round(60 - secs, 3) == 0: secs = 60 - 0.001
		return "{:.3f}s".format(secs)
	elif secs >= 60:
		return "{:n}m {:.3f}s".format(int(secs/60),secs%60)

def get_appropriate_time_unit(secs):
	if secs <= 0.0000001:
		return "ns"
	elif secs <= 0.0001:
		return "µs"
	elif secs <= 0.1:
		return "ms"
	elif secs < 60:
		return "s"
	elif secs >= 60:
		return "m"
	elif secs >= 3600:
		return "h"

def timedReturn(func):
	"""
	Same functionality as SEPTiming.timed decorator but returns the time and return-value as dictionary.
	"""
	def __wrap__(*args, **kwargs):
		sTime = time.perf_counter()
		r = func(*args, **kwargs)
		tTime = time.perf_counter() - sTime
		return {"return": r, "time": tTime}
	return __wrap__

def timed(func):
	"""
	Times the decorated function and prints the amount of time it took to execute. Returns the return-value of provided function.
	"""
	def __wrap__(*args, **kwargs):
		timedFunc = timedReturn(func)
		r = timedFunc(*args, **kwargs)
		print("{} took {} to execute.".format(cl_p(func.__name__, NAME), cl_p(get_time_str(r["time"]))))
		return r["return"]
	return __wrap__

# @timed
def console_graph(data, maxHeight=13, maxWidth=128, center=(10, 7, 2, 2), showScale=True, scaleSpacing=1, rounding=2, scaleInFront=False, \
	fillCharacters=FILL_CHARACTERS.SIMPLE, colorFunction=None, bgColor=NORMAL, \
	unitFormat=lambda x: (x,), useMiddleForUnit=False, relativeCursorPos=False, debug=True):

	#++++sort fillCharacters by descending value and grab 0 values for quicker access++++
	_sorted_characters = sorted(fillCharacters[0].items(), key=lambda item: item[1], reverse=True)
	zeroChars = _sorted_characters[-1][0] #get last entry key tuple after sorting, so should be key tuple where val is 0
	
	#++++set debug values++++
	spacer_char = " " #default value for spacer char
	if debug:
		spacer_char = "`"
		bgColor = BLUE #set zero char/background color to blue
		zeroChars = (fillCharacters[1][7], fillCharacters[1][8]) #set zero chars to something that can always be seen
	
	#++++add rounding and other shenanigans to unitFormat function++++
	def __decorate_unitFormat__(func):
		def __unitFormat_wrapper__(value):
			#format strings are too much of a hassle for numFormat to just concatenate them
			funcResult, numFormat = func(value), "{}{: ." + str(rounding) + "f}{}"
			
			#round output of unitFormat function int/float value to specified precision
			funcResult_rounded = None
			if type(funcResult[0]) in [int, float]: 
				funcResult_rounded = round(funcResult[0], rounding) if rounding > 0 else int(funcResult[0])
			
			if   len(funcResult) == 3:
			#if 3 arguments passed as tuple, display 'PREFIX + ROUNDED_VALUE + SUFFIX'
				return 	 numFormat.format(funcResult[1], funcResult_rounded, funcResult[2])
			elif len(funcResult) == 2:
			#if 2 arguments passed as tuple, display 					'ROUNDED_VALUE + SUFFIX'
				return 	 numFormat.format("",	   				 funcResult_rounded, funcResult[1])
			elif len(funcResult) == 1:
				if funcResult_rounded is not None:
				#if 1 argument passed as tuple, display 				'ROUNDED_VALUE'
					return numFormat.format("",	  				 funcResult_rounded, ""						)
				else:
				#unless said argument is not an int or float, in which case just convert argument to string and return that
					return str(funcResult[0])
			else:
				raise TypeError("unitFormat needs to return either 3, 2 or 1 value(s) of tuple format '([prefix,] value [, suffix])'")
		return __unitFormat_wrapper__
	#decorate unitFormat function
	unitFormat = __decorate_unitFormat__(unitFormat)
	
	#++++internal cell class++++
	class Cell:		"""
		Is used to represent a column of the final graph.
		"""
		def __init__(self, value, lastCell):
			self.height, self.color, self.data, self.lastCell, self.nextCell = \
						value, (str().join(bgColor),) * (int(abs(value)) + 1), list(), lastCell, None
			#			height, color defaults to being full of bg color,	 empty data, last cell, next cell
		
		#set colors and characters
		def __call__(self, ratio, minVal):
			"""
			Set the cells character data and set colors using colorFunction
			"""
			#scale height of cell and global minimum height of all cells
			_adjusted_val, minVal = self.height * ratio, minVal * ratio
			
			#set last and/or next cell to self if they are not set
			if not self.nextCell: self.nextCell = self
			if not self.lastCell: self.lastCell = self
			
			#colorFunction(height, change in local height, relative position from x-axis in percent, distance from curve in chars)
			if colorFunction:
				#change in value is just average slope over 3 cells in interval [1 before; 1 after]
				_change = (self.nextCell.height - self.lastCell.height) / 3
				_sign = 1 if _adjusted_val >= 0 else -1
				#set all color vals based on colorFunction, tuple for faster indexing
				#str join is used to concatenate all tuples of form (COLOR1, COLOR2, STYLE1, etc...) from colorFunction output
				self.color = tuple(str().join(\
									 colorFunction(_sign * (char_value / ratio), \
																 _change, \
																 (_sign * char_value) / (len(self.color) * ratio), \
																 int(_sign * _adjusted_val - char_value))) \
									 for char_value in range(0, int(_sign * _adjusted_val) + 1))
				
			#apply the char algorithm to fill each column effectively with the fill character set
			self.__set_chars__(_adjusted_val, ratio, minVal)
			
		def __set_chars__(self, value, ratio, yOffset):
			"""
			Fills one column/cell object with the character from fillCharacters set in order to
			form a smooth curve over the input data. Works by iteratively decreasing height by 1 and
			filling what space is left with the biggest character that fits within said space
			"""
			_background_color = str().join(bgColor)
			def __pad__(height, zeroCharIndex):
				self.data.extend([_background_color + zeroChars[zeroCharIndex] + RESET_ALL] * int(height))
			
			#++++pad below x-axis++++
			#by finding distance between current value (or x-axis if non-negative value) and minimum global value
			__pad__(abs(floor(yOffset) - min(value, 0)), 1)
			
			temp_data, unsignedValue = list(), abs(value)
			
			#fill graph to x-axis starting with largest characters
			for char, charValue in _sorted_characters:
				#skip 0 char (usually just the space bar character)
				if charValue == 0: continue
				
				#while character fits into height,
				#else move on to next char
				while charValue < unsignedValue:
					#invert index for color val  (total height - current height)
					temp_data.append(self.color[int(abs(value) - unsignedValue)] + char[0 if value >= 0 else 1] + RESET_ALL)
					#move down one line/row
					unsignedValue = unsignedValue - 1
			
			#if no character is small enough to fit into the space left, just add a top or bottom char extra
			if unsignedValue > 0:
				temp_data.append(_background_color + zeroChars[0 if value >= 0 else 1] + RESET_ALL)
			
			#add temp data reversed if we have a negative value or just add
			if value < 0: temp_data.reverse()
			self.data.extend(temp_data)
			
			#++++pad above x-axis++++
			#fill the rest required to have max height
			__pad__(maxHeight - len(self.data), 0)
		
		def __getitem__(self, key):
			"""
			usage: column[key/row], key is number of row, returns found row or empty string
			"""
			return self.data[key] if key < len(self.data) else str()
	
	#++++create list of cells++++
	_trimmed_data, cells  = data[-maxWidth:], list()
	
	#++++compute extreme values and scaling ratio++++
	#min value if negative, else just 0
	minVal, maxVal = min(0, min(_trimmed_data)), max(0, max(_trimmed_data))
	#distance between biggest and smallest value in graph
	diffInExtremeVals = maxVal - minVal
	
	#remove height of top scale from max height if scale is enabled
	if showScale: maxHeight = maxHeight - 2
	#how do we need to scale to make it fit max height?
	ratio = (maxHeight - 1) / diffInExtremeVals
	
	#++++calculate dimensions if scale is enabled++++
	width_side_scale = 0 #set width_side_scale to 0 as default
	if showScale:
		#the range of the y-axis scaled with the ratio to correctly represent character distances
		unitRange_offset = 1 if minVal != 0 else 0
		unitRange = range(int(minVal * ratio) - unitRange_offset, int(maxVal * ratio) + 1)
		#the half character offset used for middle-of-char unit
		use_middle_offset = 0.5 if useMiddleForUnit else 0
		#find longest word in this current setup by passing all values into the unitFormat function
		unitFormatDict = {char_val: unitFormat((char_val + use_middle_offset) / ratio) if not char_val % (scaleSpacing + 1) else spacer_char \
										 for char_val in unitRange}
		longestUnitFormat = max([len(v) for v in unitFormatDict.values()])
		#length of entire side scale
		width_side_scale = longestUnitFormat + 3
		
		#update max width
		maxWidth = maxWidth - width_side_scale
		#trim data so that entire graph fits in max width
		_trimmed_data = _trimmed_data[width_side_scale:]
	
	#set last cell value for first cell
	lastCell = None
	
	#loop over all values that fit in width and add a new cell to list
	for value in _trimmed_data:
		newCell = Cell(value, lastCell)
		cells.append(newCell) #append to main list
		
		if lastCell: lastCell.nextCell = newCell
		lastCell = newCell #set current to last cell
		
	
	for cell in cells: 
		cell(ratio, minVal) #call cells to set color and char data
	
	#++++add padding cells++++
	#height of graph = (max height of data) + (height of top scale [in this case either 2 * 0 or 2 * 1 since we have a bool])
	graph_struct_height = maxHeight + (2 * int(showScale))
	
	emptyCell = Cell(0, None)
	emptyCell.data = [spacer_char] * graph_struct_height
	
	#for left padding , insert empty cell at 0
	for _ in range(center[0]): cells.insert(0, emptyCell)
	#for right padding, append empty cell to list
	for _ in range(center[1]): cells.append(emptyCell)
	
	#++++add side and top scale++++
	if showScale:
		def _side_scale_sym(i):
			"""
			Short private function to find the correct symbol for the unit side scale
			"""
			if   i == unitRange.stop - 1 : return fillCharacters[1][11 if scaleInFront else  9] #_|
			elif i == unitRange.start		 : return fillCharacters[1][12 if scaleInFront else 10] #-|
			elif i % (scaleSpacing + 1)	 : return fillCharacters[1][0] #|
			elif scaleInFront					 	 : return fillCharacters[1][2] #|-
			else											 	 : return fillCharacters[1][5] #-|		
		
		#++++side scale++++
		#maxHeight + height of the top scale (i.e. 2 chars)
		scaleCell = Cell(maxHeight + 2, None)
		
		#set which kind of just function to use depending on location of scale
		scale_just = lambda s: s.rjust if scaleInFront else s.ljust
		
		#{Numbers}_{|}_ or _{|}_{Numbers} if scale not in front
		scaleCell.data.extend([("{num} {sym} " if scaleInFront else " {sym} {num}").format( \
														sym=_side_scale_sym(char_val), \
														num=cl_p(scale_just(unitFormatDict[char_val])(longestUnitFormat, spacer_char), BRIGHT)) \
													for char_val in unitRange])
		
		#add 2 extra rows side scale fill characters to match top scale
		scaleCell.data.extend([spacer_char * width_side_scale] * 2)
		
		#add after left padding, or after (left padding + data width) if scale not in front
		cells.insert(center[0] + (0 if scaleInFront else len(_trimmed_data)), scaleCell)
		
		#++++top scale++++
		#pad out all cells by 1 row so that the space below top scale is filled (i.e. a newline)
		for cell in cells: cell.data.extend(spacer_char)
		
		#start value is positive or 0, stop value is simply length of data
		start, stop = max(0, len(data) - maxWidth), len(data)
		#top scale is inserted into one cell located at the start of data graph (i.e. left padding + 1)
		top_scale_cell = cells[center[0] + 1]
		#length of middle segment is (length of data or maxWidth (whichever is smaller)) - (lengths of start/end strings) - (4 fill characters)
		top_scale_length_middle_segment = min(len(data), maxWidth) - len(str(start)) - len(str(stop)) - 4
		
		# {Start}_{|-}{----///----}{-|}_{Stop}
		top_scale_cell.data.extend(["{} {}{}{} {}".format(\
																	start, \
																	fillCharacters[1][1], \
																	fillCharacters[1][3] * top_scale_length_middle_segment, \
																	fillCharacters[1][4], \
																	stop)])
	
	#set newline to \n for absolute cursor position or set 
	#new line to an escape sequence moving cursor to correct
	#location if cursor position is set to relative
	newLine, debug_newline = "\n", "\\n" if debug else ""
	#width: (max width of graph part) + (padding left/right) + (width side scale)
	full_graph_struct_width = maxWidth + center[0] + center[1] + width_side_scale
	if relativeCursorPos:
		#move cursor back by width of entire graph structure (including length of debug newline chars!)
		newLine = REL_POS(-(full_graph_struct_width + len(debug_newline)), 0)
	#add debug color and character if desired
	if debug: newLine = cl_p(debug_newline, CYAN) + newLine
	
	#one empty line to pre- or append to output
	emptyLine = full_graph_struct_width * spacer_char + newLine
	
	#++++create the output string++++
	return emptyLine * center[2] + \
				 str().join([(str().join([col[row] for col in cells]) + newLine) for row in range(graph_struct_height - 1, 0 - 1, -1)]) + \
				 emptyLine * center[3]
	
def edgeChange(value, changeInValue, relativePosition, topDistance):
	if topDistance > 1: return (NORMAL)
	return (RED) if changeInValue < 0 else (GREEN)

def test_console_graph_demo(debug=True):
	#demo 1: linear graph
	print(console_graph(list(range(-100, 16, 1)) + list(range(32, 0, -1)), \
											colorFunction=edgeChange, scaleSpacing=1, rounding=2, \
											maxHeight=12, maxWidth=128, center=(10,0,1,1), showScale=True, \
											scaleInFront=False, fillCharacters=FILL_CHARACTERS.CONSOLAS, \
											bgColor=NORMAL, unitFormat=lambda x: (x,), \
											useMiddleForUnit=True, debug=debug), \
				end="")
	
	#demo 2: polynomial multiplied by sine function
	print(console_graph([10 * (1 + math.sin(0.3 * x)) + 0.2 * x**1.4 - 60 for x in range(0, 128)], \
											colorFunction=edgeChange, scaleSpacing=1, rounding=2, \
											maxHeight=12, maxWidth=128, center=(10,0,0,1), showScale=True, \
											scaleInFront=True, fillCharacters=FILL_CHARACTERS.CONSOLAS, \
											bgColor=NORMAL, unitFormat=lambda x: (x, " pt"), 
											useMiddleForUnit=False, debug=debug), \
				end="")
	
	#demo 3: random data from -50 to 50
	print(console_graph([random.random() * 100 - 50 for _ in range(0, 129)], \
											colorFunction=None, scaleSpacing=0, rounding=0, \
											maxHeight=12, maxWidth=116, center=(16,6,0,1), showScale=False, \
											scaleInFront=True, fillCharacters=FILL_CHARACTERS.CONSOLAS, \
											bgColor=(Back.CYAN, BRIGHT), unitFormat=lambda x: (x,), 
											useMiddleForUnit=False, debug=debug), \
				end="")

	#TEST CHARACTER SETS ON DEMO 2
	demo2_dataList = [10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)]
	character_sets = [FILL_CHARACTERS.MINIMAL, FILL_CHARACTERS.SIMPLE, FILL_CHARACTERS.CONSOLAS_MANUAL, FILL_CHARACTERS.CONSOLAS, FILL_CHARACTERS.CASCADIA_MONO, FILL_CHARACTERS.CASCADIA_MONO]
	demo2_height, demo2_width, demo2_center = 10, 54, (10, 0, 0, 1)
	
	_temp_rows = len(character_sets) // 2
	for _ in range((demo2_height + demo2_center[3]) * _temp_rows): print()
	print(REL_POS(-1, -(demo2_height + demo2_center[3]) * _temp_rows), end="", flush=True)
	
	for i, character_set in enumerate(character_sets):
		print(console_graph(demo2_dataList, \
												colorFunction=edgeChange, scaleSpacing=0, rounding=2, \
												maxHeight=demo2_height, maxWidth=demo2_width, center=demo2_center, showScale=True, \
												scaleInFront=False, fillCharacters=character_set, \
												bgColor=NORMAL, unitFormat=lambda x: (x,), relativeCursorPos=True, \
												useMiddleForUnit=False, debug=debug), \
					end="", flush=True)
			
		if i == len(character_sets) - 1: 
			print()
		elif i % _temp_rows == _temp_rows - 1:
			print(REL_POS(demo2_width + demo2_center[0], -(demo2_height + demo2_center[3]) * _temp_rows), end="", flush=True)

def test_console_graph_live_demo():
	os.system("clear")
	
	maxVals = 128
	times = list([0] * maxVals)
	while 1:
		for _ in range(6):
			sTime = time.time()
			for _ in range(50000):
				x = 5 * 3.28 + 3.1415
			times.append((time.time() - sTime) * 10000000)
		
		forcedUnit = get_appropriate_time_unit(statistics.fmean([x/10000000 for x in times[-maxVals:]]))
		
		output = console_graph(times, colorFunc=edgeChange, maxHeight=20, maxWidth=maxVals, \
													 unitFormat=lambda x: (get_time_str(x/10000000, forceUnit=forcedUnit),), rounding=3, \
													 debug=False)
		print(POS(0,0), end="")
		print(output, end="")
		
		sleep(0.001)

#+++++++++++++++++++++++++++
#++++++++++TESTING++++++++++
#+++++++++++++++++++++++++++		

class TestPrinting(unittest.TestCase):
	
	def test_get_time_str_return(self):
		self.assertMultiLineEqual(get_time_str(0),								"0.000ns")
		self.assertMultiLineEqual(get_time_str(0.0000000000001),	"0.000ns")
		self.assertMultiLineEqual(get_time_str(0.0000000153),			"15.300ns")
		self.assertMultiLineEqual(get_time_str(0.0000158), 				"15.800µs")
		self.assertMultiLineEqual(get_time_str(0.0001), 					"100.000µs")
		self.assertMultiLineEqual(get_time_str(0.0152), 					"15.200ms")
		self.assertMultiLineEqual(get_time_str(31.3156), 					"31.316s")
		self.assertMultiLineEqual(get_time_str(59.9999999), 			"59.999s")
		self.assertMultiLineEqual(get_time_str(59.93), 						"59.930s")
		self.assertMultiLineEqual(get_time_str(60), 							"1m 0.000s")
		self.assertMultiLineEqual(get_time_str(113.238), 					"1m 53.238s")
		self.assertMultiLineEqual(get_time_str(3620.001), 				"60m 20.001s")
					
	def test_get_time_str_forceUnit(self):
		self.assertMultiLineEqual(get_time_str(13.29732, forceUnit="ns"), "13297320000.000ns")
		self.assertMultiLineEqual(get_time_str(13.29732, forceUnit="µs"), "13297320.000µs")
		self.assertMultiLineEqual(get_time_str(13.29732, forceUnit="ms"), "13297.320ms")
		self.assertMultiLineEqual(get_time_str(13.29732, forceUnit="s"),  "13.297s")
		self.assertMultiLineEqual(get_time_str(13.29732, forceUnit="m"),  "0.222m")
		self.assertMultiLineEqual(get_time_str(13.29732, forceUnit="h"),  "0.004h")
		
	def test_get_time_str_TypeError_ValueError(self):
		with self.subTest(value="secs"):
			with self.assertRaises(TypeError):
				get_time_str("abc")
			
		with self.subTest(value="forceUnit"):
			with self.assertRaises(TypeError):
				get_time_str(3.23, True)
			
		with self.subTest(value="secs"):
			with self.assertRaises(ValueError):
				get_time_str(-0.01023)
			with self.assertRaises(ValueError):
				get_time_str(-1293)
			with self.assertRaises(ValueError):
				get_time_str(-0.0)
		
		with self.subTest(value="forceUnit"):			with self.assertRaises(ValueError):
				get_time_str(9.3927, forceUnit="d")
		
if __name__ == "__main__":
	test_console_graph_demo()
	
	unittest.main()