from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, update_session_auth_hash, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models import Count, Avg
from django.db import models
from django.contrib.auth.decorators import login_required
from django.views.generic import ListView, CreateView
from django.core.exceptions import ValidationError
from .models import Adherant, CustomUser, Preinscription
from django.contrib.auth.forms import PasswordChangeForm
from .forms import CustomUserCreationForm, CustomUserChangeForm, CustomPasswordChangeForm
from .forms import AdherantForm, PreinscriptionForm, UserProfileForm
from django.urls import reverse_lazy
from .services import send_account_creation_email, send_password_reset_email
from datetime import timedelta
from datetime import date
import logging
import csv
from django.http import HttpResponse

logger = logging.getLogger(__name__)

@login_required
def custom_logout(request):
    """Vue de déconnexion personnalisée"""
    username = request.user.username
    logout(request)
    messages.success(request, f'Vous avez été déconnecté avec succès. À bientôt {username}!')
    return redirect('login')

def custom_login(request):
    """Vue de connexion personnalisée"""
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            if user.check_password(password) and hasattr(user, 'date_joined'):
                return redirect('accueil')
            else:
                return redirect('accueil')
        else:
            messages.error(request, 'Nom d\'utilisateur ou mot de passe incorrect.')
    return render(request, 'registration/login.html')

@login_required
def change_password_required(request):
    """Page de changement de mot de passe obligatoire après première connexion"""
    if request.method == 'POST':
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Votre mot de passe a été modifié avec succès !')
            return redirect('accueil')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PasswordChangeForm(request.user)
    return render(request, 'registration/change_password_required.html', {'form': form})

@login_required
def Accueil(request):
    total_adherants = Adherant.objects.count()
    debut_mois = timezone.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    nouveaux_mois = Adherant.objects.filter(date_integration__gte=debut_mois).count()
    total_femmes = Adherant.objects.filter(sexe='F').count()
    pourcentage_femmes = round((total_femmes / total_adherants * 100) if total_adherants > 0 else 0, 1)
    aujourd_hui = date.today()
    try:
        moyenne_age = Adherant.objects.annotate(
            age=aujourd_hui.year - models.F('date_naissance__year')
        ).aggregate(avg_age=Avg('age'))['avg_age']
        moyenne_age = round(moyenne_age or 0, 1)
    except:
        moyenne_age = 25.0

    residences_stats = Adherant.objects.values('residence').annotate(
        count=Count('id')
    ).order_by('-count')[:5]
    for residence in residences_stats:
        residence['pourcentage'] = round((residence['count'] / total_adherants * 100) if total_adherants > 0 else 0, 1)
        residence['ville'] = residence['residence'] or 'Non spécifié'

    niveaux_etude_stats = Adherant.objects.values('niveau_etude').annotate(
        count=Count('id')
    ).order_by('-count')
    for niveau in niveaux_etude_stats:
        niveau['pourcentage'] = round((niveau['count'] / total_adherants * 100) if total_adherants > 0 else 0, 1)
        niveau['niveau'] = niveau['niveau_etude'] or 'Non spécifié'

    adherants_recents = Adherant.objects.all().order_by('-date_integration')[:8]

    mois_dernier = debut_mois - timedelta(days=30)
    nouveaux_mois_dernier = Adherant.objects.filter(
        date_integration__gte=mois_dernier,
        date_integration__lt=debut_mois
    ).count()
    evolution_nouveaux = round(
        ((nouveaux_mois - nouveaux_mois_dernier) / nouveaux_mois_dernier * 100) if nouveaux_mois_dernier > 0 else 100, 1
    )
    total_mois_dernier = Adherant.objects.filter(date_integration__lt=debut_mois).count()
    evolution_total = round(
        ((total_adherants - total_mois_dernier) / total_mois_dernier * 100) if total_mois_dernier > 0 else 0, 1
    )

    context = {
        'total_adherants': total_adherants,
        'nouveaux_mois': nouveaux_mois,
        'total_femmes': total_femmes,
        'pourcentage_femmes': pourcentage_femmes,
        'moyenne_age': moyenne_age,
        'residences_stats': residences_stats,
        'niveaux_etude_stats': niveaux_etude_stats,
        'adherants_recents': adherants_recents,
        'evolution_total': evolution_total,
        'evolution_nouveaux': evolution_nouveaux,
    }

    if request.user.is_superuser or request.user.is_staff:
        total_utilisateurs = CustomUser.objects.count()
        total_admins = CustomUser.objects.filter(is_superuser=True).count()
        utilisateurs_actifs = CustomUser.objects.filter(is_active=True).count()
        connexions_mois = CustomUser.objects.filter(last_login__gte=debut_mois).count()
        derniere_activite = CustomUser.objects.filter(
            last_login__isnull=False
        ).order_by('-last_login').first().last_login if CustomUser.objects.filter(last_login__isnull=False).exists() else timezone.now()
        utilisateurs_recents = CustomUser.objects.filter(last_login__isnull=False).order_by('-last_login')[:5]
        taux_utilisation = min(95, round((connexions_mois / total_utilisateurs * 100) if total_utilisateurs > 0 else 0))

        context.update({
            'total_utilisateurs': total_utilisateurs,
            'total_admins': total_admins,
            'utilisateurs_actifs': utilisateurs_actifs,
            'connexions_mois': connexions_mois,
            'derniere_activite': derniere_activite,
            'utilisateurs_recents': utilisateurs_recents,
            'taux_utilisation': taux_utilisation,
        })

    return render(request, 'index.html', context)

