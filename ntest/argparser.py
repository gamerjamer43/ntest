from argparse import Namespace, ArgumentParser

# open the parser
parser = ArgumentParser(
    prog="ntest",
    description="A minimal Python test runner"
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
        "-p", "--pattern",
        default="*_test.py",
        help="Glob pattern to match test files"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show per‐test output even if passing"
    )
    
    parser.add_argument(
        "--fail-fast",
        action="store_true",
        help="Stop on first test failure"
    )

    return parser.parse_args()