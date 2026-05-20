# services.py
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_account_creation_email(user, temporary_password):
    """Envoie un email de confirmation de création de compte"""
    subject = "Création de votre compte - Plateforme Adhérents"
    
    # Vérifier que BASE_URL est configuré
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    
    # Context pour le template
    context = {
        'user': user,
        'temporary_password': temporary_password,
        'login_url': f"{base_url}/accounts/login/",
        'support_email': getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@votreorganisation.org')
    }
    
    # Rendu du template HTML
    html_content = render_to_string('emails/account_creation.html', context)
    text_content = strip_tags(html_content)
    
    # Création de l'email
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False

def send_password_reset_email(user, new_password):
    """Envoie un email de réinitialisation de mot de passe"""
    subject = "Réinitialisation de votre mot de passe"
    
    base_url = getattr(settings, 'BASE_URL', 'http://localhost:8000')
    
    context = {
        'user': user,
        'new_password': new_password,
        'login_url': f"{base_url}/accounts/login/"
    }
    
    html_content = render_to_string('emails/password_reset.html', context)
    text_content = strip_tags(html_content)
    
    email = EmailMultiAlternatives(
        subject,
        text_content,
        settings.DEFAULT_FROM_EMAIL,
        [user.email]
    )
    email.attach_alternative(html_content, "text/html")
    
    try:
        email.send()
        return True
    except Exception as e:
        print(f"Erreur envoi email: {e}")
        return False