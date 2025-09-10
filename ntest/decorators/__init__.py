"""
Where all the decorators live. 

The list I currently have made is:
    - @loop: Mark a test to be repeated a given number of times. Good for stress or unit testing
    - @retry: Mark a test to be retried if it fails, but only a given number of times.
    - @skip: Mark a test method to be skipped. Hey idiot, this is why your test isn't running.
    - @timeout: Mark a test to be failed if it takes longer than the given number of seconds.

TBD:
    - @mock: decorator to mock objects or functions during a test
    - @benchmark: decorator to unit test performance of a function
    - @parameterize: decorator to run a test with different sets of arguments (maybe)
"""

# what other decorators i should add:
# - mock decorator to mock objects or functions during a test
# - benchmark decorator to unit test performance of a function
# - parametrize decorator to run a test with different sets of arguments (maybe)

from .loop import loop
from .retry import retry
from .skip import skip
from .timeout import timeout

__all__ = [
    "loop",
    "skip",
    "retry",
    "timeout"
]