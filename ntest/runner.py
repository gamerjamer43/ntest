# types (static typing is my friend)
from types import FunctionType, ModuleType
from importlib.machinery import ModuleSpec
from typing import Any, Callable, Generator, Union, Type, Literal

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

# multiprocessing helpers
from importlib.util import module_from_spec, spec_from_file_location
from multiprocessing import Queue, get_context
from multiprocessing.context import SpawnContext
from os import getpid
from pathlib import Path

# ...and more (fuck i need to clean up)
import io
import sys
import builtins
from contextlib import contextmanager

@contextmanager
def __no_io(output: bool) -> Generator:
    """
    Disables IO in the console (for testing functions)

    """
    # if we have output, give control back
    if output:
        yield

    else:
        # steal out, error, and input from sys
        out, error = sys.stdout, sys.stderr
        inp: FunctionType = builtins.input

        # set them to an in mem buffer
        sys.stdout = sys.stderr = io.StringIO()

        # any call to input now throws a runtime error. gonna make patch bypass this
        builtins.input = lambda prompt='': (_ for _ in ()).throw(RuntimeError("STDIN disabled"))

        # hand control back to main
        try:
            yield
        
        # catch any exceptions and reraise
        finally:
            sys.stdout, sys.stderr = out, error
            builtins.input = inp

# function helpers (__runfunc and __runclass)
def __runfunc(
    item: FunctionType, 
    times: int,
    output: bool = False
) -> tuple[bool, str | None]:
    """
    Run a single function test up to `times` attempts.
    Sends back pass/fail status, and an error (if any)

    Args:
        item (FunctionType): The function to run.
        times (int): Number of attempts.

    Returns:
        tuple[bool, str | None]: (passed, error)
    """
    # pass and error status outside
    passed: bool = False
    error: str | None = None

    for _ in range(max(1, int(times))):
        # disable io while we run
        with __no_io(output):
            # try n run that shit and flag a pass
            try:
                item()
                passed = True

                # break on success
                break
            
            # if we don't pass that shit record a traceback
            except Exception:
                error = format_exc()

    # send status back
    return passed, error

def __runclass(
               item: Type[TestCase], 
               name: str, 
               times: int,
               output: bool = False
            ) -> tuple[bool, str | None]:
    """
    Run a single TestCase method up to `times` attempts.
    Sends back passing status, and an error (if any)

    Args:
        item (Type[TestCase]): The full TestCase subclass.
        name (str): The method name to run.
        times (int): Number of attempts.

    Returns:
        tuple[bool, str | None]: (passed, error)
    """
    passed = False
    error: str | None = None

    for _ in range(max(1, int(times))):
        # disable io while we run
        with __no_io(output):
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

def __proc_runner(queue, path, parent_name, method_name, is_method, times, output: bool = False):
    """
    Runs a test function or TestCase method inside a separate process.
    Re-imports the module, resolves the parent (function or class) by name,
    runs the target and puts (passed, error) on the queue.
    """
    passed = False
    error: str | None = None
    mod: ModuleType | None = None

    try:
        # try loading from file path first
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

        # run the appropriate helper. yes this is not elegant but i'm not compressing runfunc into 1
        if is_method:
            passed, error = __runclass(parent, method_name, times, output)
        else:
            passed, error = __runfunc(parent, times, output)

    except Exception:
        passed = False
        error = format_exc()

    # try and send result back to parent
    try:
        queue.put((passed, error))
    except Exception:
        try:
            queue.put((False, "Failed to send result from child process:\n" + format_exc()))
        except Exception:
            pass

