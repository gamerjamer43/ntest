# what lets you actually run the functions
from importlib.util import module_from_spec, spec_from_file_location
from inspect import getmembers, isfunction

# path and os info related things. scanning dirs, system info, etc
from os import PathLike, listdir
from os.path import isdir, isfile, join, splitext
from platform import machine, node, python_compiler, python_version, system
from shutil import get_terminal_size

# time for timing tests i wonder...
from time import time

# traceback for error logging
from traceback import format_exc

# version info
from ntest import __version__

# colorize func unused but i might, it's in printc tho
from .colorize import Color


def _scandir(path: str | PathLike[str]) -> dict[str, list]:
    # root directory to scan
    root: str | PathLike[str] = path or '.'

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
    cols: int = get_terminal_size(fallback=(80, 24)).columns - 1

    # scan directory for tests
    files: dict[str, list] = _scandir('.')

    # print header info (gone add more as plugin manager and shit work in)
    print(f"{Color.GREEN}{'=' * (cols // 2 - 6)} TESTS START {'=' * (cols // 2 - 6)}{Color.RESET}")
    print(f"Platform: {Color.GREEN}{system()} {machine()}{Color.RESET}, Device Name: {Color.GREEN}{node()}{Color.RESET}")
    print(f"Using: {Color.GREEN}Python {python_version()} [{python_compiler()}]{Color.RESET}")
    print(f"Package Version: {Color.GREEN}ntest v{__version__}{Color.RESET}\n")

    # go thru files and print functions (we're gonna call them for the tests)
    for file, funcs in files.items():
        print(f"Found file: {Color.GREEN}{file}{Color.RESET}, tests inside: {Color.GREEN}{', '.join(func.__name__ for func in funcs)}{Color.RESET}")

    # open an empty results (to store pass fail, results are dict)
    results: list[dict] = []

    # time run entirely
    full: float = time()

    # run each test and record outcome
    for file_path, funcs in files.items():
        print(f"\n{Color.BLUE}{file_path}{Color.RESET}")
        for func in funcs:
            # time it and initialize an error value and a pass bool
            start: float = time()
            error: str | None = None
            passed: bool

            # try calling, log pass/fail and if it does fail raise error thru traceback
            try:
                func()
                passed = True

            except Exception:
                passed = False
                error = format_exc()
            
            # time it and log result
            duration: float = time() - start
            results.append({
                "name": func.__name__,
                "file": file_path,
                "passed": passed,
                "duration": duration,
                "error": error
            })

            # pass/fail symbol cuz cool, also colorize (circa me) and print results
            symbol: str = "✓" if passed else "✗"
            color: Color = Color.GREEN if passed else Color.RED
            print(f"{color}{symbol} {func.__name__}{Color.RESET} ({duration:.2f}s)")

    # summarize
    passed: list = [r for r in results if r["passed"]]
    failed: list = [r for r in results if not r["passed"]]

    # print those summaries
    print(f"\n{Color.GREEN}{len(passed)} passed{Color.RESET}, "
          f"{Color.RED}{len(failed)} failed{Color.RESET}, "
          f"{len(results)} total")

    # failure info
    if failed:
        for index, result in enumerate(failed):
            # print the name of the function that failed, and the error line by line
            print(f"\n{Color.RED}{result['name']} in {result['file']}:{Color.RESET}")
            print("\n".join(result["error"].splitlines()))
            
        print(f"\n{Color.RED}{'=' * (cols // 2 - 15)} {len(failed)} test{'s' if len(failed) > 1 else ''} failed (took {time() - full:.02f}s) {'=' * (cols // 2 - 15)}{Color.RESET}")
    
    # and if there isn't any
    else:
        print(f"\n{Color.GREEN}{'=' * (cols // 2 - 12)} {len(passed)} tests passed (took {time() - full:.02f}s) {'=' * (cols // 2 - 12)}{Color.RESET}")