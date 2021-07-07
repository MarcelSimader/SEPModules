"""
:Author: Marcel Simader
:Date: 29.06.2021
"""
import os.path
import unittest

from SEPModules.TeX.SEPTeX import *
from SEPModules.TeX.SEPTikZ import *
from SEPModules.maths.SEPAlgebra import Monoid, Field

# ~~~~~~~~~~~~~~~ DEMO 1 ~~~~~~~~~~~~~~~
def demo1():
	document: LaTeXDocument
	pre: LaTeXHandler
	body: LaTeXHandler
	with LaTeXDocument("tmp/demo1.tex",
					   title="Demo Document No. 1",
					   subtitle="for the SEPTeX module",
					   author="Marcel Simader",
					   show_page_numbers=False,
					   line_wrap_length=120) as (document, pre, body):
		pre.write(r"% This is indeed a comment in the preamble")
		body.write(
				r'\noindent This is some text, and it contains a potentially % confusing comment for the "soft" line wrap % functionality')
		body.newline()
		body.write(r"And this is some text that goes on" + (" and on" * 20) + r"\ldots")

		body.write(r"This is a \LaTeX\ sentence -- wow!")

		s = MathsEnvironment(document, "gather", star=True)
		with s as eq:
			eq.write([1, Rational(1, 3), 3, "abc"])
			eq.write({1, Fraction(-3, 5), Rational(-2, 7), "abc"})

			eq.newline()

			def addition(a, b): return a + b

			eq.write(Monoid({1, 2, 3, Rational(-9, 2)}, addition))
			eq.write(Field({1, 2, 3, Rational(-9, 2)}, addition, addition))

		document.page_break()

		colors = (RED, ORANGE, YELLOW, GREEN, LIGHT_BLUE, DARK_BLUE, PURPLE, MAGENTA,
				  PINK, ROSE, ALMOST_BLACK, DARK_GRAY, LIGHT_GRAY, ALMOST_WHITE)

		with Figure(document, caption="Captions, Figures, and the Default Colors.") as fig, \
				Center(fig) as center, \
				TikZPicture(center) as tikz:
			tikz.define_color(*colors)

			for i, color in enumerate(colors):
				with TikZScope(tikz, style=TikZStyle(scale=0.4 + (0.7 * (i / len(colors))))) as scope:
					path = TikZPath((Point(0, i), Point(4, 4 + i), Point(0, 4 + i), Point(-4, 2 + i)),
									cycle=True,
									style=TikZStyle(fill=color,
													color=ALMOST_BLACK,
													line_width=f"{0.5 + i / len(colors)}mm")
									)
					scope.write(path)

		document.page_break()

		with Figure(document, caption="The arrow styles.") as fig, \
				Center(fig) as center, \
				TikZPicture(center) as tikz:
			for i, arrow_style in enumerate(TikZArrow):
				with TikZScope(tikz, style=TikZStyle(shift=(0, -i * 0.45), scale=2)) as scope:
					scope.write(
							TikZDirectionalPath((Point(0, 0), Point(1 + (2 * i / len(TikZArrow)), 0.75), Point(4, 0)),
												style=TikZStyle(line_width="0.85mm"),
												arrow_type=arrow_style))

		document.page_break()

		num, rad = 12, 5
		nodes = list()
		for i in range(num):
			j = 2 * math.pi * i / num
			x, y = rad * math.sin(j), rad * math.cos(j)
			nodes.append(TikZNode(Point(x, y), label=str(i), name=f"x{i}", style=TikZStyle(circle=True)))

		with Figure(document, caption="Nodes, nodes, nodes.") as fig, \
				Center(fig) as center, \
				TikZPicture(center) as tikz:
			for i in range(len(nodes)):
				i = i % len(nodes)
				tikz.write(TikZDirectionalPath((nodes[i - 1], nodes[i]),
											   style=TikZStyle(bend_left=15, line_width="0.3mm", dashed=True),
											   arrow_type=TikZArrow.RIGHT_LATEX_PRIME))
			tikz.write(TikZDirectionalPath((nodes[0], nodes[len(nodes) // 2 + 1]), arrow_type=TikZArrow.RIGHT_CIRC))

	document.to_pdf(out_file_path="tmp/demo1.pdf", overwrite=True)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ UNIT TESTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class LaTeXDocumentTestCase(unittest.TestCase):

	def setUp(self) -> None:
		self.doc1 = LaTeXDocument("tmp/_test.tex",
								  document_class="article", document_options="a4paper, 12pt",
								  default_packages=(),
								  title="This is a title", subtitle=None, author="python unittest",
								  show_date=False, show_page_numbers=False, line_wrap_length=None)
		self.doc2 = LaTeXDocument("tmp/_testabc",
								  document_class="article", document_options="a3paper, 10pt",
								  default_packages=("amsmath",),
								  title="title", subtitle="subtitle", author=None,
								  show_date=False, show_page_numbers=True, line_wrap_length=None)
		self.docs = (self.doc1, self.doc2)

	def tearDown(self) -> None:
		try:
			for doc in self.docs:
				if os.path.isfile(doc.path):
					os.remove(doc.path)
		except OSError as e:
			print(f"did not delete file: {e}")
		del self.doc1, self.doc2

	def enter(self):
		for doc in self.docs:
			doc.__enter__()

	def exit(self):
		for doc in self.docs:
			doc.__exit__(None, None, None)

	def assertDocumentContentsEqual(self, document: LaTeXDocument):
		self.assertMultiLineEqual(LaTeXDocument.LaTeXTemplate.format(
				document.document_options,
				document.document_class,
				str(document._definitions),
				str(document._preamble),
				str(document._body)
				), str(document))

	def assertLaTeXContains(self, doc: Union[LaTeXDocument, LaTeXEnvironment], *strings: str):
		any_char = r"(.*\s)*"
		strings = [s.replace("\\", "\\\\")
					   .replace("{", "\\{").replace("}", "\\}")
					   .replace("[", "\\[").replace("]", "\\]") for s in strings]
		self.assertRegex(str(doc), expected_regex=any_char + any_char.join(strings) + any_char)

# noinspection PyTypeChecker
class TestLaTeXResource(unittest.TestCase):
	class TestImplementationResource(LaTeXResource):
		def __str__(self) -> str:
			return ""

	def setUp(self) -> None:
		self.no_reopen = self.TestImplementationResource()
		self.reopen = self.TestImplementationResource(can_reopen=True)

	def tearDown(self) -> None:
		del self.no_reopen, self.reopen

	def open(self):
		self.no_reopen.__enter__()
		self.reopen.__enter__()

	def close(self):
		self.no_reopen.__exit__(None, None, None)
		self.reopen.__exit__(None, None, None)

	def test_init(self):
		self.assertFalse(self.no_reopen.open)
		self.assertFalse(self.reopen.open)

	def test_open_counter(self):
		self.assertEqual(0, self.no_reopen._open_counter)
		self.assertEqual(0, self.reopen._open_counter)
		self.open()
		self.assertEqual(1, self.no_reopen._open_counter)
		self.assertEqual(1, self.reopen._open_counter)

		self.reopen.__enter__()
		self.assertEqual(2, self.reopen._open_counter)
		self.reopen.__exit__(None, None, None)
		self.assertEqual(2, self.reopen._open_counter)

	def test_open(self):
		self.open()
		self.assertTrue(self.no_reopen.open)
		self.assertTrue(self.reopen.open)

	def test_close(self):
		self.open()
		self.close()
		self.assertFalse(self.no_reopen.open)
		self.assertFalse(self.reopen.open)

	def test_require_closed(self):
		self.assertIsNone(self.no_reopen.__require_closed__())
		self.assertIsNone(self.reopen.__require_closed__())
		self.open()
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_closed__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_closed__())
		self.close()
		self.assertIsNone(self.no_reopen.__require_closed__())
		self.assertIsNone(self.reopen.__require_closed__())

	def test_require_open(self):
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_open__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_open__())
		self.open()
		self.assertIsNone(self.no_reopen.__require_open__())
		self.assertIsNone(self.reopen.__require_open__())
		self.close()
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_open__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_open__())

	def test_require_virgin(self):
		self.assertIsNone(self.no_reopen.__require_virgin__())
		self.assertIsNone(self.reopen.__require_virgin__())
		self.open()
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_virgin__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_virgin__())
		self.close()
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_virgin__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_virgin__())

	def test_require_used(self):
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_used__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_used__())
		self.open()
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__require_used__())
		self.assertRaises(LaTeXError, lambda: self.reopen.__require_used__())
		self.close()
		self.assertIsNone(self.no_reopen.__require_used__())
		self.assertIsNone(self.reopen.__require_used__())

	def test_reopen(self):
		self.open()
		self.close()
		self.assertRaises(LaTeXError, lambda: self.no_reopen.__enter__())
		self.assertIsNone(self.reopen.__enter__())

	def test_str(self):
		self.assertEqual("", str(self.no_reopen))
		self.assertEqual("", str(self.reopen))

