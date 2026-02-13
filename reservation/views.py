from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q
from .models import Utilisateur, Salle, Reservation
from .forms import InscriptionForm, ConnexionForm, ReservationForm
from .utils import envoyer_email_inscription  # ⚠️ À créer

# 📝 PAGE D'INSCRIPTION
def inscription(request):
    if request.method == 'POST':
        form = InscriptionForm(request.POST)
        if form.is_valid():
            utilisateur = form.save(commit=False)
            utilisateur.est_approuve = False  # 🔐 Compte en attente
            utilisateur.save()
            
            # 📧 Email de confirmation
            try:
                envoyer_email_inscription(utilisateur)
            except:
                pass
            
            messages.success(
                request, 
                '✅ Inscription réussie ! Votre compte est en attente d\'approbation par un administrateur.'
            )
            return redirect('reservation:connexion')  # ✅ CORRIGÉ
    else:
        form = InscriptionForm()
    
    return render(request, 'reservation/inscription.html', {'form': form})

# 🔐 PAGE DE CONNEXION
def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                # 🔐 Vérifier si le compte est approuvé
                if not user.est_approuve:
                    messages.error(
                        request,
                        '⏳ Votre compte est en attente d\'approbation par un administrateur.'
                    )
                    return redirect('reservation:connexion')  # ✅ CORRIGÉ
                
                login(request, user)
                messages.success(request, f'✅ Bienvenue {user.username}!')
                
                # 👑 Redirection selon le statut
                if user.statut == 'administrateur':
                    return redirect('reservation:admin_dashboard')  # ✅ CORRIGÉ
                else:
                    return redirect('reservation:accueil')  # ✅ CORRIGÉ
    else:
        form = ConnexionForm()
    
    return render(request, 'reservation/connexion.html', {'form': form})

# 🚪 DÉCONNEXION
def deconnexion(request):
    logout(request)
    messages.success(request, '👋 Vous avez été déconnecté')
    return redirect('reservation:connexion')  # ✅ CORRIGÉ

# 🏠 PAGE D'ACCUEIL (RÉSERVATION) - PROTÉGÉE
@login_required
def accueil(request):
    # 🔐 Vérifier que l'utilisateur est approuvé
    if not request.user.est_approuve:
        messages.error(request, '⏳ Votre compte n\'est pas encore approuvé')
        return redirect('reservation:connexion')  # ✅ CORRIGÉ
    
    salles = Salle.objects.filter(est_disponible=True)
    reservations_utilisateur = Reservation.objects.filter(
        utilisateur=request.user
    ).order_by('-date', '-heure_debut')[:5]  # 5 dernières réservations
    
    if request.method == 'POST':
        form = ReservationForm(request.POST, utilisateur=request.user)
        if form.is_valid():
            reservation = form.save(commit=False)
            reservation.utilisateur = request.user
            reservation.statut = "En attente"
            reservation.save()
            
            messages.success(
                request,
                f"✅ Votre réservation pour {reservation.salle.nom} "
                f"le {reservation.date} de {reservation.heure_debut} à {reservation.heure_fin} "
                f"a été enregistrée ! Statut : En attente de validation."
            )
            return redirect('reservation:accueil')  # ✅ CORRIGÉ
    else:
        form = ReservationForm(utilisateur=request.user)
    
    return render(request, 'reservation/accueil.html', {
        'salles': salles,
        'form': form,
        'reservations': reservations_utilisateur
    })

# 📋 MES RÉSERVATIONS
@login_required
def mes_reservations(request):
    if not request.user.est_approuve:
        return redirect('reservation:connexion')  # ✅ CORRIGÉ
    
    reservations = Reservation.objects.filter(
        utilisateur=request.user
    ).order_by('-date', '-heure_debut')
    
    return render(request, 'reservation/mes_reservations.html', {
        'reservations': reservations
    })

# ❌ ANNULER UNE RÉSERVATION
@login_required
def annuler_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id, utilisateur=request.user)
    
    if reservation.statut == 'En attente':
        reservation.statut = 'Terminée'
        reservation.save()
        messages.success(request, '✅ Réservation annulée avec succès')
    else:
        messages.error(request, '❌ Impossible d\'annuler cette réservation')
    
    return redirect('reservation:mes_reservations')  # ✅ CORRIGÉ

# 👑 DASHBOARD ADMIN
@login_required
def admin_dashboard(request):
    # Vérifier que c'est bien un administrateur
    if request.user.statut != 'administrateur':
        messages.error(request, '⛔ Accès non autorisé')
        return redirect('reservation:accueil')  # ✅ CORRIGÉ
    
    # Statistiques
    total_utilisateurs = Utilisateur.objects.count()
    utilisateurs_en_attente = Utilisateur.objects.filter(est_approuve=False).count()
    reservations_en_attente = Reservation.objects.filter(statut='En attente').count()
    reservations_validees = Reservation.objects.filter(statut='Validée').count()
    total_salles = Salle.objects.count()
    
    # Listes
    utilisateurs_non_approuves = Utilisateur.objects.filter(est_approuve=False)[:10]
    reservations_a_traiter = Reservation.objects.filter(statut='En attente').order_by('date')[:10]
    
    context = {
        'total_utilisateurs': total_utilisateurs,
        'utilisateurs_en_attente': utilisateurs_en_attente,
        'reservations_en_attente': reservations_en_attente,
        'reservations_validees': reservations_validees,
        'total_salles': total_salles,
        'utilisateurs_non_approuves': utilisateurs_non_approuves,
        'reservations_a_traiter': reservations_a_traiter,
    }
    return render(request, 'reservation/admin_dashboard.html', context)