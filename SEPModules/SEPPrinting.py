#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++

from colorama import Fore, Back, Style, Cursor, init as cl_init
import math
from math import ceil, floor

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

#+++++++++FUNCTIONS++++++++++

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

def console_graph(data, maxHeight=13, maxWidth=128, offset=(0, 5), center=(2, 2, 2, 2), \
									showScale=True, scaleSpacing=1, rounding=2, scaleInFront=False, \
									fillCharacters=FILL_CHARACTERS.SIMPLE, colorFunction=None, bgColor=NORMAL, \
									useFullWidth=True, appendZeroValue=False, zeroValue=0, \
									unitFormat=lambda x: (x,), useMiddleForUnit=False, \
									relativeCursorPos=False, debug=True):

	#++++sort fillCharacters by descending value and grab 0 values for quicker access++++
	_sorted_characters = sorted(fillCharacters[0].items(), key=lambda item: item[1], reverse=True)
	zeroChars = _sorted_characters[-1][0] #get last entry key tuple after sorting, so should be key tuple where val is 0
	
	#++++set debug values++++
	spacer_char = " " #default value for spacer char
	if debug:
		spacer_char = "`"
		bgColor = BLUE #set zero char/background color to blue
		zeroChars = (fillCharacters[1][7], fillCharacters[1][8]) #set zero chars to something that can always be seen
	
	#join background color for faster computations later
	bgColor = str().join(bgColor)
	
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
		def __init__(self, value, lastCell, color_tuple):
			self.height, self.color, self.data, self.lastCell, self.nextCell = \
						value, color_tuple, list(), lastCell, None
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
			def __pad__(height, zeroCharIndex):
				self.data.extend([bgColor + zeroChars[zeroCharIndex] + RESET_ALL] * int(height))
			
			#++++pad below x-axis++++
			#by finding distance between current value (or x-axis if non-negative value) and minimum global value
			if value >= 0:
				__pad__(max(ceil(abs(yOffset)), 				0), 1)
			else:
				__pad__(max(ceil(abs(yOffset)) + value, 0), 1)
			
			unsignedValueLoop = abs(value)
			temp_data, signedValue, valSign = list(), unsignedValueLoop, value < 0
			
			#fill graph to x-axis starting with largest characters and excluding last char (with value 0)
			for char, charValue in _sorted_characters[:-1]:
				
				#while character fits into height,
				#else move on to next char
				while charValue <= unsignedValueLoop:
					
					#invert index for color val  (total height - current height)
					temp_data.append(self.color[int(signedValue - unsignedValueLoop)] + char[valSign] + RESET_ALL)
					
					#move down one line/row
					unsignedValueLoop = unsignedValueLoop - 1
			
			#if no character is small enough to fit into the space left, just add a top or bottom char extra
			if unsignedValueLoop > 0:
				temp_data.append(bgColor + zeroChars[valSign] + RESET_ALL)
			
			# if offset[1] != 0:
				# check if we need to clip anything due to offsets
				# cut_lower, cut_upper = 	ceil(abs(yOffset)) - offset[1], \
																# floor(   yOffset)  + offset[1]
				# if value < 0:
					# if cut_lower > 0 and cut_lower < len(temp_data):
						# temp_data = temp_data[:cut_lower]
				# else:
					# if cut_upper > 0 and cut_upper < len(temp_data):
						# temp_data = temp_data[cut_upper:]
			
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
	cells = list()
	
	#trim data to fit graph
	if offset[0] > 0:
		_trimmed_data = data[-(maxWidth + offset[0]) : -offset[0]]
	else:
		_trimmed_data = data[-maxWidth:]
	
	#++++compute extreme values and scaling ratio++++
	#min value if negative, else just 0
	minVal, maxVal = min(0, min(_trimmed_data)), max(0, max(_trimmed_data))
	
	"""#TODO: think about if this should crash it or not
	#offset can't be bigger than or equal to maxValue
	if offset[1] > 0 and offset[1] >= maxVal:
		offset = (offset[0], maxVal - 1)
	
	#adjust values to offset
	for i, d in enumerate(_trimmed_data):
		if d < 0:
			_trimmed_data[i] = min(d + offset[1], 0)
		
		if d >= 0 and offset[1] > -minVal: #minval always negative so just invert
			_trimmed_data[i] = max(d - offset[1], 0)
	
	#recalculate extreme values
	minVal, maxVal = min(0, min(_trimmed_data)), max(0, max(_trimmed_data))"""
	
	_trimmed_data = [d - 15 for d in _trimmed_data]
	
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
		#trim data so that entire graph fits in max width but only if it would actually exceed bounds
		if len(_trimmed_data) > maxWidth: 
			_trimmed_data = _trimmed_data[width_side_scale:]
	
	#extend data with zeroValues if we want to always keep the graph at the same width
	if useFullWidth:
		if appendZeroValue:
			_trimmed_data.extend([zeroValue] * (maxWidth - len(_trimmed_data)))
		else:
			_trimmed_data[0:0] = [zeroValue] * (maxWidth - len(_trimmed_data))
	
	#set last cell value for first cell
	lastCell = None
	
	#initliaze with all bg color
	color_tuple = (NORMAL,) * maxHeight
	
	#loop over all values that fit in width and add a new cell to list
	for value in _trimmed_data:
		newCell = Cell(value, lastCell, color_tuple)
		cells.append(newCell) #append to main list
		
		if lastCell: lastCell.nextCell = newCell
		lastCell = newCell #set current to last cell
	
	#call cells to set color and char data
	[cell(ratio, minVal) for cell in cells]
	
	# adjust the data to offset graph
	# if offset[1] != 0:
		# for cell in cells:
			# pad above
			# if offset[1] > 0:
				# cell.data.extend([bgColor + zeroChars[0] + RESET_ALL] * offset[1])
				# cell.data = cell.data[offset[1]:]
			# pad below
			# else:
				# cell.data[0:0] = [bgColor + zeroChars[1] + RESET_ALL] * -offset[1]
				# cell.data = cell.data[:offset[1]] #offset is negative so counting from end!
	
	
	#++++add padding cells++++
	#height of graph = (max height of data) + (height of top scale [in this case either 2 * 0 or 2 * 1 since we have a bool])
	graph_struct_height = maxHeight + (2 * int(showScale))
	
	emptyCell = Cell(0, None, None)
	emptyCell.data = [spacer_char] * graph_struct_height
	
	#for left padding , insert empty cell at 0
	cells[0:0] = [emptyCell] * center[0]
	#for right padding, append empty cell to list
	cells.extend([emptyCell] * center[1])
	
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
		scaleCell = Cell(maxHeight + 2, None, None)
		
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
		[cell.data.extend(spacer_char) for cell in cells]
		
		#start value is positive or 0, stop value is simply length of data or 0
		start, stop = max(len(data) - len(_trimmed_data) - offset[0], 0), max(len(data) - offset[0], 0)
		#top scale is inserted into one cell located at the start of data graph (i.e. left padding + 1)
		top_scale_cell = cells[center[0] + 1]
		#length of middle segment is (length of data or maxWidth (whichever is smaller)) - (lengths of start/end strings) - (4 fill characters)
		top_scale_length_middle_segment = min(len(_trimmed_data), maxWidth) - len(str(start)) - len(str(stop)) - 4
		
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
				 str().join([(str().join([col[row] for col in cells]) + newLine) for row in range(graph_struct_height - 1, -1, -1)]) + \
				 emptyLine * center[3]