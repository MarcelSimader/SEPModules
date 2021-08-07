# SEPModules

[![Publish to PyPI](https://github.com/SEOriginal/SEPModules/actions/workflows/python-publish.yml/badge.svg)](https://github.com/SEOriginal/SEPModules/actions/workflows/python-publish.yml) 
|  [Documentation](https://marcelsimader.github.io/SEPModules/)

Python package providing basic modules and functionality for various common tasks.

---

The package is of the following structure:
- ### maths

  - ### SEPLogic
    Provides classes and functions for performing zeroth order logic operations and interfacing with external solvers.
>  - ### SEPQBF
>    Provides classes and functions extending ``SEPLogic`` for performing QBF operations.
  - ### SEPAlgebra
    Provides classes and functions for performing computations on algebraic structures.

- ### SEPPrinting
  Provides easy and quick implementations of console UI elements like graphs, progress bars, and colored console printing.

- ### SEPLogger
  Provides logging functionality interfacing with the color printing features of SEPPrinting.
  
- ### SEPIO
  Aids in IO tasks such as reading console line arguments and parameters.

- ### SEPDecorators
  Contains miscellaneous function decorators and decorator utilities.

- ### SEPUtils
  Contains various utilities and custom python constructions.

---

## Exmaple usages

### SEPIO.ConsoleArguments

```python
from SEPModules import SEPIO
```

```python
# Pretend that the arguments "-h --verbosity 2" were passed to script
# for this example usage. In normal use 'sys.argv' would be automatically
# populated when the python script was started from the command line.
import sys
sys.argv = ["this_script_name", "-h", "--verbosity", "2"]
```

```python
# instantiate object to hold arguments passed to this script
console_manager = SEPIO.ConsoleArguments(["h"], ["help", "verbosity="])
```

```python
# print help message
if "h" in console_manager or "help" in console_manager:
    print("This is a help message... very helpful information goes here")
```

>This is a help message... very helpful information goes here

```python
# set a verbosity value based on what was passed after "--verbosity"
verbosity = 0 # default
if "verbosity" in console_manager:
    passed_verbosity = console_manager["verbosity"]
    
    # check if input is legal number
    if passed_verbosity not in ["0", "1", "2"]:
        print(f"'{passed_verbosity}' is not a valid verbosity value")
        sys.exit(1)
    
    verbosity = int(passed_verbosity) # get passed value
```

```python
print(f"Verbosity was succesfully set to {verbosity}!")
```

>Verbosity was succesfully set to 2!

### SEPAlgebra

```python

from maths import SEPAlgebra
```

```python
# create an algebraic structure and check if it is valid, i.e. closed
binary_and = SEPAlgebra.AlgebraicStructure({0, 1}, int.__mul__)
```

```python
# this is a valid structure because it is closed
# bool(x) should amount to x.is_valid for all classes inheriting from AlgebraicStructure
print(f"is valid: {binary_and.is_valid()} \nbool alternative: {bool(binary_and)}")
```

> is valid: True
> 
> bool alternative: True

```python
# this structure is also commutative but since this is a general structure
# this function will return a list of boolean values for every operator
print(f"is commutative: {binary_and.is_commutative()}")
```

> is commutative: [True]

```python
# since it is commutative we might want to model it as monoid,
# which only takes one operator
binary_and = SEPAlgebra.Semigroup({0, 1}, int.__mul__)
```

```python
# this structure is still commutative but now the return value is simply one boolean
print(f"is commutative monoid: {binary_and.is_commutative()}")
```

> is commutative monoid: True

```python
# since a monoid needs to be a valid algebraic structure and commutative,
# we can also check if it is valid and expect this to be true
print(f"is a valid monoid: {binary_and.is_valid()}")
```

> is a valid monoid: True

```python
# but 0 does not have an inverse in this structure so
# the singleton 'NoElement' will be returned
print(f"inverse for 0: {binary_and.find_inverses(0)}")
```

> inverse for 0: NoElement
