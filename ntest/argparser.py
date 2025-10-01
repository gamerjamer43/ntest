from argparse import FileType, Namespace, ArgumentParser
from sys import stdout

# open the parser
parser = ArgumentParser(
    prog="ntest",
    description="A minimal Python unit testing framework designed to run just as good as any enterprise tests. It's both lightweight and fast for small tests, and super expansible for when you need it most."
)

def parse_args() -> Namespace:
    """Parse command line arguments and return them as a Namespace object.

    Parser Arguments:
        1. path (str, optional): The root directory to scan for tests. Defaults to the current directory.
        2. -s, --start (str, optional): The starting pattern to match test files. Defaults to an empty string.
        3. -e, --end (str, optional): The ending pattern to match test files. Defaults to "_test".
        4. -v, --verbose (bool, optional): If set, enables verbose output with more precise timing and full error logs. Defaults to False.
        5. -ff, --fail-fast (bool, optional): If set, stops execution immediately upon the first test failure. Defaults to False.

    Returns:
        Namespace: Parsed command line arguments.
    """
    # path (not required)
    parser.add_argument(
        "path",
        nargs="?",
        default=".",
        help="Root directory to scan for tests"
    )

    # other optionals
    parser.add_argument(
        "-s", "--start",
        default="",
        help="Start pattern to match test files."
    )

    parser.add_argument(
        "-e", "--end",
        default="_test",
        help="End pattern to match test files."
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show a more precise time (3 digits on time, 6 on tests), and full error logs."
    )
    
    parser.add_argument(
        "-ff", "--fail-fast",
        action="store_true",
        help="Stop immediately on first test failure"
    )

    parser.add_argument(
        "-o", "--output",
        nargs="?",
        const=stdout,
        type=FileType("w"),
        default=None,
        help="Dump results to stdout (no path) or to <path>."
    )

    return parser.parse_args()