# noinspection PyTypeChecker
class TestLaTeXHandler(unittest.TestCase):

	def setUp(self) -> None:
		self.plain = LaTeXHandler()
		self.indent = LaTeXHandler(indent_level=1)
		self.wrap = LaTeXHandler(line_wrap_length=10)
		self.wrap_indent = LaTeXHandler(indent_level=1, line_wrap_length=10)

	def tearDown(self) -> None:
		del self.plain, self.indent, self.wrap, self.wrap_indent

	def write(self, s):
		self.plain.write(s)
		self.indent.write(s)
		self.wrap.write(s)
		self.wrap_indent.write(s)

	def newline(self):
		self.plain.newline()
		self.indent.newline()
		self.wrap.newline()
		self.wrap_indent.newline()

	def test_init(self):
		self.assertEqual(list(), self.plain._data)
		self.assertEqual(list(), self.indent._data)
		self.assertEqual(list(), self.wrap._data)
		self.assertEqual(list(), self.wrap_indent._data)

	def test_write_empty(self):
		self.write("")
		self.assertTupleEqual(((0, ""),), self.plain.data)
		self.assertTupleEqual(((1, ""),), self.indent.data)
		self.assertTupleEqual(((0, ""),), self.wrap.data)
		self.assertTupleEqual(((1, ""),), self.wrap_indent.data)

	def test_newline_write_empty(self):
		self.write("\n")
		self.assertTupleEqual(((0, ""), (0, "")), self.plain.data)
		self.assertTupleEqual(((1, ""), (1, "")), self.indent.data)
		self.assertTupleEqual(((0, ""), (0, "")), self.wrap.data)
		self.assertTupleEqual(((1, ""), (1, "")), self.wrap_indent.data)

	def test_newline(self):
		self.newline()
		self.assertTupleEqual(((0, ""),), self.plain.data)
		self.assertEqual(1, len(self.plain))
		self.assertTupleEqual(((1, ""),), self.indent.data)
		self.assertEqual(1, len(self.indent))
		self.assertTupleEqual(((0, ""),), self.wrap.data)
		self.assertEqual(1, len(self.wrap))
		self.assertTupleEqual(((1, ""),), self.wrap_indent.data)
		self.assertEqual(1, len(self.wrap_indent))

	def test_write_short(self):
		self.write("test")
		self.assertTupleEqual(((0, "test"),), self.plain.data)
		self.assertTupleEqual(((1, "test"),), self.indent.data)
		self.assertTupleEqual(((0, "test"),), self.wrap.data)
		self.assertTupleEqual(((1, "test"),), self.wrap_indent.data)
		self.write("abc")
		self.assertTupleEqual(((0, "test"), (0, "abc")), self.plain.data)
		self.assertTupleEqual(((1, "test"), (1, "abc")), self.indent.data)
		self.assertTupleEqual(((0, "test"), (0, "abc")), self.wrap.data)
		self.assertTupleEqual(((1, "test"), (1, "abc")), self.wrap_indent.data)

	def test_newline_write_short(self):
		self.write("test\n  abc")
		self.assertTupleEqual(((0, "test"), (0, "  abc")), self.plain.data)
		self.assertEqual(2, len(self.plain))
		self.assertTupleEqual(((1, "test"), (1, "  abc")), self.indent.data)
		self.assertEqual(2, len(self.indent))
		self.assertTupleEqual(((0, "test"), (0, "  abc")), self.wrap.data)
		self.assertEqual(2, len(self.wrap))
		self.assertTupleEqual(((1, "test"), (1, "  abc")), self.wrap_indent.data)
		self.assertEqual(2, len(self.wrap_indent))
		self.write("123")
		self.assertTupleEqual(((0, "test"), (0, "  abc"), (0, "123")), self.plain.data)
		self.assertEqual(3, len(self.plain))
		self.assertTupleEqual(((1, "test"), (1, "  abc"), (1, "123")), self.indent.data)
		self.assertEqual(3, len(self.indent))
		self.assertTupleEqual(((0, "test"), (0, "  abc"), (0, "123")), self.wrap.data)
		self.assertEqual(3, len(self.wrap))
		self.assertTupleEqual(((1, "test"), (1, "  abc"), (1, "123")), self.wrap_indent.data)
		self.assertEqual(3, len(self.wrap_indent))

	def test_write_long(self):
		self.write("This is a long   line.")
		self.assertTupleEqual(((0, "This is a long   line."),), self.plain.data)
		self.assertTupleEqual(((1, "This is a long   line."),), self.indent.data)
		self.assertTupleEqual(((0, "This is a long   line."),), self.wrap.data)
		self.assertTupleEqual(((1, "This is a long   line."),), self.wrap_indent.data)

	def test_wrap_no_hanging_indent(self):
		self.write("This is a long   line.")
		self.plain.wrap_lines(tab_width=4, hanging_indent=False)
		self.indent.wrap_lines(tab_width=4, hanging_indent=False)
		self.wrap.wrap_lines(tab_width=4, hanging_indent=False)
		self.wrap_indent.wrap_lines(tab_width=4, hanging_indent=False)
		self.assertTupleEqual(((0, "This is a long   line."),), self.plain.data)
		self.assertTupleEqual(((1, "This is a long   line."),), self.indent.data)
		self.assertTupleEqual(((0, "This is a long "), (0, "line."),), self.wrap.data)
		self.assertTupleEqual(((1, "This is "), (1, "a long "), (1, "line."),), self.wrap_indent.data)

	def test_wrap_hanging_indent(self):
		self.write("This is a long   line.")
		self.plain.wrap_lines(tab_width=4, hanging_indent=True)
		self.indent.wrap_lines(tab_width=4, hanging_indent=True)
		self.wrap.wrap_lines(tab_width=4, hanging_indent=True)
		self.wrap_indent.wrap_lines(tab_width=4, hanging_indent=True)
		self.assertTupleEqual(((0, "This is a long   line."),), self.plain.data)
		self.assertTupleEqual(((1, "This is a long   line."),), self.indent.data)
		self.assertTupleEqual(((0, "This is a long "), (1, "line."),), self.wrap.data)
		self.assertTupleEqual(((1, "This is "), (2, "a long "), (2, "line."),), self.wrap_indent.data)

	def test_write_handler_to_handler(self):
		self.write("abc 123")
		self.assertTupleEqual(((0, "abc 123"),), self.plain.data)
		self.assertTupleEqual(((1, "abc 123"),), self.indent.data)
		self.assertTupleEqual(((0, "abc 123"),), self.wrap.data)
		self.assertTupleEqual(((1, "abc 123"),), self.wrap_indent.data)

		self.plain.write(self.indent)
		self.assertTupleEqual(((0, "abc 123"), (1, "abc 123")), self.plain.data)
		self.assertTupleEqual(((1, "abc 123"),), self.indent.data)

		self.wrap_indent.write(self.wrap)
		self.assertTupleEqual(((0, "abc 123"),), self.wrap.data)
		self.assertTupleEqual(((1, "abc 123"), (1, "abc 123")), self.wrap_indent.data)

