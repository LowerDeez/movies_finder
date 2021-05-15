from typing import TYPE_CHECKING

from django.utils.translation import ugettext_lazy as _

from apps.bot.dispatcher.consts import CONSTS, STATE_CHOICES
from apps.bot.dispatcher.services import (
    get_current_page,
    render_movies,
    get_last_movie_keyboard
)
from apps.bot.tmdb import TMDBWrapper

if TYPE_CHECKING:
    from telegram import Update
    from telegram.ext import CallbackContext

__all__ = (
    'search_movies_callback',
    'display_movies_callback'
)


def search_movies_callback(update: 'Update', context: 'CallbackContext'):
    print('Search movies...')
    text = str(_('Okay, please enter some keywords to search:'))
    print(update.callback_query.data)
    search_keyword = context.user_data.pop(CONSTS.search_keyword, None)
    print('Previous search keyword:', search_keyword)
    update.callback_query.answer()

    if search_keyword:
        update.callback_query.message.reply_text(
            text=text
        )
        update.callback_query.edit_message_reply_markup(
            reply_markup=None
        )
    else:
        update.callback_query.edit_message_text(text=text)

    return STATE_CHOICES.searching_movies


def display_movies_callback(update: 'Update', context: 'CallbackContext'):
    print('Display movies...')
    user_data = context.user_data
    search_keyword = user_data.get(CONSTS.search_keyword)
    page = get_current_page()
    message = update.message

    if update.message:
        page = 1
        search_keyword = update.message.text
        user_data[CONSTS.search_keyword] = search_keyword

    # if we have callback query with `next_movies`
    if update.callback_query:
        message = update.callback_query.message
        page += 1

    print('Search keywords:', search_keyword)
    print('Page:', page)
    movies = (
        TMDBWrapper(
            language=context.user_data.get('language')
        )
        .search_movies(
            query=search_keyword,
            page=page
        )
    )
    render_movies(
        context=context,
        movies=movies,
        message=message,
        reply_markup=get_last_movie_keyboard(movies=movies)
    )

    return STATE_CHOICES.displaying_movies
