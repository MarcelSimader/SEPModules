from distutils.core import setup, Extension

SEPCMaths_ext = Extension("SEPCMaths", ["SEPCMaths/SEPCMaths.c"])

setup(name="SEPModules",
			version="0.0.1",
			author="Marcel Simader",
			author_email="marcel0simader@gmail.com",
			packages=["SEPModules"],
			ext_modules=[SEPCMaths_ext])