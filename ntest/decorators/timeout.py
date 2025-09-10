from types import FunctionType

def timeout(seconds: float, reason: str) -> FunctionType:
    """Decorator to fail a test if it takes longer than the given number of seconds.
    
    Args:
        seconds (int): The maximum number of seconds a test can take before failing.
    """
    def decorator(fn):
        fn.__timeout__ = (seconds, f"failing function {fn.__name__} if test is longer than {seconds} seconds, reason: {reason}")
        return fn
    
    return decorator