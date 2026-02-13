from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def envoyer_email_inscription(utilisateur):
    """📧 Email de confirmation d'inscription (compte en attente)"""
    sujet = "⏳ Votre compte est en attente d'approbation"
    message = f"""
    Bonjour {utilisateur.username},
    
    Votre compte a été créé avec succès en tant que {utilisateur.get_statut_display()}.
    
    🔐 Un administrateur va approuver votre compte dans les plus brefs délais.
    Vous recevrez un email de confirmation dès que votre compte sera actif.
    
    📅 Vous pourrez alors réserver des salles de conférence.
    
    Cordialement,
    Service de réservation
    """
    
    send_mail(
        sujet,
        message,
        settings.EMAIL_HOST_USER,
        [utilisateur.email],
        fail_silently=True,
    )

def envoyer_email_validation(reservation):
    """📧 Email de validation de réservation"""
    sujet = "✅ Votre réservation a été validée"
    message = f"""
    Bonjour {reservation.utilisateur.username},
    
    Votre réservation pour {reservation.salle.nom} a été VALIDÉE !
    
    📅 Date : {reservation.date}
    ⏰ Horaire : {reservation.heure_debut} - {reservation.heure_fin}
    📍 Salle : {reservation.salle.nom} - {reservation.salle.localisation}
    
    Merci d'utiliser notre service de réservation.
    
    Cordialement,
    Service de réservation
    """
    
    send_mail(
        sujet,
        message,
        settings.EMAIL_HOST_USER,
        [reservation.utilisateur.email],
        fail_silently=True,
    )