# basic ass template for __init__ which i will definitely be reusing
from importlib.metadata import version as _version

"""
ntest – A Lightweight Python toolkit for writing and running unit tests. 
This is an effort to "write my own unit tests" as the cool kids say. I don't hate pyunit I just like making my own.

installation:
    pip install ntest

quickstart:
    - just make a funcy:

    def test() -> None:
        assert 1 + 1 == 2

    - then run ntest

    [output here when i'm not lazy]


For more details and examples, see the README on GitHub:
https://github.com/username/ntest
"""

__title__ = "ntest"
__license__ = "MIT"
__author__ = "Noah Mingolelli"
__copyright__ = "2025 till 9999, and then maybe you can have it, Noah Mingolelli."

try:
    __version__ = _version("ntest")
except Exception:
    __version__ = "0.0.1"

# top level imports
from .core import main

__all__ = [
    "main",
]

# template for imports (i'm a lazy developer)
# from .module1 import ClassName, function_name
# from .module2 import AnotherClass, another_function
