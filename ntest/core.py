# my scanner and runner functions
from .scanner import scandir
from .runner import runtest
from .argparser import parse_args

# colorize (also made by meeeee)
from .colorize import Color

# system/version info
from platform import machine, node, python_compiler, python_version, system
from shutil import get_terminal_size
from ntest import __version__ # type: ignore

# necessary types for checking
from argparse import Namespace
from .classes.TestResult import TestResult

# time for timing tests i wonder...
from time import time

def run() -> None:
    # parse args using my function
    args: Namespace = parse_args()

    # further parse into easily accessible vars
    path: str = args.path
    starting: str = args.start
    ending: str = args.end
    verbose: bool = args.verbose
    ff: bool = args.fail_fast
    output: bool = args.output

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
    testinfo: tuple[list, list, int] = runtest(files, ff, verbose, output)
    passed: list = testinfo[0]
    failed: list = testinfo[1]
    count: int = testinfo[2]

    # print those summaries
    print(f"\n{Color.GREEN}{len(passed)} passed{Color.RESET}, {Color.RED}{len(failed)} failed{Color.RESET}, {count} total")
    
    # clock precision in a CLEAN MANNER
    precision: int = 3 if verbose else 2
    finish: str = f"{time() - start:.{precision}f}"

    if failed:
        print(f"\n{Color.RED}Failures:{Color.RESET}")

        # loop through failures
        result: TestResult
        for index, result in enumerate(failed):
            # print the name of the function that failed, and the error line by line (more content if -v)
            print(f"{Color.RED}{index + 1}. {result.name} in {result.file}:{Color.RESET}")

            if verbose and result.error:
                print("\n".join(result.error.splitlines()), end="\n")

            elif result.error:
                print(result.error.strip().splitlines()[-1], end="\n")

            else:
                print(f"{Color.YELLOW}No error message provided.{Color.RESET}")

        # print summary of failures
        print(f"{Color.RED}{seperator} {len(failed)} test{'s' if len(failed) > 1 else ''} failed (took {finish}s) {seperator}{Color.RESET}")
    
    # and if there isn't any
    else:
        print(f"{Color.GREEN}{seperator} {len(passed)} tests passed (took {finish}s) {seperator}{Color.RESET}")