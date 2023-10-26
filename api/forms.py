# forms.py
from django import forms
from .models import Application, User
from django.contrib.auth.forms import UserCreationForm

class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = '__all__'  # You can specify specific fields if needed

class AuthenticationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = '__all__'  # You can specify specific fields if needed

class CustomUserAdminForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2')