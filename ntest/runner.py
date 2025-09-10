# typing stuff
from typing import Any, Callable, Union, Type
from types import FunctionType

# time and traceback for tests
from time import perf_counter
from traceback import format_exc

# class checking, and the actual class to check for
from inspect import isclass
from .classes.TestCase import TestCase

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color

# function helpers (_runfunc and _runclass)
def _runfunc(
               item: FunctionType, 
               times: int
            ) -> tuple[bool, str | None, float]:
    """
    Run a single basic function test up to `times` attempts.
    Sends back passing status, and an error (if any)

    Args:
        item (FunctionType): The function to run.
        times (int): Number of attempts.

    Returns:
        tuple[bool, str | None]: (passed, error)
    """
    passed = False
    error: str | None = None

    for _ in range(max(1, int(times))):
        try:
            item()
            passed = True
            error = None

            # break on success
            break

        except Exception:
            # record last traceback
            error = format_exc()

    return passed, error

def _runclass(
               item: Type[TestCase], 
               name: str, 
               times: int
            ) -> tuple[bool, str | None]:
    """
    Run a single TestCase method up to `times` attempts.
    Sends back passing status, and an error (if any)

    Args:
        item (Type[TestCase]): The TestCase subclass.
        name (str): The method name to run.
        times (int): Number of attempts.

    Returns:
        tuple[bool, str | None]: (passed, error)
    """
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

    
    return passed, error

# iterate through all of the potential specs, determine class or function and call
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

    # empty list for results
    results: list[dict[str, str | bool | float | None]] = []

    # check if skip decorator is present
    skip: str | bool = getattr(item, "__skip__", False)
    if skip:
        print(f"{Color.YELLOW}{skip}{Color.RESET}")
        return results

    # build targets as (object, name, is_method)
    targets: list[tuple[Union[Callable[..., Any], Type[TestCase]], str, bool]] = []

    # if it is a proper class set er up first
    if isclass(item) and issubclass(item, TestCase):
        # this is just pass in case someone wants to override it
        item.setUpClass()

        # collect test_ methods (will change to be dynamic start/end) and .run driver
        test_methods = [
            name for name in dir(item)
            if name.startswith("test_") or name == "run"
        ]
        
        # add methods as targets
        targets = [(item, name, True) for name in test_methods]

    # otherwise a normal function
    else:
        targets = [(item, getattr(item, "__name__", str(item)), False)]

    for obj, name, is_method in targets:
        # find callable, skip flag, and display name
        parent: Any = getattr(obj, name) if is_method else obj
        skip: str | bool = getattr(parent, "__skip__", False)
        display: str = getattr(parent, "__name__", parent)

        # skip check
        if skip:
            print(f"{Color.YELLOW}skipping function {display}.{name} because: {skip}{Color.RESET}")
            continue

        # things we need get initialized here
        start: float = perf_counter()
        error: str | None = None
        passed: bool = False
        times: int
        reason: str

        # check for retry count and reason
        retry: int | tuple[int, str] = getattr(item, "__retry__", 0)
        times, reason = retry if isinstance(retry, tuple) else (retry, "")
        if times > 0 and reason:
            print(f"{Color.YELLOW}{reason}{Color.RESET}")

        # unpack timeout tuple if it's present
        timeout: str = getattr(parent if is_method else item, "__timeout__", False)
        clock: float | None = timeout[0] if timeout else None
        message: str = timeout[1] if timeout else ""
        
        # if we got output print it
        if message:
            print(f"{Color.YELLOW}{message}{Color.RESET}")

        # time
        start: float = perf_counter()

        # execute
        if is_method:
            # reuse existing helper for class methods
            passed, error = _runclass(item, name, times)

        else:
           # reuse existing helper for class methods
            passed, error = _runfunc(item, times)

        # time it
        duration: float = perf_counter() - start

        # apply timeout check if needed
        if clock is not None and duration > clock:
            passed = False
            error = f"Test timed out after {clock} seconds.\n" + (error or "")

        # formatted name (.run is shorthanded to the class name itself)
        formatted = f"{item.__name__}.{name}" if is_method and name != "run" else (item.__name__ if is_method else name)
        results.append({
            "name": formatted,
            "file": path,
            "passed": passed,
            "duration": duration,
            "error": error
        })

        # if we didn't pass and fast-fail is on, stop everything
        if not passed and ff:
            break

    return results

# main runner, takes a dict of files and functions, runs them all, and returns a summary
def runtest(files: dict[str, list], ff: bool, verbose: bool = False) -> tuple[list, list, int]:
    """
    Main test runner. Takes a dictionary of file paths and their associated test functions or classes.
    Runs each test, collecting results, and returns lists of passes, fails, and total run count. Prints test data along the way.

    Args:
        files (dict[str, list]): Dictionary mapping file paths to lists of test functions or classes.
        ff (bool): Fast fail flag.
        verbose (bool, optional): Verbose output flag. Defaults to False.

    Returns:
        tuple[list, list, int]: A tuple containing:
            - List of passing test result dictionaries.
            - List of failing test result dictionaries.
            - Total number of tests run.
    """
    # open empty pass and fail lists, count total runs
    passes: list[dict] = []
    fails: list[dict] = []
    runs: int = 0

    # go thru each file
    for path, funcs in files.items():
        # print file path
        print(f"\n{Color.BLUE}{path}{Color.RESET}")

        # if no funcs, skip
        if not funcs:
            print(f"{Color.YELLOW}No test functions found{Color.RESET}")
            continue

        # hoist iteration and message definitions
        iterations: int
        message: str
        
        # go thru each function in the file
        for func in funcs:
            # determine loop count and get message
            loopdata = getattr(func, "__loop__", 1)
            iterations, message = (loopdata, "") if not isinstance(loopdata, tuple) else loopdata

            if message:
                print(f"{Color.YELLOW}{message}{Color.RESET}")

            for index in range(iterations):
                # iterate thru all functions
                results = _iterfuncs(func, path, ff)

                for res in results:
                    # increment run count
                    runs += 1
                    
                    # add to pass or fail list
                    target_list = passes if res["passed"] else fails
                    target_list.append(res)

                    # print results
                    symbol = "✓" if res["passed"] else "✗"
                    color = Color.GREEN if res["passed"] else Color.RED
                    formatted: str = f"{res["duration"]:.6f}" if verbose else f"{res["duration"]:.3f}"

                    # if looping, add loop tag
                    loopcount: int = f"#{index + 1} " if iterations > 1 else ""
                    print(f"{color}{symbol} {res['name']} {loopcount}{Color.RESET}({formatted}s)")

                    # if we didn't pass and fast-fail is on, stop everything
                    if not res["passed"] and ff:
                        print(f"{Color.RED}Fail-fast enabled, stopping tests.{Color.RESET}")
                        return passes, fails, runs

    return passes, fails, runs