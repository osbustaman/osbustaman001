#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, Select, PasswordInput, Textarea, HiddenInput, NumberInput, DateInput, \
    FileField
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from configuracion.models import Parametros, Moneda
from documento.models import TipoDocumentos

from usuario.models import Empresa, Pais, Region, Comuna, Cargo, CentroCosto, Afp, Salud, Bancos

import datetime
from _datetime import date


class ParametrosForm(ModelForm):
    param_codigo = forms.CharField(label="Código", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': 'autofocus', 'autocomplete': 'off'}))
    param_descripcion = forms.CharField(label="Descripción",
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    param_valor = forms.CharField(label="Valor", initial='0',
                                  widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    param_rangoini = forms.DecimalField(label="Rango inicial", initial='0',
                                        widget=forms.NumberInput(
                                            attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                        required=False)
    param_rangofin = forms.DecimalField(label="Rango final", initial='0',
                                        widget=forms.NumberInput(
                                            attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                        required=False)
    param_factor = forms.CharField(label="Factor", initial='0',
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                   required=False)
    param_activo = forms.ChoiceField(label="Activo?", choices=Parametros.OPCIONES, initial='S',
                                     widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = Parametros
        fields = [
            'param_codigo',
            'param_descripcion',
            'param_rangoini',
            'param_rangofin',
            'param_valor',
            'param_factor',
            'param_activo',
        ]


class ExportadorForm(forms.Form):
    archivo = forms.FileField(label="Archivo a importar", widget=forms.FileInput(
        attrs={'class': 'filestyle col-md-12 col-sm-12 col-xs-12', 'data-buttonText': 'Buscar archivo',
               'data-placeholder': 'Sin archivos...', 'data-iconName': 'fa fa-file-excel-o'}))

    class Meta:
        fields = [
            'archivo'
        ]

    def clean_archivo(self):
        file = self.cleaned_data['archivo']

        if not file.name.endswith('.csv'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .csv ")


class CamposExtrasForm(forms.Form):
    pais = forms.ModelChoiceField(label='País', queryset=Pais.objects.all(), to_field_name='pa_id', widget=forms.Select(
        attrs={'class': 'form-control select2', 'style': 'width: 100%', 'onchange': 'buscar_id(this)'}))
    region = forms.ModelChoiceField(label='Región', queryset=Region.objects.all(), to_field_name='re_id',
                                    widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                               'onchange': 'buscar_id(this)'}))
    comuna = forms.ModelChoiceField(label='Comuna', queryset=Comuna.objects.all(), to_field_name='com_id',
                                    widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                               'onchange': 'buscar_id(this)'}))
    cargo = forms.ModelChoiceField(label='Cargo', queryset=Cargo.objects.all(), to_field_name='car_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                              'onchange': 'buscar_id(this)'}))
    centrocosto = forms.ModelChoiceField(label='Centro de costo', queryset=CentroCosto.objects.all(),
                                         to_field_name='cencost_id', widget=forms.Select(
            attrs={'class': 'form-control select2', 'style': 'width: 100%', 'onchange': 'buscar_id(this)'}))
    afp = forms.ModelChoiceField(label='Afp', queryset=Afp.objects.all(), to_field_name='afp_id', widget=forms.Select(
        attrs={'class': 'form-control select2', 'style': 'width: 100%', 'onchange': 'buscar_id(this)'}))
    salud = forms.ModelChoiceField(label='Salud', queryset=Salud.objects.all(), to_field_name='sa_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                              'onchange': 'buscar_id(this)'}))
    banco = forms.ModelChoiceField(label='Banco', queryset=Bancos.objects.all(), to_field_name='ban_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                              'onchange': 'buscar_id(this)'}))


class CargaLogoEmpresaForm(forms.Form):
    cac_rutabase = forms.CharField(label="Ruta base de la aplicación", widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': True, 'disabled': True}), required=False)
    cac_rutadocumentos = forms.CharField(label="Ruta base de los doscumentos", widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': True, 'disabled': True}), required=False)
    cac_rutausuarios = forms.CharField(label="Ruta carpeta de usuarios", widget=forms.TextInput(
        attrs={'class': 'form-control', 'readonly': True, 'disabled': True}), required=False)

    archivo = forms.FileField(label="Logo de la empresa a importar", widget=forms.FileInput(
        attrs={'class': 'filestyle col-md-12 col-sm-12 col-xs-12', 'data-buttonText': 'Buscar imagen',
               'data-placeholder': 'Sin imagen...', 'data-iconName': 'fa fa-file-image-o'}))

    class Meta:
        fields = [
            'archivo',
            'cac_rutabase',
            'cac_rutadocumentos',
            'cac_rutausuarios',
        ]

    def clean_archivo(self):
        file = self.cleaned_data['archivo']

        if not file.name.endswith('.jpg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")

        if not file.name.endswith('.jpeg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")

        if not file.name.endswith('.png'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")


class CargaLogoPorEmpresaForm(forms.Form):

    archivo = forms.FileField(label="Buscar logo", widget=forms.FileInput(
        attrs={'class': 'filestyle col-md-12 col-sm-12 col-xs-12', 'data-buttonText': 'Buscar imagen',
               'data-placeholder': 'Sin imagen...', 'data-iconName': 'fa fa-file-image-o'}))

    class Meta:
        fields = [
            'archivo',
        ]

    def clean_archivo(self):
        file = self.cleaned_data['archivo']

        if not file.name.endswith('.jpg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")

        if not file.name.endswith('.jpeg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")

        if not file.name.endswith('.png'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .jpg/.jpeg, .png ")


class MonedaForm(ModelForm):
    mon_id = forms.CharField(label="ID moneda",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    mon_simbolo = forms.CharField(label="Simbolo",
                                  widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    mon_cantidaddecimales = forms.ChoiceField(label="Cantidad de decimales", initial='0',
                                              choices=Moneda.CANTIDAD_DECIMALES, widget=forms.Select(
            attrs={'class': 'form-control', 'autocomplete': 'off'}))
    mon_descripcion = forms.CharField(label="Nombre",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    class Meta:
        model = Moneda
        fields = [
            'mon_id',
            'mon_simbolo',
            'mon_cantidaddecimales',
            'mon_descripcion',
        ]
