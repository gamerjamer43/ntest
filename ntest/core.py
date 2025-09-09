# my scanner and runner functions
from .scanner import scandir
from .runner import runtest
from .argparser import parse_args

# colorize (also made by meeeee)
from .colorize import Color

# system/version info
from platform import machine, node, python_compiler, python_version, system
from shutil import get_terminal_size
from ntest import __version__

# namespace type for argparser
from argparse import Namespace

# time for timing tests i wonder...
from time import time

def main() -> None:
    # argparser woohoo (now make it fuckin work)
    args: Namespace = parse_args()
    print(args)

    # unpack args into easy to access shit
    path: str = args.path
    starting: str = args.start
    ending: str = args.end
    verbose: bool = args.verbose # finish adding verbose
    ff: bool = args.fail_fast

    # get terminal width
    COLS: int = (get_terminal_size(fallback=(80, 24)).columns - 1) // 2

    # scan directory for tests
    files: dict[str, list] = scandir(path)

    # print header info (gone add more as plugin manager and shit work in)
    print(f"{Color.GREEN}{'=' * (COLS - 6)} TESTS START {'=' * (COLS - 6)}{Color.RESET}")
    print(f"Platform: {Color.GREEN}{system()} {machine()}{Color.RESET}, Device Name: {Color.GREEN}{node()}{Color.RESET}")
    print(f"Using: {Color.GREEN}Python {python_version()} [{python_compiler()}]{Color.RESET}")
    print(f"Package Version: {Color.GREEN}ntest v{__version__}{Color.RESET}\n")

    # go thru files and print functions (we're gonna call them for the tests)
    for file, funcs in files.items():
        print(f"Found file: {Color.GREEN}{file}{Color.RESET}, tests inside: {Color.GREEN}{', '.join(func.__name__ for func in funcs)}{Color.RESET}")

    # CLOCK IT
    start: float = time()

    # run test and unpack info (static typing is my friend i'm super redundant)
    testinfo: tuple[list, list, int] = runtest(files, ff)
    passed: list = testinfo[0]
    failed: list = testinfo[1]
    count: int = testinfo[2]

    # print those summaries
    print(f"\n{Color.GREEN}{len(passed)} passed{Color.RESET}, "
          f"{Color.RED}{len(failed)} failed{Color.RESET}, "
          f"{count} total")

    # failure info
    if failed:
        print(f"\n{Color.RED}Failures:")
        for index, result in enumerate(failed):
            # print the name of the function that failed, and the error line by line
            print(f"{index + 1}. {result['name']} in {result['file']}:{Color.RESET}")
            print("\n".join(result["error"].splitlines()))
            
        print(f"\n{Color.RED}{'=' * (COLS - 15)} {len(failed)} test{'s' if len(failed) > 1 else ''} failed (took {time() - start:.02f}s) {'=' * (COLS - 15)}{Color.RESET}")
    
    # and if there isn't any
    else:
        print(f"\n{Color.GREEN}{'=' * (COLS - 15)} {len(passed)} tests passed (took {time() - start:.02f}s) {'=' * (COLS - 15)}{Color.RESET}")