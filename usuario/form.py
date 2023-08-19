#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, Select, PasswordInput, Textarea, HiddenInput, NumberInput, DateInput
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from usuario.models import Usuario, Pais, Region, Comuna, Haberes


class UsuarioForm(ModelForm):
    usu_tiporut = forms.ChoiceField(initial=1, label="Tipo de rut", choices=Usuario.TIPO_RUT,
                                    widget=forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    usu_sexo = forms.ChoiceField(initial='M', label="Sexo", choices=Usuario.SEXO,
                                 widget=forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    usu_fono = forms.CharField(label="Teléfono", widget=forms.TextInput(
        attrs={'class': 'form-control ', 'data-inputmask': '"mask": "9-9999-9999"', 'data-mask': ''}))
    usu_fechanacimiento = forms.DateField(input_formats=["%d/%m/%Y"], label="Fecha de nacimiento",
                                          widget=forms.DateInput(format="%d/%m/%Y",
                                                                 attrs={'class': 'form-control pull-right',
                                                                        'placeholder': 'Ej: 31/12/1999'}))

    pais = forms.ModelChoiceField(queryset=Pais.objects.all(), label='Pais', to_field_name='pa_id',
                                  required=False,
                                  widget=forms.Select(attrs={'class': 'form-control  select2', 'style': 'width: 100%'}))
    region = forms.ModelChoiceField(queryset=Region.objects.all(), label='Region', to_field_name='re_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all(), label='Comuna', to_field_name='com_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    usu_direccion = forms.CharField(label="Dirección",
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    usu_estadocivil = forms.ChoiceField(initial='A', label="Estado civil", choices=Usuario.ESTADO_CIVIL,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    usu_usuarioactivo = forms.ChoiceField(initial='S', label="Estado del empleado", choices=Usuario.ESTADO_USUARIO,
                                          widget=forms.Select(attrs={'class': 'form-control'}))
    usu_profesion = forms.CharField(label="Profesión",
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    usu_paisextranjeros = forms.CharField(label="País extranjero",
                                          widget=forms.TextInput(
                                              attrs={'class': 'form-control', 'autocomplete': 'off'}), required=False)

    usu_licenciaconducir = forms.ChoiceField(initial='N', label="Licencia de conducir", choices=Usuario.OPCIONES,
                                             widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Usuario
        fields = [
            'usu_tiporut',
            'usu_rut',
            'usu_sexo',
            'usu_fono',
            'usu_fechanacimiento',
            'pais',
            'region',
            'comuna',
            'usu_direccion',
            'usu_estadocivil',
            'usu_usuarioactivo',
            'usu_profesion',
            'usu_licenciaconducir',
            'usu_paisextranjeros',
        ]


class CargaFotoUsuario(forms.Form):
    archivo = forms.FileField(label="Foto a importar", widget=forms.FileInput(
        attrs={'class': 'filestyle col-md-12 col-sm-12 col-xs-12', 'data-buttonText': 'Buscar imagen',
               'data-placeholder': 'Sin imagen...', 'data-iconName': 'fa fa-file-image-o'}))

    class Meta:
        fields = [
            'archivo'
        ]

    def clean_archivo(self):
        file = self.cleaned_data['archivo']

        if not file.name.endswith('.jpg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")

        if not file.name.endswith('.jpeg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")

        if not file.name.endswith('.png'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")


class HaberesForm(ModelForm):
    TIPO = (
        ('', '--- Seleccione ---'),
        ('HI', 'Haberes imponible'),
        ('HNI', 'Haberes no imponibles'),
    )

    hab_nombre = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control '}))
    hab_monto = forms.DecimalField(label='Monto', initial='0',
                                   widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    hab_tipo = forms.ChoiceField(initial='', label="Tipo haber", choices=TIPO,
                                 widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Haberes
        fields = [
            'hab_nombre',
            'hab_monto',
            'hab_tipo',
        ]


class HaberesDescuentosForm(ModelForm):
    hab_nombre = forms.CharField(label="Nombre", widget=forms.TextInput(attrs={'class': 'form-control '}))
    hab_monto = forms.DecimalField(label='Monto', initial='0',
                                   widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    hab_tipohaberdescuento = forms.ChoiceField(initial='', label="Haber/Descuento", choices=Haberes.FINIQUITO,
                                               widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Haberes
        fields = [
            'hab_nombre',
            'hab_monto',
            'hab_tipohaberdescuento',
        ]
