from importlib.util import module_from_spec, spec_from_file_location
from os import listdir
from os.path import isfile, splitext
from sys import platform
from inspect import getmembers, isfunction

# colorize func unused but i might, it's in printc tho
from .colorize import Color, colorize, printc


def main() -> None:
    for f in listdir('.'):
        # print file, if its in dir... adding subdirectory checks soon but i can't rn it's 2 am
        print(f, isfile(f))

        # this is where subdirectory checks are gonna go
        if not isfile(f):
            continue

        # if it is a file lets a go!
        name, ext = splitext(f)
        if ext == ".py" and name.endswith("_test"):
            print("found a test!")

            # load and exec test module
            module_name = name
            spec = spec_from_file_location(module_name, f)
            module = module_from_spec(spec)
            spec.loader.exec_module(module)

            # gather all functions
            functions = [
                func for _, func in getmembers(module, isfunction)
                if func.__module__ == module_name
            ]

            # print dem jawns out. this all i can do frn i need sleep
            print(f"Functions: {", ".join(func.__name__ for func in functions)}")
    
    printc("\nPlatform:", Color.GREEN, platform, Color.RESET)