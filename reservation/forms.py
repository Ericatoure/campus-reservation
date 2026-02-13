from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.db.models import Q
from django.utils import timezone
from .models import Utilisateur, Reservation, Salle

# 📝 FORMULAIRE D'INSCRIPTION - À AJOUTER !
class InscriptionForm(UserCreationForm):
    class Meta:
        model = Utilisateur
        fields = ['username', 'email', 'first_name', 'last_name', 'telephone', 'statut', 'password1', 'password2']
        widgets = {
            'statut': forms.RadioSelect(choices=Utilisateur.STATUT_CHOICES),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['statut'].initial = 'delegue'
        self.fields['email'].required = True
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
        self.fields['statut'].widget.attrs.update({'class': 'form-check-input'})

# 🔐 FORMULAIRE DE CONNEXION
class ConnexionForm(AuthenticationForm):
    username = forms.CharField(label="Nom d'utilisateur", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(label="Mot de passe", widget=forms.PasswordInput(attrs={'class': 'form-control'}))

# 📅 FORMULAIRE DE RÉSERVATION
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['salle', 'date', 'heure_debut', 'heure_fin']
        widgets = {
            'date': forms.DateInput(
                attrs={
                    'type': 'date',
                    'min': timezone.now().date().isoformat(),
                    'class': 'form-control'
                }
            ),
            'heure_debut': forms.Select(
                choices=[(f"{h:02d}:00", f"{h:02d}:00") for h in range(8, 20)],
                attrs={'class': 'form-control'}
            ),
            'heure_fin': forms.Select(
                choices=[(f"{h:02d}:00", f"{h:02d}:00") for h in range(9, 21)],
                attrs={'class': 'form-control'}
            ),
            'salle': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'salle': 'Choisissez une salle',
            'date': 'Date de la réservation',
            'heure_debut': 'Heure de début',
            'heure_fin': 'Heure de fin',
        }
    
    def __init__(self, *args, **kwargs):
        self.utilisateur = kwargs.pop('utilisateur', None)
        super().__init__(*args, **kwargs)
        self.fields['salle'].queryset = Salle.objects.filter(est_disponible=True)
    
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        heure_debut = cleaned_data.get('heure_debut')
        heure_fin = cleaned_data.get('heure_fin')
        salle = cleaned_data.get('salle')
        
        if date and date < timezone.now().date():
            raise forms.ValidationError("❌ Vous ne pouvez pas réserver une date passée.")
        
        if heure_debut and heure_fin and heure_debut >= heure_fin:
            raise forms.ValidationError("❌ L'heure de fin doit être après l'heure de début.")
        
        if all([date, heure_debut, heure_fin, salle]):
            conflits = Reservation.objects.filter(
                salle=salle,
                date=date,
                statut__in=['En attente', 'Validée']
            ).filter(
                Q(heure_debut__lt=heure_fin, heure_fin__gt=heure_debut)
            )
            
            if conflits.exists():
                raise forms.ValidationError(
                    f"❌ La salle {salle.nom} est déjà réservée sur ce créneau."
                )
        
        return cleaned_data