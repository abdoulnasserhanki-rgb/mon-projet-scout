import os
import logging

from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate

logger = logging.getLogger(__name__)


def create_default_superadmin(sender, **kwargs):
    User = get_user_model()
    if User.objects.filter(is_superuser=True).exists():
        return

    username = getattr(settings, 'DEFAULT_SUPERADMIN_USERNAME', 'admin')
    email = getattr(settings, 'DEFAULT_SUPERADMIN_EMAIL', 'admin@example.com')
    password = getattr(settings, 'DEFAULT_SUPERADMIN_PASSWORD', 'AdminPass123!')
    role = getattr(settings, 'DEFAULT_SUPERADMIN_ROLE', 'ADMIN')

    user = User.objects.create_superuser(username=username, email=email, password=password)
    user.role = role
    user.save()
    logger.info(f"Création automatique du superadmin '{username}'")


class AderantConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'aderant'

    def ready(self):
        post_migrate.connect(create_default_superadmin, sender=self)
