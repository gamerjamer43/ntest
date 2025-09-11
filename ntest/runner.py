# typing stuff
from importlib.machinery import ModuleSpec
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

# module helpers
from importlib import import_module
from sys import modules

# multiprocessing helpers (all this for timeouts)
from importlib.util import module_from_spec, spec_from_file_location
from multiprocessing import get_context
from os import getpid
from pathlib import Path

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

# helper to run a test target inside a separate process and return results via a queue
def _proc_runner(queue, path, parent_name, method_name, is_method, times):
    """
    Runs a test function or TestCase method inside a separate process.
    Imports the module (by file path or module name), resolves the parent (function or class) by name,
    runs the target and puts (passed, error) on the queue.

    Args:
        queue (multiprocessing.Queue): Queue to send results back to parent process.
        path (str): The module name or file path where the function/class is defined.
        parent_name (str): The name of the function or class to run.
        method_name (str): The method name to run if parent is a class.
        is_method (bool): True if parent is a class, False if it's a function.
        times (int): Number of attempts.

    Returns:
        None: Results are sent via the queue.
    """
    passed = False
    error: str | None = None

    try:
        mod = None
        fp: str = Path(path)
        if fp.suffix == ".py" and fp.exists():
            module_name = f"{fp.stem}_{getpid()}"
            spec: ModuleSpec = spec_from_file_location(module_name, str(fp))
            if spec and spec.loader:
                mod = module_from_spec(spec)
                modules[module_name] = mod
                spec.loader.exec_module(mod)

        # normal import if load failed or path is a module name
        if mod is None:
            mod = import_module(path)

        # resolve the parent (could raise AttributeError)
        parent = getattr(mod, parent_name)

        # if it's a method, run class helper, else func helper
        if is_method:
            passed, error = _runclass(parent, method_name, times)

        else:
            passed, error = _runfunc(parent, times)

    except Exception:
        passed = False
        error = format_exc()

    # best-effort send result back to parent
    try:
        queue.put((passed, error))

    # also put errors
    except Exception:
        queue.put((False, "Failed to send result from child process:\n" + format_exc()))

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

        # execute with optional timeout in a separate process
        start = perf_counter()
        if clock is not None:

            ctx = get_context("spawn")
            q = ctx.Queue()
            parent_name = getattr(item, "__name__", str(item))
            p = ctx.Process(target=_proc_runner, args=(q, path, parent_name, name, is_method, times))
            p.start()
            p.join(clock)

            duration = perf_counter() - start

            if p.is_alive():
                # timeout exceeded: terminate process and mark failed
                p.terminate()
                p.join()
                passed = False
                error = f"Test timed out after {clock} seconds.\n" + (error or "")
            else:
                # process finished within timeout, fetch result if available
                try:
                    passed, error = q.get_nowait()
                except Exception:
                    passed = False
                    error = None

        else:
            # no timeout: run in-process as before
            if is_method:
                passed, error = _runclass(item, name, times)
            else:
                passed, error = _runfunc(item, times)

            duration = perf_counter() - start

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