@login_required
def user_list(request):
    if request.user.role != 'CHEF_GROUPE' and request.user.role != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')
    users = CustomUser.objects.all().order_by('-date_joined')
    total_users = users.count()
    admin_count = users.filter(role='ADMIN').count()
    chef_unite_count = users.filter(role='CHEF_UNITE').count()
    chef_groupe_count = users.filter(role='CHEF_GROUPE').count()
    chef_section_count = users.filter(role='CHEF_SECTION').count()
    context = {
        'users': users,
        'total_users': total_users,
        'admin_count': admin_count,
        'chef_unite_count': chef_unite_count,
        'chef_groupe_count': chef_groupe_count,
        'chef_section_count': chef_section_count,
    }
    return render(request, 'users/user_list.html', context)

# ------------------- CORRIGÉE --------------------
@login_required
def user_create(request):
    if request.user.role != 'CHEF_SECTION' and request.user.role != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accueil')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Génération du mot de passe temporaire protégée
            try:
                temp_password = user.set_temporary_password()
            except Exception as e:
                logger.error(f"Erreur génération mot de passe temporaire : {e}", exc_info=True)
                messages.error(request, "Une erreur est survenue lors de la création du compte.")
                return redirect('user_list')

            # Envoi de l'email protégé contre tout crash
            try:
                email_sent = send_account_creation_email(user, temp_password)
                if email_sent:
                    messages.success(request, f"Utilisateur {user.username} créé avec succès. Un email de confirmation a été envoyé.")
                else:
                    messages.warning(request, f"Utilisateur {user.username} créé, mais l'email n'a pas pu être envoyé.")
            except Exception as e:
                logger.error(f"Erreur inattendue envoi email création pour {user.username} : {e}", exc_info=True)
                messages.warning(request, f"Utilisateur {user.username} créé, mais l'email n'a pas pu être envoyé (erreur technique).")

            return redirect('user_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'users/user_create.html', {'form': form})

@login_required
def user_edit(request, user_id):
    if request.user.role != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accueil')
    user = get_object_or_404(CustomUser, id=user_id)
    if user == request.user:
        messages.error(request, "Vous ne pouvez pas modifier votre propre compte.")
        return redirect('user_list')
    if user.is_superuser and not request.user.is_superuser:
        messages.error(request, "Vous ne pouvez pas modifier un superutilisateur.")
        return redirect('user_list')
    if request.method == 'POST':
        form = CustomUserChangeForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            if 'role' in form.changed_data:
                messages.success(request, f"✅ Rôle de {user.username} modifié : {form.cleaned_data['role']}")
            else:
                messages.success(request, f"✅ Utilisateur {user.username} modifié avec succès.")
            return redirect('user_list')
        else:
            messages.error(request, "Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomUserChangeForm(instance=user)
    return render(request, 'users/user_edit.html', {'form': form, 'user_obj': user})

# ------------------- CORRIGÉE --------------------
@login_required
def user_reset_password(request, user_id):
    if request.user.role != 'CHEF_SECTION' and request.user.role != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('accueil')

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == 'POST':
        # Génération du nouveau mot de passe protégée
        try:
            new_password = user.set_temporary_password()
        except Exception as e:
            logger.error(f"Erreur génération mot de passe reset pour {user.username} : {e}", exc_info=True)
            messages.error(request, "Une erreur est survenue lors de la réinitialisation du mot de passe.")
            return redirect('user_list')

        # Envoi de l'email protégé contre tout crash
        try:
            email_sent = send_password_reset_email(user, new_password)
            if email_sent:
                messages.success(request, f"Mot de passe réinitialisé pour {user.username}. Un email a été envoyé.")
            else:
                messages.warning(request, f"Mot de passe réinitialisé, mais l'email n'a pas pu être envoyé.")
        except Exception as e:
            logger.error(f"Erreur inattendue envoi email reset pour {user.username} : {e}", exc_info=True)
            messages.warning(request, f"Mot de passe réinitialisé, mais l'email n'a pas pu être envoyé (erreur technique).")

        return redirect('user_list')

    return render(request, 'users/user_confirm_reset.html', {'user': user})

@login_required
def user_toggle_active(request, user_id):
    if request.user.role != 'CHEF_SECTION' and request.user.role != 'ADMIN':
        messages.error(request, "Accès réservé aux administrateurs.")
        return redirect('dashboard')
    user = get_object_or_404(CustomUser, id=user_id)
    if user != request.user:
        user.is_active = not user.is_active
        user.save()
        status = "activé" if user.is_active else "désactivé"
        messages.success(request, f"Utilisateur {user.username} {status} avec succès.")
    else:
        messages.error(request, "Vous ne pouvez pas désactiver votre propre compte.")
    return redirect('user_list')

@login_required
def user_profile(request):
    return render(request, 'users/user_profile.html', {'user': request.user})

@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "✅ Votre profil a été mis à jour avec succès!")
            return redirect('user_profile')
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs ci-dessous.")
    else:
        form = UserProfileForm(instance=request.user)
    return render(request, 'users/edit_profile.html', {'form': form, 'active_tab': 'profile'})

@login_required
def change_password(request):
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "✅ Votre mot de passe a été changé avec succès!")
            return redirect('user_profile')
        else:
            messages.error(request, "❌ Veuillez corriger les erreurs ci-dessous.")
    else:
        form = CustomPasswordChangeForm(request.user)
    return render(request, 'users/change_password.html', {'form': form, 'active_tab': 'password'})

