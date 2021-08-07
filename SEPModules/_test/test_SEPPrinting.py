"""
:Author: Marcel Simader
:Date: 17.07.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import unittest

from SEPModules.SEPPrinting import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ TESTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# noinspection PyTypeChecker
class TestPrinting(unittest.TestCase):

	def test_color_print(self):
		for _cl_s in [color_string, cl_s]:
			with self.subTest(func=_cl_s.__name__):
				for msg in [True, False, [], "this is a\n _test", u"unicode string\u0394", 1, 2, [1, 2], "ovo",
							(object())]:
					with self.subTest(type=type(msg).__name__):
						with self.subTest(boolean=False):
							self.assertMultiLineEqual(str(NORMAL) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, NORMAL))
							self.assertMultiLineEqual(str(RED) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, RED))
							self.assertMultiLineEqual(str(RED + BRIGHT) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, RED | BRIGHT))
							self.assertMultiLineEqual(str(RED & BRIGHT) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, RED & BRIGHT))
							self.assertMultiLineEqual(str(RED | BRIGHT) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, RED + BRIGHT))
							self.assertMultiLineEqual(str(msg) + str(RESET_ALL),
													  _cl_s(msg, AnsiControl()))

						with self.subTest(boolean=True):
							self.assertMultiLineEqual(str(NORMAL + (GREEN if msg else RED)) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, NORMAL, boolean=True))
							self.assertMultiLineEqual(str(NORMAL + BLUE + (GREEN if msg else RED))
													  + str(msg) + str(RESET_ALL),
													  _cl_s(msg, NORMAL + BLUE, boolean=True))
							self.assertMultiLineEqual(str(DIM + (GREEN if msg else RED)) + str(msg) + str(RESET_ALL),
													  _cl_s(msg, DIM, boolean=True))

	def test_get_time_str_return(self):
		self.assertMultiLineEqual("0.000ns", time_str(0))
		self.assertMultiLineEqual("0.000ns", time_str(0.0000000000001))
		self.assertMultiLineEqual("15.300ns", time_str(0.0000000153))
		self.assertMultiLineEqual("15.800µs", time_str(0.0000158))
		self.assertMultiLineEqual("100.000µs", time_str(0.0001))
		self.assertMultiLineEqual("15.200ms", time_str(0.0152))
		self.assertMultiLineEqual("31.316s", time_str(31.3156))
		self.assertMultiLineEqual("59.999s", time_str(59.9999999))
		self.assertMultiLineEqual("59.998s", time_str(59.9985))
		self.assertMultiLineEqual("59.930s", time_str(59.93))
		self.assertMultiLineEqual("1m 0.000s", time_str(60))
		self.assertMultiLineEqual("1m 53.238s", time_str(113.238))
		self.assertMultiLineEqual("60m 20.001s", time_str(3620.001))

		self.assertMultiLineEqual("0ns", time_str(0, n_digits=0))
		self.assertMultiLineEqual("0ns", time_str(0.0000000000001, n_digits=0))
		self.assertMultiLineEqual("15ns", time_str(0.0000000153, n_digits=0))
		self.assertMultiLineEqual("16µs", time_str(0.0000158, n_digits=0))
		self.assertMultiLineEqual("100µs", time_str(0.0001, n_digits=0))
		self.assertMultiLineEqual("15ms", time_str(0.0152, n_digits=0))
		self.assertMultiLineEqual("31s", time_str(31.3156, n_digits=0))
		self.assertMultiLineEqual("59s", time_str(59.9999999, n_digits=0))
		self.assertMultiLineEqual("59s", time_str(59.9985, n_digits=0))
		self.assertMultiLineEqual("59s", time_str(59.93, n_digits=0))
		self.assertMultiLineEqual("1m 0s", time_str(60, n_digits=0))
		self.assertMultiLineEqual("1m 53s", time_str(113.238, n_digits=0))
		self.assertMultiLineEqual("60m 20s", time_str(3620.001, n_digits=0))

	def test_get_time_str_force_unit(self):
		self.assertMultiLineEqual("13297320000.000ns", time_str(13.29732, force_unit="ns"))
		self.assertMultiLineEqual("13297320.000µs", time_str(13.29732, force_unit="µs"))
		self.assertMultiLineEqual("13297.320ms", time_str(13.29732, force_unit="ms"))
		self.assertMultiLineEqual("13.297s", time_str(13.29732, force_unit="s"))
		self.assertMultiLineEqual("0.222m", time_str(13.29732, force_unit="m"))
		self.assertMultiLineEqual("0.004h", time_str(13.29732, force_unit="h"))

		self.assertMultiLineEqual("13297320000.0ns", time_str(13.29732, n_digits=1, force_unit="ns"))
		self.assertMultiLineEqual("13297320.0µs", time_str(13.29732, n_digits=1, force_unit="µs"))
		self.assertMultiLineEqual("13297.3ms", time_str(13.29732, n_digits=1, force_unit="ms"))
		self.assertMultiLineEqual("13.3s", time_str(13.29732, n_digits=1, force_unit="s"))
		self.assertMultiLineEqual("0.2m", time_str(13.29732, n_digits=1, force_unit="m"))
		self.assertMultiLineEqual("0.0h", time_str(13.29732, n_digits=1, force_unit="h"))

	def test_get_time_str_TypeError_ValueError(self):
		with self.subTest(value="secs"):
			with self.assertRaises(TypeError):
				time_str("abc")

		with self.subTest(value="forceUnit"):
			with self.assertRaises(TypeError):
				time_str(3.23, object())

		with self.subTest(value="secs"):
			with self.assertRaises(ValueError):
				time_str(-0.01023)
			with self.assertRaises(ValueError):
				time_str(-1293)
			with self.assertRaises(ValueError):
				time_str(-0.0)

		with self.subTest(value="forceUnit"):
			with self.assertRaises(ValueError):
				time_str(9.3927, force_unit="d")
