"""
:Author: Marcel Simader
:Date: 17.07.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

import sys
import unittest

from SEPModules.SEPIO import ConsoleArguments, ConsoleArgsError

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ TESTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

# TODO: requires

# noinspection PyTypeChecker
class TestConsoleArgumentsMethods(unittest.TestCase):

	# Set up a console arg manager with inputs:
	#		args	: -a, -c 3, -d 			( -b   not set)
	#		kwargs: --_test=ok, --one=1 	(--two not set)
	#		pars	: install
	def setUp(self):
		# setup empty console arg manager
		self.CAM = ConsoleArguments([], [], no_load=True)

		# add fake inputs to the manager
		self.CAM._argnames, self.CAM._kwargnames = "ab:c:d", ["_test", "one=", "two"]
		self.CAM._requires_arg = {"a"  : False, "b": True, "c": True, "d": False, "_test": False, "one": True,
								  "two": False}
		self.CAM._args, self.CAM._kwargs = {"a": "", "c": "3", "d": ""}, {"_test": "ok", "one": "1"}
		self.CAM._pars = ["install", "quit"]

	def tearDown(self):
		del self.CAM

	def test_load_arguments(self):
		sys.argv = ["test_SEPIO.py", "-a", "-o", "-p", "3", "other_parameter",
					"--yes-this-is-a-long-long-flag", "value"]

		with self.assertRaises(ConsoleArgsError):
			cam0 = ConsoleArguments(["a", "p:", "o"], ["yes-this-is-a-long-long-flag="])

		sys.argv = ["test_SEPIO.py", "-a", "-o", "-p", "3",
					"--yes-this-is-a-long-long-flag", "value", "other_parameter"]

		cam1 = ConsoleArguments(["a", "o", "p:"], ["yes-this-is-a-long-long-flag="])
		self.assertEqual("aop:", cam1._argnames)
		self.assertListEqual(["yes-this-is-a-long-long-flag="], cam1._kwargnames)
		self.assertDictEqual({"a": False, "o": False, "p": True, "yes-this-is-a-long-long-flag": True},
							 cam1._requires_arg)
		self.assertDictEqual({"a": "", "o": "", "p": "3"}, cam1._args)
		self.assertDictEqual({"yes-this-is-a-long-long-flag": "value"}, cam1._kwargs)
		self.assertListEqual(["other_parameter"], cam1._pars)

	def test_cam_init_TypeError_ValueError(self):
		with self.assertRaises(TypeError):
			test_cam = ConsoleArguments(False, ["ananas", "one", "two="], no_load=True)
		with self.assertRaises(ValueError):
			test_cam = ConsoleArguments(["a", "b", "c:"], ["a=", "b=", "ef"], no_load=True)

	def test_cam_init_return(self):
		test_cam = ConsoleArguments(["a", "b", "c:"], ["ananas", "one", "two="], no_load=True)
		self.assertEqual("abc:", test_cam._argnames)
		self.assertListEqual(["ananas", "one", "two="], test_cam._kwargnames)
		self.assertDictEqual({"a": False, "b": False, "c": True, "ananas": False, "one": False, "two": True},
							 test_cam._requires_arg)

	def test_size_return(self):
		self.assertEqual(7, self.CAM.set_total)
		self.assertEqual(3, self.CAM.set_args)
		self.assertEqual(2, self.CAM.set_kwargs)
		self.assertEqual(2, self.CAM.set_pars)
		self.assertEqual(3, self.CAM.required)
		self.assertEqual(2, self.CAM.required_and_set)

	def test_contains_TypeError(self):
		with self.assertRaises(TypeError):
			a = object() in self.CAM

	def test_contains_return(self):
		with self.subTest(type='int'):
			self.assertIn(0, self.CAM)
			self.assertNotIn(-1, self.CAM)
			self.assertIn(1, self.CAM)
			self.assertNotIn(2, self.CAM)

		with self.subTest(type='str'):
			self.assertIn("c", self.CAM)
			self.assertNotIn("b", self.CAM)
			self.assertIn("one", self.CAM)
			self.assertNotIn("two", self.CAM)

		with self.subTest(type='list'):
			self.assertIn(["a", "d", "one", 0], self.CAM)
			self.assertNotIn(["a", "b", "one", 3], self.CAM)

		with self.subTest(type='dict'):
			self.assertIn({"a": "", "c": "3", "_test": "ok", 0: "install", 1: "quit"}, self.CAM)
			self.assertNotIn({"a": "3", "c": "3", "one": "1", 0: "uninstall", 2: "_test"}, self.CAM)

	def test_getitem_TypeError(self):
		with self.assertRaises(TypeError):
			a = self.CAM[["abc"]]

	def test_getitem_return(self):
		self.assertEqual("", self.CAM["a"])
		self.assertEqual("3", self.CAM["c"])
		self.assertEqual("ok", self.CAM["_test"])
		with self.assertRaises(KeyError):
			a = self.CAM["Idk"]
		self.assertEqual("install", self.CAM[0])
		self.assertEqual("quit", self.CAM[1])
		with self.assertRaises(KeyError):
			a = self.CAM[2]

	def test_iter(self):
		for item in self.CAM:
			with self.subTest(item=item):
				self.assertEqual((item[0], self.CAM[item[0]]), item)

if __name__ == "__main__":
	pass
