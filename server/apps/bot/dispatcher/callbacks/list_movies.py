from typing import TYPE_CHECKING

from apps.bot.dispatcher.consts import (
    CONSTS,
    ACTION_CHOICES,
    STATE_CHOICES
)
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
    'list_movies_callback',
)


def list_movies_callback(update: 'Update', context: 'CallbackContext'):
    print('List movies...')
    update.callback_query.answer()
    page = get_current_page()
    list_method = context.user_data.get(CONSTS.list_method)
    callback_data = update.callback_query.data

    if callback_data == ACTION_CHOICES.next_movies:
        page += 1
    else:
        # new list method
        if list_method != callback_data:
            page = 1

        list_method = callback_data

    print('List method:', list_method)
    context.user_data[CONSTS.list_method] = list_method

    tmdb = TMDBWrapper(language=context.user_data.get('language'))
    method = getattr(tmdb, list_method)

    movies = method(page=page)

    render_movies(
        context=context,
        movies=movies,
        message=update.callback_query.message,
        reply_markup=get_last_movie_keyboard(movies=movies)
    )

    return STATE_CHOICES.listing_movies