# noinspection PyTypeChecker
class TestLaTeXDocument(LaTeXDocumentTestCase):

	def test_init(self):
		self.assertTrue(self.doc1._has_title)
		self.assertTrue(self.doc2._has_title)
		self.assertEqual(os.path.abspath("tmp/_test.tex"), self.doc1.path)
		self.assertEqual(os.path.abspath("tmp/_testabc.tex"), self.doc2.path)
		self.assertTupleEqual((), self.doc1.definitions)
		self.assertTupleEqual((("usepackage", "amsmath"),), self.doc2.definitions)

		self.assertRaises(LaTeXError, lambda: self.doc1.body)
		self.assertRaises(LaTeXError, lambda: self.doc1.preamble)
		self.assertRaises(LaTeXError, lambda: self.doc2.body)
		self.assertRaises(LaTeXError, lambda: self.doc2.preamble)

		self.assertRaises(LaTeXError, lambda: self.doc1.to_pdf("_"))
		self.assertRaises(LaTeXError, lambda: self.doc2.to_pdf("_"))

		self.assertDocumentContentsEqual(self.doc1)
		self.assertDocumentContentsEqual(self.doc2)

	def test_open(self):
		self.assertFalse(self.doc1.open)
		self.assertFalse(self.doc2.open)
		self.enter()
		self.assertTrue(self.doc1.open)
		self.assertTrue(self.doc2.open)

	def test_close(self):
		self.enter()
		self.exit()
		self.assertFalse(self.doc1.open)
		self.assertFalse(self.doc2.open)

	def test_include_statement(self):
		self.doc1.use_package("mathtools")
		self.doc1.use_tikz_library("arrows")
		self.enter()
		self.doc2.use_package("mathtools")
		self.doc2.use_tikz_library("arrows")
		self.exit()
		self.assertTupleEqual((("usepackage", "mathtools"), ("usepackage", "tikz"), ("usetikzlibrary", "arrows"),
							   ("usepackage", "relsize")), self.doc1.definitions)
		self.assertTupleEqual((("usepackage", "amsmath"), ("usepackage", "relsize"), ("usepackage", "mathtools"),
							   ("usepackage", "tikz"), ("usetikzlibrary", "arrows")), self.doc2.definitions)
		self.assertDocumentContentsEqual(self.doc1)
		self.assertDocumentContentsEqual(self.doc2)

	def test_init_document(self):
		self.enter()
		self.exit()
		self.assertLaTeXContains(self.doc1, r"\title{This is a title}", r"\author{python unittest}", r"\date{}",
								 r"\pagenumbering{gobble}", r"\maketitle")

		self.assertLaTeXContains(self.doc2, r"\title{title\\[0.4em]\smaller{subtitle}}", r"\date{}", r"\maketitle")

	def test_exit(self):
		self.assertFalse(self.doc1.successfully_saved)
		self.assertFalse(self.doc2.successfully_saved)
		self.enter()
		self.assertFalse(self.doc1.successfully_saved)
		self.assertFalse(self.doc2.successfully_saved)
		self.exit()
		self.assertTrue(self.doc1.successfully_saved)
		self.assertTrue(self.doc2.successfully_saved)
		try:
			self.assertTrue(os.path.isfile(self.doc1.path))
			self.assertTrue(os.path.isfile(self.doc2.path))
			# at least 50 bytes
			self.assertGreaterEqual(os.path.getsize(self.doc1.path), 50)
			self.assertGreaterEqual(os.path.getsize(self.doc2.path), 50)
		except OSError:
			self.fail("file does not exist")

	def test_to_pdf(self):
		self.assertRaises(LaTeXError, lambda: self.doc1.to_pdf("_"))
		self.assertRaises(LaTeXError, lambda: self.doc2.to_pdf("_"))
		self.enter()
		self.assertRaises(LaTeXError, lambda: self.doc1.to_pdf("_"))
		self.assertRaises(LaTeXError, lambda: self.doc2.to_pdf("_"))
		self.exit()

		path = "tmp/_test.pdf"
		aux_path = "tmp/.aux"
		try:
			if os.path.isdir(aux_path):
				shutil.rmtree(aux_path)
			if os.path.isfile(path):
				os.remove(path)
		except OSError as e:
			print(f"did not delete file: {e}")

		# only test on one for now so it's faster
		self.assertRaises(NotImplementedError, lambda: self.doc1.to_pdf(path, engine="abc123"))
		self.doc1.to_pdf(path, overwrite=False, delete_aux_files=False, engine="pdftex", custom_options="")
		self.assertTrue(os.path.isdir(aux_path))
		self.assertTrue(os.path.isfile(path))
		self.assertRaises(FileExistsError, lambda: self.doc1.to_pdf(path))
		self.doc1.to_pdf(path, overwrite=True, delete_aux_files=True, engine="pdftex", custom_options="")
		self.assertFalse(os.path.isdir(aux_path))
		self.assertTrue(os.path.isfile(path))

