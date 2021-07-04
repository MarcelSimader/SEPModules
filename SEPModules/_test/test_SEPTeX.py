"""
:Author: Marcel Simader
:Date: 29.06.2021
"""

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

		with Figure(document, caption="Captions, Figures, and the Default Colors.") as fig, Center(
				fig) as center, TikZPicture(center) as tikz:
			colors = (RED, ORANGE, YELLOW, GREEN, LIGHT_BLUE, DARK_BLUE, PURPLE, MAGENTA,
					  PINK, ROSE, ALMOST_BLACK, DARK_GRAY, LIGHT_GRAY, ALMOST_WHITE)
			tikz.define_color(colors)

			s = TikZStyle(fill=ALMOST_BLACK, color=ALMOST_BLACK, line_width=f"{0.5 + 1 / len(colors)}mm")

			for i, color in enumerate(colors):
				with TikZScope(tikz, style=TikZStyle(scale=0.4 + (0.7 * (i / len(colors))))) as scope:
					path = TikZPath(((0, i), (4, 4 + i), (0, 4 + i), (-4, 2 + i)),
									coord_unit="cm",
									cycle=True,
									style=TikZStyle(fill=color,
													color=ALMOST_BLACK,
													line_width=f"{0.5 + i / len(colors)}mm")
									)
					scope.write(path)

	document.to_pdf(out_file_path="tmp/demo1.pdf", overwrite=True)

# ~~~~~~~~~~~~~~~ DEMO 2 ~~~~~~~~~~~~~~~

def demo2():
	document: LaTeXDocument
	pre: LaTeXHandler
	body: LaTeXHandler
	with LaTeXDocument("tmp/demo2.tex",
					   title="Demo Document No. 2",
					   subtitle="for the SEPTeX module",
					   author="Marcel Simader",
					   line_wrap_length=120) as (document, pre, body):
		with Center(document) as center, TikZPicture(center) as tikz:
			tikz.write("abc")

	document.to_pdf("tmp/demo2.pdf", overwrite=True)

if __name__ == "__main__":
	demo1()
	demo2()
