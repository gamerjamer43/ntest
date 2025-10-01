from types import FunctionType

def patch(data: str | list, reason: str) -> FunctionType:
    """Mark a test to have input patched to it (if it's got an input function)
    
    Args:
        data (str | list): Data to be patched to input.
        reason (str): Reason for patching the data.
    """

    def decorator(fn: FunctionType) -> FunctionType:
        fn.__patch__ = (data, f"patching data to {fn.__name__} {data}, reason: {reason}") # type: ignore
        return fn
    
    return decorator