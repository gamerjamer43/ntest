from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers, isfunction
from os import PathLike, listdir
from os.path import isdir, isfile, join, splitext
from platform import machine, node, python_compiler, python_version, system
from shutil import get_terminal_size

# version info
from ntest import __version__

# colorize func unused but i might, it's in printc tho
from .colorize import Color


def _scandir(path: str | PathLike[str]) -> dict[str, list]:
    # root directory to scan
    root = path or '.'

    # dict of test file paths and their lists of functions
    tests: dict[str, list] = {}

    # walk directory
    for entry in listdir(root):
        # get full path by joining current dir and current item
        full_path = join(root, entry)
        if isdir(full_path):
            # recurse into subdirectories
            tests.update(_scandir(full_path))

        elif isfile(full_path):
            name, ext = splitext(entry)
            if ext == ".py" and name.endswith("_test"):
                # load and exec test module
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

def main() -> None:
    # get terminal width
    cols = get_terminal_size(fallback=(80, 24)).columns - 1

    # scan directory for tests
    files: dict[str, list] = _scandir('.')

    # print header info (gone add more as plugin manager and shit work in)
    print(f"{Color.GREEN}{'=' * (cols // 2 - 6)} TESTS START {'=' * (cols // 2 - 6)}{Color.RESET}")
    print(f"Platform: {Color.GREEN}{system()} {machine()}{Color.RESET}, Device Name: {Color.GREEN}{node()}{Color.RESET}")
    print(f"Using: {Color.GREEN}Python {python_version()} [{python_compiler()}]{Color.RESET}")
    print(f"Package Version: {Color.GREEN}ntest v{__version__}{Color.RESET}")

    # go thru files and print functions (we're gonna call them for the tests)
    for file, funcs in files.items():
        print(f"Found file: {Color.GREEN}{file}{Color.RESET}, tests inside: {Color.GREEN}{', '.join(func.__name__ for func in funcs)}{Color.RESET}")

    print(f"{Color.GREEN}{'=' * cols}{Color.RESET}")