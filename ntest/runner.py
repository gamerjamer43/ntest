# time and traceback for tests
from time import perf_counter
from traceback import format_exc

# class checking, and the actual class to check for
from inspect import isclass
from .TestCase import TestCase

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color

# typing stuff
from typing import Any, Callable, Union, Type


def _runfunc(
    item: Union[Callable[[], Any], Type[TestCase]],
    path: str,
    ff: bool
    ) -> list[dict[str, str | bool | float | None]]:

    """Unified runner for simple functions or TestCase subclasses.
    
    Args:
        item (big fat type): The test item, can be a function or a TestCase subclass.
        path (str): The file path where the function is defined.
        ff (bool): Fast fail flag.

    Returns:
        list[dict[str, str, bool, str | None]]: A list of dictionaries with the test result values: name, file, passed (bool), and error (str | None)."""
    
    # empty list to hold results
    results: list[dict[str, str | bool | float | None]] = []

    # skip entire flat function or TestCase class
    if getattr(item, "__skip__", False):
        return results

    if isclass(item) and issubclass(item, TestCase):
        # class-level setUpClass
        try:
            item.setUpClass()
        except AttributeError:
            pass

        # collect test_ methods and .run driver
        test_methods = [
            name for name in dir(item)
            if name.startswith("test_") or name == "run"
        ]

        for name in test_methods:
            method = getattr(item, name)

            # skip this test method if marked
            if getattr(method, "__skip__", False):
                continue

            start = perf_counter()
            error = None

            try:
                inst = item()
                inst.setUp()
                getattr(inst, name)()
                inst.tearDown()
                passed = True
            except Exception:
                passed = False
                error = format_exc()

            formatted = f"{item.__name__}.{name}" if name != "run" else item.__name__
            duration = perf_counter() - start

            results.append({
                "name": formatted,
                "file": path,
                "passed": passed,
                "duration": duration,
                "error": error
            })

            if not passed and ff:
                break

        # class-level tearDownClass
        try:
            item.tearDownClass()
        
        except AttributeError:
            pass

    else:
        # skip this test method if marked
        if not getattr(item, "__skip__", False):
            # flat function
            start = perf_counter()
            error = None

            try:
                item()
                passed = True

            except Exception:
                passed = False
                error = format_exc()

            duration = perf_counter() - start
            results.append({
                "name": item.__name__,
                "file": path,
                "passed": passed,
                "duration": duration,
                "error": error
            })

    return results

def runtest(files: dict[str, list], ff: bool, verbose: bool = False) -> tuple[list, list, int]:
    # open empty pass and fail lists
    passes: list[dict] = []
    fails: list[dict] = []

    # run each test and record outcome
    for path, funcs in files.items():
        # print the path
        print(f"\n{Color.BLUE}{path}{Color.RESET}")

        # test if there's any functions
        if funcs == []:
            print(f"{Color.YELLOW}No test functions found{Color.RESET}")

        for func in funcs:
            # check for loop decorator
            iterations: int = getattr(func, "__loop__", 1)

            for index in range(iterations):
                # unified runner
                results = _runfunc(func, path, ff)

                # if there are results (not skipped)
                for result in results:
                    # pass/fail
                    if result["passed"]: passes.append(result) 
                    else: fails.append(result)

                    # colorize (circa me) and print results
                    color: str = Color.GREEN if result["passed"] else Color.RED
                    fmt: str = f"{result['duration']:.6f}" if verbose else f"{result['duration']:.3f}"
                    print(f"{color}{'✓' if result['passed'] else '✗'} {result['name']} {"#" + str(index + 1) + " " if iterations > 1 else ""}{Color.RESET}({fmt}s)")

                    # if we didn't pass and fast-fail is on, stop everything
                    if not result['passed'] and ff:
                        print(f"{Color.RED}Fail-fast enabled, stopping tests.{Color.RESET}")
                        return passes, fails, len(passes) + len(fails)

    # summarize
    return passes, fails, len(passes) + len(fails)