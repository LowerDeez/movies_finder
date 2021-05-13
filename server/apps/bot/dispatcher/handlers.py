from os import environ

from django.utils.translation import ugettext_lazy as _

from telegram import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Update,
    ParseMode,
)
from telegram.ext import (
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackQueryHandler,
    CallbackContext
)

from .consts import (
    ACTION_CHOICES,
    STATE_CHOICES,
    CONSTS,
    YEARS_CHOICES,
    END,
    BACK_BUTTON,

)
from .tmdb import (
    TMDBWrapper,
    get_cached_movies_genres
)
from .services import (
    render_movies,
    get_last_movie_keyboard,
    build_search_params,
    display_search_params,
    set_search_params,
    get_discovering_movies_callback_text,
    get_current_page
)
from ..services.user import parse_user, save_user


def start(update: 'Update', context: 'CallbackContext'):
    print('Start...')
    user = parse_user(
        update=update,
        context=context
    )
    save_user(user_entity=user)
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
        update.callback_query.answer()
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=keyboard
        )
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


def end_second_level_conversation(update: 'Update', context: 'CallbackContext'):
    """
    Returns to start
    """
    print('End second level conversation...')
    start(update, context)
    context.user_data.clear()
    return END


def end_third_level_conversation(update: 'Update', context: 'CallbackContext'):
    """
    Returns to discovering movies menu from nested options like "Show data"
    """
    print('End third level conversation...')
    return discovering_movies_callback(update, context)


def search_movies_callback(update: 'Update', context: 'CallbackContext'):
    print('Search movies...')
    text = str(_('Okay, please enter some keywords to search:'))
    update.callback_query.answer()
    update.callback_query.edit_message_text(text=text)
    return STATE_CHOICES.searching_movies


def display_movies_callback(update: 'Update', context: 'CallbackContext'):
    print('Display movies...')
    user_data = context.user_data
    search_keyword = user_data.get(CONSTS.search_keyword)
    page = get_current_page()
    message = update.message

    if update.message:
        search_keyword = (
            user_data.setdefault(
                CONSTS.search_keyword,
                update.message.text
            )
        )

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


# Second level conversation callbacks
def discovering_movies_callback(update: 'Update', context: 'CallbackContext') -> str:
    """Choose to add a parent or a child."""
    print('Discover movies:')
    set_search_params(
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
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=keyboard
    )

    return STATE_CHOICES.discovering_movies


def select_genre_callback(update: 'Update', context: 'CallbackContext'):
    print('Select genre:')
    text = str(_('Okay, that is genres:'))
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
    text = str(_('Okay, that is years:'))
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


def show_data(update: 'Update', context: 'CallbackContext') -> str:
    """Pretty print gathered data."""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=str(_('Discover')),
                    callback_data=ACTION_CHOICES.discover
                )
            ],
            BACK_BUTTON
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
                        end_second_level_conversation,
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
                        end_third_level_conversation,
                        pattern=f'^{END}$'
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
                    show_data,
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
            show_data,
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
            # CallbackQueryHandler(
            #     end_second_level_conversation,
            #     pattern=f'^{END}$'
            # ),
        ],
    )

    return conversation_handler
