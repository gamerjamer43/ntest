from types import FunctionType

def retry(attempts: int, reason: str) -> FunctionType:
    """Decorator to retry a test function/method if it fails., but only a given number of times.
    
    Args:
        attempts (int): The maximum number attempts a test can retry before failing for good.
    """
    def decorator(fn):
        fn.__retry__ = (attempts, f"retrying function {fn.__name__} {attempts} times (if it fails) because: {reason}")
        return fn
    
    return decorator