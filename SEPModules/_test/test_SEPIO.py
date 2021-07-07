import unittest

from SEPModules.SEPIO import ConsoleArguments

#TODO: _test __load_arguments__ and requires

# noinspection PyTypeChecker
class TestConsoleArgumentsMethods(unittest.TestCase):
	
	#Set up a console arg manager with inputs:
	#		args	: -a, -c 3, -d 				( -b   not set)
	#		kwargs: --_test=ok, --one=1 	(--two not set)
	#		pars	: install
	def setUp(self):
		#setup empty console arg manager
		self.CAM = ConsoleArguments([], [], no_load=True)

		#add fake inputs to the manager
		self.CAM._argnames, self.CAM._kwargnames = "ab:c:d", ["_test", "one=", "two"]
		self.CAM.requires_arg = {"a": False, "b": True, "c": True, "d": False, "_test": False, "one": True, "two": False}
		self.CAM._args, self.CAM._kwargs = {"a":"", "c": "3", "d":""}, {"_test": "ok", "one": "1"}
		self.CAM._pars = ["install", "quit"]
		
	def tearDown(self):
		del self.CAM
	
	def test_cam_init_TypeError_ValueError(self):
		with self.assertRaises(TypeError):
			test_cam = ConsoleArguments(False, ["ananas", "one", "two="], no_load=True)
		with self.assertRaises(ValueError):
			test_cam = ConsoleArguments(["a", "b", "c:"], ["a=", "b=", "ef"], no_load=True)
			
	def test_cam_init_return(self):
		testCAM = ConsoleArguments(["a", "b", "c:"], ["ananas", "one", "two="], no_load=True)
		self.assertEqual(testCAM._argnames, "abc:")
		self.assertListEqual(testCAM._kwargnames, ["ananas", "one", "two="])
		self.assertDictEqual(testCAM.requires_arg, {"a": False, "b": False, "c": True, "ananas": False, "one": False, "two": True})
		
	def test_size_return(self):
		self.assertEqual(self.CAM.set_total,		5)
		self.assertEqual(self.CAM.set_args,		    3)
		self.assertEqual(self.CAM.set_kwargs,	    2)
		self.assertEqual(self.CAM.set_pars,  	    2)
		self.assertEqual(self.CAM.required,  	    3)
		self.assertEqual(self.CAM.required_and_set, 2)
		
	def test_contains_TypeError(self):
		with self.assertRaises(TypeError):
			object() in self.CAM
		
	def test_contains_return(self):
		with self.subTest(type='int'):
			self.assertTrue (0 	in self.CAM)
			self.assertFalse(-1 in self.CAM)
			self.assertTrue (1 	in self.CAM)
			self.assertFalse(2 	in self.CAM)

		with self.subTest(type='str'):
			self.assertTrue ("c" 		in self.CAM)
			self.assertFalse("b" 		in self.CAM)
			self.assertTrue ("one" 		in self.CAM)
			self.assertFalse("two" 		in self.CAM)

		with self.subTest(type='list'):
			self.assertTrue (["a", "d", "one", 0] in self.CAM)
			self.assertFalse(["a", "b", "one", 3] in self.CAM)

		with self.subTest(type='dict'):
			self.assertTrue ({"a":"",   "c": "3", "_test": "ok", 0: "install",   1: "quit"} 	in self.CAM)
			self.assertFalse({"a": "3", "c": "3", "one": "1",   0: "uninstall", 2: "_test"} 	in self.CAM)
		
	def test_getitem_TypeError(self):
		with self.assertRaises(TypeError):
			self.CAM[["abc"]]
		
	def test_getitem_return(self):
		self.assertTrue (self.CAM["a"])
		self.assertEqual(self.CAM["c"]   	 , "3")
		self.assertEqual(self.CAM["_test"]	 , "ok")
		self.assertEqual(self.CAM["Idk"] 	 , None)
		self.assertEqual(self.CAM[0]		 , "install")
		self.assertEqual(self.CAM[1]		 , "quit")
		self.assertEqual(self.CAM[2]		 , None)
		
	def test_iter(self):
		for item in self.CAM:
			with self.subTest(item=item):
				self.assertEqual(item, (item[0], self.CAM[item[0]]))
	
if __name__ == "__main__":
	pass