def calculer_branche(age):
    if age <= 10:
        return "Louveteau"
    elif age <= 15:
        return "Éclaireur"
    elif age <= 20:
        return "Cheminot"
    else:
        return "Routier"

def calculer_age(date_naissance):
    aujourd_hui = date.today()
    return aujourd_hui.year - date_naissance.year - ((aujourd_hui.month, aujourd_hui.day) < (date_naissance.month, date_naissance.day))

def est_nouvel_adherant(date_integration):
    if not date_integration:
        return False
    un_mois = timedelta(days=30)
    return timezone.now().date() - date_integration <= un_mois

@login_required
def AdherantListView(request):
    adherants = Adherant.objects.all()
    for adherant in adherants:
        if adherant.date_naissance:
            adherant.age = calculer_age(adherant.date_naissance)
            adherant.branche = calculer_branche(adherant.age)
        else:
            adherant.age = 0
            adherant.branche = "Non défini"
        adherant.est_nouveau = est_nouvel_adherant(adherant.date_integration)

    total_adherants = adherants.count()
    hommes_count = adherants.filter(sexe='M').count()
    femmes_count = adherants.filter(sexe='F').count()
    louveteaux_count = sum(1 for a in adherants if a.branche == "Louveteau")
    eclaireurs_count = sum(1 for a in adherants if a.branche == "Éclaireur")
    cheminots_count = sum(1 for a in adherants if a.branche == "Cheminot")
    routiers_count = sum(1 for a in adherants if a.branche == "Routier")
    louveteaux_pourcentage = round((louveteaux_count / total_adherants * 100) if total_adherants > 0 else 0, 1)
    eclaireurs_pourcentage = round((eclaireurs_count / total_adherants * 100) if total_adherants > 0 else 0, 1)
    cheminots_pourcentage = round((cheminots_count / total_adherants * 100) if total_adherants > 0 else 0, 1)
    routiers_pourcentage = round((routiers_count / total_adherants * 100) if total_adherants > 0 else 0, 1)

    user_role = request.user.role
    user_unite = getattr(request.user, 'unite', None)
    user_section = getattr(request.user, 'section', None)
    if user_role == 'CHEF_UNITE' and user_unite:
        adherants = [a for a in adherants if a.unite == user_unite]
    elif user_role == 'CHEF_SECTION' and user_section:
        adherants = [a for a in adherants if getattr(a, 'section', None) == user_section]

    context = {
        'adherants': adherants,
        'total_adherants': total_adherants,
        'hommes_count': hommes_count,
        'femmes_count': femmes_count,
        'louveteaux_count': louveteaux_count,
        'eclaireurs_count': eclaireurs_count,
        'cheminots_count': cheminots_count,
        'routiers_count': routiers_count,
        'louveteaux_pourcentage': louveteaux_pourcentage,
        'eclaireurs_pourcentage': eclaireurs_pourcentage,
        'cheminots_pourcentage': cheminots_pourcentage,
        'routiers_pourcentage': routiers_pourcentage,
    }
    return render(request, 'adherants/adherant_list.html', context)

