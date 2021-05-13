from django.db import models
from django.utils.translation import ugettext_lazy as _

__all__ = (
    'Bot',
    'ChatUser'
)


class Bot(models.Model):
    title = models.CharField(
        'Title',
        max_length=255
    )
    token = models.CharField(
        'Token',
        max_length=255
    )

    class Meta:
        verbose_name = _('Bot')
        verbose_name_plural = _('Bots')

    def __str__(self):
        return self.title


class ChatUser(models.Model):
    user_id = models.CharField(
        _('User id'),
        max_length=25
    )
    username = models.CharField(
        _('Username'),
        blank=True,
        max_length=32
    )
    first_name = models.CharField(
        _('First name'),
        blank=True,
        max_length=256
    )
    last_name = models.CharField(
        _('Last name'),
        blank=True,
        max_length=256
    )
    language_code = models.CharField(
        _('Language code'),
        blank=True,
        max_length=256
    )
    is_blocked_bot = models.BooleanField(
        _('Is blocked bot'),
        default=False
    )

    class Meta:
        verbose_name = _('Chat user')
        verbose_name_plural = _('Chat users')

    def __str__(self):
        return self.user_id
