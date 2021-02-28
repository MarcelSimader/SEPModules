from fontTools.ttLib import TTFont
from fontTools.ttLib.tables._c_m_a_p import CmapSubtable
import sys
from platform import system
from random import random
import math

#+++++++++++++++++Do not edit+++++++++++++++++
#function for charset weight
def logexp(bulge, bend, limit):
	if bulge < 2 or limit < 0 or limit > 1 or bend < 0:
		raise ValueError("bulge >= 2, 0 <= limit <= 1 and bend >= 0")
	def __logexp__(x):
		return math.log(1 + ((bulge - 2) * x) + (limit * x) ** bend, bulge)
	return __logexp__

#+++++++++++++++++++++++++++++++++++++++++
#++++++++++ VARIABLES TO CHANGE ++++++++++
#+++++++++++++++++++++++++++++++++++++++++

list_optimize = True #if True, generate a bunch of lists and find the best
total_list_tries = 10_000
amount_best_lists = 2

search_range = 50_000
rounding = 0 #higher -> less precise, lower -> more precise

lower_thresholds = (-400, 100) #bigger than [0] smaller than [1]
upper_thresholds = (1000, 1400) # 		---//---
wide_tall_thresholds = (1050, 1050) #	---//---

max_similar_chars = 50
similar_threshold_range = 1 #searches for similar chars in interval [-similar_threshold_range, similar_threshold_range]
max_similar_chars_wide_tall = 5

match_tolerance = 20 #match heights of characters in interval [-match_tolerance, match_tolerance]
allow_randomness_matching = True
remove_matching_chars_iteratively = False

final_charset_rounding = 2
final_charset_weight_func = lambda x: x
# final_charset_weight_func = logexp(2.0, 1.62, 1.0)

remove_duplicate_values_in_final_charset = True

space_chars = (" ", " ")
full_char = None #if None, picks random char

print_chars = True
print_progress = True
print_progress_verbose = False

#find these extra chars in the font or replace them with default ones
replacement_extra_chars = ["|", "|", "|", "-", "|", "|", "'", "+", "#", "|", "|", "|", "|"]
extra_chars 						= ["│", "├", "┝", "╌", "┤", "┥", "░", "▒" , "▓", "┐", "┘", "┌", "└"]

character_fill_name = None #if None, name is set to name of font automatically

#++++++++++++++++++++++++++++++++++++++++
#+++++++++++++++++ CODE +++++++++++++++++
#++++++++++++++++++++++++++++++++++++++++

_enable_color = system() in ["Linux"]

#check if <font-path> argument is supplied
if len(sys.argv) != 2:
	if _enable_color:
		sys.stderr.write("\033[38;2;225;60;110mToo many or too few arguments supplied. Usage: 'python glyph_height.py TTF_PATH'\n\033[0m")
	else:
		sys.stderr.write("Too many or too few arguments supplied. Usage: 'python glyph_height.py TTF_PATH'\n")
	sys.exit(1)

def _print_progress(msg, verbose=False):
	if not print_progress_verbose and verbose: return
	if print_progress: 
		if _enable_color:
			sys.stdout.write("\033[38;2;120;220;190m" + msg + "...\033[0m\n")
		else:
			sys.stdout.write(msg + "...\n")

#load up font and c-map
font = TTFont(sys.argv[1])
cmap = font["cmap"]

#retrieve unicode map table
unicode_map = cmap.getBestCmap()
#retrieve glyphs
glyphs = font.getGlyphSet()

#class and list for sorting glyphs
class _Char:
	def __init__(self, char, yMin, yMax, width):
		self.char, self.yMin, self.yMax, self.width = char, yMin, yMax, width
		
	def __repr__(self):
		return "<'{}' ({}, {}, {})>".format(self.char, self.yMin, self.yMax, self.width)


bound_list = []

#iterate over characters
_print_progress("Find chars in font")
for c in range(search_range):
	
	#check if characters exist in font
	if c in unicode_map and unicode_map[c] in glyphs:
		glyph = glyphs[unicode_map[c]]._glyph
		
		#check if character has bounds
		if all(el in dir(glyph) for el in ["yMin", "yMax", "xMin", "xMax"]):
			bound_list.append(_Char(chr(c), glyph.yMin, glyph.yMax, glyph.xMax - glyph.xMin))

