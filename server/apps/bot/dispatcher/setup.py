from telegram import Bot as TelegramBot
from telegram.ext import (
    Dispatcher,
)

from .handlers import get_movie_handler
from .inline_handlers import get_inline_handler

__all__ = (
    'setup_dispatcher',
)


def setup_dispatcher(token: str) -> 'Dispatcher':
    bot = TelegramBot(token=token)

    dispatcher = Dispatcher(
        bot=bot,
        update_queue=None,
        workers=0,
        use_context=True,
    )

    dispatcher.add_handler(get_movie_handler())
    dispatcher.add_handler(get_inline_handler())

    return dispatcher
