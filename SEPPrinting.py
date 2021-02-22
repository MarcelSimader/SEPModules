#+++++++++++++++++++++++++++++++++++++++++
#++++++++++Imports & Global Vars++++++++++
#+++++++++++++++++++++++++++++++++++++++++
from colorama import Fore, Back, Style, init as cl_init
from numbers import Number
import math
from math import ceil, floor
import random
import time
from time import sleep
import os

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

RED = (Fore.RED)
GREEN = (Fore.GREEN)
BLUE = (Fore.BLUE)
YELLOW = (Fore.YELLOW)
CYAN = (Fore.CYAN)
WHITE = (Fore.WHITE)
BLACK = (Fore.BLACK)

BRIGHT = (Style.BRIGHT)
DIM = (Style.DIM)
NORMAL = (Style.NORMAL)
RESET_ALL = (Style.RESET_ALL)

class FILL_CHARACTERS:
	"""
	#
	#
	"""
	minimal = {(" ", " "): 0, ("#", "#"): 1}

	"""
	_.:+I#
	‾˙:+I#
	"""
	simple = {(" ", " "): 0,   ("_", "‾"): 0.05, (".", "˙"): 0.1, (":", ":"): 0.3, \
						("+", "+"): 0.5, ("I", "I"): 0.7,  ("#", "#"): 1}

	"""
	_˷,ᵦı:+Ii⌠ʬ
	‾˜ ˟ᴵᵝ˸+!I⌡ʬ
	"""
	extended = {(" ", " "): 0  , ("_", "‾"): 0.02 , ("˷", "͂"): 0.1, (",", "˟"): 0.25, ("ᵦ", "ᴵ"):   0.3, \
							("ı", "ᵝ"): 0.4, (":", "˸"): 0.55, ("I", "!"): 0.70, ("⌠", "⌡"): 0.85, ("ʬ", "ʬ"): 1}

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

def console_graph(data, maxHeight=16, maxLength=128, \
	fillCharacters=FILL_CHARACTERS.extended, colorFunc=None, bgColor=NORMAL):

	#sort fillCharacters by descending value and grab 0 values for quicker access
	_sorted_characters = sorted(fillCharacters.items(), key=lambda item: item[1], reverse=True)
	zeroChars = _sorted_characters[-1][0][0:2]
	
	#internal cell class
	class Cell:
		def __init__(self, value, lastCell):
			self.height, self.color, self.data, self.lastCell, self.nextCell = \
						value, [bgColor] * (int(abs(value)) + 1), list(), lastCell, None
			
		#set colors and characters
		def __call__(self, ratio, minVal):
			#compute ratio for scaling
			_adjusted_val, minVal = self.height * ratio, minVal * ratio
			
			#colorFunc(height, change in local height, relative position from bottom in percent, distance from top in chars)
			if colorFunc:
				self.color = [colorFunc(value, \
															 (self.nextCell.height - self.lastCell.height) / 3, \
																value / len(self.color), \
																int((1 - (value / len(self.color)) if value >= 0 else (value / len(self.color))) * _adjusted_val)) \
													for value in (range(0, len(self.color) + 1) if _adjusted_val >= 0 else range(-len(self.color), 1))]
				
			self.__set_chars__(_adjusted_val, ratio, minVal)
			
		def __set_chars__(self, value, ratio, yOffset):
			
			#pad below x-axis
			yOffsetRange = range(int(floor(yOffset)), 0) if value >= 0 else \
										 range(int(floor(yOffset) - value), 0)
			
			for _ in yOffsetRange:
				self.data.append((zeroChars[1], bgColor))
			
			#fill graph to x-axis starting with largest characters
			temp_data, absValue, unsignedValue = list(), 0, abs(value)
			for char, charValue in _sorted_characters:
				if charValue == 0: break #stop loop if we hit zero-value character
				
				while charValue < unsignedValue: #while character fits into height
					#char[0] -> top character, char[1] -> bottom character (inverted)
					temp_data.append((char[0] if value >= 0 else char[1], self.color[int(ceil(absValue))]))
					
					unsignedValue, absValue = unsignedValue - 1, absValue + (1 / ratio) #move up/down one cell
				#else move on to next char
			
			#if no character is small enough to fit into the space left, just add a top or bottom char extra
			if unsignedValue > 0:
				temp_data.append((zeroChars[0 if value >= 0 else 1], bgColor))
			
			#add temp data reversed if we have a negative value
			if value < 0: temp_data.reverse()
			self.data.extend(temp_data)
			
			#pad above x-axis
			while len(self.data) < maxHeight: #fill the rest with smallest char in fillCharacters
				self.data.append((zeroChars[0], bgColor))
			
		#return tuple of form (character from data, color of cell)
		def __getitem__(self, key):
			return self.data[key]
	
	"""
	"""
	
	#create list of cells
	_trimmed_data, cells, lastCell = data[-maxLength:], list(), None
	for value in _trimmed_data: #only consider the last maxLength elements
		cell = Cell(value, lastCell) #(value, biggest value, last cell)
		if lastCell: lastCell.nextCell = cell #set next cell value of last cell
		lastCell = cell #set current to last cell
		
		cells.append(cell) #append to main list
	
	#set next and lastcell for first and last in cells list
	cells[ 0].lastCell = Cell(cells[ 0].height, None)
	cells[-1].nextCell = Cell(cells[-1].height, None)
	
	#compute extreme values and scaling ratio
	minVal = min(_trimmed_data) if min(_trimmed_data) < 0 else 0 #set min to 0 if greater equal than 0
	diffInExtremeVals = max(_trimmed_data) - minVal
	ratio = 1 if diffInExtremeVals <= maxHeight else (maxHeight - 1) / diffInExtremeVals
	#update the color of cells
	for cell in cells:
		cell(ratio, minVal)
	
	#create the output string
	outStrList = list()
	for i in range(maxHeight, 0, -1):
		for cell in cells:
			outStrList.append(cl_p(cell[i - 1][0], *cell[i - 1][1]))
		outStrList.append("\n")
		
	return str().join(outStrList)
	
def edgeChange(value, changeInValue, relativePosition, topDistance):
	if topDistance > 1: return (NORMAL)
	return (RED) if changeInValue < 0 else (GREEN)
	
print()
print(console_graph(list(range(-15, 16, 1)) + list(range(32, 10, -1)), colorFunc=edgeChange))
print(console_graph([10 * (1 + math.sin(0.3 * x)) + 0.2 * x**1.4 - 60 for x in range(0, 128)], colorFunc=edgeChange))
print(console_graph([random.random()*100 - 50 for x in range(0, 128)], colorFunc=edgeChange))

# print(console_graph([10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)], colorFunc=edgeChange, \
										# fillCharacters=FILL_CHARACTERS.minimal))
# print(console_graph([10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)], colorFunc=edgeChange, \
										# fillCharacters=FILL_CHARACTERS.simple))
# print(console_graph([10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)], colorFunc=edgeChange, \
										# fillCharacters=FILL_CHARACTERS.extended))

# os.system("clear")
# times = list()
# while 1:
	# for _ in range(5):
		# stime = time.time()
		# for _ in range(500):
			# x = 5 * 3.28 + 3.1415
		# times.append((time.time() - stime) * 100000)
	
	# output = console_graph(times, colorFunc=edgeChange)
	# print("\033[0;0H")
	# print(output, end="")
	# sleep(0.01)
	
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