#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++
from colorama import Fore, Back, Style, Cursor, init as cl_init
from numbers import Number
import math, random, statistics
from math import ceil, floor, log
import os, sys, time
from time import sleep

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

POS = lambda x=0,y=0: (Cursor.POS(x, y))
UP, DOWN, FORWARD, BACK = (Cursor.UP), (Cursor.DOWN), (Cursor.FORWARD), (Cursor.BACK)

RESET_ALL = (Style.RESET_ALL)

class FILL_CHARACTERS:
	"""
	#
	#
	BD: | - | `+#
	"""
	minimal = (	{	(" ", " "): 0, ("#", "#"): 1}, \
							("|", "-", "|", "`", "+", "#"))

	"""
	_.:+I#
	‾˙:+I#
	BD: | - | `+#
	"""
	simple = (	{	(" ", " "): 0,   ("_", "‾"): 0.05, (".", "˙"): 0.1, (":", ":"): 0.3, \
								("+", "+"): 0.5, ("I", "I"): 0.7,  ("#", "#"): 1}, \
							("|", "-", "|", "`", "+", "#"))

	"""
	_˷,ᵦı:+Ii⌠ʬ
	‾˜ ˟ᴵᵝ˸+!I⌡ʬ
	BD: ├ ╌ ┤ ░▒▓
	"""
	extended = (	{	(" ", " "): 0  , ("_", "‾"): 0.02, ("˷", "͂"): 0.1 , (",", "˟"): 0.25, ("ᵦ", "ᴵ"): 0.3, \
									("ı", "ᵝ"): 0.4, (":", "˸"): 0.55, ("I", "!"): 0.70, ("⌠", "⌡"): 0.85, ("ʬ", "ʬ"): 1}, \
								("├", "╌", "┤", "░", "▒", "▓"))

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
	fillCharacters=FILL_CHARACTERS.extended, colorFunc=None, bgColor=NORMAL, \
	unitFormat=lambda x: (x), debug=True):

	#sort fillCharacters by descending value and grab 0 values for quicker access
	_sorted_characters = sorted(fillCharacters[0].items(), key=lambda item: item[1], reverse=True)
	zeroChars = tuple(_sorted_characters[-1][0][0:2])
	
	#add rounding to unitFormat
	def __decorate_unitFormat__(func):
		def __unitFormat_wrapper__(value):
			res = func(value)
			if len(res) == 3:
				return "{}{:G}{}".format(res[1], round(res[0], rounding) if rounding > 0 else int(res[0]), res[2])
			elif len(res) == 2:
				return   "{:G}{}".format(				 round(res[0], rounding) if rounding > 0 else int(res[0]), res[1])
			else:
				if type(res[0]) is not str:
					return   "{:G}".format(				 round(res[0], rounding) if rounding > 0 else int(res[0]))
				else:
					return res[0]
			return "#ERROR"
		return __unitFormat_wrapper__
	unitFormat = __decorate_unitFormat__(unitFormat)
	
	"""
	"""
	TEST = 1
	debugChar, newLine = " ", "\n"
	if debug:
		debugChar, newLine = "`", "\\n\n"
		bgColor = BLUE
		zeroChars = (fillCharacters[1][3], fillCharacters[1][5])
	
	#internal cell class
	class Cell:
		def __init__(self, value, lastCell):
			self.height, self.color, self.data, self.lastCell, self.nextCell = \
						value, [bgColor] * (int(abs(value)) + 1), list(), lastCell, None
			
		#set colors and characters
		def __call__(self, ratio, minVal):
			#compute ratio for scaling
			_adjusted_val, minVal = self.height * ratio, minVal * ratio
			
			#colorFunc(height, change in local height, relative position from x-axis in percent, distance from curve in chars)
			if colorFunc:
				colorLen = len(self.color)
				_change = ((self.nextCell.height if self.nextCell else self.height) - (self.lastCell.height if self.lastCell else self.height)) / 3
				self.color = tuple(str().join(colorFunc((1 if _adjusted_val >= 0 else -1) * (value / ratio), \
																							  _change, \
																							  (1 if _adjusted_val >= 0 else -1) * value / (colorLen * ratio), \
																							  int(abs(_adjusted_val) - value))) \
																		for value in range(0, int(abs(_adjusted_val)) + 1))
				
			self.__set_chars__(_adjusted_val, ratio, minVal)
			
		def __set_chars__(self, value, ratio, yOffset):
			
			#pad below x-axis
			self.data.extend([str().join(bgColor) + zeroChars[1] + RESET_ALL] * int(abs(floor(yOffset) - (value if value < 0 else 0))))
			
			#fill graph to x-axis starting with largest characters
			temp_data, unsignedValue = list(), abs(value)
			for char, charValue in _sorted_characters:
				while charValue < unsignedValue: #while character fits into height
					#char[0] -> top character, char[1] -> bottom character (inverted)
					temp_data.append(self.color[int(abs(value) - unsignedValue)] + char[0 if value >= 0 else 1] + RESET_ALL)
					unsignedValue = unsignedValue - 1 #move up/down one cell
				#else move on to next char
			
			#if no character is small enough to fit into the space left, just add a top or bottom char extra
			if unsignedValue > 0:
				temp_data.append(str().join(bgColor) + zeroChars[0 if value >= 0 else 1] + RESET_ALL)
			
			#add temp data reversed if we have a negative value
			if value < 0: temp_data.reverse()
			self.data.extend(temp_data)
			
			#fill the rest with smallest char in fillCharacters
			self.data.extend([str().join(bgColor) + zeroChars[0] + RESET_ALL] * (maxHeight - len(self.data)))
			
		#return tuple of form (character from data, color of cell)
		def __getitem__(self, key):
			return self.data[key] if key < len(self.data) else str()
	
	#create list of cells
	_trimmed_data, cells  = data[-maxWidth*TEST::TEST], list()
	lastCell = Cell(_trimmed_data[0], None)
	
	#compute extreme values and scaling ratio
	minVal = min(_trimmed_data) if min(_trimmed_data) < 0 else 0 #set min to 0 if greater equal than 0
	diffInExtremeVals = max(_trimmed_data) - minVal
	ratio = 1 if diffInExtremeVals <= maxHeight else (maxHeight - 1) / diffInExtremeVals
	
	for value in _trimmed_data: #only consider the last maxWidth elements
		cell = Cell(value, lastCell) #(value, biggest value, last cell)
		lastCell.nextCell = cell #set next cell value of last cell
		lastCell = cell #set current to last cell
		
		cells.append(cell) #append to main list
	
	for cell in cells: cell(ratio, minVal) #update the color and chars of cell
	
	#add cell in front for spacing
	emptyCell = Cell(0, None)
	emptyCell.data = [debugChar] * (maxHeight + (2 if showScale else 0))
	for _ in range(center[0]): cells.insert(0, emptyCell)
	for _ in range(center[1]): cells.append(emptyCell)
	
	#add scale as last cell with text
	if showScale:
		countDigits = lambda x: int(log(x, 10)) + 1 if x > 1 else 1
		
		#side scale
		longestUnitFormat = max([\
															len(unitFormat(x/ratio)) \
															for x in range(int(minVal * ratio) - (1 if minVal else 0), int(max(_trimmed_data) * ratio) + 1)\
														if not (x % (scaleSpacing + 1))])
		
		scaleCell = Cell(maxHeight, None)
			
		scaleCell.data.extend([("{}  " if scaleInFront else "  {}").format( \
															(unitFormat(value/ratio) \
														if not value % (scaleSpacing + 1) \
															else "  ") \
														.ljust(longestUnitFormat, debugChar)) \
													for value in range(int(minVal * ratio) - (1 if minVal else 0), int(max(_trimmed_data) * ratio) + 1)])
		
		cells.insert(center[0] if scaleInFront else len(_trimmed_data) + center[0], scaleCell)
		
		#top scale
		start, stop = len(data) - maxWidth * TEST if len(data) > maxWidth * TEST else 0, len(data)
		cells[center[0]].data.extend([str(), \
																		"{}{} {}{}{} {}".format(\
																		str().ljust(longestUnitFormat, debugChar) if scaleInFront else str(), \
																		start, \
																		fillCharacters[1][0], \
																		str().center(min(len(data)//TEST, maxWidth) - countDigits(start) - countDigits(stop) - 4, fillCharacters[1][1]), \
																		fillCharacters[1][2], \
																		stop)])
	
	#create the output string
	return newLine * center[2] + \
				 str().join([str().join([cell[i] for cell in cells]) + "\n" for i in range(maxHeight + (1 if showScale else 0), -1, -1)]) + \
				 newLine * center[3]
	
def edgeChange(value, changeInValue, relativePosition, topDistance):
	if topDistance > 1: return (NORMAL)
	return (RED) if changeInValue < 0 else (GREEN)

# print(console_graph(list(range(-100, 16, 1)) + list(range(32, 0, -1)), colorFunc=edgeChange))
# print(console_graph([10 * (1 + math.sin(0.3 * x)) + 0.2 * x**1.4 - 60 for x in range(0, 128)], colorFunc=edgeChange))
# print(console_graph([random.random()*100 - 50 for x in range(0, 128)], colorFunc=edgeChange))

# print(console_graph([10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)], colorFunc=edgeChange, \
										# fillCharacters=FILL_CHARACTERS.minimal))
# print(console_graph([10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)], colorFunc=edgeChange, \
										# fillCharacters=FILL_CHARACTERS.simple))
# print(console_graph([10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)], colorFunc=edgeChange, \
										# fillCharacters=FILL_CHARACTERS.extended))

# os.system("clear")
# times = list()
# stdcon = curses.initscr()
# while 1:
	# for _ in range(6):
		# sTime = time.time()
		# for _ in range(500):
			# x = 5 * 3.28 + 3.1415
		# times.append((time.time() - sTime) * 10000000)
	
	# maxVals = 128
	
	# forcedUnit = get_appropriate_time_unit(statistics.geometric_mean([x/10000000 for x in times[-maxVals:]]))
	
	# output = console_graph(times, colorFunc=edgeChange, maxHeight=20, maxWidth=maxVals, \
												 # unitFormat=lambda x: [get_time_str(x/10000000, forceUnit=forcedUnit)], rounding=3, \
												 # debug=False, scaleInFront=True)
	# print(POS(0,0), end="")
	# print(output, end="")
	# curses.start_color()
	# curses.use_default_colors()
	# for i in range(curses.COLORS - 1):
		# curses.init_pair(i + 1, i, -1)
		# stdcon.addstr(str(i), curses.color_pair(i + 1))
	# stdcon.addstr(0, 0, output)
	# stdcon.refresh()
	# sleep(0.001)

# curses.endwin()

# rand = [random.random()*100 - 50 for x in range(0, 128)]

# for _ in range(1_00):
	# console_graph(rand, colorFunc=edgeChange)

#+++++++++++++++++++++++++++
#++++++++++TESTING++++++++++
#+++++++++++++++++++++++++++		

class TestPrinting(unittest.TestCase):
	
	def test_get_time_str_return(self):
		self.assertMultiLineEqual(get_time_str(0),								"0.000ns")
		self.assertMultiLineEqual(get_time_str(0.0000000000001),	"0.000ns")
		self.assertMultiLineEqual(get_time_str(0.0000000153),		"15.300ns")
		self.assertMultiLineEqual(get_time_str(0.0000158), 			"15.800µs")
		self.assertMultiLineEqual(get_time_str(0.0001), 					"100.000µs")
		self.assertMultiLineEqual(get_time_str(0.0152), 					"15.200ms")
		self.assertMultiLineEqual(get_time_str(31.3156), 				"31.316s")
		self.assertMultiLineEqual(get_time_str(59.9999999), 			"59.999s")
		self.assertMultiLineEqual(get_time_str(59.93), 					"59.930s")
		self.assertMultiLineEqual(get_time_str(60), 							"1m 0.000s")
		self.assertMultiLineEqual(get_time_str(113.238), 				"1m 53.238s")
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
	unittest.main()