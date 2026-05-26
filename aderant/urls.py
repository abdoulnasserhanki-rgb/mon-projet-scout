from django.urls import path
from . import views
from .views import AdherantListView, AdherantCreateView, Accueil

urlpatterns = [
    # Authentication URLs
    path('accounts/login/', views.custom_login, name='login'),
    path('accounts/logout/', views.custom_logout, name='logout'),
    path('accounts/change-password-required/', views.change_password_required, name='change_password_required'),
    
    path('', views.Accueil, name='accueil'),
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/<int:user_id>/edit/', views.user_edit, name='user_edit'),
    path('users/<int:user_id>/reset-password/', views.user_reset_password, name='user_reset_password'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/export/all/', views.export_users_csv, name='export_users_all'),
    # URLs de profil utilisateur
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/change-password/', views.change_password, name='change_password'),
    
    path('list/', views.AdherantListView, name='adherant_list'),
    path('new/', AdherantCreateView.as_view(), name='adherant_create'),
    path('adherant/<int:adherant_id>/', views.adherant_detail, name='adherant_detail'),
    path('adherant/<int:adherant_id>/export/', views.export_adherant_detail_csv, name='export_adherant_detail'),
    path('export/all/', views.export_adherants_csv, name='export_adherants_all'),
    path('preinscription/', views.preinscription_create, name='preinscription_create'),
    path('preinscription/pending/', views.preinscription_list, name='preinscription_list'),
    path('preinscription/<int:preinscription_id>/approve/', views.preinscription_approve, name='preinscription_approve'),
]