def calculer_duree_adhesion(date_integration):
    if not date_integration:
        return 0
    aujourd_hui = date.today()
    return (aujourd_hui.year - date_integration.year) * 12 + aujourd_hui.month - date_integration.month

@login_required
def adherant_detail(request, adherant_id):
    adherant = get_object_or_404(Adherant, id=adherant_id)
    user_role = request.user.role
    user_unite = getattr(request.user, 'unite', None)
    user_section = getattr(request.user, 'section', None)
    can_edit = False
    if user_role == 'CHEF_GROUPE':
        can_edit = True
    elif user_role == 'CHEF_UNITE' and user_unite and adherant.unite == user_unite:
        can_edit = True
    elif user_role == 'CHEF_SECTION' and user_section and getattr(adherant, 'section', None) == user_section:
        can_edit = True

    age = calculer_age(adherant.date_naissance) if adherant.date_naissance else 0
    branche = calculer_branche(age)
    duree_adhesion = calculer_duree_adhesion(adherant.date_integration)
    est_nouveau = est_nouvel_adherant(adherant.date_integration)
    competences_list = []
    if adherant.competences:
        competences_list = [comp.strip() for comp in adherant.competences.split(',')]

    form = None
    if request.method == 'POST' and can_edit:
        form = AdherantForm(request.POST, request.FILES, instance=adherant)
        if form.is_valid():
            form.save()
            messages.success(request, 'Adhérent mis à jour avec succès!')
            return redirect('adherant_detail', adherant_id=adherant_id)
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = AdherantForm(instance=adherant)

    context = {
        'adherant': adherant,
        'can_edit': can_edit,
        'form': form,
        'age': age,
        'branche': branche,
        'duree_adhesion': duree_adhesion,
        'est_nouveau': est_nouveau,
        'competences_list': competences_list,
    }
    return render(request, 'adherants/adherant_detail.html', context)

