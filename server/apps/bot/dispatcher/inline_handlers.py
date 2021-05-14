from telegram import InlineQueryResultArticle, ParseMode, InputTextMessageContent, Update
from telegram.ext import InlineQueryHandler, CallbackContext

from .cases import save_user_and_activate_user_language
from .services import (
    get_movie_url,
    get_movie_image_url,
    render_movie_html
)
from ..tmdb import TMDBWrapper

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

    if search_keyword == "":
        return

    wrapper = TMDBWrapper(
        language=user.language_code
    )

    movies = []

    for page in range(1, 6):
        movies.extend(
            wrapper
            .search_movies(
                query=search_keyword,
                page=page
            )
        )

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
            description=movie.overview[:500],
            thumb_url=get_movie_image_url(movie=movie),
        )
        for movie in movies
    ])


def get_inline_handler():
    return InlineQueryHandler(search_movies)