_print_progress("Round char bound values")
#round values gathered to ~n digits
for char in bound_list:
	if rounding > 0:
		char.yMin  = int(round(char.yMin  / 10**rounding, rounding))
		char.yMax  = int(round(char.yMax  / 10**rounding, rounding))
		char.width = int(round(char.width / 10**rounding, rounding))

_print_progress("Sort and filter bound values")
#sort list by height
bound_list = sorted(bound_list, key=lambda c: c.yMax - c.yMin)

#find lower bound characters
lower_bound_list = [c for c in bound_list if c.yMin > lower_thresholds[0] and c.yMin < lower_thresholds[1]]

#find upper bound characters
upper_bound_list = [c for c in bound_list if c.yMax > upper_thresholds[0] and c.yMax < upper_thresholds[1]]

widest_tallest_list = sorted([c for c in bound_list if c.yMax - c.yMin > wide_tall_thresholds[0] and c.width > wide_tall_thresholds[1]], \
														 key=lambda c: c.width)

def filter_similar_chars(list, key, max_similar=max_similar_chars):
	max_char_count_dict = dict()
	res_list = []

	for c in list:
		#add to dict if not in it
		if key(c) not in max_char_count_dict:
			max_char_count_dict[key(c)] = 0
		
		#increment
		max_char_count_dict[key(c)] += 1
		
		#skip chars of same height that are seen more than allowed times
		if any([None if key(c) + n not in max_char_count_dict else max_char_count_dict[key(c) + n] > max_similar \
						for n in range(-similar_threshold_range, similar_threshold_range + 1)]):
			continue
		
		#print and add to result
		res_list.append(c)
	
	return res_list
	
final_lower 		= filter_similar_chars(lower_bound_list,    lambda c: c.yMax)
final_upper 		= filter_similar_chars(upper_bound_list,    lambda c: c.yMin)
final_wide_tall = filter_similar_chars(widest_tallest_list, lambda c: c.width, \
																			 max_similar=max_similar_chars_wide_tall)

def getList():
	global font, cmap, unicode_map, glyphs, search_range, rounding, lower_thresholds, upper_thresholds, wide_tall_thresholds, max_similar_chars, similar_threshold_range, max_similar_chars_wide_tall, match_tolerance, allow_randomness_matching, remove_matching_chars_iteratively, final_charset_rounding, final_charset_weight_func, remove_duplicate_values_in_final_charset, space_chars, full_char, print_progress, replacement_extra_chars, extra_chars, character_fill_name, final_lower, final_upper, final_wide_tall
	
	#find matching pairs of chars
	final_charset = dict()

	_print_progress("Find matching pairs for final char set", verbose=True)
	#iterate over longer list
	_longer_list_i = 0 if len(final_lower) > len(final_upper) else 1

	#scramble list if enabled0
	_maybe_scrambled_other_list = (final_lower, final_upper)[1 - _longer_list_i]
	if allow_randomness_matching:
		_maybe_scrambled_other_list = sorted(_maybe_scrambled_other_list, key=lambda x: random())

	#keep track of error
	_matching_error = 0

	for c1 in (final_lower, final_upper)[_longer_list_i]:
		
		c1_height = c1.yMax - c1.yMin
		
		#iterate over other list
		for c2 in _maybe_scrambled_other_list:
			
			#check if heights are within tolerance
			c2_height = c2.yMax - c2.yMin
			if c2_height > c1_height - match_tolerance and c2_height < c1_height + match_tolerance:
				
				#add error
				_matching_error = _matching_error + ((c2_height - c1_height) ** 2)
				
				#add pair to output
				final_charset[(str(c2.char), str(c1.char)) if _longer_list_i else (str(c1.char), str(c2.char))] = (c1_height + c2_height) / 2
				
				#possibly remove from list
				if remove_matching_chars_iteratively:
					if _longer_list_i:
						final_upper.remove(c1)
						final_lower.remove(c2)
					else:
						final_upper.remove(c2)
						final_lower.remove(c1)
						
				break #break out of this loop to find next pair			

	#mean of error
	_matching_error = _matching_error / len(final_charset)

	#normalize values
	max_value = max(final_charset.items(), key=lambda item: item[1])
	#exclude biggest value from set so that it can chose form wide + tall chars
	final_charset = {k: v / max_value[1] for k, v in final_charset.items() if k != max_value[0]}

	#apply weight function
	final_charset = {k: final_charset_weight_func(v) for k, v in final_charset.items()}

	#rounding
	final_charset = {k: round(v, final_charset_rounding) for k, v in final_charset.items()}

	#remove duplicate values
	if remove_duplicate_values_in_final_charset:
		_print_progress("Remove duplicates", verbose=True)
		
		seen = []
		for k, v in final_charset.items():
			
			if v not in seen:
				seen.append(v)
			else:
				final_charset[k] = "REMOVAL_FLAG"
		
		final_charset = {k: v for k, v in final_charset.items() if type(v) in (int, float)}

	#do more error calculations
	#quantify how even the spread of characters is
	_even_spread_rounded_list = [round(x, 1) for x in final_charset.values()]
	_even_spread_count = {round(k / 10, 1): 0 for k in range(0, 10+1)}
	_even_spread_seen = list()

	for v in _even_spread_rounded_list:
		if v in _even_spread_seen: continue
		
		_even_spread_count[v] = _even_spread_rounded_list.count(v)
		_even_spread_seen.append(v)

	_even_spread_expected_per_entry = sum(_even_spread_count.values()) / len(_even_spread_count)

	#final error is standard deviation from expected even linear spread or root of mean squared error
	_even_spread_count_error = math.sqrt(sum([(v - _even_spread_expected_per_entry) ** 2 for v in _even_spread_count.values()]) / len(_even_spread_count))

	#combine errors
	final_error = _matching_error * _even_spread_count_error


	_print_progress("Adding space and full characters", verbose=True)
	#add space character
	final_charset[space_chars] = 0.0
	#add full character
	_full = str(final_wide_tall[int(random() * len(final_wide_tall)) if type(full_char) is not int else full_char].char)
	final_charset[(_full, _full)] = 1.0

	#check extra chars and replace if needed
	_print_progress("Check extra chars", verbose=True)
	extra_chars = tuple([c if ord(c) in unicode_map and \
													unicode_map[ord(c)] in glyphs else \
											 replacement_extra_chars[i] for i, c in enumerate(extra_chars)])

	#set auto name
	if type(character_fill_name) is not str:
		character_fill_name = (font["name"].getDebugName(16) if font["name"].getDebugName(16) else \
																	font["name"].getDebugName(1)).replace(" ", "_").upper()
	
	return (final_charset, extra_chars, character_fill_name, final_error)

