SEPLogger
==========================

..  automodule:: SEPModules.SEPLogger

Logger Levels
-----------------------

..	autoclass:: SEPModules.SEPLogger.Levels
	:members:

..	autoclass:: SEPModules.SEPLogger.DefaultLevels
	:show-inheritance:

..	data:: 	VERBOSE
			INFO
			OK
			WARNING
			ERROR
			FATAL_ERROR

		These constants are provided as aliases for ``SEPModules.SEPLogger.DefaultLevels.*``.

Logger
-----------------------

..	autoclass:: SEPModules.SEPLogger.Logger
	:special-members: __provide_timestamp__
	:members:
