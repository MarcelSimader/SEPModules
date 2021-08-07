SEPLogic
==========================

..  automodule:: SEPModules.maths.SEPLogic

..	autodata:: SEPModules.maths.SEPLogic.Assignment

Exceptions
-----------------------------------

..	autoexception:: SEPModules.maths.SEPLogic.LogicError

..	autoexception:: SEPModules.maths.SEPLogic.LogicSyntaxError
	:members:

Connective Bases
------------------------------------

..	autoclass:: SEPModules.maths.SEPLogic._Connective
	:members:

..	autoclass:: SEPModules.maths.SEPLogic.ConnectiveArity
	:members:

..	autoclass:: SEPModules.maths.SEPLogic.ConnectiveFormat
	:members:

Logical Connective Enum
------------------------------------

..	autoclass:: SEPModules.maths.SEPLogic.LogicalConnective
..	autoclass:: SEPModules.maths.SEPLogic.SupportsLogicalConnective

Connective Format Protocols
-------------------------------------

..	autoclass:: SEPModules.maths.SEPLogic.SupportsConnectiveFormat

..	autoclass:: SEPModules.maths.SEPLogic.SupportsToPrettyPrint
	:members:

..	autoclass:: SEPModules.maths.SEPLogic.SupportsToLimboole
	:members:

..	autoclass:: SEPModules.maths.SEPLogic.SupportsToLaTeX
	:members:

Proposition Protocols
-------------------------------------

..	autoclass:: SEPModules.maths.SEPLogic.SupportsEval
	:members:

..	autoclass:: SEPModules.maths.SEPLogic.SupportsLimbooleEval
	:members:

Propositions
-------------------------------------

Proposition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..	autoclass:: SEPModules.maths.SEPLogic.Proposition
	:members:

Atomic Proposition
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..	autoclass:: SEPModules.maths.SEPLogic.AtomicProposition
	:members:
	:private-members: _next_id, _next_volatile_name

Truth constants
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

..	autodata:: SEPModules.maths.SEPLogic.Top
..	autodata:: SEPModules.maths.SEPLogic.Bottom

