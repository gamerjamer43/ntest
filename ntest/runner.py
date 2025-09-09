# time and traceback for tests
from time import time
from traceback import format_exc

# my color library (if u can even call it that its rly just a class tbh, i made so cool functions tho)
from .colorize import Color


def runtest(files: dict[str, list]) -> None:
    # open an empty results (to store pass fail, results are dict)
    results: list[dict] = []

    # run each test and record outcome
    for file_path, funcs in files.items():
        print(f"\n{Color.BLUE}{file_path}{Color.RESET}")
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
                "file": file_path,
                "passed": passed,
                "duration": duration,
                "error": error
            })

            # pass/fail symbol cuz cool, also colorize (circa me) and print results
            symbol: str = "✓" if passed else "✗"
            color: Color = Color.GREEN if passed else Color.RED
            print(f"{color}{symbol} {func.__name__}{Color.RESET} ({duration:.2f}s)")

    # summarize
    passed: list = [r for r in results if r["passed"]]
    failed: list = [r for r in results if not r["passed"]]

    return passed, failed, len(results)