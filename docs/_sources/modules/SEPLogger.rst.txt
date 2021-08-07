SEPLogger
==========================

..  automodule:: SEPModules.SEPLogger

Logger Levels
-----------------------

..	sidebar:: Verbosity Constants

	..	data:: 	VERBOSE
				INFO
				OK
				WARNING
				ERROR
				FATAL_ERROR

			These constants are provided as aliases for ``SEPModules.SEPLogger.DefaultLevels.*``.

..	autoclass:: SEPModules.SEPLogger.Level
	:members:

..	autoclass:: SEPModules.SEPLogger.DefaultLevel

Logger
-----------------------

..	autoclass:: SEPModules.SEPLogger.Logger

	.. automethod:: _provide_timestamp
	.. automethod:: default_print_function

	.. autoproperty:: min_level
	.. autoproperty:: level_mask
	.. autoproperty:: level_class

	.. automethod:: log
	.. automethod:: newline
	.. automethod:: debug

	.. autodecorator:: SEPModules.SEPLogger.Logger.log_call
	.. autodecorator:: SEPModules.SEPLogger.Logger.log_class
