from functools import wraps

__all__ = (
    'modify_result',
    'lookahead'
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


def lookahead(iterable):
    """Pass through all values from the given iterable, augmented by the
    information if there are more values to come after the current one
    (True), or if it is the last value (False).
    """
    # Get an iterator and pull the first value.
    it = iter(iterable)
    last = next(it)

    # Run the iterator to exhaustion (starting from the second value).
    for val in it:
        # Report the *previous* value (more to come).
        yield last, False
        last = val

    # Report the last value.
    yield last, True
