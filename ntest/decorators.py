from types import FunctionType

def skip(reason: str):
    """Decorator to skip a test method. 
    Hey idiot, this is why your test isn't running.
    
    Args:
        reason (str): The reason for skipping the test.
    """

    def decorator(fn: FunctionType) -> FunctionType:
        print(f"skipping function {fn.__name__} because: {reason}")
        fn.__skip__ = reason # type: ignore
        return fn
    
    return decorator

def loop(times: int, reason: str):
    """Mark a test function to be repeated a given number of times.
    Good for stress or unit testing.
    
    Args:
        reason (str): The reason for skipping the test.
        times (int): The number of times to repeat the test.
    """
    def decorator(fn):
        print(f"looping function {fn.__name__} {times} times because: {reason}")
        fn.__loop__ = times
        return fn
    
    return decorator