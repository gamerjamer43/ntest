# time and traceback for tests
from time import time
from traceback import format_exc

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color


def runtest(files: dict[str, list], ff: bool) -> tuple[list, list, int]:
    # open an empty results (to store pass fail, results are dict)
    results: list[dict] = []

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
            results.append({
                "name": func.__name__,
                "file": path,
                "passed": passed,
                "duration": duration,
                "error": error
            })

            if passed == False and ff:
                # if fast fail, we just stop right here. summarize in place
                passes: list = [r for r in results if r["passed"]]
                fails: list = [r for r in results if not r["passed"]]

                # print the warning and return
                print(f"{Color.RED}✗ {func.__name__}{Color.RESET} ({duration:.5f}s)")
                print(f"{Color.RED}Fail‐fast enabled, stopping tests.{Color.RESET}")
                return passes, fails, len(results)

            # pass/fail symbol cuz cool, also colorize (circa me) and print results
            color: Color = Color.GREEN if passed else Color.RED
            print(f"{color}{"✓" if passed else "✗"} {func.__name__}{Color.RESET} ({duration:.2f}s)")

    # summarize
    passes: list = [r for r in results if r["passed"]]
    fails: list = [r for r in results if not r["passed"]]

    return passes, fails, len(results)