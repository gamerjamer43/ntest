"""
ntest – A Lightweight Python toolkit for writing and running unit tests. 
This is an effort to "write my own unit tests" as the cool kids say. 
I don't hate pyunit (I hate their prints) but I just like making my own stuff.

installation:
    `pip install ntest`

quickstart:
    - just make a funcy:

    def test() -> None:
        assert 1 + 1 == 2

    - then run ntest:
    `ntest [path: default='.'] -s START -e END -v -ff`
    
    ```python
    Platform: Windows AMD64, Device Name: NoahsPC                                                                                                                                                                                             
    Using: Python 3.13.2 [MSC v.1942 64 bit (AMD64)]
    Package Version: ntest v0.0.1

    .\\test2_test.py
    ✓ test_addition (0.000s)

    .\\test_test.py
    No test functions found

    1 passed, 0 failed, 1 total
    ```

    - classes are also provided but that's unnecessary to put here just look into the docs (when i make em)
    
simple azzat.


For more details and examples, see the README on GitHub:
https://github.com/gamerjamer43/ntest
"""

# basic ass template for __init__ which i will definitely be reusing
from importlib.metadata import version as _version

__title__ = "ntest"
__license__ = "MIT"
__author__ = "Noah Mingolelli"
__copyright__ = "2025 till 9999, and then maybe you can have it, Noah Mingolelli."

try:
    __version__ = _version("ntest")

except Exception:
    __version__ = "0.0.1" # if i'm still to lazy to publish we're still in 0.0.1

# top level imports
from .core import main
from .classes.TestCase import TestCase
from .classes.TestResult import TestResult

__all__ = [
    "main",
    "TestCase",
    "TestResult",
]