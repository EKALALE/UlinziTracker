from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Incident
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

# --- Role choices (keep in sync with Profile model) ---
ROLE_CHOICES = [
    ('resident', 'Resident'),
    ('officer', 'Officer'),
    ('chief', 'Chief'),
    ('authority', 'Authority'),
    ('admin', 'Admin'),
]

# --- Incident form ---
class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'category', 'location', 'image', 'video', 'audio', 'document']

# --- Incident status update form ---
class StatusUpdateForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ('status',)
        help_texts = {
            'status': None,
        }

# --- User registration form ---
class UserRegisterForm(UserCreationForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')

# --- Initial profile form used at registration ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('role', 'contact_number', 'location')

# --- User account update form (for User model) ---
# Matches views.py usage: p_form = ProfileUpdateForm(instance=request.user)
class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly': 'readonly'}))
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        try:
            User.objects.exclude(pk=self.instance.pk).get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')

# --- Profile update form (for Profile model) ---
# Matches views.py usage: profile_update_form = UserProfileUpdateForm(instance=profile, user=request.user)
# By default excludes 'role' for non-admins; includes role for superusers only.
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['contact_number', 'location']  # exclude 'role' by default

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user and user.is_superuser:
            self.fields['role'] = forms.ChoiceField(choices=ROLE_CHOICES)
