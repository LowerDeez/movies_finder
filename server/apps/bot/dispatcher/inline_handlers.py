from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import InlineQueryHandler, CallbackContext

from django.utils.translation import ugettext_lazy as _

from .cases import save_user_and_activate_user_language
from .services import (
    get_movie_url,
    get_movie_poster_url,
    render_movie_html,
    get_movies_genres
)
from ..tmdb import TMDBWrapper, get_cached_movies_genres

__all__ = (
    'search_movies',
    'get_inline_handler'
)


def search_movies(update: 'Update', context: 'CallbackContext') -> None:
    """Handle the inline query."""
    user = save_user_and_activate_user_language(
        update=update,
        context=context
    )
    search_keyword = update.inline_query.query

    print('Search keyword:', search_keyword)

    if search_keyword == "":
        return

    genres_map = (
        get_cached_movies_genres(
            language=context.user_data.get('language')
        )
    )

    wrapper = TMDBWrapper(
        language=user.language_code
    )

    movies = []

    for page in range(1, 5):
        movies.extend(
            wrapper
            .search_movies(
                query=search_keyword,
                page=page
            )
        )

    movies = sorted(set(movies), key=lambda x: x.vote_average)

    update.inline_query.answer([
        InlineQueryResultArticle(
            id=str(movie.id),
            title=movie.title,
            input_message_content=InputTextMessageContent(
                render_movie_html(
                    movie=movie,
                    context=context,
                    with_image=True
                ),
                disable_web_page_preview=False,
                parse_mode=ParseMode.HTML
            ),
            url=get_movie_url(movie=movie),
            description=(
                f"{_('Rating:')} "
                f"{movie.vote_average}/{movie.vote_count} "
                f"({get_movies_genres(movie=movie, context=context, genres_map=genres_map, limit=2)})\n"
                f"{movie.overview[:500]}"
            ),
            thumb_url=get_movie_poster_url(movie=movie, width=92),
        )
        for movie in movies
    ])


def get_inline_handler():
    return InlineQueryHandler(search_movies)
