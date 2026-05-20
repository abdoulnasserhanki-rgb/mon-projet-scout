from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .models import Adherant, CustomUser, Preinscription

class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'role', 'unite', 'section', 'telephone')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rendre les champs de mot de passe optionnels car ils seront générés automatiquement
        self.fields['password1'].required = False
        self.fields['password2'].required = False
        self.fields['password1'].widget.attrs.update({'style': 'display:none'})
        self.fields['password2'].widget.attrs.update({'style': 'display:none'})

class CustomUserChangeForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'role', 'unite', 'section', 'telephone', 'is_active']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'section': forms.Select(attrs={'class': 'form-select'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Personnaliser les labels si nécessaire
        self.fields['is_active'].label = "Compte actif"

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['email', 'telephone', 'photo_profil']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'photo_profil': forms.FileInput(attrs={'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['photo_profil'].required = False

class CustomPasswordChangeForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})

class AdherantForm(forms.ModelForm):
    class Meta:
        model = Adherant
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe',
            'situation_matrimoniale', 'residence', 'niveau_etude', 'competences',
            'date_integration', 'numero', 'numero_parent', 'unite', 'situation',
            'motif', 'motivation', 'religion', 'photo'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de naissance'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'situation_matrimoniale': forms.Select(attrs={'class': 'form-select'}),
            'residence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse de résidence'}),
            'niveau_etude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Niveau d\'étude'}),
            'competences': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Compétences séparées par des virgules'}),
            'date_integration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'}),
            'numero_parent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro du parent'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'situation': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motif d\'adhésion'}),
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Motivations personnelles'}),
            'religion': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero_parent': 'Numéro du parent (optionnel)',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Ajouter des classes CSS aux champs
        for field_name, field in self.fields.items():
            if field_name not in ['photo']:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'
    
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero and len(numero) != 8:
            raise forms.ValidationError("Le numéro doit contenir exactement 8 caractères.")
        return numero
    
    def clean_numero_parent(self):
        numero_parent = self.cleaned_data.get('numero_parent')
        if numero_parent and len(numero_parent) != 8:
            raise forms.ValidationError("Le numéro parent doit contenir exactement 8 caractères.")
        return numero_parent

class PreinscriptionForm(forms.ModelForm):
    class Meta:
        model = Preinscription
        fields = [
            'nom', 'prenom', 'date_naissance', 'lieu_naissance', 'sexe',
            'situation_matrimoniale', 'residence', 'niveau_etude', 'competences',
            'date_integration', 'numero', 'numero_parent', 'unite', 'situation',
            'motif', 'motivation', 'religion', 'photo'
        ]
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de famille'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Prénom'}),
            'date_naissance': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'lieu_naissance': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Lieu de naissance'}),
            'sexe': forms.Select(attrs={'class': 'form-select'}),
            'situation_matrimoniale': forms.Select(attrs={'class': 'form-select'}),
            'residence': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Adresse de résidence'}),
            'niveau_etude': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Niveau d\'étude (optionnel)'}),
            'competences': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Compétences séparées par des virgules (optionnel)'}),
            'date_integration': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'numero': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'}),
            'numero_parent': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro du parent'}),
            'unite': forms.Select(attrs={'class': 'form-select'}),
            'situation': forms.Select(attrs={'class': 'form-select'}),
            'motif': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Motif d\'adhésion (optionnel)'}),
            'motivation': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Pourquoi souhaitez-vous rejoindre?'}),
            'religion': forms.Select(attrs={'class': 'form-select'}),
            'photo': forms.FileInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'numero_parent': 'Numéro du parent (optionnel)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if field_name not in ['photo']:
                field.widget.attrs['class'] = field.widget.attrs.get('class', '') + ' form-control'

    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero and len(numero) != 8:
            raise forms.ValidationError("Le numéro doit contenir exactement 8 caractères.")
        return numero

    def clean_numero_parent(self):
        numero_parent = self.cleaned_data.get('numero_parent')
        if numero_parent and len(numero_parent) != 8:
            raise forms.ValidationError("Le numéro parent doit contenir exactement 8 caractères.")
        return numero_parent

    def clean(self):
        cleaned_data = super().clean()
        nom = cleaned_data.get('nom')
        prenom = cleaned_data.get('prenom')
        date_naissance = cleaned_data.get('date_naissance')
        lieu_naissance = cleaned_data.get('lieu_naissance')

        if nom and prenom and date_naissance and lieu_naissance:
            duplicate_exists = Adherant.objects.filter(
                nom__iexact=nom.strip(),
                prenom__iexact=prenom.strip(),
                date_naissance=date_naissance,
                lieu_naissance__iexact=lieu_naissance.strip(),
            )
            if self.instance.pk:
                duplicate_exists = duplicate_exists.exclude(pk=self.instance.pk)
            if duplicate_exists.exists():
                raise ValidationError("Un adhérent avec ces informations existe déjà.")

        return cleaned_data

