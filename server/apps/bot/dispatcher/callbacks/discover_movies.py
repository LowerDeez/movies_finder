from typing import TYPE_CHECKING

from django.utils.translation import ugettext_lazy as _

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ParseMode

from apps.bot.dispatcher.consts import (
    END,
    ACTION_CHOICES,
    BACK_BUTTON,
    STATE_CHOICES,
    CONSTS,
    YEARS_CHOICES
)
from apps.bot.dispatcher.services import (
    set_search_params,
    get_discovering_movies_callback_text,
    display_search_params,
    build_search_params,
    render_movies,
    get_last_movie_keyboard
)
from apps.bot.tmdb import get_cached_movies_genres, TMDBWrapper

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext

__all__ = (
    'back_or_clear_show_data_callback',
    'discovering_movies_callback',
    'select_genre_callback',
    'select_years_callback',
    'show_data_callback',
    'discover_movies_callback'
)


def discovering_movies_callback(update: 'Update', context: 'CallbackContext') -> str:
    """Choose to add a parent or a child."""
    print('Discovering movies:')
    current_search_param = set_search_params(
        update=update,
        context=context,
    )
    text = get_discovering_movies_callback_text(
        update=update,
        context=context
    )

    buttons = [
        [
            InlineKeyboardButton(
                text=str(_('Genres')),
                callback_data=ACTION_CHOICES.select_genre
            )
        ],
        [
            InlineKeyboardButton(
                text=str(_('Years range')),
                callback_data=ACTION_CHOICES.select_years
            )
        ],
        [
            InlineKeyboardButton(
                text=str(_('Show data')),
                callback_data=ACTION_CHOICES.show_search_params
            )
        ],
        [
            InlineKeyboardButton(
                text=str(_('Discover')),
                callback_data=ACTION_CHOICES.discover
            )
        ],
        BACK_BUTTON
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    print('Callback:', update.callback_query.data)
    if update.callback_query.data == str(END):
        if (
                current_search_param
                in [CONSTS.genres, CONSTS.years]
        ):
            update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard
            )
        else:
            update.callback_query.message.reply_text(
                text=text,
                reply_markup=keyboard
            )
            update.callback_query.edit_message_reply_markup()
    else:
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )

    return STATE_CHOICES.discovering_movies


# Second level conversation callbacks
def select_genre_callback(update: 'Update', context: 'CallbackContext'):
    print('Select genre:')
    text = str(_('Okay, these are genres:'))
    buttons = []

    genres = (
        get_cached_movies_genres(
            language=context.user_data.get('language')
        )
    )

    for genre_id, genre_name in genres.items():
        button = InlineKeyboardButton(
            text=genre_name,
            # * callback data to handle by description_conversation handler entry point
            callback_data=genre_id
        )
        buttons.append([button])

    buttons.append(BACK_BUTTON)
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard
    )
    context.user_data[CONSTS.current_search_param] = CONSTS.genres

    return STATE_CHOICES.selecting_search_param


def select_years_callback(update: 'Update', context: 'CallbackContext'):
    print('Select years:')
    text = str(_('Okay, these are years:'))
    buttons = []

    for year, title in YEARS_CHOICES:
        button = InlineKeyboardButton(
            text=title,
            # * callback data to handle by description_conversation handler entry point
            callback_data=year
        )
        buttons.append([button])

    buttons.append(BACK_BUTTON)
    keyboard = InlineKeyboardMarkup(buttons)

    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text, reply_markup=keyboard)
    context.user_data[CONSTS.current_search_param] = CONSTS.years

    return STATE_CHOICES.selecting_search_param


def show_data_callback(update: 'Update', context: 'CallbackContext') -> str:
    """Pretty print gathered data."""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=str(_('Discover')),
                    callback_data=ACTION_CHOICES.discover
                )
            ],
            [
                InlineKeyboardButton(
                    text=str(_('Clear')),
                    callback_data=ACTION_CHOICES.clear_search_params
                )
            ],
            [
                InlineKeyboardButton(
                    text=str(_('Back')),
                    callback_data=ACTION_CHOICES.back_from_show_search_params
                )
            ],
        ]
    )

    update.callback_query.answer()
    update.callback_query.edit_message_text(
        text=display_search_params(
            update=update,
            context=context
        ),
        reply_markup=keyboard,
        parse_mode=ParseMode.HTML
    )

    return STATE_CHOICES.showing_search_params


def back_or_clear_show_data_callback(update: 'Update', context: 'CallbackContext'):
    """
    Returns to discovering movies menu from nested options like "Show data"
    """
    print('Back or clear from show data...')
    print(update.callback_query.data)
    if update.callback_query.data == ACTION_CHOICES.clear_search_params:
        context.user_data.clear()

    return discovering_movies_callback(update, context)


def discover_movies_callback(update: 'Update', context: 'CallbackContext'):
    print('Discover movies...')
    update.callback_query.answer()
    movies = (
        TMDBWrapper(
            language=context.user_data.get('language')
        )
        .discover_movies(
            params=build_search_params(
                update=update,
                context=context,
            )
        )
    )
    # + INFO
    # When replying to a text message (from a MessageHandler) is fine
    # to use update.message.reply_text, but in your case the incoming message
    # is a managed by the CallbackHandler which receives a different object.
    render_movies(
        context=context,
        movies=movies,
        message=update.callback_query.message,
        reply_markup=get_last_movie_keyboard(movies=movies)
    )
