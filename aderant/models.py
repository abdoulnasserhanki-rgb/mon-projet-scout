from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.exceptions import ValidationError

import logging
logger = logging.getLogger(__name__)

class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('ADMIN', 'Administrateur'),
        ('CHEF_GROUPE', 'Chef de Groupe'),
        ('CHEF_UNITE', 'Chef d\'Unité'),
        ('CHEF_SECTION', 'chef de section'),
    )
    Unite = (
        ('All', 'Tous les unités'),
        ('liberte', 'Unité Liberté'),
        ('boukoki', 'Unité Boukoki'),
    )
    Section = (
        ('All', 'Tous les branches'),
        ('Routiere', 'Routière'),
        ('Cheminot', 'Chéminot'),
        ('Eclaireure', 'Eclaireure'),
        ('Louveteau', 'Louveteau'),
    )
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(unique=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='ADMIN')
    unite = models.CharField(max_length=100, choices=Unite, default='Tous les unités')
    section = models.CharField(max_length=100, choices=Section, default='Tous les branches')
    telephone = models.CharField(max_length=20, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    email_confirmed = models.BooleanField(default=False)
    temporary_password = models.CharField(max_length=100, blank=True)
    # champ photo de profil
    photo_profil = models.ImageField(
        upload_to='profils/',
        null=True,
        blank=True,
        verbose_name="Photo de profil"
    )
    
    def generate_temporary_password(self):
        """Génère et retourne un mot de passe temporaire SANS sauvegarder"""
        temp_password = get_random_string(12)
        logger.info(f"🔑 Mot de passe temporaire généré pour {self.username}: {temp_password}")
        return temp_password
    
    def set_temporary_password(self):
        """Génère, définit et sauvegarde un mot de passe temporaire"""
        temp_password = self.generate_temporary_password()
        self.set_password(temp_password)
        self.save()
        logger.info(f"✅ Mot de passe temporaire défini pour {self.username}")
        return temp_password
    
    def get_photo_url(self):
        """Retourne l'URL de la photo ou une image par défaut"""
        if self.photo_profil and hasattr(self.photo_profil, 'url'):
            return self.photo_profil.url

    def __str__(self):
        return f"{self.username} - {self.role}"

class Adherant(models.Model):
    Sexe = (
        ('M', 'Masculin'),
        ('F', 'Feminin'),
    )
    Situation_matrimoniale = (
        ('celibataire', 'Célibataire'),
        ('marie', 'Marié'),
        ('divorce', 'Divorcé'),
    )
    Unite = (
        ('liberte', 'Liberté'),
        ('boukoki', 'Boukoki'),
    )
    Situation = (
        ('actif', 'Actif'),
        ('aleatoire', 'Aléatoire'),
        ('suspendu', 'Suspendu'),
    )
    Religion = (
        ('islam', 'Islam'),
        ('christianisme', 'Christianisme'),
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    sexe = models.CharField(max_length=20, choices=Sexe)
    situation_matrimoniale = models.CharField(max_length=50, choices=Situation_matrimoniale, default='celibataire')
    residence = models.CharField(max_length=100)
    niveau_etude = models.CharField(max_length=100, null=True, blank=True)
    competences = models.CharField(max_length=255, null=True, blank=True)
    date_integration = models.DateField()
    numero = models.CharField(max_length=8, null=True, blank=True)
    numero_parent = models.CharField(max_length=8, null=True, blank=True) 
    unite = models.CharField(max_length=100, choices=Unite)
    situation = models.CharField(max_length=100, choices=Situation, default='actif')
    motif = models.CharField(max_length=100, null=True, blank=True)
    motivation = models.CharField(max_length=100, null=True, blank=True)
    religion = models.CharField(max_length=100, choices=Religion, default='islam')
    photo = models.ImageField(upload_to='adherants/', null=True, blank=True)
    date_creation = models.DateField(auto_now_add=True)  # Utilisez auto_now_add pour la date de création

    class Meta:
        unique_together = ('nom', 'prenom', 'date_naissance', 'lieu_naissance')
        indexes = [
            models.Index(fields=['nom', 'prenom', 'date_naissance', 'lieu_naissance'], name='adherant_ident_idx')
        ]

    def clean(self):
        super().clean()
        if self.nom and self.prenom and self.date_naissance and self.lieu_naissance:
            duplicate_exists = Adherant.objects.filter(
                nom__iexact=self.nom.strip(),
                prenom__iexact=self.prenom.strip(),
                date_naissance=self.date_naissance,
                lieu_naissance__iexact=self.lieu_naissance.strip(),
            ).exclude(pk=self.pk).exists()
            if duplicate_exists:
                raise ValidationError("Un adhérent avec ce nom, prénom, date de naissance et lieu de naissance existe déjà.")

    def __str__(self):
        return f"{self.prenom} {self.nom}"

    def get_sexe_display(self):
        return "Masculin" if self.sexe == 'M' else "Féminin"


class Preinscription(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'En attente'),
        ('APPROVED', 'Validée'),
        ('REJECTED', 'Refusée'),
    )

    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    date_naissance = models.DateField()
    lieu_naissance = models.CharField(max_length=100)
    sexe = models.CharField(max_length=20, choices=Adherant.Sexe)
    situation_matrimoniale = models.CharField(max_length=50, choices=Adherant.Situation_matrimoniale, default='celibataire')
    residence = models.CharField(max_length=100)
    niveau_etude = models.CharField(max_length=100, null=True, blank=True)
    competences = models.CharField(max_length=255, null=True, blank=True)
    date_integration = models.DateField()
    numero = models.CharField(max_length=8, null=True, blank=True)
    numero_parent = models.CharField(max_length=8, null=True, blank=True)
    unite = models.CharField(max_length=100, choices=Adherant.Unite)
    situation = models.CharField(max_length=100, choices=Adherant.Situation, default='actif')
    motif = models.CharField(max_length=100, null=True, blank=True)
    motivation = models.CharField(max_length=100, null=True, blank=True)
    religion = models.CharField(max_length=100, choices=Adherant.Religion, default='islam')
    photo = models.ImageField(upload_to='preinscriptions/', null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    approved_by = models.ForeignKey(CustomUser, null=True, blank=True, on_delete=models.SET_NULL, related_name='approved_preinscriptions')
    approved_at = models.DateTimeField(null=True, blank=True)
    rejected_reason = models.TextField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def approve(self, user):
        if self.status != 'PENDING':
            raise ValidationError('Cette préinscription ne peut plus être validée.')

        duplicate_exists = Adherant.objects.filter(
            nom__iexact=self.nom.strip(),
            prenom__iexact=self.prenom.strip(),
            date_naissance=self.date_naissance,
            lieu_naissance__iexact=self.lieu_naissance.strip(),
        ).exists()
        if duplicate_exists:
            raise ValidationError('Un adhérent avec ces informations existe déjà.')

        adherant = Adherant.objects.create(
            nom=self.nom,
            prenom=self.prenom,
            date_naissance=self.date_naissance,
            lieu_naissance=self.lieu_naissance,
            sexe=self.sexe,
            situation_matrimoniale=self.situation_matrimoniale,
            residence=self.residence,
            niveau_etude=self.niveau_etude,
            competences=self.competences,
            date_integration=self.date_integration,
            numero=self.numero,
            numero_parent=self.numero_parent,
            unite=self.unite,
            situation=self.situation,
            motif=self.motif,
            motivation=self.motivation,
            religion=self.religion,
            photo=self.photo,
        )

        self.status = 'APPROVED'
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
        return adherant

    def reject(self, user, reason=None):
        if self.status != 'PENDING':
            raise ValidationError('Cette préinscription ne peut plus être rejetée.')
        self.status = 'REJECTED'
        self.rejected_reason = reason
        self.approved_by = user
        self.approved_at = timezone.now()
        self.save()
        return self

    def __str__(self):
        return f"Préinscription {self.prenom} {self.nom} ({self.get_status_display()})"