# iterate through all of the potential specs, determine class or function and call
def __iterfuncs(
    item: Union[Callable[[], Any], FunctionType],
    path: str,
    ff: bool,
    output: bool = False
) -> list[TestResult]:
    """
    Runner for both simple functions or TestCase subclasses.
    Iterates thru every function and calls either __runfunc or __runclass as needed.
    Threads are used if a timeout is provided, which may make this slow
    
    Args:
        item (big fat type): The test item, can be a function or a TestCase subclass.
        path (str): The file path where the function is defined.
        ff (bool): Fast fail flag.

    Returns:
        list[TestResult]: A list of TestResult items, check TestResult for more but: name, file, passed (bool), and error (str | None).
    """
    # store all test results
    results: list[TestResult] = []

    # check for skip decorator at class level
    if getattr(item, "__skip__", False):
        print(f"{Color.YELLOW}{getattr(item, '__skip__')}{Color.RESET}")
        return results

    # build targets as (object: TestCase, name: str, is_method: bool)
    if isclass(item) and issubclass(item, TestCase):
        # class-level setup
        item.setUpClass()

        # methods = list of method names starting with "test_" or "run"
        # targets = list of test case, method, and mark method as method. these genexps are ugly but save me like 15 lines
        methods: list[str] = [n for n in dir(item) if n.startswith("test_") or n == "run"]
        targets: list[tuple[type[TestCase], str, Literal[True]]] = [(item, n, True) for n in methods]

    # otherwise just a function
    else:
        targets = [(item, getattr(item, "__name__", str(item)), False)] # type: ignore (i am NOT doin all that)

    # if no targets quit
    if not targets:
        return results

    # unpack (cuz remember, tuple(object: TestCase, name: str, is_method: bool))
    for obj, name, is_method in targets:
        # test status stored outside so no fuckies
        passed: bool = False
        error: str | None = None
    
        # resolve parent (either a class or function nothing else)
        parent = getattr(obj, name) if is_method else obj

        # get all decorators up top
        timeout: tuple[float, str] | bool = getattr(parent if is_method else item, "__timeout__", False)
        xfail: tuple[str, str] | bool = getattr(parent if is_method else item, "__xfail__", False)
        retry: tuple[int, str] | int = getattr(item, "__retry__", 0)

        # check for skip decorator at method/function level
        if getattr(parent, "__skip__", False):
            # what does disp mean? explain: stupid robot what does disp mean: 
            display: str | Any = getattr(parent, "__name__", parent)
            reason: str = getattr(parent, "__skip__")

            print(f"{Color.YELLOW}skipping function {display}.{name} because: {reason}{Color.RESET}")
            continue

        # handle retries
        times, reason = (retry, "") if not isinstance(retry, tuple) else retry
        if times > 0 and reason:
            print(f"{Color.YELLOW}{reason}{Color.RESET}")
        
        # ugly ternaries but they allow for handling of non provided time
        clock: float | None = timeout[0] if timeout else None # type: ignore (shut to fuck up pylance)
        message: str = timeout[1] if timeout else "" # type: ignore
        if message:
            print(f"{Color.YELLOW}{message}{Color.RESET}")

        # start the clock baby
        start: float = perf_counter()

        # run with timeout in separate process
        if clock:
            # create a queue in context
            ctx: SpawnContext = get_context("spawn")
            pqueue: Queue = ctx.Queue()

            # target process runner and spawn with a whole fuckload of arguments... its documented
            pname: str = getattr(item, "__name__", str(item))
            p = ctx.Process(
                target = __proc_runner,
                args = (pqueue, path, pname, name, is_method, times, output)
            )
            
            # lifetime of the process is here, kill after timeout and time how long it took
            p.start()
            p.join(timeout=clock)
            duration: float = perf_counter() - start
            
            # if it's somehow still alive kill it
            if p.is_alive():
                p.terminate()
                p.join()
                passed = False
                error = f"Test timed out after {clock} seconds.\n"

            else:
                try:
                    # get status
                    passed, error = pqueue.get_nowait()

                except:
                    # and if it fucks up one more time just return a generic msg
                    passed = False
                    error = "Process ended without returning result.\n"
        
        # nesting hell it's all fucking necessary though
        else:
            # run a class method
            if is_method:
                passed, error = __runclass(item, name, times, output) # type: ignore

            # run a function if it's not a method
            else:
                passed, error = __runfunc(item, times, output)

            # time duration
            duration: float = perf_counter() - start

        # enforce timeout even if returned quickly. 
        # this shouldn't get reached but for you fuckers tryna fudge tests
        if clock and duration > clock:
            passed = False
            error = f"Test timed out after {clock} seconds.\n" + (error or "")

        # mark a test as expected to fail
        if xfail:
            # either unpack to a tuple if we have xfail strict provided
            if isinstance(xfail, tuple):
                xfail_reason, xfail_strict = xfail

            # strictness by default is just false
            else:
                xfail_reason, xfail_strict = (str(xfail) if xfail else "", False)
            
            # handle an unexpected pass
            if passed:
                if xfail_strict:
                    # if it's strict fail it no matter what
                    passed = False
                    error = f"XPASS (strict): test passed unexpectedly but marked xfail, reason for this: {xfail_reason}".strip()

                else:
                    # otherwise allow it to pass but make a note
                    error = f"XPASS: test passed unexpectedly but marked xfail, reason for this: {xfail_reason}".strip()

            else:
                # expected failures should reach here
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

