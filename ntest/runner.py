# time and traceback for tests
from time import perf_counter
from traceback import format_exc

# class checking, and the actual class to check for
from inspect import isclass
from .TestCase import TestCase

# typing bullshit
from typing import Callable

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color

def _runfunc(item, path: str, ff: bool) -> list[dict[str, str, bool, str | None]]:
    """Unified runner for simple functions or TestCase subclasses.
    Args:
        item: The test item, can be a function or a TestCase subclass.
        path (str): The file path where the function is defined.
        ff (bool): Fast fail flag.

    Returns:
        list[dict[str, str, bool, str | None]]: A list of dictionaries with the test result values: name, file, passed (bool), and error (str | None).
    """
    results = []

    # check if class first
    if isclass(item) and issubclass(item, TestCase):
        # class‐level setUpClass
        try:
            item.setUpClass()
        except AttributeError:
            pass

        # collect all test_ methods
        test_methods = [name for name in dir(item) if name.startswith("test_") or name == "run"]

        # run each test method
        for name in test_methods:
            start = perf_counter()
            error = None

            # move this inside _runfunc
            try:
                inst = item()
                inst.setUp()
                getattr(inst, name)()
                inst.tearDown()
                passed = True

            except Exception:
                passed = False
                error = format_exc()

            # format the name nicely (if driver, just call it the class)
            formatted: str = f"{item.__name__}.{name}" if name != "run" else item.__name__

            # no matter what tho, time it and log result
            duration: float = perf_counter() - start
            result: dict = {
                "name": formatted,
                "file": path,
                "passed": passed,
                "duration": duration,
                "error": error
            }

            results.append(result)

            # fast‐fail
            if not passed and ff:
                break

        # class‐level tearDownClass
        try:
            item.tearDownClass()
        except AttributeError:
            pass

    # otherwise assume function   
    else:
        start = perf_counter()
        error = None

        # run function and time
        try:
            item()
            passed = True
        except Exception:
            passed = False
            error = format_exc()

        duration = perf_counter() - start
        results.append({"name": item.__name__, "file": path, "passed": passed, "duration": duration, "error": error})

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
            # replace inline logic with unified runner
            results = _runfunc(func, path, ff)
            for result in results:
                if result["passed"]: passes.append(result) 
                else: fails.append(result)

                # pass/fail symbol cuz cool, also colorize (circa me) and print results
                color: str = Color.GREEN if result["passed"] else Color.RED
                fmt: str = f"{result['duration']:.6f}" if verbose else f"{result['duration']:.3f}"
                print(f"{color}{'✓' if result['passed'] else '✗'} {result['name']}{Color.RESET} ({fmt}s)")

                if not result['passed'] and ff:
                    print(f"{Color.RED}Fail-fast enabled, stopping tests.{Color.RESET}")
                    return passes, fails, len(passes) + len(fails)

    # summarize
    return passes, fails, len(passes) + len(fails)