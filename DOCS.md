# ntest — User documentation (concise)

## Work In Progress

Quick start
-----------
1. Install the package (editable for development):
   pip install -e .

2. Create a tests directory and add a file named like `example_test.py` (default discovery looks for files matching the configured start/end but out of the box filenames ending in `_test.py` are used).

3. Run the runner from code or the CLI (if installed):
   - Programmatic:
     from ntest import scanner, runner
     files = scanner.scandir('tests')
     passes, fails, runs = runner.runtest(files, ff=False, verbose=False)

   - Or Quick Command:
      ntest [path: str = "."] [-s START --s START] [-e END --end END] [-v --verbose] [-ff --fail-fast]

Basic function test
-------------------
```python
# tests/example_test.py (TESTS BY DEFAULT MUST END IN _test YOU CAN CHANGE THIS, 
# FUNCTIONS MUST START WITH TEST_ YOU CANT CHANGE THIS YET)

def test_simple():
    assert 1 + 1 == 2
```

TestCase example
----------------
ntest also supports xUnit-style TestCase classes with setUp/tearDown and a class-level setUpClass hook.

```python
from ntest.classes.TestCase import TestCase

class MyTests(TestCase):
    @classmethod
    def setUpClass(cls):
        # optional class-level setup
        pass

    def setUp(self):
        # runs before each test method
        self.x = 1

    def tearDown(self):
        # runs after each test method
        del self.x

    def test_add(self):
        self.assertEqual(self.x + 1, 2)
```

Discovery and runner behavior
----------------------------
- scanner.scandir(path, start="", end="_test") -> dict[file_path, list]
  - Walks the given path recursively, finds .py files matching start/end, loads them, and returns a mapping of file paths to discovered callables (module-level test_ functions and TestCase subclasses).

- runner.runtest(files, ff, verbose=False) -> (passes, fails, runs)
  - Runs discovered items. For TestCase subclasses it runs all methods that start with `test_` plus an optional `run` method. Returns lists of passed and failed test result dictionaries and a run count.

Controlling tests: attributes and small decorators
------------------------------------------------
The runner recognizes a few attributes on functions and classes to control execution: __skip__, __retry__, __loop__, and __timeout__. You can set these attributes manually on functions or classes, or use small helper decorators like the examples below.

Common attributes
- __skip__: bool | str — if truthy, the item is skipped. If a string, printed as the reason.
- __retry__: int | (int, str) — number of attempts. If provided as (n, reason) the reason is printed before attempts.
- __loop__: int | (int, str) — repeat the *callable-group* this many times; if a tuple, a message is printed once.
- __timeout__: (seconds, message) | False — run the test in a child process and kill it if it exceeds seconds; message is printed if present.

These all come with decorators to call them, so you can literally just do:

- Skip a test function:
```python
  @skip("not implemented")
  def test_future():
      ...
```

- Retry a whole TestCase class up to 3 times with reason:
```python
  @retry(3, "flaky resource")
  class Flaky(TestCase):
      def test_something(self):
          ...
```

- Loop a module-level grouping (useful when a scanner returns the grouping as a single callable):
```python
  @loop(5, "running 5 times")
  def group():
      # group runner that calls multiple test functions
      ...
```

- Add a per-test timeout:
```python
  @timeout(2.5, "This test may hang")
  def test_hang():
      ...
```

Timeouts and isolation
----------------------
- If __timeout__ is set on a function or a TestCase method, the runner will execute the target in a separate process and kill it if it exceeds the timeout. The child process tries to import the module by file path and run only the requested target.

A short note on module loading and isolation
-------------------------------------------
- scanner and the child-process loader currently import modules from file paths using importlib.util.spec_from_file_location. When loading by file, ensure module names are unique to avoid importing two different files into the same module object. If you see odd cross-test interference, consider either making your test files unique by path/name or applying the recommended fix in the codebase (generate a unique module name from the absolute path and remove temporary entries from sys.modules after introspection).

Minimal usage pattern (programmatic)
-----------------------------------
```python
from ntest import scanner, runner
files = scanner.scandir('tests')
passes, fails, runs = runner.runtest(files, ff=False, verbose=True)
print(f"Passed: {len(passes)}  Failed: {len(fails)}  Total: {runs}")
```

If you want the concise README-style quick reference, use the project README. This document is focused on the features and how to use the attributes/decorators when writing tests.