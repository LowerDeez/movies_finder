from functools import wraps

__all__ = (
    'modify_result',
)


def modify_result(func):
    """
    Easily add caching to a function
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):

            result = fn(*args, **kwargs)

            return func(result)
        return wrapper
    return decorator
