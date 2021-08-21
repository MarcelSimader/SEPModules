"""
:Author: Marcel Simader
:Date: 15.07.2021

..	versionadded:: 1.3.0
"""

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ IMPORTS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
import sys
from typing import Optional

from SEPTeX.LaTeX import LaTeXDocument, Center
from SEPTeX.TikZ import TikZNode, Point, TikZLabel
from SEPTeX.TikZBase import TikZPicture, TikZStyle, TikZArrow, TikZColor
from SEPTeX.TikZGraph import TikZGraph

from SEPModules.maths.SEPLogic import AtomicProposition
from SEPModules.maths.SEPQBF import PQBF

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

def demo1():
	_ = AtomicProposition
	a, b, c, d, e, f, g, h = _(), _(), _(), _(), _(), _(), _(), _()

	def _print(name, *obj):
		text = "~" * 20
		text += f"\n{name}:\n"
		for o in obj:
			text += str(o) + "\n"
		text += ("~" * 20) + "\n"
		print(text)

	props = (a | ~a,
			 a & ~a,
			 (a >> b) & a,
			 (a >> b) & ~b,
			 ~~a,
			 (a >> b) & (b >> c),
			 (a & b) >> a,
			 (a & b) >> b,
			 a >> (a | b),
			 b >> (a | b),
			 (a >> b) & (b >> a),
			 ~(a & b),
			 ~(a | b),
			 a | (b & c),
			 a & (b | c),
			 ~a >> ~b,
			 a | a,
			 a & a)

	prop1 = (a & b) | (a & c) | (a & d) | (a & e)
	prop2 = (a & b) >> ((a & c) | (a & d) | (a & e))
	prop3 = (~a & b) | (~~a & c) | ~(a & d) | (~~a & ~~~e)
	prop4 = ~(~a & b) >> ((~~a & c) | ~(a & d) | (~~a & ~~~e))

	for p in (*props, prop1, prop2, prop3, prop4):
		_print("reduce, expand", p, p.reduce(), p.reduce().expand())

	for p in (*props, prop1, prop2, prop3, prop4):
		_print("first expand then reduce", p, p.expand().reduce())

def demo2():
	# create atomic propositions
	atomic_prop = AtomicProposition
	a, b, c, d, e = atomic_prop(), atomic_prop(), atomic_prop(), atomic_prop(), atomic_prop()

	# enter formula (syntax will be in documentation soon)
	formula = a // ((b, c) / (
			~((a & b) | c) & ((a >> b) ** (b << a))
	))
	# convert to QBF
	qbf = PQBF.from_formula(formula)

	# open LaTeX document
	doc: LaTeXDocument
	with LaTeXDocument("_tmp/pqbf.tex", default_packages=()) as doc:
		with Center(doc) as center, TikZPicture(center) as tikz:
			# define a TikZGraph
			graph = TikZGraph(default_node_style=TikZStyle(draw=False))

			# create assignment tree from QBF
			root = qbf.assignment_tree()

			# recursively define edges for graph
			def __add_edges__(curr: PQBF.Node,
							  parent: Optional[TikZNode],
							  offset: float) -> None:
				if curr is not None:
					node = TikZNode(Point(0, 0) if parent is None else Point(offset, -3),
									name=str(hash(curr)), label=curr.to_latex(), relative_to=parent)
					if parent is not None:
						graph.add_edge(parent, node,
									   style=TikZStyle(color=TikZColor.GREEN if curr.eval_node() else TikZColor.RED,
													   line_width="0.45mm"),
									   arrow_type=TikZArrow.LINE)
					__add_edges__(curr.left, parent=node, offset=-abs(offset) / 2)
					__add_edges__(curr.right, parent=node, offset=abs(offset) / 2)

			__add_edges__(root, parent=None, offset=8)

			# write TikZGraph
			tikz.write(graph)

	# convert .tex to .pdf
	doc.to_pdf("_tmp/pqbf.pdf", overwrite=True)

if __name__ == "__main__":
	# demo1()
	# demo2()

	a, b, c, d, e, f, g = AtomicProposition.init_atomic_props(7)
	p = (a & b & c & g) | (a & c & ~g & f) | ((d >> e) & (e << d)) | ((~(d ** ~f) & g) >> (g | ~f))
	print(p)
	q = p.expand().reduce()
	print(q)
