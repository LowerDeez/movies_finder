from typing import TYPE_CHECKING

from django.conf import settings
from django.utils.translation import activate

if TYPE_CHECKING:
    from ..entities import User

__all__ = (
    'lookahead',
    'activate_user_language'
)


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


def activate_user_language(*, user: 'User'):
    language_codes = list(dict(settings.LANGUAGES).keys())
    print(language_codes)
    if user.language_code:
        if user.language_code in language_codes:
            activate(user.language_code)
