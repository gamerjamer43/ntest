from argparse import Namespace, ArgumentParser

# open the parser
parser = ArgumentParser(
    prog="ntest",
    description="A minimal Python unit testing framework designed to run just as good as any enterprise tests. It's both lightweight and fast for small tests, and super expansible for when you need it most."
)

def parse_args() -> Namespace:
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

    return parser.parse_args()