# test_email.py
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'scout.settings')
django.setup()

from django.conf import settings
from aderant.services import send_account_creation_email
from aderant.models import CustomUser

# Test
print(f"BASE_URL: {getattr(settings, 'BASE_URL', 'Non configuré')}")
print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Non configuré')}")

# Pour tester l'envoi d'email (en développement avec console backend)
user = CustomUser.objects.first()
if user:
    send_account_creation_email(user, "TEST123")