def print_list(l):
	print("{}\"\"\"\nAuto generated console_graph fill character set by console_glyph_gen.py from '{}'.\n{}\nBD: {}\nError: {}\n\"\"\"{}".format(\
																								 "\033[38;2;210;170;20m" if _enable_color else "", \
																								 sys.argv[1], \
																								 str("\n").join([str().join([k[n] for k in l[0].keys()]) for n in [0, 1]]), \
																								 str().join([c + (" " if i in [5, 8] else "") for i, c in enumerate(l[1])]), \
																								 str(round(l[3], 3)), \
																								 "\033[0m" if _enable_color else ""))
	print("{}{}{} = \t(\t{}, \n{}{})\n".format(\
																								"\033[38;2;225;60;110m" if _enable_color else "", \
																								l[2], \
																								"\033[0m" if _enable_color else "", \
																								str(l[0]), \
																								"\t" * (1 + len(l[2]) // 4), \
																								str(l[1])), end="\n")


def print_chars_func():
	global final_upper, final_lower, final_wide_tall
	if print_chars: 
		print("\n\nUpper bound chars: ".ljust(25), end="")
		for c in final_upper: print(c.char, end="")
		print("\n\nLower bound chars: ".ljust(25), end="")
		for c in final_lower: print(c.char, end="")
		print("\n\nWide tall chars: ".ljust(25), end="")
		for c in final_wide_tall: print(c.char, end="")
		print("\n\n")

#find best list
if list_optimize:
	final_charsets = list()
	for i in range(0, total_list_tries):
		_print_progress("{}List {} of {}".format("\n" + str().ljust(45, "~") + "\n" if print_progress_verbose else "", \
														str(i + 1).rjust(len(str(total_list_tries))), total_list_tries))
		if print_progress_verbose: print()
		
		l = getList()
		final_charsets.append(l)
	
	#sort by error
	final_charsets = sorted(final_charsets, key=lambda s: s[3])
	
	print("\nFinal result:\n\n")
	
	print_chars_func()
	
	#print best n sets
	for s in final_charsets[:amount_best_lists]:
		print_list(s)
	

#else just find one list
else:
	print("\nFinal result:\n\n")
	
	print_chars_func()
	
	print_list(getList())