from typing import TYPE_CHECKING

from django.utils.translation import ugettext_lazy as _

from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from apps.bot.dispatcher.cases import (
    save_user_and_activate_user_language,
)
from apps.bot.dispatcher.consts import (
    ACTION_CHOICES,
    END,
    CONSTS,
    STATE_CHOICES
)

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext


__all__ = (
    'start',
    'end',
    'stop',
    'stop_nested',
    'back_to_start'
)


def start(update: 'Update', context: 'CallbackContext'):
    print('Start...')
    user = save_user_and_activate_user_language(
        update=update,
        context=context
    )
    context.user_data['language'] = user.language_code
    print('User:', user)
    text = str(_(
        "Lets find a movie for you..."
    ))

    buttons = [
        [
            InlineKeyboardButton(
                text=str(_('Discover movies')),
                callback_data=ACTION_CHOICES.discover_movies
            ),
            InlineKeyboardButton(
                text=str(_('Search movies')),
                callback_data=ACTION_CHOICES.search_movies
            ),
        ],
        [
            InlineKeyboardButton(
                text=str(_('Popular')),
                callback_data=ACTION_CHOICES.popular
            ),
            InlineKeyboardButton(
                text=str(_('Top Rated')),
                callback_data=ACTION_CHOICES.top_rated
            ),
        ],
        [
            InlineKeyboardButton(
                text=str(_('Upcoming')),
                callback_data=ACTION_CHOICES.upcoming
            ),
            InlineKeyboardButton(
                text=str(_('Now playing')),
                callback_data=ACTION_CHOICES.now_playing
            ),
        ],
        [
            InlineKeyboardButton(
                text=str(_('Done')),
                callback_data=str(END)
            ),
        ],
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # case for back from `discovering_movies_callback`
    print('Start message:', update.message)
    if not update.message:
        print('Callback:', update.callback_query.data)
        print('User data:', context.user_data)
        update.callback_query.answer()
        # remove back button
        # update.callback_query.message.delete()
        update.callback_query.edit_message_reply_markup(
            reply_markup=None
        )
        update.callback_query.message.reply_text(
            text=text,
            reply_markup=keyboard
        )
        if context.user_data.pop(CONSTS.search_params, None) is not None:
            update.callback_query.delete_message()
    else:
        update.message.reply_text(
            text=text,
            reply_markup=keyboard
        )

    # * through `selecting_action`
    return STATE_CHOICES.selecting_action


def end(update: 'Update', context: 'CallbackContext') -> int:
    """End conversation from InlineKeyboardButton."""
    print('End...')
    text = str(_('See you around!'))
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    context.user_data.clear()
    return END


def stop(update: 'Update', context: 'CallbackContext') -> int:
    """End Conversation by command."""
    print('Stop...')
    update.message.reply_text(str(_('Okay, bye.')))
    context.user_data.clear()
    return END


def stop_nested(update: 'Update', context: 'CallbackContext') -> str:
    """Completely end conversation from within nested conversation."""
    print('Stop nested...')
    update.message.reply_text(str(_('Okay, bye.')))
    return STATE_CHOICES.stopping


def back_to_start(update: 'Update', context: 'CallbackContext'):
    """
    Returns to start
    """
    print('End second level conversation...')
    start(update, context)
    context.user_data.clear()
    return END