class AdherantCreateView(CreateView):
    model = Adherant
    form_class = AdherantForm
    template_name = 'adherants/adherant_form.html'
    success_url = reverse_lazy('adherant_list')

def preinscription_create(request):
    if request.method == 'POST':
        form = PreinscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Votre préinscription a été envoyée avec succès. Un responsable validera votre dossier prochainement.')
            return redirect('preinscription_create')
        else:
            messages.error(request, 'Veuillez corriger les erreurs ci-dessous.')
    else:
        form = PreinscriptionForm()
    return render(request, 'adherants/preinscription_form.html', {'form': form})

@login_required
def preinscription_list(request):
    if request.user.role not in ['ADMIN', 'CHEF_GROUPE', 'CHEF_UNITE', 'CHEF_SECTION']:
        messages.error(request, "Accès réservé aux responsables.")
        return redirect('accueil')
    preinscriptions = Preinscription.objects.filter(status='PENDING')
    return render(request, 'adherants/preinscription_list.html', {'preinscriptions': preinscriptions})
# ===== EXPORT VIEWS =====

@login_required
def export_adherants_csv(request):
    """Exporte la liste complète des adhérents en CSV (ADMIN et CHEF_GROUPE uniquement)"""
    if request.user.role not in ['ADMIN', 'CHEF_GROUPE']:
        messages.error(request, "Accès réservé aux administrateurs et chefs de groupe.")
        return redirect('adherant_list')
    
    adherants = Adherant.objects.all()
    
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = 'attachment; filename="adherants_export.csv"'
    
    writer = csv.writer(response)
    writer.writerow(['Prénom', 'Nom', 'Date de naissance', 'Lieu de naissance', 
                     'Sexe', 'Situation matrimoniale', 'Résidence', 'Niveau d\'étude',
                     'Compétences', 'Unité', 'Situation', 'Motif d\'adhésion', 
                     'Motivation', 'Religion', 'Numéro personnel', 'Numéro parent',
                     'Date d\'intégration', 'Date de création'])
    
    for adherant in adherants:
        writer.writerow([
            adherant.prenom,
            adherant.nom,
            adherant.date_naissance.strftime('%d/%m/%Y') if adherant.date_naissance else '',
            adherant.lieu_naissance,
            adherant.get_sexe_display(),
            adherant.get_situation_matrimoniale_display(),
            adherant.residence,
            adherant.niveau_etude,
            adherant.competences if adherant.competences else '',
            adherant.get_unite_display(),
            adherant.get_situation_display(),
            adherant.motif if adherant.motif else '',
            adherant.motivation if adherant.motivation else '',
            adherant.get_religion_display(),
            adherant.numero if adherant.numero else '',
            adherant.numero_parent if adherant.numero_parent else '',
            adherant.date_integration.strftime('%d/%m/%Y') if adherant.date_integration else '',
            adherant.date_creation.strftime('%d/%m/%Y') if adherant.date_creation else '',
        ])
    
    messages.success(request, f'Export de {adherants.count()} adhérent(s) effectué avec succès.')
    return response

