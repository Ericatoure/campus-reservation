from django.contrib import admin
from django.contrib import messages
from django.contrib.auth.admin import UserAdmin
from django.db.models import Q
from django.utils.html import format_html
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Utilisateur, Salle, Reservation

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'email', 'statut', 'est_approuve', 'date_inscription']
    list_filter = ['statut', 'est_approuve']
    search_fields = ['username', 'email']
    actions = ['approuver_comptes']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Infos', {'fields': ('statut', 'telephone', 'est_approuve')}),
    )
    
    def approuver_comptes(self, request, queryset):
        queryset.update(est_approuve=True)
        self.message_user(request, f"✅ {queryset.count()} compte(s) approuvé(s)")
    approuver_comptes.short_description = "Approuver les comptes"

@admin.register(Salle)
class SalleAdmin(admin.ModelAdmin):
    list_display = ['nom', 'capacite', 'localisation', 'equipements', 'est_disponible']
    list_filter = ['est_disponible']
    search_fields = ['nom']
    list_editable = ['est_disponible']

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['salle', 'utilisateur', 'date', 'heure_debut', 'heure_fin', 'statut']
    list_filter = ['statut', 'date', 'salle']
    search_fields = ['utilisateur__username', 'salle__nom']
    actions = ['valider_reservations', 'refuser_reservations']
    list_editable = ['statut']
    
    def valider_reservations(self, request, queryset):
        for resa in queryset:
            conflits = Reservation.objects.filter(
                salle=resa.salle,
                date=resa.date,
                statut="Validée",
            ).filter(
                Q(heure_debut__lt=resa.heure_fin, 
                  heure_fin__gt=resa.heure_debut)
            ).exclude(pk=resa.pk)
            
            if not conflits.exists():
                resa.statut = "Validée"
                resa.save()
        self.message_user(request, f"✅ Réservation(s) validée(s)")
    valider_reservations.short_description = "Valider"
    
    def refuser_reservations(self, request, queryset):
        queryset.update(statut="Refusée")
        self.message_user(request, f"❌ Réservation(s) refusée(s)")
    refuser_reservations.short_description = "Refuser"