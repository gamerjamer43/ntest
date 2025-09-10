from sys import stdout
from typing import ClassVar

class Color:
    """Basic color/style class used to store all these colors."""
    # reset
    RESET: ClassVar[str]          = "\033[0m"

    # styles
    BOLD: ClassVar[str]           = "\033[1m"
    UNDERLINE: ClassVar[str]      = "\033[4m"

    # fg colors
    BLACK: ClassVar[str]          = "\033[30m"
    RED: ClassVar[str]            = "\033[31m"
    GREEN: ClassVar[str]          = "\033[32m"
    YELLOW: ClassVar[str]         = "\033[33m"
    BLUE: ClassVar[str]           = "\033[34m"
    MAGENTA: ClassVar[str]        = "\033[35m"
    CYAN: ClassVar[str]           = "\033[36m"
    WHITE: ClassVar[str]          = "\033[37m"

    # bright fg colors
    BRIGHT_BLACK: ClassVar[str]   = "\033[90m"
    BRIGHT_RED: ClassVar[str]     = "\033[91m"
    BRIGHT_GREEN: ClassVar[str]   = "\033[92m"
    BRIGHT_YELLOW: ClassVar[str]  = "\033[93m"
    BRIGHT_BLUE: ClassVar[str]    = "\033[94m"
    BRIGHT_MAGENTA: ClassVar[str] = "\033[95m"
    BRIGHT_CYAN: ClassVar[str]    = "\033[96m"
    BRIGHT_WHITE: ClassVar[str]   = "\033[97m"

    # bg colors
    BG_BLACK: ClassVar[str]       = "\033[40m"
    BG_RED: ClassVar[str]         = "\033[41m"
    BG_GREEN: ClassVar[str]       = "\033[42m"
    BG_YELLOW: ClassVar[str]      = "\033[43m"
    BG_BLUE: ClassVar[str]        = "\033[44m"
    BG_MAGENTA: ClassVar[str]     = "\033[45m"
    BG_CYAN: ClassVar[str]        = "\033[46m"
    BG_WHITE: ClassVar[str]       = "\033[47m"


def colorize(text: str, *styles) -> str:
    """
    Wrap the provided string in the provided styles.
    Example:
        colorize("Hello", Color.RED, Color.BOLD)
    """
    sequence: str = "".join(styles)
    return f"{sequence}{text}{Color.RESET}"

def _parse_colors(args: list[Color | str], sep: str = " ") -> str:
    """
    Function to parse color and text arguments into a single, colorized string.
    """
    # output string
    out: str = ""

    for arg in args:
        # convert to string first
        arg = str(arg)

        # if it's an ansi code just add it
        if arg.startswith("\033["):
            out += arg

        # otherwise treat like a string
        else:
            # check for seperator
            if out and not (out.endswith(sep) or arg.startswith(sep)):
                out += sep

            # add to arg
            out += arg

    return out


def printc(*args, end: str = "\n", file=stdout, sep: str = " "):
    """
    Print colored text with mixed values and styles. Styles applied in order.
    Example:
        printc("This is ", Color.RED, "red", Color.RESET, " and this is ", Color.BOLD, "bold", Color.RESET, ".")
    """
    # use color parser, add reset and end
    out: str = _parse_colors(list(args), sep)
    out += Color.RESET + end

    # print to stdout (or whatever file u specify)
    file.write(out)


def inputc(*args, sep: str = " ", end: str = "", file=stdout) -> str:
    """
    Prompt colored text with mixed values and styles. Styles applied in order.
    Example:
        name = inputc("Enter ", Color.GREEN, "value", ": ")
    """
    # use color parser, add reset and end
    prompt = _parse_colors(list(args), sep)
    prompt += Color.RESET + end
    
    # print to stdout (or whatever file u specify), flush and get input
    file.write(prompt)
    file.flush()
    return input("")

# and some easy to access top level aliases duhhhh, colors:
black = lambda text: colorize(text, Color.BLACK)
red = lambda text: colorize(text, Color.RED)
green = lambda text: colorize(text, Color.GREEN)
yellow = lambda text: colorize(text, Color.YELLOW)
blue = lambda text: colorize(text, Color.BLUE)
magenta = lambda text: colorize(text, Color.MAGENTA)
cyan = lambda text: colorize(text, Color.CYAN)
white = lambda text: colorize(text, Color.WHITE)

# styles
bold = lambda text: colorize(text, Color.BOLD)
underline = lambda text: colorize(text, Color.UNDERLINE)