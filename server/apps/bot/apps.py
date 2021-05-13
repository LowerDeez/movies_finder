from django.apps import AppConfig


class BotConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.bot'

    def ready(self):
        print('INIT BOTS:')
        from .models import Bot
        from .registry import registry
        from .services import get_dispatcher

        for bot in Bot.objects.all():
            dispatcher = get_dispatcher(token=bot.token)
            registry.add_entry(dispatcher)

        print('INIT REGISTRY:', registry)