@login_required
def export_adherant_detail_csv(request, adherant_id):
    """Exporte les détails d'un adhérent en CSV"""
    adherant = get_object_or_404(Adherant, id=adherant_id)
    
    user_role = request.user.role
    user_unite = getattr(request.user, 'unite', None)
    user_section = getattr(request.user, 'section', None)
    can_view = False
    
    if user_role == 'ADMIN':
        can_view = True
    elif user_role == 'CHEF_GROUPE':
        can_view = True
    elif user_role == 'CHEF_UNITE' and user_unite and adherant.unite == user_unite:
        can_view = True
    elif user_role == 'CHEF_SECTION' and user_section and getattr(adherant, 'section', None) == user_section:
        can_view = True
    
    if not can_view:
        messages.error(request, "Accès non autorisé à cet adhérent.")
        return redirect('adherant_list')
    
    age = calculer_age(adherant.date_naissance) if adherant.date_naissance else 0
    branche = calculer_branche(age)
    duree_adhesion = calculer_duree_adhesion(adherant.date_integration)
    
    response = HttpResponse(content_type='text/csv; charset=utf-8-sig')
    response['Content-Disposition'] = f'attachment; filename="adherant_{adherant.prenom}_{adherant.nom}.csv"'
    
    writer = csv.writer(response)
    
    # En-tête avec le nom complet
    writer.writerow([f'Détails - {adherant.prenom} {adherant.nom}'])
    writer.writerow([])
    
    # Informations personnelles
    writer.writerow(['INFORMATIONS PERSONNELLES'])
    writer.writerow(['Prénom', adherant.prenom])
    writer.writerow(['Nom', adherant.nom])
    writer.writerow(['Date de naissance', adherant.date_naissance.strftime('%d/%m/%Y') if adherant.date_naissance else ''])
    writer.writerow(['Lieu de naissance', adherant.lieu_naissance])
    writer.writerow(['Sexe', adherant.get_sexe_display()])
    writer.writerow(['Âge', age])
    writer.writerow(['Situation matrimoniale', adherant.get_situation_matrimoniale_display()])
    writer.writerow(['Niveau d\'étude', adherant.niveau_etude if adherant.niveau_etude else ''])
    writer.writerow(['Religion', adherant.get_religion_display()])
    writer.writerow([])
    
    # Informations scoutes
    writer.writerow(['INFORMATIONS SCOUTES'])
    writer.writerow(['Unité', adherant.get_unite_display()])
    writer.writerow(['Branche', branche])
    writer.writerow(['Situation', adherant.get_situation_display()])
    writer.writerow(['Date d\'intégration', adherant.date_integration.strftime('%d/%m/%Y') if adherant.date_integration else ''])
    writer.writerow(['Durée d\'adhésion (mois)', duree_adhesion])
    writer.writerow(['Motif d\'adhésion', adherant.motif if adherant.motif else ''])
    writer.writerow(['Motivation', adherant.motivation if adherant.motivation else ''])
    writer.writerow([])
    
    # Contact et compétences
    writer.writerow(['CONTACT ET COMPÉTENCES'])
    writer.writerow(['Résidence', adherant.residence])
    writer.writerow(['Numéro personnel', adherant.numero if adherant.numero else ''])
    writer.writerow(['Numéro parent', adherant.numero_parent if adherant.numero_parent else ''])
    writer.writerow(['Compétences', adherant.competences if adherant.competences else 'Aucune'])
    writer.writerow([])
    
    # Dates
    writer.writerow(['DATES SYSTÈME'])
    writer.writerow(['Date de création', adherant.date_creation.strftime('%d/%m/%Y') if adherant.date_creation else ''])
    
    return response
@login_required
def preinscription_approve(request, preinscription_id):
    if request.user.role not in ['ADMIN', 'CHEF_GROUPE', 'CHEF_UNITE', 'CHEF_SECTION']:
        messages.error(request, "Accès réservé aux responsables.")
        return redirect('accueil')
    preinscription = get_object_or_404(Preinscription, id=preinscription_id, status='PENDING')
    if request.method == 'POST':
        duplicate_exists = Adherant.objects.filter(
            nom__iexact=preinscription.nom.strip(),
            prenom__iexact=preinscription.prenom.strip(),
            date_naissance=preinscription.date_naissance,
            lieu_naissance__iexact=preinscription.lieu_naissance.strip(),
        ).exists()
        if duplicate_exists:
            preinscription.reject(request.user, reason='Adhérent existant déjà dans la base.')
            messages.warning(request, 'La préinscription a été rejetée car un adhérent existe déjà avec ces informations.')
        else:
            try:
                preinscription.approve(request.user)
                messages.success(request, 'La préinscription a été validée et l’adhérent a été ajouté à la base.')
            except ValidationError as e:
                messages.error(request, e.message)
        return redirect('preinscription_list')
    return render(request, 'adherants/preinscription_approve.html', {'preinscription': preinscription})