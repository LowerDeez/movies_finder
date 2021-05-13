from django.conf import settings
from django.dispatch import receiver
from rosetta.signals import post_save


@receiver(post_save)
def restart_server(sender, **kwargs):
    """
    Restart server after rosetta translations fix.
    """
    # TODO: restart
