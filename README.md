# ntest

### Overview:

ntest is a minimal Python unit testing framework designed to run just as good as any enterprise tests. It's both lightweight and fast for small tests, and super expansible for when you need it most. I also kinda suck at naming BUT...

---

A simple test:
```python
def test_other_test():
    assert "test" == "test"
```

Should give you some simple results:

<img width="403" height="172" alt="image" src="https://github.com/user-attachments/assets/072d5ed8-e856-4bd9-be47-74325030836f" />


---

### Inside the ntest folder:
```
ntest/
├── __init__.py     # package marker
│
├── argparser.py    # i wonder what this does... provides optional pattern, -v, and --fix-fast
├── scanner.py      # a basic function to walk directories (recursively scanning subs), returns the test files inside them, and their functions
├── runner.py       # goes thru the scanned functions and tests each one, logs output
├── colorize.py     # cool little color lib (if you could even call a lib, i'm only really using the class for colors instead of the functions)
└── core.py         # will have TestCase base class (soon) + all the assertion methods (will be moving main out of here)
```

---

### Quick Start

1. Clone this repo and install:

   ```bash
   git clone https://github.com/gamerjamer43/ntest
   cd ntest
   pip install -e .
   ```

2. Write a test (e.g., `tests/test_example.py`):

   ```python
   from ntest.core import TestCase
   
   # by default tests should prefix with test_, you can change both prefix and suffix tho
   def test_() -> None:
        assert True == True
   
   # TestCases were added babey lets go, some easy stuff
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
- `-s, --start`: specify the file name prefix for test files (default `''`).
- `-e, --end`: specify the file name suffix for test files (default `'_test.py'`).

- `-v, --verbose`: show a more precise time (3 digits on total time, 6 on tests. double the originals), and full error logs.
- `-ff, --fail-fast`: immediately quit on first failure (default `False`)

- `-h, --help`: display help message

---
### Docs:

Docs will be provided if this actually gets large.

### Contributing:

Contributions welcome, feel free to report issues or send pull requests. Please include tests for any new behavior. If you really do wanna contribute I'll be shocked!

### License:

This project is released under the MIT License. Will add it soon.