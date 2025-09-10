# directory scanning
from os import PathLike, listdir
from os.path import isdir, isfile, join, splitext

# what lets you actually run the functions
from importlib.util import module_from_spec, spec_from_file_location
from importlib.machinery import ModuleSpec
from types import ModuleType
from inspect import getmembers, isfunction, isclass

# the testcase class and some other types
from .classes.TestCase import TestCase
from typing import Any, Callable

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
        split: tuple[str, str] = splitext(entry)
        name: str = split[0]
        ext: str = split[1]

        # find subdirectories by recursion!!!!! yippee!!!
        if isdir(long):
            tests.update(scandir(long))

        # if it is a file (and a python file that matches start and end)
        elif isfile(long) and ext == ".py" and name.startswith(start) and name.endswith(end):
            # load the module from the file
            spec: ModuleSpec | None = spec_from_file_location(name, long)

            # if we couldn't load it, skip it
            if spec is None or spec.loader is None:
                continue
            
            # get its contents
            module: ModuleType = module_from_spec(spec)
            spec.loader.exec_module(module)

            # gather all test functions and TestCase methods
            funcs: list[Callable[..., Any]] = []
            for _, member in getmembers(module):
                # first is function check, second is class. ik it's ugly
                if (
                    isfunction(member)
                    and member.__module__ == module.__name__
                    and member.__name__.startswith("test_")  # edit these two lines
                    and member.__name__.endswith("")         # to function pattern params (not the start and stop we have already)
                ) \
                or (
                    isclass(member)
                    and issubclass(member, TestCase)
                    and member.__module__ == module.__name__
                ):
                    funcs.append(member)

            # add to the dict if we found any at all
            tests[long] = funcs

    return tests