def __result(
    result: TestResult,
    passes: list[TestResult],
    fails: list[TestResult],
    verbose: bool,
    iterations: int,
    index: int
) -> None:
    """
    Processes and displays one test result, adding it to the proper list of passes or fails.

    Args:
        - result (TestResult) = A single test result.
        - passes (list[TestResult]) = A list of passing results (will be added directly via a reference.)
        - fails (list[TestResult]) = A list of failing results (will be added directly via a reference.)
        - verbose (bool) = Prints a full error result and .6f if True, else defaults to .3f and just the error
        - iterations (int) = How many times it took (and if looped we print that), doesn't print if 1.
        - index (int) = What result number this was.
    """
    # add to the proper list
    target = passes if result.passed else fails
    target.append(result)
    
    # ugly text formatting shit i will minimize the pain on your eyes
    color = Color.GREEN if result.passed else Color.RED
    duration_fmt = f"{result.duration:.6f}" if verbose else f"{result.duration:.3f}"
    loop_tag = f"#{index + 1} " if iterations > 1 else ""
    status = '✓' if result.passed else '✗'
    
    # ok now we log!!!
    print(f"{color}{status} {result.name} {loop_tag}{Color.RESET}({duration_fmt}s)")

# main runner
def runtest(files: dict[str, list], ff: bool, verbose: bool = False, output: bool = False) -> tuple[list[TestResult], list[TestResult], int]:
    """
    Main test runner. Given a dictionary of file paths and their associated test functions or classes,
    this function runs each test; takes results from it; and returns a list of passes and fails, as well as a total run count.
    Also displays results using __result.

    Args:
        files (dict[str, list]) = Dictionary mapping file paths to lists of test functions or classes.
        ff (bool) = Fast fail flag.
        verbose (bool, optional) = Verbose output flag. Defaults to False.

    Returns:
        tuple[list, list, int] = A tuple containing:
            - list[TestResult] = containing passing tests
            - list[TestResult] = containing failing tests
            - int = number of tests run
    """
    # lists of passes and fails, and a run count
    passes: list[TestResult] = []
    fails: list[TestResult] = []
    runs: int = 0

    for path, funcs in files.items():
        print(f"\n{Color.BLUE}{path}{Color.RESET}")

        # if no tests found in a file warn the user
        if not funcs:
            print(f"{Color.YELLOW}No test functions found{Color.RESET}")
            continue
        
        for func in funcs:
            # loop info is tupled with a message, get that and send iteration count. if not found default to 1
            loopdata: tuple[int, str] | int = getattr(func, "__loop__", 1)
            iterations, message = (loopdata, "") if isinstance(loopdata, int) else loopdata
            if message:
                print(f"{Color.YELLOW}{message}{Color.RESET}")

            # retry function that many times
            for index in range(iterations):
                for result in __iterfuncs(func, path, ff, output):
                    runs += 1
                    __result(result, passes, fails, verbose, iterations, index)

                    # fast fail stops all testing immediately
                    if not result.passed and ff:
                        print(f"{Color.RED}Fail-fast enabled, stopping tests.{Color.RESET}")
                        return passes, fails, runs

    # return pass/fail lists and run count
    return passes, fails, runs