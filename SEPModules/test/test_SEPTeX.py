"""
:Author: Marcel Simader
:Date: 29.06.2021
"""

from SEPTeX import *

if __name__ == "__main__":

	document : LaTeXDocument
	with LaTeXDocument("tmp/test.tex") as (document, pre, body):
		pre.write(r"% This is indeed a comment in the preamble")
		body.write(r"\noindent This is a \LaTeX\ sentence!")

		with Equation(document, star=True) as eq:
			eq.write([1, 2, 3, "abc"])
			eq.write({1, 2, 3, "abc"})

	document.to_pdf(out_file_path="tmp/test123.pdf", overwrite=True, engine="pdflatex")