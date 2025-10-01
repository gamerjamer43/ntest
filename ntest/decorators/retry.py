from types import FunctionType

def retry(attempts: int, reason: str) -> FunctionType:
    """Mark a test to be retried if it fails, but only a given number of times.
    
    Args:
        attempts (int): The maximum number attempts a test can retry before failing for good.
    """

    def decorator(fn: FunctionType) -> FunctionType:
        fn.__retry__ = (attempts, f"retrying function {fn.__name__} {attempts} times (if it fails) because: {reason}") # type: ignore
        return fn
    
    return decorator