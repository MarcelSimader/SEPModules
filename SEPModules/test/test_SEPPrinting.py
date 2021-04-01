import math
import unittest
from random import random

from colorama import Back

from SEPModules.SEPPrinting import get_time_str, console_graph, FILL_CHARACTERS, REL_POS, NORMAL, BRIGHT, RED, GREEN


def test_console_graph_demo(debug=True):

	def edge_change(value, change_in_value, relative_position, top_distance):
		if top_distance > 1: return NORMAL
		return RED if change_in_value < 0 else GREEN

	# demo 1: linear graph
	print(console_graph(list(range(-2, 7, 1)) + list(range(10, 0, -1)),
						color_function=edge_change, scale_spacing=1, rounding=2,
						max_height=12, max_width=128, center=(10, 0, 1, 1), show_scale=True,
						scale_in_front=False, fill_characters=FILL_CHARACTERS.CONSOLAS,
						bg_color=NORMAL, unit_format_function=lambda x: (x,),
						use_middle_for_unit_position=True, debug=debug),
		  end="")

	# demo 2: polynomial multiplied by sine function
	print(console_graph([10 * (1 + math.sin(0.3 * x)) + 0.2 * x ** 1.4 - 60 for x in range(0, 128)],
						color_function=edge_change, scale_spacing=1, rounding=2,
						max_height=12, max_width=128, center=(10, 0, 0, 1), show_scale=True,
						scale_in_front=True, fill_characters=FILL_CHARACTERS.CONSOLAS,
						bg_color=NORMAL, unit_format_function=lambda x: (x, " pt"),
						use_middle_for_unit_position=False, debug=debug),
		  end="")

	# demo 3: random data from -50 to 50
	print(console_graph([random() * 100 - 50 for _ in range(0, 129)],
						color_function=None, scale_spacing=0, rounding=0,
						max_height=12, max_width=116, center=(16, 6, 0, 1), show_scale=False,
						scale_in_front=True, fill_characters=FILL_CHARACTERS.CONSOLAS,
						bg_color=(Back.CYAN, BRIGHT), unit_format_function=lambda x: (x,),
						use_middle_for_unit_position=False, debug=debug),
		  end="")

	#TEST CHARACTER SETS ON DEMO 2
	demo2_data_list = [10 * (1 + 2 * math.sin(0.3 * x)) + 0.2 * x**1.4 - 80 for x in range(0, 128)]
	character_sets = [FILL_CHARACTERS.MINIMAL,
					  FILL_CHARACTERS.SIMPLE,
					  FILL_CHARACTERS.CONSOLAS_MANUAL,
					  FILL_CHARACTERS.CONSOLAS,
					  FILL_CHARACTERS.CASCADIA_MONO,
					  FILL_CHARACTERS.CASCADIA_MONO]
	demo2_height, demo2_width, demo2_center = 10, 59, (10, 0, 0, 1)
	
	_temp_rows = len(character_sets) // 2
	for _ in range((demo2_height + demo2_center[3]) * _temp_rows): print()
	print(REL_POS(-1, -(demo2_height + demo2_center[3]) * _temp_rows), end="", flush=True)
	
	for i, character_set in enumerate(character_sets):
		print(console_graph(demo2_data_list,
							color_function=edge_change, scale_spacing=0, rounding=2,
							max_height=demo2_height, max_width=demo2_width, center=demo2_center, show_scale=True,
							scale_in_front=False, fill_characters=character_set,
							bg_color=NORMAL, unit_format_function=lambda x: (x,), relative_cursor_position=True,
							use_middle_for_unit_position=False, debug=debug),
			  end="", flush=True)
			
		if i == len(character_sets) - 1: 
			print()
		elif i % _temp_rows == _temp_rows - 1:
			print(REL_POS(demo2_width + demo2_center[0], -(demo2_height + demo2_center[3]) * _temp_rows), end="", flush=True)

class TestPrinting(unittest.TestCase):

	def test_get_time_str_return(self):
		self.assertMultiLineEqual(get_time_str(0), "0.000ns")
		self.assertMultiLineEqual(get_time_str(0.0000000000001), "0.000ns")
		self.assertMultiLineEqual(get_time_str(0.0000000153), "15.300ns")
		self.assertMultiLineEqual(get_time_str(0.0000158), "15.800µs")
		self.assertMultiLineEqual(get_time_str(0.0001), "100.000µs")
		self.assertMultiLineEqual(get_time_str(0.0152), "15.200ms")
		self.assertMultiLineEqual(get_time_str(31.3156), "31.316s")
		self.assertMultiLineEqual(get_time_str(59.9999999), "59.999s")
		self.assertMultiLineEqual(get_time_str(59.93), "59.930s")
		self.assertMultiLineEqual(get_time_str(60), "1m 0.000s")
		self.assertMultiLineEqual(get_time_str(113.238), "1m 53.238s")
		self.assertMultiLineEqual(get_time_str(3620.001), "60m 20.001s")
					
	def test_get_time_str_forceUnit(self):
		self.assertMultiLineEqual(get_time_str(13.29732, force_unit="ns"), "13297320000.000ns")
		self.assertMultiLineEqual(get_time_str(13.29732, force_unit="µs"), "13297320.000µs")
		self.assertMultiLineEqual(get_time_str(13.29732, force_unit="ms"), "13297.320ms")
		self.assertMultiLineEqual(get_time_str(13.29732, force_unit="s"), "13.297s")
		self.assertMultiLineEqual(get_time_str(13.29732, force_unit="m"), "0.222m")
		self.assertMultiLineEqual(get_time_str(13.29732, force_unit="h"), "0.004h")
		
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
		
		with self.subTest(value="forceUnit"):
			with self.assertRaises(ValueError):
				get_time_str(9.3927, force_unit="d")
		
if __name__ == "__main__":
	test_console_graph_demo()
	
	unittest.main()