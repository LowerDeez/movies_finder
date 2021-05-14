from dataclasses import asdict, fields

from django.conf import settings
from django.utils.translation import activate
from typing import TYPE_CHECKING

from telegram import Bot, MessageEntity
from telegram.error import Unauthorized

from ..entities import User as UserEntity
from ..models import ChatUser

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext

__all__ = (
    'parse_user',
    'save_user',
    'send_message',
    'activate_user_language'
)


def parse_user(*, update: 'Update', context: 'CallbackContext') -> 'UserEntity':
    if update.message is not None:
        user = update.message.from_user.to_dict()
    elif update.inline_query is not None:
        user = update.inline_query.from_user.to_dict()
    elif update.chosen_inline_result is not None:
        user = update.chosen_inline_result.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.from_user is not None:
        user = update.callback_query.from_user.to_dict()
    elif update.callback_query is not None and update.callback_query.message is not None:
        user = update.callback_query.message.chat.to_dict()
    else:
        raise Exception(f"Can't extract user data from update: {update}")

    user_fields = (field.name for field in fields(UserEntity))

    print('Context args:', context.args)

    return UserEntity(
        **{
            field: user[field] for field in user_fields
        },
    )


def save_user(*, user_entity: 'UserEntity') -> 'ChatUser':
    data = asdict(user_entity)
    user_id = data.pop('id')
    return ChatUser.objects.update_or_create(
        user_id=user_id,
        defaults=data
    )


def send_message(
        *,
        token: str,
        user_id: str,
        text: str,
        parse_mode=None,
        reply_markup=None,
        reply_to_message_id=None,
        disable_web_page_preview=None,
        entities=None,
) -> bool:
    bot = Bot(token)

    try:
        if entities:
            entities = [
                MessageEntity(
                    type=entity['type'],
                    offset=entity['offset'],
                    length=entity['length']
                )
                for entity in entities
            ]

        message = bot.send_message(
            chat_id=user_id,
            text=text,
            parse_mode=parse_mode,
            reply_markup=reply_markup,
            reply_to_message_id=reply_to_message_id,
            disable_web_page_preview=disable_web_page_preview,
            entities=entities,
        )
    except Unauthorized:
        print(f"Can't send message to {user_id}. Reason: Bot was stopped.")
        ChatUser.objects.filter(user_id=user_id).update(is_blocked_bot=True)
        success = False
    except Exception as e:
        print(f"Can't send message to {user_id}. Reason: {e}")
        success = False
    else:
        success = True
        ChatUser.objects.filter(user_id=user_id).update(is_blocked_bot=False)
    return success


def activate_user_language(*, user: 'UserEntity'):
    language_codes = list(dict(settings.LANGUAGES).keys())

    if user.language_code:
        if user.language_code in language_codes:
            activate(user.language_code)
