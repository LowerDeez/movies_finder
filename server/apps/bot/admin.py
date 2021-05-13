from django.contrib import admin

from .models import Bot
from .services.webhook import set_webhook


def set_webhook_(modeladmin, request, queryset):
    for bot in queryset:
        set_webhook(bot=bot, request=request)


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    actions = [
        set_webhook_
    ]
