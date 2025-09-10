# directory scanning
from os import PathLike, listdir
from os.path import isdir, isfile, join, splitext

# what lets you actually run the functions
from importlib.util import module_from_spec, spec_from_file_location
from importlib.machinery import ModuleSpec
from types import ModuleType
from inspect import getmembers, isfunction, isclass

# the testcase class and some other types
from .TestCase import TestCase
from typing import Any, Callable
from importlib.machinery import ModuleSpec
from types import ModuleType
from inspect import getmembers, isfunction, isclass

def _collect_tests(obj: Any, module: ModuleType, start: str = "test_", end: str = "") -> list[Callable[..., Any]]:
    """Collect all test functions and TestCase methods from a given object within a module.
    When you provide a start and end, functions are ONLY matched that start or end with those strings.
    The class itself is ran thru the run method, so it is added to the list by its own name.

    Args:
        obj (Any): The object to inspect (function or class).
        module (ModuleType): The module where the object is defined.
        start (str, optional): The prefix that test function/method names should start with. Defaults to "test_".
        end (str, optional): The suffix that test function/method names should end with. Defaults to "".
    
    Returns:
        list[Callable[..., Any]]: A list of collected test functions and methods.
    """
    # start an empty list for the functions we have rn
    funcs: list[Callable[..., Any]] = []

    # normal top level functions
    if (
        isfunction(obj)
        and obj.__module__ == module.__name__
        and obj.__name__.startswith(start)
        and obj.__name__.endswith(end)
    ):
        funcs.append(obj)

    # TestCase subclasses (just append the class, not its methods)
    elif (
        isclass(obj)
        and issubclass(obj, TestCase)
        and obj.__module__ == module.__name__
    ):
        funcs.append(obj)

    return funcs

def scandir(path: str | PathLike[str], start: str = "", end: str = "_test") -> dict[str, list]:
    """Walk the provided path and find all *_test.py files, returning a dict of file paths and their functions.
    Also works thru subdirectories using my little friend recursion. Looks for functions only in modules named *_test.py for right now.
    Will eventually make it so: 
    1) you can specify your own test file pattern 
    2) you can specify your own test function pattern 
    3) you can just plug a custom file

    Args:
        path (str | PathLike[str]): The root directory to scan for test files. Defaults to current directory.
    
        
    Returns:
        dict[str, list]:  Keys are file paths, values are lists of callables found in matched files.
    """

    # root directory to scan
    root: str | PathLike[str] = path or '.'

    # dict of test file paths and their lists of functions
    tests: dict[str, list] = {}

    # walk directory
    for entry in listdir(root):
        # get full path by joining current dir and current item, split name and ext
        long: str = join(root, entry)

        # split into name and extension
        name: str = splitext(entry)[0]
        ext: str = splitext(entry)[1]

        # find subdirectories by recursion!!!!! yippee!!!
        if isdir(long):
            tests.update(scandir(long))

        # if it is a file (and a python file that matches start and end)
        elif isfile(long) and ext == ".py" and name.startswith(start) and name.endswith(end):
            spec: ModuleSpec | None = spec_from_file_location(name, long)
            if spec is None or spec.loader is None:
                continue
            
            module: ModuleType = module_from_spec(spec)
            spec.loader.exec_module(module)

            # gather all test functions and TestCase methods
            funcs: list[Callable[..., Any]] = []
            for _, member in getmembers(module):
                funcs.extend(_collect_tests(member, module))
            
            # add to the dict if we found any at all
            tests[long] = funcs

    return tests