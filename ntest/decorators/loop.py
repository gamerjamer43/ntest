from types import FunctionType

def loop(times: int, reason: str) -> FunctionType:
    """Mark a test to be repeated a given number of times. Good for stress or unit testing.
    
    Args:
        reason (str): The reason for skipping the test.
        times (int): The number of times to repeat the test.
    """
    def decorator(fn: FunctionType) -> FunctionType:
        fn.__loop__ = (times, f"looping function {fn.__name__} {times} times, reason: {reason}")
        return fn
    
    return decorator