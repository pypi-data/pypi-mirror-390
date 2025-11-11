# enumex (Python)

An extension of the std enum, with the added ability to inherit and use abstract methods.

Lowest python version tested 3.9.13

Converted enum.py from Python 3.11.4

### Install
``` bash
pip install enumex
```

## Usage

Use exactly like the standard enum, with inheritance and `@abstractmethod`.

``` python
from enumex import EnumEx, autoex as auto

class A(EnumEx):
    Val1 = auto()
    Val2 = auto()  

    def print(self):
        print(f"{self.__class__.__name__} {self.name} : {self.value}")

class B(A):
    Val3 = auto()
    Val4 = auto()

print("Printing A...")
for e in A:
    e.print()  

print("\nPrinting B...")
for e in B:
    e.print()

# Printing A...
# A Val1 : 1
# A Val2 : 2

# Printing B...
# B Val1 : 1
# B Val2 : 2
# B Val3 : 3
# B Val4 : 4
```

## License
[Python](https://github.com/python/cpython/blob/main/LICENSE)