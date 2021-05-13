from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _

__all__ = ("SharedConfig",)


class SharedConfig(AppConfig):
    name = "shared"
    verbose_name = _("Shared")

    def ready(self):
        # Load this module so django will register an event
        from shared.rosetta import restart_server
