from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile, Incident
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

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
            match = User.objects.get(email=email)
        except User.DoesNotExist:
            return email
        raise forms.ValidationError('This email address is already in use.')

# --- Profile forms ---
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('role', 'contact_number', 'location')

class ProfileUpdateForm(forms.ModelForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'readonly':'readonly'}))
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

class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('role', 'contact_number', 'location')
