"""A decorator to mark functions as vibe-coded."""

from functools import wraps


def vibe_coded(func):
    """
    Decorator that adds a notice to the function's docstring indicating it was vibe-coded.
    
    This decorator prepends "**THIS FUNCTION HAS BEEN VIBE CODED**" to the function's
    docstring, which will appear in documentation tools like FastAPI's automatic docs.
    
    Args:
        func: The function to be decorated.
    
    Returns:
        The decorated function with modified docstring.
    
    Example:
        @vibe_coded
        def my_function():
            \"\"\"This is my function.\"\"\"
            pass
        
        # The docstring will become:
        # "**THIS FUNCTION HAS BEEN VIBE CODED**\n\nThis is my function."
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    
    # Modify the docstring
    notice = "**THIS FUNCTION HAS BEEN VIBE CODED**"
    
    if func.__doc__:
        # If docstring exists, prepend the notice
        wrapper.__doc__ = f"{notice}\n\n{func.__doc__}"
    else:
        # If no docstring exists, create one with just the notice
        wrapper.__doc__ = notice
    
    return wrapper


__all__ = ['vibe_coded']

