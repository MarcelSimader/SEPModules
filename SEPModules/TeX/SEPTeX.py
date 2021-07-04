"""
:Author: Marcel Simader
:Date: 29.06.2021

.. versionadded:: v0.1.2.dev1
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

from __future__ import annotations

import abc
import inspect
import os
import shutil
from fractions import Fraction
from inspect import getframeinfo, stack
from numbers import Number
from os import PathLike
from subprocess import STDOUT, call
from typing import Union, AnyStr, Tuple, List, Final, Collection, final, Literal, Any, Set, Optional, NoReturn

from SEPModules.maths.SEPAlgebra import AlgebraicStructure
from SEPModules.maths.SEPMaths import Rational

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def vspace(length: Union[AnyStr, Number]) -> str:
	""" Inserts a vertical space of length ``length`` in the document. """
	return r"\vspace*{{{}}}".format(length)

def parentheses(text: Any) -> str:
	return r"\left( {} \right)".format(text)

def brackets(text: Any) -> str:
	return r"\left[ {} \right]".format(text)

def braces(text: Any) -> str:
	return r"\left\{{ {} \right\}}".format(text)

def tex_maths_string(s: Any) -> str:
	r"""
	Formats the given object in a LaTeX-friendly way for **math mode**.

    +----------------------+-------------------------------------------------------------------------------------+
    | Supertype            | Behaviour                                                                           |
    +----------------------+-------------------------------------------------------------------------------------+
    | SEPMaths.Rational	   | print as LaTeX fraction                                                             |
    +----------------------+-------------------------------------------------------------------------------------+
    | Fraction             | print as LaTeX fraction                                                             |
    +----------------------+-------------------------------------------------------------------------------------+
    | Set                  | print set in curly braces, call :py:func:`tex_maths_string` on                       |
    |                      | each object of the set                                                              |
    +----------------------+-------------------------------------------------------------------------------------+
    | Tuple or List        | print list or tuple in square brackets, call :py:func:`tex_maths_string`             |
    |                      | on each object of the set except if the object is a string                          |
    +----------------------+-------------------------------------------------------------------------------------+
    | Algebraic Structure  | print the set using :py:func:`tex_maths_string`, and format the operator             |
    |                      | names as text, both set and operators are in parentheses                            |
    +----------------------+-------------------------------------------------------------------------------------+

    Default behaviour is to call the ``__str__`` method of an object.

	:param s: the object to format
	:return: a string which can be written to a LaTeX document in a math mode environment
	"""
	text_f = r"\text{{{}}}"

	formats = {
			Rational             : lambda o: f"{'-' if o < 0 else ''}\\frac{{{abs(o.a)}}}{{{o.b}}}",
			Fraction             : lambda o: f"{'-' if o < 0 else ''}\\frac{{{abs(o.numerator)}}}{{{o.denominator}}}",
			Set                  : lambda o: braces(", ".join([tex_maths_string(el) for el in s])),
			(Tuple, List,)       : lambda o: brackets(
					", ".join([text_f.format(el) if isinstance(el, str) else tex_maths_string(el) for el in s])),
			AlgebraicStructure   : lambda o: parentheses(
					f"{tex_maths_string(o.elements)}, {', '.join([text_f.format(op.__name__) for op in o.binary_operators])}")
			}

	# if sub-type of dict key
	for super_type, format_function in formats.items():
		if isinstance(s, super_type):
			return format_function(s)

	# default case
	return str(s)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CLASSES ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@final
class LaTeXError(Exception):
	"""
	Exception class for the :py:mod:`SEPTeX` module.
	"""

	def __init__(self, msg: AnyStr, obj: Union[LaTeXResource, LaTeXHandler]):
		self.msg = msg
		self.obj = obj

	def __str__(self) -> str:
		return f"{self.msg} (raised from {repr(self.obj)})"

class LaTeXResource(abc.ABC):
	"""
	Abstract base class for marking a class as having an open and closed state, along with text data of some sort. This
	class requires :py:meth:`__str__` to be implemented to provide the contents of the handlers to any other caller.

	In addition to the open and closed states, one can configure the resource to allow multiple openings. The default
	behaviour is to throw an exception if the resource is opened a second time. The opening and closing is implemented as
	context manager, with :py:meth:`__enter__` triggering an opening and :py:meth:`__exit__` triggering a closing. The
	private helper methods :py:meth:`__require_closed__`, :py:meth:`__require_open__`, and :py:meth:`__require_virgin__`
	are provided to check these states.
	"""

	@staticmethod
	@final
	def __get_context__(n: int = 1) -> str:
		"""
		:return: the name of the function which called this function, ``n`` frames above the scope of the caller of this function.
		"""
		try:
			frame = getframeinfo(stack()[n + 1][0])
			return frame.function
		finally:
			del frame

	def __init__(self, *, can_reopen=False):
		self._open = False
		self._open_counter = 0
		self._can_reopen = can_reopen

	@property
	def open(self) -> bool:
		return self._open

	def __enter__(self) -> None:
		if self._open_counter > 0 and not self._can_reopen:
			raise LaTeXError(f"Cannot open the {self.__class__.__name__} object more than once", self)
		self._open = True
		self._open_counter += 1

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		self._open = False
		return exc_val is None

	@final
	def __require_state__(self, state_name: str, frame_depth: int = 1) -> NoReturn:
		raise LaTeXError(
				f"The {self.__class__.__name__} object must {state_name} before accessing "
				f"'{self.__get_context__(n=frame_depth + 1)}'",
				self)

	@final
	def __require_closed__(self, frame_depth: int = 1) -> None:
		"""
		Requires a resource to be closed.

		:param frame_depth: how many stack frames to go backwards in order to retrieve the name of the function which
			represents the public API call which caused the error

		:raise LaTeXError: if the resource is open when this function is called
		"""
		if self.open:
			self.__require_state__("be closed", frame_depth)

	@final
	def __require_open__(self, frame_depth: int = 1) -> None:
		"""
		Requires a resource to be opened.

		:param frame_depth: how many stack frames to go backwards in order to retrieve the name of the function which
			represents the public API call which caused the error

		:raise LaTeXError: if the resource is closed when this function is called
		"""
		if not self.open:
			self.__require_state__("be open", frame_depth)

	@final
	def __require_virgin__(self, frame_depth: int = 1):
		"""
		Requires a resource to have never been opened.

		:param frame_depth: how many stack frames to go backwards in order to retrieve the name of the function which
			represents the public API call which caused the error

		:raise LaTeXError: if the resource has been opened once before when this function is called
		"""
		if self._open_counter > 0:
			self.__require_state__("not have been opened at any point", frame_depth)

	@abc.abstractmethod
	def __str__(self) -> str:
		raise NotImplementedError("Subclasses of LaTeXResource must implement this method")

@final
class LaTeXHandler:
	r"""
	:py:class:`LaTeXHandler` aids as container for lines of text to be written to a document. This class can automatically
	apply a specific level of indentation and pseudo soft-wrap lines that are too long.

	..	note::

		The algorithm for the soft-wrap will insert ``\n`` newline characters in available spaces of each "line entry" of
		this instance, which does not cause the line to be split into multiple entries but still places a new line in the
		final document.

	:param indent_level: the number of tab character to place at the beginning of each line
	:param line_wrap_length: keyword-only argument, when set to an int this value dictates how long a line can be before
		a pseudo soft-wrap is applied during the :py:meth:`write` operations of this instance
	"""

	def __init__(self, indent_level: int = 0, *, line_wrap_length: Optional[int] = None):
		self._data: List[str] = list()
		self._offset: int = 0
		self._indent_level = indent_level
		self._line_wrap_length = line_wrap_length

	@property
	def data(self) -> Tuple[str]:
		""" :return: a tuple of strings where each string is exactly one line in the document """
		return tuple(self._data)

	@property
	def offset(self) -> int:
		""" :return: the current cursor offset of the handler """
		return self._offset

	@property
	def indent_level(self) -> int:
		""" :return: what the default amount of indentation for this handler should be """
		return self._indent_level

	@property
	def line_wrap_length(self) -> Optional[int]:
		"""
		:return: the number of characters before a line is split into two using a soft-wrap, **this means that in the handler,
			the line will still only have one entry but contain the newline character**
		"""
		return self._line_wrap_length

	def write(self, s: AnyStr) -> None:
		"""
		Write string ``s`` to the handler.

		:param s: the string to write, can be any string of any length including line breaks
		"""
		# preprocess
		s_split = [str(("\t" * self._indent_level) + sub.replace("\n", "")) for sub in s.split("\n")]

		# wrap long lines
		if self._line_wrap_length is not None:
			for i, temp_s in enumerate(s_split):
				# search as long as we are past the limit
				cur_pos = 0
				comment = False
				while len(temp_s) >= self._line_wrap_length:
					space_pos = temp_s.find(" ", self._line_wrap_length)
					comment |= "%" in temp_s[:self._line_wrap_length]
					# check if line can be wrapped at all
					if space_pos != -1:
						newline = "\n%" if comment else "\n"
						cur_pos += space_pos
						s_split[i] = s_split[i][:cur_pos] + newline + s_split[i][cur_pos:]
						cur_pos += len(newline) + 1
						temp_s = temp_s[space_pos + 1:]
					else:
						# give up, no way to wrap
						break

		# add to data
		self._data.extend(s_split)

	def newline(self) -> None:
		""" Write an empty line. """
		self.write("")

	def readline(self, size: int = 1) -> Tuple[str]:
		"""
		Read ``size`` lines from this document, starting at :py:attr:`offset`.

		:param size: how many lines to read
		:return: the lines to be read as tuple
		:raise ValueError: if size is negative
		"""
		if size < 0:
			raise ValueError(f"size parameter must be bigger than or equal to 0, received {size}")
		return tuple(self._data[self._offset: min(self._offset + size, len(self._data))])

	def __len__(self):
		""" :return: the number of lines stored in the :py:attr:`data` attribute """
		return len(self._data)

	def __str__(self) -> str:
		return "\n".join(self._data)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ DOCUMENT AND ENVIRONMENTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LaTeXDocument(LaTeXResource):
	"""
	:py:class:`LaTeXDocument` represents a LaTeX document that can be written to in a similar fashion as a text file. To
	do so, one must use the context manager of this object or retrieve the file path to write to it directly. The context
	manager will return three objects: the created document itself, the handler for writing to the preamble, and the
	handler for writing to the body of the document.

	Example usage with the context manager: ::

		with LaTeXDocument("abc.tex") as (latex_document, pre, body):
			latex_document.use_package("abc123")
			body.write(r"This is some \LaTeX.")

	For extensions to the functionality of this class, see :py:class:`LaTeXEnvironment` as base class.

	..	warning::

		The data stored in and added to this :py:class:`LaTeXDocument` instance is only saved once the context manager
		is closed!

	:param path: the path to the main ``.tex`` file
	:param document_class: the name of the document class to include at the start of the document
	:param document_options: the options to pass to the chosen document class
	:param default_packages: the packages to include right at the beginning of initialization
	:param title: the title of the document
	:param subtitle: the subtitle of the document, is ignored unless ``title`` is not ``None``
	:param author: the author of the document
	:param line_wrap_length: keyword-only argument, if set to an int this value will dictate how long a line can be
		before a pseudo soft-wrap is applied (see :py:class:`LaTeXHandler` for details)

	"""

	LaTeXTemplate: Final = inspect.cleandoc(
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
			)

	def __init__(self,
				 path: Union[AnyStr, PathLike],
				 document_class: AnyStr = "article",
				 document_options: AnyStr = "a4paper, 12pt",
				 default_packages: Tuple[AnyStr] = ("amsmath",),
				 title: Optional[AnyStr] = None,
				 subtitle: Optional[AnyStr] = None,
				 author: Optional[AnyStr] = None,
				 *,
				 show_page_numbers: bool = False,
				 line_wrap_length: Optional[int] = None):
		super(LaTeXDocument, self).__init__()

		self._path = path
		self._document_class = document_class
		self._document_options = document_options

		self._title = title
		self._subtitle = subtitle
		self._author = author
		self._has_title = self._title is not None or self._author is not None
		self._show_page_numbers = show_page_numbers

		self._package_list: List[AnyStr] = list()

		# set up handlers
		self._packages = LaTeXHandler(indent_level=0)
		self._preamble = LaTeXHandler(indent_level=0, line_wrap_length=line_wrap_length)
		self._body = LaTeXHandler(indent_level=1, line_wrap_length=line_wrap_length)

		# default packages
		for package_name in default_packages:
			self.use_package(package_name)

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
	def line_wrap_lengths(self) -> Tuple[Optional[int], Optional[int]]:
		""" :return: the line wrap lengths of preamble and body, see :py:attr:`LaTeXHandler.line_wrap_length` for details """
		return self._preamble.line_wrap_length, self._body.line_wrap_length

	@property
	def title(self) -> Optional[AnyStr]:
		return self._title

	@property
	def subtitle(self) -> Optional[AnyStr]:
		return self._subtitle

	@property
	def author(self) -> Optional[AnyStr]:
		return self._author

	@property
	def show_page_numbers(self) -> bool:
		return self._show_page_numbers

	def __fspath__(self) -> bytes:
		return str(self.path).encode("utf_8")

	def use_package(self, package: Union[AnyStr, Tuple[AnyStr]]) -> None:
		"""
		Include a usepackage statement in this document. This function checks the list of already included packages to
		avoid duplicates.

		:param package: the name or names of the package to include
		"""
		if not isinstance(package, Tuple):
			package = (package,)
		for p in package:
			if p not in self._package_list:
				self._package_list.append(p)
				self._packages.write(f"\\usepackage{{{p}}}")

	def page_break(self) -> None:
		""" Inserts a page break. """
		self.body.write(r"\newpage")
		self.body.newline()

	def __init_document__(self):
		"""
		This function should be called when the context manager of a document is entered. It sets up basic things like
		the page numbering and titles.
		"""
		# write title
		if self._has_title:
			self._body.write(r"\maketitle")
			self._body.newline()
			if self._title is not None:
				self.use_package("relsize")
				self._preamble.write(f"\\title{{{self._title}"
									 + (
											 r"}" if self._subtitle is None else f"\\\\[0.4em]\\smaller{{{self._subtitle}}}}}"))
			if self._author is not None:
				self._preamble.write(f"\\author{{{self._author}}}")

		# page numbers
		if not self._show_page_numbers:
			self._preamble.write(r"\pagenumbering{gobble}")

	def __enter__(self) -> Tuple[LaTeXDocument, LaTeXHandler, LaTeXHandler]:
		super(LaTeXDocument, self).__enter__()
		self.__init_document__()
		return self, self._preamble, self._body

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		file = None
		try:
			# write to actual file
			file = open(self.path, "w")
			file.write(str(self))
		except (LaTeXError, OSError, IOError) as e:
			raise LaTeXError(f"Error while writing to '.tex' file", self) from e
		finally:
			if file is not None:
				file.close()
			# super call!
			return super(LaTeXDocument, self).__exit__(exc_type, exc_val, exc_tb)

	def to_pdf(self,
			   out_file_path: Union[PathLike, AnyStr],
			   overwrite: bool = False,
			   delete_aux_files: bool = True,
			   engine: Literal["pdftex", "pdflatex"] = "pdflatex",
			   custom_options: AnyStr = "") -> None:
		"""
		Compile the LaTeX document at :py:attr:`path` to a PDF file. The document must be closed before attempting to perform
		this operation.

		:param out_file_path: which path to output the file to
		:param overwrite: whether or not to overwrite a file that already exists
		:param delete_aux_files: delete the generated auxiliary files after compilation of the document is complete
		:param engine: which engine to use for conversion between the TeX and PDF files (specifically which string to use to
			call said engine), currently only ``pdflatex`` is supported
		:param custom_options: options to directly pass to the engine which are not included as argument to this function

		:raise LaTeXError: if the document was still opened while calling this function or if there was an error while
			executing the engine command in the subshell
		:raise FileExistsError: if the file is already exists and ``overwrite`` is not set to True
		"""
		self.__require_closed__()

		if not overwrite and os.path.isfile(out_file_path):
			raise FileExistsError(
					f"Cannot write PDF of {repr(self)} to {out_file_path}, if you want to overwrite files "
					f"by default use overwrite=True in the arguments")

		out_file_path = os.path.abspath(out_file_path)
		if out_file_path.lower().endswith(".pdf"):
			out_file_path = out_file_path[:-4]

		out_dir = os.path.dirname(out_file_path)
		out_aux_dir = os.path.join(out_dir, '.aux')
		out_file = os.path.basename(out_file_path)

		error_msg = f"Error while converting to PDF using {engine}"
		try:
			if engine == "pdflatex" or engine == "pdftex":
				return_value = call(
						f"pdflatex -output-directory '{out_dir}' -job-name '{out_file}' {os.path.basename(self.path)} "
						f"-quiet -aux-directory '{out_aux_dir}' {custom_options}",
						shell=True,
						stderr=STDOUT)
			# TODO: support more engines
			else:
				raise NotImplementedError(f"Currently only 'pdflatex' is supported, but received request for {engine}")

			if return_value < 0:
				raise LaTeXError(f"{error_msg}, return code: {return_value}", self)
		except OSError as e:
			raise LaTeXError(error_msg, self) from e
		finally:
			# delete aux files
			if delete_aux_files:
				shutil.rmtree(out_aux_dir)

	def __str__(self) -> str:
		""" :return: a string representation of this document """
		return self.LaTeXTemplate.format(
				self._document_options,
				self._document_class,
				str(self._packages),
				str(self._preamble),
				str(self._body)
				)

	def __repr__(self) -> str:
		try:
			# windows might throw an error for paths across drives
			path = os.path.relpath(self._path)
		except OSError:
			path = self._path
		return f"LaTeXDocument(" \
			   f"path={path}, " \
			   f"packages={self._package_list}, " \
			   f"open={self._open})"

class LaTeXEnvironment(LaTeXResource):
	r"""
	Base class for an environment in a LaTeX document (see :py:class:`LaTeXDocument`). This class usually acts as base
	class for extensions that add simpler ways to write to an environment.

	Example usage with two nested context managers: ::

		with LaTeXEnvironment(document, "center") as env_center:
			with LaTeXEnvironment(env_center, "equation", required_packages=("amsmath",)) as env_eq:
				env_eq.write(r"\forall a, b \in \mathbb{R}, \exists c \in \mathbb{R} \colon a^2 + b^2 = c^2")

	..	note::

		When inheriting from this class, one should usually only overwrite the following methods: :py:meth:`__init__`,
		:py:meth:`write`, and :py:meth:`newline`. Overwriting other methods is allowed if needed, unless marked as final.

		It is highly recommended to use either a super call to this class or at least the private methods :py:meth:`_write`
		and :py:meth:`_newline` to handle internal write calls to the LaTeXHandler instance, since these check additional
		requirements.

	:param parent_env: the parent environment or document to this environment
	:param environment_name: the name of the environment, this value is put for the ``\begin`` and ``\end`` commands
	:param options: the options to pass to the environment, this value is put after the ``\begin`` command
	:param required_packages: the packages which are required to use this environment
	:param indent_level: the number of tab characters to indent this environment relative to the parent environment
	"""

	BEGIN_TEMPLATE: Final = r"\begin{{{}}}{}"
	END_TEMPLATE: Final = r"\end{{{}}}"

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 environment_name: AnyStr,
				 options: AnyStr = "",
				 required_packages: Collection[AnyStr] = (),
				 indent_level: int = 1):
		super(LaTeXEnvironment, self).__init__()

		self._document = None
		self._parent_env = parent_env
		self._environment_name = environment_name
		self._options = options if options == "" else f"[{options}]"

		# packages
		for package in required_packages:
			self.document.use_package(package)

		# write handler and alias
		self._handler = LaTeXHandler(indent_level)

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
					error_doc = type(self._document)
					self._document = None
					raise LaTeXError(
							f"Found a value which is neither LaTeXDocument nor LaTeXEnvironment but {error_doc} "
							f"while processing root document", self)
				self._document = self._document._parent_env
		return self._document

	@final
	@property
	def parent_env(self) -> LaTeXDocument:
		return self._parent_env

	@final
	@property
	def parent_handler(self) -> LaTeXHandler:
		# get handler of parent instance (body for document!)
		if isinstance(self._parent_env, LaTeXDocument):
			return self._parent_env.body
		else:
			return self._parent_env._handler

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

	def __enter__(self) -> LaTeXEnvironment:
		super(LaTeXEnvironment, self).__enter__()
		self.document.__require_open__()

		# write begin to parent env
		self.parent_handler.write(self.begin_text)

		return self

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		try:
			# write handler data to parent env
			self.parent_handler.write(str(self._handler))
			# write end to parent env
			self.parent_handler.write(self.end_text)
			self.parent_handler.newline()
		finally:
			return super(LaTeXEnvironment, self).__exit__(exc_type, exc_val, exc_tb)

	def write(self, s: AnyStr) -> None:
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
	def _write(self, s: AnyStr) -> None:
		self.__require_open__(frame_depth=2)
		self._handler.write(s)

	@final
	def _newline(self) -> None:
		self.__require_open__(frame_depth=2)
		self._handler.newline()

	def __str__(self) -> str:
		""" :return: a string representation of this environment """
		return f"{self.begin_text}\n{str(self._handler)}\n{self.end_text}"

	def __repr__(self) -> str:
		return f"{self.__class__.__name__}(" \
			   f"parent={self._parent_env.__class__.__name__}, " \
			   f"options={self._options}, " \
			   f"opened={self._open})"

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ CONCRETE ENVIRONMENTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

@final
class Center(LaTeXEnvironment):
	"""
	:py:class:`Center` represents the standard LaTeX ``center`` environment. It has no options or required packages.

	:param parent_env: the parent environment or document to this environment
	:param indent_level: the number of tab characters to indent this environment relative to the parent environment
	"""

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 indent_level: int = 1):
		super(Center, self).__init__(parent_env,
									 environment_name="center",
									 options="",
									 required_packages=(),
									 indent_level=indent_level)

class Figure(LaTeXEnvironment):
	"""
	:py:class:`Figure` represents the standard LaTeX ``figure`` environment. It can be initialized with a caption, a label,
	and options. The options default to ``h!`` to force placement at the location of the definition of the figure.

	When referencing this figure use the :py:attr:`label` property as follows, as it adds the ``fig:`` prefix
	automatically when left out and makes referencing easier:

	>>> with LaTeXDocument("ham.tex") as (doc, _, _):
	... 	f1 = Figure(doc, "Caption.", "a-label")
	... 	assert f1.label == "fig:a-label"
	...
	... 	f2 = Figure(doc, "Spam Ham Caption.", "fig:label-label")
	... 	assert f2.label == "fig:label-label"

	:param parent_env: the parent environment or document to this environment
	:param caption: the caption of the figure, may be ``None``
	:param label: the label of the figure, can include ``fig:`` as prefix but if this is absent the prefix will be added
		automatically by the :py:attr:`label` property, may be ``None``
	:param options: the options to pass to the environment, this value is put after the ``\begin`` command
	:param indent_level: the number of tab characters to indent this environment relative to the parent environment
	"""

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 caption: Optional[AnyStr] = "",
				 label: Optional[AnyStr] = "",
				 options: AnyStr = "h!",
				 indent_level: int = 1):
		super(Figure, self).__init__(parent_env,
									 environment_name="figure",
									 options=options,
									 required_packages=(),
									 indent_level=indent_level)
		self._caption = caption
		self._label = label

	@property
	def caption(self) -> Optional[AnyStr]:
		""" :return: the caption of this figure """
		return self._caption

	@property
	def label(self) -> Optional[AnyStr]:
		""" :return: the label referencing this figure, automatically adds ``fig:`` prefix if missing """
		if self._label is not None and not self._label.startswith("fig:"):
			return f"fig:{self._label}"
		else:
			return self._label

	def write_figure_table(self) -> None:
		""" Write a table of the figures in this document at this location. """
		self.document.body.write(r"\listoffigures")

	def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
		# write caption and label
		if self._caption is not None:
			self.write(f"\\caption{{{self._caption}}}")
		if self._label is not None:
			self.write(f"\\label{{{self.label}}}")

		return super(Figure, self).__exit__(exc_type, exc_val, exc_tb)

class MathsEnvironment(LaTeXEnvironment):
	r"""
	:py:class:`MathsEnvironment` represents a base implementation of any (``amsmath``) math environment. It can be passed
	the star flag upon creation, which will be inserted at the start of the environment name. When writing to this instance,
	text will automatically be formatted using :py:func:`tex_maths_string` and the :py:meth:`newline` method will write a
	double backslash ``\\`` instead of the newline character ``\n``.

	:param parent_env: the parent environment or document to this environment
	:param env_name: the parent environment or document to this environment
	:param star: whether or not to prefix the environment name with a star like so: ``*env_name`` or ``env_name``
	:param indent_level: the number of tab characters to indent this environment relative to the parent environment
	"""

	def __init__(self,
				 parent_env: Union[LaTeXDocument, LaTeXEnvironment],
				 env_name: str,
				 star: bool = True,
				 indent_level: int = 1):
		super(MathsEnvironment, self).__init__(parent_env,
											   environment_name=f"{env_name}{'*' if star else ''}",
											   options="",
											   required_packages=("amsmath",),
											   indent_level=indent_level)

	def write(self, s: Any) -> None:
		r"""
		Shorthand for writing to the handler of this instance. Automatically calls :py:func:`tex_maths_string` on every
		object ``s`` passed to it.

		:raise LaTeXError: if the document has not been opened
		"""
		super(MathsEnvironment, self).write(tex_maths_string(s))

	def newline(self) -> None:
		r"""
		Shorthand for writing a newline to the handler of this instance. Instead of ``\n`` this method places ``\\`` to
		indicate a line break.

		:raise LaTeXError: if the document has not been opened
		"""
		super(MathsEnvironment, self).write(r"\\")
