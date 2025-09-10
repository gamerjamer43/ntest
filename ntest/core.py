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
    # parse args using my function
    args: Namespace = parse_args()

    # further parse into easily accessible vars
    path: str = args.path
    starting: str = args.start
    ending: str = args.end
    verbose: bool = args.verbose
    ff: bool = args.fail_fast

    # get terminal width
    COLS: int = (get_terminal_size(fallback=(80, 24)).columns - 1) // 2
    seperator: str = '=' * (COLS - 16) if verbose else '=' * (COLS - 15)

    # scan directory for tests
    files: dict[str, list] = scandir(path, start=starting, end=ending)

    # print header info (gone add more as plugin manager and shit work in)
    print(f"{Color.GREEN}{'=' * (COLS - 6)} TESTS START {'=' * (COLS - 6)}{Color.RESET}")
    print(f"Platform: {Color.GREEN}{system()} {machine()}{Color.RESET}, Device Name: {Color.GREEN}{node()}{Color.RESET}")
    print(f"Using: {Color.GREEN}Python {python_version()} [{python_compiler()}]{Color.RESET}")
    print(f"Package Version: {Color.GREEN}ntest v{__version__}{Color.RESET}")

    # CLOCK IT
    start: float = time()

    # run test and unpack info (static typing is my friend i'm super redundant)
    testinfo: tuple[list, list, int] = runtest(files, ff, verbose)
    passed: list = testinfo[0]
    failed: list = testinfo[1]
    count: int = testinfo[2]

    # print those summaries
    print(f"\n{Color.GREEN}{len(passed)} passed{Color.RESET}, {Color.RED}{len(failed)} failed{Color.RESET}, {count} total")
    
    # mark and format finish time
    finish: str = f"{time() - start:.03f}" if verbose else f"{time() - start:.02f}"

    # failure info
    if failed:
        print(f"\n{Color.RED}Failures:{Color.RESET}")
        for index, result in enumerate(failed):
            # print the name of the function that failed, and the error line by line
            print(f"{Color.RED}{index + 1}. {result['name']} in {result['file']}:{Color.RESET}")

            # print based on if verbose is on
            if verbose:
                print("\n".join(result["error"].splitlines()))

            else:
                print(result["error"].strip().splitlines()[-1])

            print() # blank line between failures

        # print summary of failures
        print(f"{Color.RED}{seperator} {len(failed)} test{'s' if len(failed) > 1 else ''} failed (took {finish}s) {seperator}{Color.RESET}")
    
    # and if there isn't any
    else:
        print(f"{Color.GREEN}{seperator} {len(passed)} tests passed (took {finish}s) {seperator}{Color.RESET}")