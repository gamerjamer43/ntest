# time and traceback for tests
from time import time
from traceback import format_exc

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color


def runtest(files: dict[str, list], ff: bool) -> tuple[list, list, int]:
    # open empty pass and fail lists
    passes: list[dict] = []
    fails: list[dict] = []

    # run each test and record outcome
    for path, funcs in files.items():
        print(f"\n{Color.BLUE}{path}{Color.RESET}")
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
            result: dict = {
                "name": func.__name__,
                "file": path,
                "passed": passed,
                "duration": duration,
                "error": error
            }

            if passed: passes.append(result)
            elif not passed: fails.append(result)
            else: raise ValueError("how did we get here.")

            if passed == False and ff:
                # if fast fail, we just stop right here. summarize in place
                print(f"{Color.RED}✗ {func.__name__}{Color.RESET} ({duration:.5f}s)")
                print(f"{Color.RED}Fail‐fast enabled, stopping tests.{Color.RESET}")
                return passes, fails, len(passes) + len(fails)

            # pass/fail symbol cuz cool, also colorize (circa me) and print results
            color: Color = Color.GREEN if passed else Color.RED
            print(f"{color}{"✓" if passed else "✗"} {func.__name__}{Color.RESET} ({duration:.2f}s)")

    # summarize
    return passes, fails, len(passes) + len(fails)