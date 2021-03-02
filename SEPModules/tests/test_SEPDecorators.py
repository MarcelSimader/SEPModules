import unittest

from SEPModules.SEPDecorators import check_type, timedReturn
	
def test_performance_check_type(n=1_000):
	def add(a :int, b:float) -> type(None):
		return None
		
	add_norm = add
	add_type = check_type()(add)
	
	_range = range(n)
	
	@timedReturn
	def __test_performance_check_type__(func, *args, **kwargs):
		for _ in _range:
			func(*args, **kwargs)
			
	times = {func.__name__: __test_performance_check_type__(func, 3, 5.5)["time"] for func in [add_norm, add_type]}
	
	for k, v in times.items():
		print("{} took {}.".format(cl_p(k, NAME), cl_p(get_time_str(v), NUMBER)))

class TestRequireType(unittest.TestCase):
	
	def setUp(self):
		def add(a :int, b :int) -> float:
			return a + b
		self.add = add
		
		def addLists(list1 :list, list2 :list, list3 :list):
			result = []
			for el in [list1, list2, list3]:
				result = result + el
			return result
		self.addLists = addLists
		
		def nothing():
			return
		self.nothing = nothing
		
		def rangeAdd(a :range(0,10), b :range(0, 20, 2)):
			return a + b
		self.rangeAdd = rangeAdd
		
	def tearDown(self):
		del self.add, self.addLists, self.nothing, self.rangeAdd
	
	def test_check_type_TypeError(self):
		with self.assertRaises(TypeError):
			_func = check_type(enable=3)(self.add)
			_func(2, 2)
			
		with self.assertRaises(TypeError):
			_func = check_type(enable=True, iterable=[int, float])(self.add)
			_func(2, 2)
			
	def test_check_type_simple(self):
		with self.assertRaises(TypeError):
			_func = check_type()(self.add)
			_func(2, 2.3)
			
		with self.assertRaises(TypeError):
			_func = check_type()(self.add)
			_func("test", 3)
		
	def test_check_type_iter(self):
		with self.assertRaises(TypeError):
			_func = check_type(iterable={"list1": int, "list2": float, "list3": str})(self.addLists)
			_func([2, 3], [3.3, True], ["test"])
			
	def test_check_type_result(self):
		with self.assertRaises(TypeError):
			_func = check_type()(self.add)
			_func(2, 2)
			
	def test_check_type_range(self):
		with self.assertRaises(ValueError):
			_func = check_type()(self.rangeAdd)
			_func(2, 11)
	
if __name__ == "__main__":
	test_performance_check_type()
	
	unittest.main()