from types import FunctionType

def xfail(reason: str, strict: bool = False) -> FunctionType:
    """Mark a test as expected to fail.

    Args:
        reason (str): Explanation for the expected failure.
        strict (bool): If True, a test that unexpectedly passes should be treated as a failure.
                       If False, an unexpected pass is reported as xpass but does not fail the run.
    """

    def decorator(fn: FunctionType) -> FunctionType:
        fn.__xfail__ = (reason, strict) # type: ignore
        return fn
    
    return decorator