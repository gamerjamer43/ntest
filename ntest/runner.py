# types (static typing is my friend)
from queue import Queue
from types import FunctionType, ModuleType
from importlib.machinery import ModuleSpec
from multiprocessing.context import SpawnContext
from typing import Any, Callable, Union, Type, Literal

# test utilities
from time import perf_counter
from traceback import format_exc

from .classes.TestResult import TestResult

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

import io
import sys
import builtins
from contextlib import contextmanager

@contextmanager
def _no_io(output: bool):
    if output:
        yield
    else:
        orig_out, orig_err = sys.stdout, sys.stderr
        orig_input = builtins.input
        sys.stdout = sys.stderr = io.StringIO()
        builtins.input = lambda prompt='': (_ for _ in ()).throw(RuntimeError("STDIN disabled"))

        # yield control back
        try:
            yield
        
        # catch any exceptions and reraise
        finally:
            sys.stdout, sys.stderr = orig_out, orig_err
            builtins.input = orig_input

# function helpers (_runfunc and _runclass)
def _runfunc(
    item: FunctionType, 
    times: int,
    output: bool = False
) -> tuple[bool, str | None]:
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
        with _no_io(output):
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
               times: int,
               output: bool = False
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
        with _no_io(output):
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
def _proc_runner(queue, path, parent_name, method_name, is_method, times, output: bool = False):
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
    mod: ModuleType | None = None

    try:

        # i am a little upset b/c 
        fp = Path(path)
        if fp.suffix == ".py" and fp.exists():
            modname: str = f"{fp.stem}_{getpid()}"
            spec: ModuleSpec | None = spec_from_file_location(modname, str(fp))

            if spec and spec.loader:
                module: ModuleType = module_from_spec(spec)
                modules[modname] = module
                spec.loader.exec_module(module)
                mod = module

        # if we didn't load from file, try normal imports
        if mod is None:
            mod = import_module(path)

        # resolve the parent (could raise AttributeError)
        parent = getattr(mod, parent_name)

        # run the appropriate helper
        if is_method:
            passed, error = _runclass(parent, method_name, times, output)

        else:
            passed, error = _runfunc(parent, times, output)

    # catch errors
    except Exception:
        passed = False
        error = format_exc()

    # try and send result back to parent
    try:
        queue.put((passed, error))

    except Exception:
        # attempt one more time with a safe message, then swallow any exceptions
        try:
            queue.put((False, "Failed to send result from child process:\n" + format_exc()))
        except Exception:
            pass

