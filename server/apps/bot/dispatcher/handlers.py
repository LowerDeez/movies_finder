from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler
)

from apps.bot.dispatcher.callbacks.discover_movies import (
    back_or_clear_show_data_callback,
    discovering_movies_callback,
    select_genre_callback,
    select_years_callback,
    show_data_callback,
    discover_movies_callback
)
from apps.bot.dispatcher.callbacks.entry_points import (
    start,
    end,
    stop,
    stop_nested, back_to_start
)
from apps.bot.dispatcher.callbacks.list_movies import (
    list_movies_callback,
)
from apps.bot.dispatcher.callbacks.search_movies import (
    search_movies_callback,
    display_movies_callback
)
from .consts import (
    ACTION_CHOICES,
    STATE_CHOICES,
    END,
)

__all__ = (
    'get_select_action_handlers',
    'get_movie_handler'
)


def get_select_action_handlers():
    selection_handlers = [
        # ? nested conversation handler to discover movies by genres and years
        # * handles `discover_movies` callback from start
        ConversationHandler(
            entry_points=[
                CallbackQueryHandler(
                    discovering_movies_callback,
                    pattern=f'^{ACTION_CHOICES.discover_movies}$'
                )
            ],
            states={
                STATE_CHOICES.discovering_movies: [
                    CallbackQueryHandler(
                        select_genre_callback,
                        pattern=f'^{ACTION_CHOICES.select_genre}$'
                    ),
                    CallbackQueryHandler(
                        select_years_callback,
                        pattern=f'^{ACTION_CHOICES.select_years}$'
                    ),
                    CallbackQueryHandler(
                        discover_movies_callback,
                        pattern=f'^{ACTION_CHOICES.discover}$'
                    ),
                    CallbackQueryHandler(
                        discover_movies_callback,
                        pattern=f'^{ACTION_CHOICES.next_movies}$'
                    ),
                    CallbackQueryHandler(
                        back_to_start,
                        pattern=f'^{END}$'
                    ),
                ],
                STATE_CHOICES.selecting_search_param: [
                    CallbackQueryHandler(
                        discovering_movies_callback,
                    ),
                ],
                STATE_CHOICES.showing_search_params: [
                    CallbackQueryHandler(
                        discover_movies_callback,
                        pattern=f'^{ACTION_CHOICES.discover}$'
                    ),
                    CallbackQueryHandler(
                        back_or_clear_show_data_callback,
                        pattern=(
                            f'^{ACTION_CHOICES.back_from_show_search_params}$'
                            f'|^{ACTION_CHOICES.clear_search_params}$'
                        )
                    ),
                ]
            },
            # + INFO
            # used if the user is currently in a conversation but
            # the state has either no associated handler
            # or the handler that is associated to the state
            # is inappropriate for the update
            fallbacks=[
                CallbackQueryHandler(
                    show_data_callback,
                    pattern=f'^{ACTION_CHOICES.show_search_params}$'
                ),
                CommandHandler('stop', stop_nested),
            ],
            map_to_parent={
                # Return to top level menu
                END: STATE_CHOICES.selecting_action,

                # Return to first level stopping - to /movies
                STATE_CHOICES.stopping: STATE_CHOICES.stopping,
            },
        ),

        # * handles `search_movies` callback from start
        CallbackQueryHandler(
            search_movies_callback,
            pattern=f'^{ACTION_CHOICES.search_movies}$'
        ),

        CallbackQueryHandler(
            list_movies_callback,
            pattern=(
                f'^{ACTION_CHOICES.popular}$'
                f'|^{ACTION_CHOICES.top_rated}$'
                f'|^{ACTION_CHOICES.upcoming}$'
                f'|^{ACTION_CHOICES.now_playing}$'
            )
        ),

        CallbackQueryHandler(
            show_data_callback,
            pattern=f'^{ACTION_CHOICES.show_search_params}$'
        ),

        # * handles `end` callback from start
        CallbackQueryHandler(
            end,
            pattern=f'^{END}$'
        ),
    ]

    return selection_handlers


def get_movie_handler() -> 'ConversationHandler':
    conversation_handler = ConversationHandler(
        entry_points=[
            CommandHandler('movies', start)
        ],
        states={
            # * handle `selecting_action`
            STATE_CHOICES.selecting_action: get_select_action_handlers(),

            # * handle `searching_movies`
            STATE_CHOICES.searching_movies: [
                MessageHandler(
                    filters=Filters.text & ~Filters.command,  # text and not command
                    callback=display_movies_callback
                )
            ],

            STATE_CHOICES.stopping: [
                CommandHandler('movies', start)
            ],

            STATE_CHOICES.displaying_movies: [
                CallbackQueryHandler(
                    display_movies_callback,
                    pattern=f'^{ACTION_CHOICES.next_movies}$'
                ),
                CallbackQueryHandler(start, pattern=f'^{END}$')
            ],

            STATE_CHOICES.listing_movies: [
                CallbackQueryHandler(
                    list_movies_callback,
                    pattern=f'^{ACTION_CHOICES.next_movies}$'
                ),
                CallbackQueryHandler(start, pattern=f'^{END}$')
            ]
        },
        fallbacks=[
            CommandHandler('stop', stop),
        ],
    )

    return conversation_handler
