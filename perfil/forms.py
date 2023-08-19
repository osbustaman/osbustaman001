# -*- encoding: utf-8 -*-
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from .models import Perfil

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(max_length=140, required=True)
    last_name = forms.CharField(max_length=140, required=False)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = (
            'username',
            'email',
            'first_name',
            'last_name',
            'password1',
            'password2',
        )


class LoginForm(AuthenticationForm):
    username     = forms.CharField(widget=forms.DateInput(attrs={"class": "form-control", "placeholder": "Nombre usuario", "autofocus": "autofocus", "autocomplete":"off"},), required=True)
    password     = forms.CharField(widget=forms.PasswordInput(attrs={"class": "form-control", "placeholder": "Clave"},), required=False)

    class Meta:
        model = User
        fields = (
            'username',
            'password'
        )