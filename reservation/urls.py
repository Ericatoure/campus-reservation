from django.urls import path
from . import views

app_name = 'reservation'

urlpatterns = [
    # 📝 Authentification
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    
    # 🏠 Utilisateur standard
    path('', views.accueil, name='accueil'),
    path('mes-reservations/', views.mes_reservations, name='mes_reservations'),
    path('annuler/<int:reservation_id>/', views.annuler_reservation, name='annuler_reservation'),
    
    # 👑 Administrateur
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
]