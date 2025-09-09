# directory scanning
from os import PathLike, listdir
from os.path import isdir, isfile, join, splitext

# what lets you actually run the functions
from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers, isfunction

def scandir(path: str | PathLike[str]) -> dict[str, list]:
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
        # get full path by joining current dir and current item
        full_path = join(root, entry)

        # find subdirectories by recursion!!!!! yippee!!!
        if isdir(full_path):
            tests.update(scandir(full_path))

        # if it is a file let's check it out
        elif isfile(full_path):
            name, ext = splitext(entry)

            # load and exec test module
            if ext == ".py" and name.endswith("_test"):
                spec = spec_from_file_location(name, full_path)
                module = module_from_spec(spec)
                spec.loader.exec_module(module)

                # gather all functions defined in that module
                funcs = [
                    func for _, func in getmembers(module, isfunction)
                    if func.__module__ == name
                ]
                tests[full_path] = funcs

    return tests