# ntest

Overview

ntest is a minimal Python unit testing framework designed to run just as good as any enterprise tests. It's both lightweight and fast for small tests, and super expansible for when you need it most.

A simple test:
```python
def test_other_test():
    assert "test" == "test"
```

Should give you some simple results:
```
Platform: Windows AMD64, Device Name: NoahsPC
Using: Python 3.13.2 [MSC v.1942 64 bit (AMD64)]
Package Version: ntest v0.0.1

Found file: .\test2_test.py, tests inside: test_other_test

.\test2_test.py
✓ test_other_test (0.00s)

1 passed, 0 failed, 1 total
```

Project Structure

- __init__.py: package marker
- argparser.py: defines CLI options (pattern, verbose, help)
- scanner.py: discovers test files and classes
- runner.py: executes tests and aggregates results
- colorize.py: applies ANSI colors to terminal output
- core.py: provides TestCase base class (IN A MINUTE!) and assertion methods

Quick Start

1. Clone this repo and install:

   ```bash
   git clone https://github.com/gamerjamer43/ntest
   cd ntest
   pip install -e .
   ```

2. Write a test (e.g., `tests/test_example.py`):

   ```python
   # when we add base cases you will be able to use a test case, for rn just use plain assert
   from ntest.core import TestCase

   def test() -> None:
        assert True == True

   class MathTests(TestCase):
       def test_addition(self):
           self.assertEqual(1 + 1, 2)

       def test_truth(self):
           self.assertTrue(True)
   ```

3. Run tests:

   ```bash
   ntest
   ```

I also added some command line options because we're def gonna need them:
- `-p, --pattern`: glob pattern for test file names (default `test_*.py`)
- `-v, --verbose`: show individual test names and statuses
- `-h, --help`: display help message

Docs will be provided if this actually gets large.

Contributing
Contributions welcome, feel free to report issues or send pull requests. Please include tests for any new behavior. If you really do wanna contribute I'll be shocked!

License
This project is released under the MIT License.
