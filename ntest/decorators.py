from types import FunctionType

def skip(reason: str):
    """Decorator to skip a test method. 
    Hey idiot, this is why your test isn't running.
    
    Args:
        reason (str): The reason for skipping the test.
    """

    def decorator(fn: FunctionType) -> FunctionType:
        print(f"skipping function {fn.__name__} because: {reason}")
        fn.__skip__ = reason
        return fn
    
    return decorator