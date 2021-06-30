"""
:Author: Marcel Simader
:Date: 29.06.2021

.. versionadded:: v0.1.2.dev1
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import os
from os import PathLike
from subprocess import STDOUT, call
from typing import Union, AnyStr, Tuple, List, Final, Collection, final, Literal

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@final
class LaTeXError(Exception):
	"""
	Exception class for the :py:mod:`SEPTeX` module.
	"""

	def __init__(self, msg : AnyStr, obj : Union[LaTeXDocument, LaTeXEnvironment]):
		self.msg = msg
		self.obj = obj

	def __str__(self):
		return self.msg

@final
class LaTeXHandler:
	"""
	:py:class:`LaTeXHandler` aids as container for lines of text to be written to either the preamble or body of a document.
	"""

	def __init__(self, indent_level : int=0):
		self._data : List[str] = list()
		self._offset : int = 0
		self._indent_level = indent_level

	@property
	def data(self) -> Tuple[str]:
		""" :return: a tuple of strings where each string is exactly one line in the document """
		return tuple(self._data)

	@property
	def offset(self) -> int:
		""" :return: the current cursor offset of the handler """
		return self._offset

	@property
	def indent_level(self):
		""" :return: what the default amount of indentation for this handler should be """
		return self._indent_level

	def write(self, s : AnyStr) -> None:
		"""
		Write string ``s`` to the handler.

		:param s: the string to write, can be any string of any length including line breaks
		"""
		# preprocess
		s_split = [str(("\t" * self._indent_level) + sub.replace("\n", "")) for sub in s.split("\n")]
		# add to data
		self._data.extend(s_split)

	def newline(self) -> None:
		""" Write an empty line. """
		self.write("")

	def readline(self, size : int=1) -> Tuple[str]:
		"""
		Read ``size`` lines from this document, starting at :py:attr:`offset`.

		:param size: how many lines to read
		:return: the lines to be read as tuple
		:raise ValueError: if size is negative
		"""
		if size < 0:
			raise ValueError(f"size parameter must be bigger than or equal to 0, received {size}")
		return tuple(self._data[self._offset : min(self._offset + size, len(self._data))])

	def __str__(self) -> str:
		return "\n".join(self._data)

class LaTeXDocument:
	"""
	:py:class:`LaTeXDocument` represents a LaTeX document that can be written to in a similar fashion as a text file. To do so,
	one must use the context manager of this object or retrieve the file path to write to it directly. The context manager
	will return two objects: the handler for writing to the preamble and the handler for writing to the body of the document.

	Example usage with the context manager: ::

		with LaTeXDocument("abc.tex") as (latex_document, pre, body):
			latex_document.use_package("abc123")
			body.write(r"This is some \LaTeX.")

	For extensions to the functionality of this class, see :py:class:`LaTeXEnvironment` as base class.

	..	warning::

		The data stored in and added to this :py:class:`LaTeXDocument` instance is only saved once the context manager
		is closed!

	"""

	LaTeXTemplate : Final = \
r"""
\documentclass[{}]{{{}}}

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% ~~~~~~~~~~~~~~~ PACKAGES ~~~~~~~~~~~~~~~
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{}

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% ~~~~~~~~~~~~~~~ PREAMBLE ~~~~~~~~~~~~~~~
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

{}

% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
% ~~~~~~~~~~~~~~~ BODY ~~~~~~~~~~~~~~~
% ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

\begin{{document}}

{}

