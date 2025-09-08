from sys import stdout

class Color:
    """Basic color/style class used to store all these colors."""
    # reset
    RESET = "\033[0m"

    # styles
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"

    # fg colors
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"

    # bright fg colors
    BRIGHT_BLACK = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    # bg colors
    BG_BLACK = "\033[40m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_WHITE = "\033[47m"


def colorize(text: str, *styles) -> str:
    """
    Apply ANSI styles to the given text
    Example:
        colorize("Hello", Color.RED, Color.BOLD)
    """
    sequence: str = "".join(styles)
    return f"{sequence}{text}{Color.RESET}"


def printc(*args, end="\n", file=stdout):
    """
    Print colored text with mixed strings and styles.
    Strings are colored with the current accumulated styles.
    Example:
        printc("hi", Color.GREEN, " world", Color.RESET)
    """
    text: str = ""
    styles: list = []

    for arg in args:
        if isinstance(arg, str):
            text += colorize(arg, *styles)

        else:
            # assume a style
            styles.append(arg)

    print(text, end=end, file=file)


# and top level aliases duhhhh
red = lambda text: colorize(text, Color.RED)
green = lambda text: colorize(text, Color.GREEN)
blue = lambda text: colorize(text, Color.BLUE)
bold = lambda text: colorize(text, Color.BOLD)
underline = lambda text: colorize(text, Color.UNDERLINE)