# noinspection PyTypeChecker
class TestLaTeXEnvironment(LaTeXDocumentTestCase):

	def setUp(self) -> None:
		super(TestLaTeXEnvironment, self).setUp()
		self.env1 = LaTeXEnvironment(self.doc1, "itemize", "align=left", ("enumitem",), 1)
		self.env2 = LaTeXEnvironment(self.doc2, "enumerate", "", (), 1)
		self.env3 = LaTeXEnvironment(self.env2, "center", "", ("random_package",), 0)
		self.envs = (self.env1, self.env2, self.env3)

	def tearDown(self) -> None:
		super(TestLaTeXEnvironment, self).tearDown()
		del self.env1, self.env2, self.env3

	def enter_env(self):
		for env in self.envs:
			env.__enter__()

	def enter(self):
		super(TestLaTeXEnvironment, self).enter()
		self.enter_env()

	def exit_env(self):
		for env in reversed(self.envs):
			env.__exit__(None, None, None)

	def exit(self):
		self.exit_env()
		super(TestLaTeXEnvironment, self).exit()

	def test_init(self):
		self.assertEqual("[align=left]", self.env1.options)
		self.assertEqual("", self.env2.options)

		self.assertIn(("usepackage", "enumitem"), self.doc1.definitions)
		self.assertIn(("usepackage", "random_package"), self.doc2.definitions)

		self.assertEqual(self.doc1, self.env1.document)
		self.assertEqual(self.doc1, self.env1.document)
		self.assertEqual(self.doc1, self.env1.parent_env)
		self.assertEqual(self.doc2, self.env2.document)
		self.assertEqual(self.doc2, self.env2.document)
		self.assertEqual(self.doc2, self.env2.parent_env)
		self.assertEqual(self.doc2, self.env3.document)
		self.assertEqual(self.doc2, self.env3.document)
		self.assertEqual(self.env2, self.env3.parent_env)

		self.assertEqual(r"\begin{itemize}[align=left]", self.env1.begin_text)
		self.assertEqual(r"\end{itemize}", self.env1.end_text)
		self.assertEqual(r"\begin{enumerate}", self.env2.begin_text)
		self.assertEqual(r"\end{enumerate}", self.env2.end_text)
		self.assertEqual(r"\begin{center}", self.env3.begin_text)
		self.assertEqual(r"\end{center}", self.env3.end_text)

	def test_open(self):
		self.assertRaises(LaTeXError, lambda: self.enter_env())
		self.assertRaises(LaTeXError, lambda: self.env3.__enter__())

		self.enter()
		self.assertEqual(self.doc1.body, self.env1.parent_handler)
		self.assertEqual(self.doc2.body, self.env2.parent_handler)
		self.assertEqual(self.env2._handler, self.env3.parent_handler)

		self.assertLaTeXContains(self.doc1, r"\begin{itemize}[align=left]")
		self.assertLaTeXContains(self.doc2, r"\begin{enumerate}")
		self.assertLaTeXContains(self.env2, r"\begin{center}")

		self.assertTrue(self.env1.open)
		self.assertTrue(self.env2.open)
		self.assertTrue(self.env3.open)

	def test_close_order(self):
		self.enter()
		# exit docs
		super(TestLaTeXEnvironment, self).exit()
		self.assertRaises(LaTeXError, lambda: self.exit_env())

	def test_close(self):
		self.enter()
		self.exit()
		self.assertFalse(self.env1.open)
		self.assertFalse(self.env2.open)
		self.assertFalse(self.env3.open)

		self.assertLaTeXContains(self.doc1, r"\begin{itemize}[align=left]", r"\end{itemize}")
		self.assertLaTeXContains(self.env2, r"\begin{center}", r"\end{center}")
		self.assertLaTeXContains(self.doc2, r"\begin{enumerate}", r"\begin{center}", r"\end{center}",
								 r"\end{enumerate}")

	def test_write(self):
		self.assertRaises(LaTeXError, lambda: self.env1.write("test"))
		self.assertRaises(LaTeXError, lambda: self.env2.write("test"))
		self.assertRaises(LaTeXError, lambda: self.env3.write("test"))
		# enter docs
		super(TestLaTeXEnvironment, self).enter()

		self.env1.__enter__()
		self.env2.__enter__()
		self.env1.write("abc123")
		self.env2.write("abc123")
		self.assertLaTeXContains(self.env1, r"\begin{itemize}[align=left]", r"abc123", r"\end{itemize}")
		self.assertLaTeXContains(self.env2, r"\begin{enumerate}", r"abc123", r"\end{enumerate}")

		self.assertRaises(LaTeXError, lambda: self.env3.write("test"))
		self.env3.__enter__()
		self.env3.write("abc123")
		self.assertLaTeXContains(self.env3, r"\begin{center}", r"abc123", r"\end{center}")

		self.env3.__exit__(None, None, None)
		self.assertLaTeXContains(self.env2, r"\begin{enumerate}", r"abc123", r"\begin{center}", r"abc123",
								 r"\end{center}", r"\end{enumerate}")

		self.env2.__exit__(None, None, None)
		self.env1.__exit__(None, None, None)
		self.assertLaTeXContains(self.doc1, r"\begin{itemize}[align=left]", r"abc123", r"\end{itemize}")
		self.assertLaTeXContains(self.doc2, r"\begin{enumerate}", r"abc123", r"\begin{center}", r"abc123",
								 r"\end{center}", r"\end{enumerate}")

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ MAIN ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

if __name__ == "__main__":
	demo1()
