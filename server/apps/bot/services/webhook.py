import json
from typing import TYPE_CHECKING

from django.urls import reverse
from telegram import Bot as TelegramBot, Update
from telegram.ext import Updater

from ..dispatcher.setup import setup_dispatcher

if TYPE_CHECKING:
    from django.http import HttpRequest
    from telegram.ext import Dispatcher
    from ..models import Bot

__all__ = (
    'set_webhook',
    'process_webhook_event'
)


def set_webhook(
        *,
        bot: 'Bot',
        request: 'HttpRequest',
        force_https: bool = True
) -> bool:
    updater = Updater(token=bot.token)

    if request.scheme != 'https' and force_https:
        request._get_scheme = lambda: 'https'

    url = (
        request.build_absolute_uri(
            reverse(
                'telegram-bot:webhook',
                kwargs={'token': bot.token}
            )
        )
    )
    print('Webhook url:', url)
    result = updater.bot.setWebhook(url)
    print('Webhook result:', result)
    return result


def get_dispatcher(token: str) -> 'Dispatcher':
    dispatcher: 'Dispatcher' = setup_dispatcher(token=token)
    return dispatcher


def process_webhook_event(
        token: str,
        request_body: bytes,
        dispatcher: 'Dispatcher' = None
):
    if not isinstance(request_body, dict):
        request_body = json.loads(request_body)

    bot = TelegramBot(token=token)
    data = Update.de_json(request_body, bot)

    if dispatcher is None:
        dispatcher: 'Dispatcher' = get_dispatcher(token)

    dispatcher.process_update(data)

    return dispatcher
