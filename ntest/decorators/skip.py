from types import FunctionType

def skip(reason: str) -> FunctionType:
    """Decorator to skip a test method. 
    Hey idiot, this is why your test isn't running.
    
    Args:
        reason (str): The reason for skipping the test.
    """

    def decorator(fn: FunctionType) -> FunctionType:
        fn.__skip__ = f"skipping {fn.__name__}, reason: {reason}" # type: ignore
        return fn
    
    return decorator