\end{{document}}
"""

	def __init__(self,
				 path : Union[AnyStr, PathLike],
				 document_class : AnyStr="article",
				 document_options : AnyStr="a4paper, 12pt",
				 default_packages : Tuple[AnyStr]=("amsmath",),
				 document_template : AnyStr=LaTeXTemplate):
		self._path = path
		self._document_class = document_class
		self._document_options = document_options
		self._document_template = document_template

		self._package_list : List[AnyStr] = list()
		self._open = False

		# set up handlers
		self._packages = LaTeXHandler(indent_level=0)
		self._preamble = LaTeXHandler(indent_level=0)
		self._body 	   = LaTeXHandler(indent_level=1)

		# default packages
		for package_name in default_packages:
			self.use_package(package_name)

	def __require_closed__(self):
		if self._open:
			raise LaTeXError(f"The document {repr(self)} must be closed before accessing this function", self)

	def __require_open__(self):
		if not self._open:
			raise LaTeXError(f"The document {repr(self)} must be opened before accessing it", self)

	@property
	def path(self) -> PathLike:
		return os.path.abspath(self._path)

	@property
	def preamble(self) -> LaTeXHandler:
		""" :raise LaTeXError: if the document has not been opened """
		self.__require_open__()
		return self._preamble

	@property
	def body(self) -> LaTeXHandler:
		""" :raise LaTeXError: if the document has not been opened """
		self.__require_open__()
		return self._body

	@property
	def document_class(self) -> AnyStr:
		return self._document_class

	@property
	def document_options(self) -> AnyStr:
		return self._document_options

	@property
	def packages(self) -> Tuple[AnyStr]:
		return tuple(self._package_list)

	@property
	def open(self):
		return self._open

	def use_package(self, name : AnyStr) -> None:
		"""
		Include a usepackage statement in this document. This function checks the list of already included packages to
		avoid duplicates.

		:param name: the name of the package to include
		"""
		if name not in self._package_list:
			self._package_list.append(name)
			self._packages.write(f"\\usepackage{{{name}}}")

	def __fspath__(self) -> bytes:
		return str(self.path).encode("utf_8")

	def __enter__(self) -> Tuple[LaTeXDocument, LaTeXHandler, LaTeXHandler]:
		self._open = True
		return self, self._preamble, self._body

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		file = None
		try:
			file = open(self.path, "w")
			file.write(str(self))
		except (LaTeXError, OSError, IOError) as e:
			raise LaTeXError(f"Error while writing to LaTeX document at {repr(self)}", self) from e
		finally:
			self._open = False
			file.close()

			# throw exception
			if exc_type is not None:
				raise exc_val

			return True

	def to_pdf(self,
			   out_file_path : Union[PathLike, AnyStr],
			   overwrite : bool=False,
			   engine : Literal["pdflatex"]="pdflatex") -> None:
		"""
		Compile the LaTeX document at :py:attr:`path` to a PDF file. The document must be closed before attempting to perform
		this operation.

		:param out_file_path: which path to output the file to
		:param overwrite: whether or not to overwrite a file that already exists
		:param engine: which engine to use for conversion between the TeX and PDF files (specifically which string to use to
			call said engine), currently only ``pdflatex`` is supported

		:raise LaTeXError: if the document was still opened while calling this function or if there was an error while
			executing the engine command in the subshell
		:raise FileExistsError: if the file is already exists and ``overwrite`` is not set to True
		"""
		self.__require_closed__()

		error_msg = f"Error while converting {repr(self)} to PDF using {engine}"
		# working_dir = os.path.dirname(self.path)

		if not overwrite and os.path.isfile(out_file_path):
			raise FileExistsError(f"Cannot write PDF of {repr(self)} to {out_file_path}, if you want to overwrite files "
								  f"by default use overwrite=True in the arguments")
		out_file_path = os.path.abspath(out_file_path)
		if out_file_path.lower().endswith(".pdf"):
			out_file_path = out_file_path[:out_file_path.lower().rfind(".pdf")]
		out_dir  = os.path.dirname(out_file_path)
		out_file = os.path.basename(out_file_path)

		try:
			if engine == "pdflatex":
				return_value = call(f"pdflatex -output-directory '{out_dir}' -job-name '{out_file}' {os.path.basename(self.path)}",
									# cwd=working_dir,
									shell=True,
									stderr=STDOUT)
			else:
				raise NotImplementedError(f"Currently only 'pdftex' is supported, but received request for {engine}")

			if return_value < 0:
				raise LaTeXError(f"{error_msg}, return code: {return_value}", self)

		except OSError as e:
			raise LaTeXError(error_msg, self) from e

	def __str__(self) -> str:
		""" :return: a string representation of this document """
		return self._document_template.format(
					self._document_options,
					self._document_class,
					str(self._packages),
					str(self._preamble),
					str(self._body)
					)

	def __repr__(self) -> str:
		return f"LaTeXDocument(" \
			   f"path={self._path}, " \
			   f"packages={self._package_list}, " \
			   f"open={self._open})"

class LaTeXEnvironment:
	r"""
	Base class for an environment in a LaTeX document (see :py:class:`LaTeXDocument`). This class usually acts as base
	class for extensions that add simpler ways to write to an environment.

	Example usage with two nested context managers: ::

		with LaTeXEnvironment(document, "center") as env_center:
			with LaTeXEnvironment(env_center, "equation", required_packages=("amsmath",)) as env_eq:
				env_eq.write(r"\forall a, b \in \mathbb{R}, \exists c \in \mathbb{R} \colon a^2 + b^2 = c^2")

	"""

	BEGIN_TEMPLATE : Final = r"\begin{{{}}}{}"
	END_TEMPLATE   : Final = r"\end{{{}}}"

	def __init__(self,
				 parent_env : Union[LaTeXDocument, LaTeXEnvironment],
				 environment_name : AnyStr,
				 options : AnyStr="",
				 required_packages : Collection[AnyStr]=(),
				 indent_level : int=1):
		self._document = None
		self._parent_env = parent_env
		self._environment_name = environment_name
		self._options = options if options == "" else f"[{options}]"

		self._open = False

		# packages
		for package in required_packages:
			self.document.use_package(package)

		# write handler and alias
		self._handler = LaTeXHandler(indent_level)

	@final
	def __require_open__(self):
		if not self.open:
			raise LaTeXError(f"{repr(self)} must be opened using the context manager before accessing it", self)

	@final
	def __require_closed__(self):
		if not self.open:
			raise LaTeXError(f"{repr(self)} must be closed before accessing this function", self)

	@final
	@property
	def document(self) -> LaTeXDocument:
		"""
		:return: the root document of this environment stack
		:raise LaTeXError: if one of the parent environments is neither of type LaTeXDocument nor LaTeXEnvironment
		"""
		if self._document is None:
			self._document = self._parent_env
			while not isinstance(self._document, LaTeXDocument):
				if not isinstance(self._document, LaTeXEnvironment):
					raise LaTeXError(f"Found a value which is neither LaTeXDocument nor LaTeXEnvironment but {type(self._document)} "
									f"while processing root document in {repr(self)}", self)
				self._document = self._document._parent_env
		return self._document

	@final
	@property
	def parent_env(self) -> LaTeXDocument:
		return self._parent_env

	@final
	@property
	def environment_name(self) -> AnyStr:
		return self._environment_name

	@property
	def options(self) -> AnyStr:
		return self._options

	@property
	def begin_text(self) -> str:
		return self.BEGIN_TEMPLATE.format(self._environment_name, self._options)

	@property
	def end_text(self) -> str:
		return self.END_TEMPLATE.format(self._environment_name)

	@property
	def open(self):
		return self._open

	def __enter__(self) -> LaTeXEnvironment:

		# get handler of parent instance (body for document!)
		if isinstance(self._parent_env, LaTeXDocument):
			self._parent_handler = self._parent_env.body
		else:
			self._parent_handler = self._parent_env

		# write begin to parent env
		# self._parent_handler.newline()
		self._parent_handler.write(self.begin_text)

		self._open = True

		return self

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		# write handler data to parent env
		self._parent_handler.write(str(self._handler))
		# write end to parent env
		self._parent_handler.write(self.end_text)

		self._open = False

		# throw exception
		if exc_type is not None:
			raise exc_val

		return True

	def write(self, s : AnyStr) -> None:
		"""
		Shorthand for writing to the handler of this instance.
		:raise LaTeXError: if the document has not been opened
		"""
		self._write(s)

	def newline(self) -> None:
		"""
		Shorthand for writing a newline the handler of this instance.
		:raise LaTeXError: if the document has not been opened
		"""
		self._newline()

	@final
	def _write(self, s : AnyStr) -> None:
		self.__require_open__()
		self._handler.write(s)

	@final
	def _newline(self) -> None:
		self.__require_open__()
		self._handler.newline()

	def __str__(self) -> str:
		""" :return: a string representation of this environment """
		return f"{self.begin_text}\n{str(self._handler)}\n{self.end_text}"

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}(" \
			   f"parent={self._parent_env.__class__.__name__}, " \
			   f"options={self._options}, " \
			   f"opened={self._open})"

# TODO add/finish LaTeXEnvironment subclasses

@final
class Center(LaTeXEnvironment):

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 indent_level: int = 1):
		super(Center, self).__init__(parent_env,
									 environment_name="center",
									 options="",
									 required_packages=(),
									 indent_level=indent_level)

# @final
# class Equation(LaTeXEnvironment):
#
# 	def __init__(self,
# 				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
# 				 star : bool=True,
# 				 indent_level: int = 1):
# 		super(Equation, self).__init__(parent_env,
# 									   environment_name=f"equation{'*' if star else ''}",
# 									   options="",
# 									   required_packages=("amsmath",),
# 									   indent_level=indent_level)
#
# 	def write(self, s : Any) -> None:
# 		super(Equation, self).write(tex_string(s))

class TikZPicture(LaTeXEnvironment):

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 options: AnyStr = "",
				 indent_level: int = 1):
		super(TikZPicture, self).__init__(parent_env,
										  environment_name="tikzpicture",
										  options=options,
										  required_packages=("tikz",),
										  indent_level=indent_level)

	def abc(self):
		""" Test function. """
		for x in range(20):
			self.write(f"\draw[gray, thick] (-1, 2) -- ({x}, -4);")
