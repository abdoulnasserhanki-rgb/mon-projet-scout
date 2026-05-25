Configuration de l'envoi d'emails via SendGrid (django-anymail)

1) Installer la dépendance (en local / CI) :

```bash
pip install "django-anymail[sendgrid]"
```

2) Variables d'environnement à définir sur Render (Dashboard > Environment):

- `SENDGRID_API_KEY` : votre clé API SendGrid
- `DEFAULT_FROM_EMAIL` : adresse d'expédition par défaut (ex: noreply@votre-domaine.com)

3) Ce qui a été modifié dans le projet:

- `scout/settings.py` : configuration AnyMail/SendGrid ajoutée et ancienne configuration SMTP supprimée.

4) Vérification rapide en local:

- Installer la dépendance et démarrer le projet. Envoyer un email via l'interface qui déclenche l'envoi (création d'utilisateur / mot de passe oublié).

5) Remarques de sécurité:

- Ne mettez jamais de clés secrètes dans `settings.py`. Utilisez les variables d'environnement.
- Si vous avez encore des problèmes d'envoi sur Render, vérifiez les logs d'application et la console SendGrid.
