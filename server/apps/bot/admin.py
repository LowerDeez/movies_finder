from django.contrib import admin

from .models import Bot, ChatUser
from .services.webhook import set_webhook


def set_webhook_(modeladmin, request, queryset):
    for bot in queryset:
        set_webhook(bot=bot, request=request)


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    actions = [
        set_webhook_
    ]


@admin.register(ChatUser)
class ChatUserAdmin(admin.ModelAdmin):
    list_display = [
        'user_id',
        'username',
        'first_name',
        'last_name',
        'language_code'
    ]
