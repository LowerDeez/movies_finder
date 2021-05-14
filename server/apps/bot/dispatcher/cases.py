from typing import TYPE_CHECKING

from ..services.user import parse_user, save_user, activate_user_language

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext

    from ..entities import User

__all__ = (
    'save_user_and_activate_user_language',
)


def save_user_and_activate_user_language(
        *,
        update: 'Update',
        context: 'CallbackContext'
) -> 'User':
    user = parse_user(
        update=update,
        context=context
    )
    save_user(user_entity=user)
    activate_user_language(user=user)

    return user
