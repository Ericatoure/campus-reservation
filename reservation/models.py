from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import EmailValidator
from django.utils import timezone

# 👑 MODÈLE UTILISATEUR PERSONNALISÉ
class Utilisateur(AbstractUser):
    STATUT_CHOICES = [
        ('delegue', 'Délégué'),
        ('enseignant', 'Enseignant'),
        ('administrateur', 'Administrateur'),
    ]
    
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='delegue')
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    telephone = models.CharField(max_length=15, blank=True)
    est_approuve = models.BooleanField(default=False)  # 🔐 Compte en attente
    date_inscription = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.get_statut_display()}) - {'✅ Approuvé' if self.est_approuve else '⏳ En attente'}"

class Salle(models.Model):
    nom = models.CharField(max_length=100)
    capacite = models.IntegerField()
    localisation = models.CharField(max_length=200)
    equipements = models.TextField()
    est_disponible = models.BooleanField(default=True)  # 🟢 Pour désactiver une salle

    def __str__(self):
        return self.nom

class Reservation(models.Model):
    STATUT_CHOIX = [
        ('En attente', 'En attente'),
        ('Validée', 'Validée'),
        ('Refusée', 'Refusée'),
        ('Terminée', 'Terminée'),  # ✅ Pour l'historique
    ]

    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE)  # 🔥 Utilisateur personnalisé
    date = models.DateField()
    heure_debut = models.TimeField()
    heure_fin = models.TimeField()
    statut = models.CharField(
        max_length=20,
        choices=STATUT_CHOIX,
        default='En attente'
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_traitement = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.salle.nom} - {self.date} ({self.statut})"