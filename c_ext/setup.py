from distutils.core import setup, Extension

SEPCMaths = Extension("SEPCMaths", sources=["SEPCMaths.c"])

setup(name="SEPCMaths", version="0.1", \
			description="""Package that provides additional built-in functions to speed up various algorithms in the SEPMaths module.""", \
			ext_modules=[SEPCMaths])