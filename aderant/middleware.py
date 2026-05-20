# aderant/middleware.py
from django.shortcuts import redirect
from django.urls import reverse

class PasswordChangeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Vérifier si l'utilisateur est connecté et doit changer son mot de passe
        if (request.user.is_authenticated and 
            not request.path.startswith('/accounts/change-password-required') and
            not request.path.startswith('/accounts/logout') and
            self._needs_password_change(request)):
            return redirect('change_password_required')
        
        return response
    
    def _needs_password_change(self, request):
        """Détermine si l'utilisateur doit changer son mot de passe"""
        # Vous pouvez ajouter votre propre logique ici
        # Par exemple, vérifier si c'est la première connexion
        # ou si le mot de passe est temporaire
        return False  # À adapter selon vos besoins