# iterate through all of the potential specs, determine class or function and call
def _iterfuncs(
    item: Union[Callable[[], Any], FunctionType],
    path: str,
    ff: bool,
    output: bool = False
) -> list[TestResult]:
    """
    Unified runner for simple functions or TestCase subclasses.
    Iterates thru every function and calls either _runfunc or _runclass as needed.
    Threads are used if a timeout is provided, which may make this slow
    
    Args:
        item (big fat type): The test item, can be a function or a TestCase subclass.
        path (str): The file path where the function is defined.
        ff (bool): Fast fail flag.

    Returns:
        list[TestResult]: A list of TestResult items, check TestResult for more but: name, file, passed (bool), and error (str | None)."""

    # open empty list
    results: list[TestResult] = []

    # skip decorator at class level
    if getattr(item, "__skip__", False):
        print(f"{Color.YELLOW}{getattr(item, '__skip__')}{Color.RESET}")
        return results

    # build targets as (object, name, is_method)
    if isclass(item) and issubclass(item, TestCase):
        # class-level setup
        item.setUpClass()

        # methods = list of method names starting with "test_" or "run"
        # targets = list of test case, method, and mark method as method
        methods: list[str] = [n for n in dir(item) if n.startswith("test_") or n == "run"]
        targets: list[tuple[TestCase, str, Literal[True]]] = [(item, n, True) for n in methods] # type: ignore

    # otherwise just a function
    else:
        targets = [(item, getattr(item, "__name__", str(item)), False)] # type: ignore

    if not targets:
        return results

    # iterate through targets
    for obj, name, is_method in targets:
        # resolve parent (only two choices are class or function)
        parent = getattr(obj, name) if is_method else obj
        xfail: tuple[str, str] | bool = getattr(parent if is_method else item, "__xfail__", False)

        # skip decorator at method/function level
        if getattr(parent, "__skip__", False):
            # what does disp mean? explain: stupid robot what does disp mean: 
            display: str | Any = getattr(parent, "__name__", parent)
            reason: str = getattr(parent, "__skip__")

            print(f"{Color.YELLOW}skipping function {display}.{name} because: {reason}{Color.RESET}")
            continue
        
        # mark what we must
        start: float = perf_counter()
        passed: bool = False
        error: str | None = None

        # retry count and reason
        retry: tuple[int, str] | int = getattr(item, "__retry__", 0)
        times, reason = (retry, "") if not isinstance(retry, tuple) else retry
        if times > 0 and reason:
            print(f"{Color.YELLOW}{reason}{Color.RESET}")

        # timeout tuple
        timeout: tuple[float, str] = getattr(parent if is_method else item, "__timeout__", False) # type: ignore
        clock: float | None = timeout[0] if timeout else None
        message: str = timeout[1] if timeout else ""
        if message:
            print(f"{Color.YELLOW}{message}{Color.RESET}")

        # run in separate process if timeout is set
        if clock is not None:
            # multiprocess so we can yank it out of existence
            ctx: SpawnContext = get_context("spawn")
            q: Queue = ctx.Queue() # type: ignore

            # get parent and open process
            pname: str = getattr(item, "__name__", str(item))
            p = ctx.Process(
                target=_proc_runner,
                args=(q, path, pname, name, is_method, times, output)
            )

            # start and join with timeout
            p.start()
            p.join(clock)

            # clock er!
            duration: float = perf_counter() - start

            # if we're really still going??? timeout and error
            if p.is_alive():
                p.terminate()
                p.join()
                passed = False
                error = f"Test timed out after {clock} seconds.\n" + (error or "")

            # otherwise get result from queue
            else:
                try:
                    passed, error = q.get_nowait() # type: ignore

                except Exception:
                    passed = False
                    error = None
        else:
            # in-process run
            if is_method:
                passed, error = _runclass(item, name, times, output) # type: ignore
            else:
                passed, error = _runfunc(item, times, output)
            duration = perf_counter() - start

        # enforce timeout even if process returned quickly
        if clock is not None and duration > clock:
            passed = False
            error = f"Test timed out after {clock} seconds.\n" + (error or "")

        # xfail marks tests expected to fail
        if xfail:
            # unpack tuple or default
            if isinstance(xfail, tuple):
                xfail_reason, xfail_strict = xfail

            else:
                xfail_reason, xfail_strict = (str(xfail) if xfail else "", False)

            if passed:
                # Unexpected pass
                if xfail_strict:
                    # if it's strict fail it no matter what
                    passed = False
                    error = f"XPASS (strict): test passed unexpectedly but marked xfail, reason for this: {xfail_reason}".strip()

                else:
                    # allow pass but annotate
                    error = f"XPASS: test passed unexpectedly but marked xfail, reason for this: {xfail_reason}".strip()
            else:
                # expected failure means it counts as a pass
                passed = True
                error = f"XFAIL: expected failure. {xfail_reason}\n{error or ''}".strip()

        # formatted test name. lotta checks here
        formatted = (f"{item.__name__}.{name}"
                     if is_method and name != "run"
                     else (item.__name__ if is_method else name))
        
        results.append(TestResult(name=formatted, file=path, passed=passed, duration=duration, error=error))

        # fail-fast
        if not passed and ff:
            break

    return results

# main runner, takes a dict of files and functions, runs them all, and returns a summary
def runtest(files: dict[str, list], ff: bool, verbose: bool = False, output: bool = False) -> tuple[list[TestResult], list[TestResult], int]:
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
    passes: list[TestResult] = []
    fails: list[TestResult] = []
    runs = 0

    # go thru each file
    for path, funcs in files.items():
        # always print the file header
        print(f"\n{Color.BLUE}{path}{Color.RESET}")

        if not funcs:
            print(f"{Color.YELLOW}No test functions found{Color.RESET}")
            continue
        
        for func in funcs:
            # check for loop decorator
            loopdata = getattr(func, "__loop__", 1)
            iterations, message = (loopdata, "") if not isinstance(loopdata, tuple) else loopdata

            # print loop message if any
            if message:
                print(f"{Color.YELLOW}{message}{Color.RESET}")

            for index in range(iterations):
                for result in _iterfuncs(func, path, ff, output):
                    runs += 1
                    target: list = passes if result.passed else fails
                    target.append(result)

                    # always show test result
                    color = Color.GREEN if result.passed else Color.RED
                    formatted = f"{result.duration:.6f}" if verbose else f"{result.duration:.3f}"
                    looptag = f"#{index + 1} " if iterations > 1 else ""
                    print(f"{color}{'✓' if result.passed else '✗'} {result.name} {looptag}{Color.RESET}({formatted}s)")

                    if not result.passed and ff:
                        print(f"{Color.RED}Fail-fast enabled, stopping tests.{Color.RESET}")
                        return passes, fails, runs

    return passes, fails, runs