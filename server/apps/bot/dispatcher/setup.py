from telegram import Bot as TelegramBot
from telegram.ext import (
    Dispatcher,
)

from .handlers import get_movie_handler

__all__ = (
    'setup_dispatcher',
)


def setup_dispatcher(token: str) -> 'Dispatcher':
    # Create bot, update queue and bots instances
    bot = TelegramBot(token=token)

    dispatcher = Dispatcher(
        bot=bot,
        update_queue=None,
        workers=0,
        use_context=True,
        # persistence=persistence
    )

    dispatcher.add_handler(get_movie_handler())

    return dispatcher
