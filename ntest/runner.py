# typing stuff
from typing import Any, Callable, Union, Type

# time and traceback for tests
from time import perf_counter
from traceback import format_exc

# class checking, and the actual class to check for
from inspect import isclass
from .classes.TestCase import TestCase

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color

def _runclass(
               item: Type[TestCase], 
               name: str, 
               times: int
            ) -> tuple[bool, str | None, float]:
    """
    Run a single TestCase method up to `times` attempts.
    Sends back passing status, error (if any), and duration.

    Args:
        item (Type[TestCase]): The TestCase subclass.
        name (str): The method name to run.
        times (int): Number of attempts.

    Returns:
        tuple[bool, str | None, float]: (passed, error, duration)
    """
    start: float = perf_counter()
    passed = False
    error: str | None = None

    for _ in range(max(1, int(times))):
        try:
            # instantiate
            inst = item()

            # run with setup and teardown
            inst.setUp()
            getattr(inst, name)()
            inst.tearDown()

            # log results
            passed = True
            error = None

            # break on success
            break

        except Exception:
            # record last traceback
            error = format_exc()

    # time it
    duration: float = perf_counter() - start
    return passed, error, duration

def _iterfuncs(
        item: Union[Callable[[], Any], Type[TestCase]],
        path: str,
        ff: bool
    ) -> list[dict[str, str | bool | float | None]]:
    """
    Unified runner for simple functions or TestCase subclasses.
    Iterates thru every function and calls either _runfunc or _runclass as needed.
    Threads are used if a timeout is provided, which may make this slow
    
    Args:
        item (big fat type): The test item, can be a function or a TestCase subclass.
        path (str): The file path where the function is defined.
        ff (bool): Fast fail flag.

    Returns:
        list[dict[str, str, bool, str | None]]: A list of dictionaries with the test result values: name, file, passed (bool), and error (str | None)."""
    
    # empty list to hold results
    results: list[dict[str, str | bool | float | None]] = []

    # unified skip check for functions and TestCase classes
    skip: str | bool = getattr(item, "__skip__", False)
    if skip:
        print(f"{Color.YELLOW}{skip}{Color.RESET}")
        return results

    if isclass(item) and issubclass(item, TestCase):
        # setup class before running each test
        item.setUpClass()

        # collect test_ methods and .run driver
        test_methods = [
            name for name in dir(item)
            if name.startswith("test_") or name == "run"
        ]

        # work thru all of em
        for name in test_methods:
            method = getattr(item, name)

            # skip this test method if marked
            if skip:
                print(f"{Color.YELLOW}skipping function {item.__name__}.{name} because: {skip}{Color.RESET}")
                continue
            
            # init empty error, start timer
            start: float = perf_counter()
            error: str | None = None
            passed: bool

            # retry count is the first element and reason is the 2nd
            times: tuple | int = getattr(item, "__retry__", 1)
            if isinstance(times, tuple): times: tuple = times[0]

            # print if timing out
            if getattr(method, "__timeout__", False):
                timeout: float = getattr(method, "__timeout__")[0]
                message: str = getattr(method, "__timeout__")[1]

                print(f"{Color.YELLOW}{message}{Color.RESET}")

            # try running everything
            passed, error, duration = _runclass(item, name, times)

            # timeouts do NOT
            if getattr(item, "__timeout__", False) and duration > timeout:
                passed = False
                error = f"Test timed out after {timeout} seconds.\n" + (error or "")

            formatted = f"{item.__name__}.{name}" if name != "run" else item.__name__

            results.append({
                "name": formatted,
                "file": path,
                "passed": passed,
                "duration": duration,
                "error": error
            })

            if not passed and ff:
                break

    else:
        # flat function
        start: float = perf_counter()
        error: str | None = None
        passed: bool
        
        # retry count is the first element and reason is the 2nd
        times: tuple | int = getattr(item, "__retry__", 1)
        if isinstance(times, tuple): times: tuple = times[0]

        # print if retrying
        if times > 1:
            reason: str = getattr(item, "__retry__", ("", ""))[1]
            print(f"{Color.YELLOW}{reason}{Color.RESET}")

        # print if timing out
        if getattr(item, "__timeout__", False):
            timeout: float = getattr(item, "__timeout__")[0]
            message: str = getattr(item, "__timeout__")[1]

            print(f"{Color.YELLOW}{message}{Color.RESET}")

        # try running everything
        for _ in range(times):
            try:
                item()
                passed = True

            except Exception:
                passed = False
                error = format_exc()

            # time and break if passed
            duration = perf_counter() - start
            if passed:
                break
        
        # timeouts do NOT
        if getattr(item, "__timeout__", False) and duration > timeout:
            passed = False
            error = f"Test timed out after {timeout} seconds.\n" + (error or "")
        
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
            # determine the number of iterations (first element if __loop__ is a tuple)
            loop: tuple | int = getattr(func, "__loop__", 1)
            reason: str = ""

            # if tuple, get first element
            if isinstance(loop, tuple): 
                iterations = loop[0]
                reason = loop[1]
            
            # otherwise just 1
            else: iterations = 1

            if reason != "":
                print(f"{Color.YELLOW}{reason}{Color.RESET}")

            for index in range(iterations):
                # unified runner
                results = _iterfuncs(func, path, ff)

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