from itertools import chain
from os import environ
from typing import List, TYPE_CHECKING, Dict

from django.template.loader import render_to_string
from django.utils.datastructures import MultiValueDict
from django.utils.translation import ugettext_lazy as _

from telegram import ParseMode, InlineKeyboardButton, InlineKeyboardMarkup

from .consts import ACTION_CHOICES, BACK_BUTTON, CONSTS, END
from ..utils import lookahead
from ..tmdb import get_cached_movies_genres

if TYPE_CHECKING:
    from telegram import Message, Update
    from telegram.ext import CallbackContext
    from tmdbv3api import Movie

__all__ = (
    'get_movie_backdrop_url',
    'get_movie_poster_url',
    'get_movie_url',
    'get_movies_genres',
    'render_movie_html',
    'render_movies',
    'get_last_movie_keyboard',
    'set_search_params',
    'build_search_params',
    'display_search_params',
    'get_discovering_movies_callback_text',
    'get_current_page',
    'movies_search_has_more_pages'
)


def get_movie_backdrop_url(
        *,
        movie: 'Movie',
        width: int = 600,
        height: int = 900
) -> str:
    return (
        f'https://www.themoviedb.org/t/p/'
        f'w{width}_and_h{height}_bestv2'
        f'{movie.backdrop_path}'
    )


def get_movie_poster_url(
        *,
        movie: 'Movie',
        width: int = 92,
) -> str:
    return (
        f'https://www.themoviedb.org/t/p/'
        f'w{width}'
        f'{movie.poster_path}'
    )


def get_movie_url(*, movie: 'Movie') -> str:
    return (
        f'https://www.themoviedb.org/movie/'
        f'{movie.id}'
    )


def get_movies_genres(
        *,
        movie: 'Movie',
        context: 'CallbackContext',
        genres_map: Dict = None,
        limit: int = None
) -> str:
    if genres_map is None:
        genres_map = (
            get_cached_movies_genres(
                language=context.user_data.get('language')
            )
        )

    genres = [
        genres_map[genre_id]
        for genre_id in movie.genre_ids
    ]

    if limit:
        genres = genres[:limit]

    return ', '.join(genres)


def render_movie_html(
        *,
        movie: 'Movie',
        context: 'CallbackContext',
        genres_map: Dict = None,
        with_image: bool = False
) -> str:
    context = {
        'link': get_movie_url(movie=movie),
        'title': movie.title,
        'rating': movie.vote_average,
        'description': movie.overview[:500],
        'release_date': movie.release_date,
        'vote_count': movie.vote_count,
        'genres': get_movies_genres(
            movie=movie,
            context=context,
            genres_map=genres_map
        )
    }

    if with_image:
        context['image'] = get_movie_backdrop_url(movie=movie)

    text = render_to_string(
        'movies/card.html',
        context=context
    )

    return text


def render_movies(
        *,
        context: 'CallbackContext',
        movies: List['Movie'],
        message: 'Message',
        reply_markup: 'InlineKeyboardMarkup' = None
):
    genres_map = (
        get_cached_movies_genres(
            language=context.user_data.get('language')
        )
    )

    if not movies:
        message.edit_text(
            text='That\'s all',
            reply_markup=reply_markup
        )
    else:
        for movie, is_last in lookahead(movies):
            image = get_movie_backdrop_url(movie=movie)
            print('Image:', image)
            message.bot.send_photo(
                message.chat.id,
                photo=image,
                parse_mode=ParseMode.HTML
            )

            text = render_movie_html(
                movie=movie,
                context=context,
                genres_map=genres_map
            )

            message.reply_text(
                text=text,
                parse_mode=ParseMode.HTML,
                reply_markup=reply_markup if is_last else None
            )


def get_last_movie_keyboard(*, movies: List['Movie']):
    buttons = [
        BACK_BUTTON
    ]

    if movies and movies_search_has_more_pages():
        buttons.insert(0, [
            InlineKeyboardButton(
                text=str(_('Next movies')),
                callback_data=ACTION_CHOICES.next_movies
            )
        ])

    keyboard = InlineKeyboardMarkup(buttons)
    return keyboard


def set_search_params(
        *,
        update: 'Update',
        context: 'CallbackContext'
) -> str:
    user_data = context.user_data
    callback_data = update.callback_query.data
    search_params: 'MultiValueDict' = (
        user_data.setdefault(
            CONSTS.search_params,
            MultiValueDict()
        )
    )
    current_search_param = (
        user_data.pop(
            CONSTS.current_search_param,
            None
        )
    )

    print('User data:', user_data)
    print('Current search param:', current_search_param)
    print('Callback data:', callback_data)

    if current_search_param in [CONSTS.genres, CONSTS.years] and callback_data != str(END):
        if callback_data not in search_params.values():
            search_params.appendlist(current_search_param, callback_data)

    print('New user data:', user_data)
    return current_search_param


def build_search_params(
        *,
        update: 'Update',
        context: 'CallbackContext',
) -> Dict:
    user_data = context.user_data
    page = get_current_page()
    search_params: 'MultiValueDict' = user_data[CONSTS.search_params]
    callback_data = update.callback_query.data
    print('Callback data:', callback_data)

    params = {
        'language': 'ru',
        'sort_by': 'popularity.desc',
        'include_adult': True,
        'vote_average.gte': 6,
        'vote_count.gte': 200,
        'page': page
    }

    if callback_data == ACTION_CHOICES.next_movies:
        params['page'] += 1

    genres: List = search_params.getlist(CONSTS.genres)
    years: List = search_params.getlist(CONSTS.years)

    if genres:
        params['with_genres'] = ','.join(genres)

    if years:
        years_range = list(chain.from_iterable([
            year.split('-')
            for year in years
        ]))
        years_range = [int(year) for year in years_range]
        params['primary_release_date.gte'] = f'{min(years_range)}-01-01'
        params['primary_release_date.lte'] = f'{max(years_range)}-12-31'

    print('Params:', params)
    return params


def display_search_params(
        *,
        update: 'Update',
        context: 'CallbackContext'
) -> str:
    search_params: 'MultiValueDict' = context.user_data[CONSTS.search_params]
    genres = search_params.getlist(CONSTS.genres)
    years = set(search_params.getlist(CONSTS.years))
    genres_map = (
        get_cached_movies_genres(
            language=context.user_data.get('language')
        )
    )
    genres = (
        ', '.join(
            [
                genres_map[int(genre_id)]
                for genre_id in genres
            ]
        )
        if genres else '-'
    )
    years = ', '.join(years) if years else '-'

    return render_to_string(
        'movies/search_params.html',
        context={
            'genres': genres,
            'years': years
        }
    )


def get_discovering_movies_callback_text(
        *,
        update: 'Update',
        context: 'CallbackContext'
) -> str:
    user_data = context.user_data
    current_search_param = user_data.get(CONSTS.current_search_param)

    if current_search_param == CONSTS.genres:
        text = 'Now select years or another genre or try to search:'
    elif current_search_param == CONSTS.years:
        text = 'Now select genre or try to search:'
    else:
        text = 'Select options to discover movies:'

    return text


def get_current_page() -> int:
    current_page = int(environ.get('page', 1))
    return current_page


def movies_search_has_more_pages() -> bool:
    current_page = get_current_page()
    total_pages = int(environ.get('total_pages', 1))
    print('Page:', current_page)
    print('Total pages:', total_pages)

    return current_page < total_pages
