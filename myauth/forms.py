from django import forms
from django.core.exceptions import ValidationError
import re

class Registration(forms.Form):
    fname = forms.CharField(max_length=20,label='First Name', required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    lname = forms.CharField(max_length=20,label='Last Name', required=True,widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))
    email = forms.EmailField(max_length=30, required=True,widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    password = forms.CharField(max_length=30, required=True,  widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    confirm_password = forms.CharField(max_length=30, required=True,widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'}))

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one digit.")
        if not re.search(r'[A-Z]', password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data


class Login(forms.Form):
    email = forms.EmailField(max_length=30,  widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'}))
    password = forms.CharField(max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        return password
