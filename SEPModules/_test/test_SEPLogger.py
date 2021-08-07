"""
:Author: Marcel Simader
:Date: 17.07.2021
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from SEPModules.SEPLogger import *

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ TESTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

logger = Logger()

print("~" * 30)

@logger.log_class(level=DefaultLevel.DEBUG, include_arguments=True)
class A:

	def __init__(self, msg: str, *, other=None):
		self._msg = msg

	@staticmethod
	def test():
		print("tested")

	@classmethod
	def test_class(cls, test=0):
		print("classed")

	@property
	def msg(self):
		return self._msg

	def run(self):
		for x in range(500000):
			y = x * x
		print("ran", self._msg)

	def __gt__(self, other):
		return True

	def __call__(self, *args, **kwargs):
		print("called")

	def __str__(self):
		return "abc"

	def __repr__(self):
		return "abcrepr"

if __name__ == '__main__':
	a = A("hello")
	print(a.msg)
	a.run()
	a.run()
	a = A("hewwo")
	a.run()
	A.test()
	print(a > 3)
	a = A("hewwo", other=[1, 2, 3])
	a()
	A.test_class()
	A.test_class(test=5)
	print(a.msg)
	a()

	print("~" * 30)
