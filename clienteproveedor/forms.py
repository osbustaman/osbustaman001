#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, Select, PasswordInput, Textarea, HiddenInput, NumberInput, DateInput

import datetime
from _datetime import date

from clienteproveedor.models import ClienteProveedor, ClienteProveedorEmpresa
from configuracion.models import TablaGeneral
from jab.views import calculo_digito_verificador
from usuario.models import Pais, Region, Comuna, Empresa, Bancos


class ClienteProveedorForm(ModelForm):
    cp_rut = forms.CharField(label="Rut",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_razonsocial = forms.CharField(label="Razón social",
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_nombrefantasia = forms.CharField(label="Nombre de fantasía",
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_giro = forms.CharField(label="Giro",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_direccion = forms.CharField(label="Calle",
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_numero = forms.IntegerField(label="N°",
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_piso = forms.CharField(label="Piso",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                              required=False)
    cp_dptooficina = forms.CharField(label="Departamento/oficina",
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                     required=False)
    pais = forms.ModelChoiceField(label="País", queryset=Pais.objects.all(), to_field_name='pa_id',
                                  widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    region = forms.ModelChoiceField(label="Región", queryset=Region.objects.all(), to_field_name='re_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    comuna = forms.ModelChoiceField(label="Comuna", queryset=Comuna.objects.all(), to_field_name='com_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    cp_email = forms.EmailField(label="Email",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_comentario = forms.CharField(label="Comentario",
                                    widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                    required=False)
    cp_estado = forms.ChoiceField(label="Activo", choices=ClienteProveedor.OPCIONES,
                                  widget=forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cp_fono = forms.CharField(label="teléfono", widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-inputmask': '"mask": "9-9999-9999"', 'data-mask': '',
               'autocomplete': 'off'}), required=False)
    cp_tipoentidad = forms.ChoiceField(label="Tipo de entidad", choices=ClienteProveedor.TIPO_ENTIDAD,
                                       widget=forms.Select(
                                           attrs={'class': 'form-control select2', 'style': 'width: 100%'}))

    def clean(self, *args, **kwargs):
        cp_rut = self.cleaned_data.get('cp_rut')

        x_username = cp_rut.split('-')

        dv_rut = calculo_digito_verificador(cp_rut)
        if not str(dv_rut).lower() == str(x_username[1]).lower():
            self.add_error('cp_rut', "Rut no valido")

    class Meta:
        model = ClienteProveedor
        fields = [
            'cp_rut',
            'cp_razonsocial',
            'cp_nombrefantasia',
            'cp_giro',
            'cp_direccion',
            'cp_numero',
            'cp_piso',
            'cp_dptooficina',
            'pais',
            'region',
            'comuna',
            'cp_email',
            'cp_comentario',
            'cp_estado',
            'cp_fono',
            'cp_tipoentidad',
        ]


class ClienteProveedorEmpresaForm(ModelForm):
    empresa = forms.ModelChoiceField(label="Empresa", queryset=Empresa.objects.all(), to_field_name='emp_id',
                                     widget=forms.Select(
                                         attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    # ----
    cpe_tipocliente = forms.ChoiceField(label="Tipo de Cliente", choices=ClienteProveedorEmpresa.TIPO_CLI_CHOICES,
                                        widget=forms.Select(
                                            attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
                                        required=False)
    # ----
    cpe_tipoproveedor = forms.ChoiceField(label="Tipo de Proveedor", choices=ClienteProveedorEmpresa.TIPO_PROV_CHOICES,
                                          widget=forms.Select(
                                              attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
                                          required=False)
    # cpe_plazopago       = forms.IntegerField(label="Plazo de pago proveedor", widget=forms.Select(attrs={'class': 'form-control select2', 'autocomplete': 'off'}), required=False)
    cpe_plazopago = forms.ModelChoiceField(label="Plazo de pago proveedor", queryset=TablaGeneral.objects.filter(
        tg_nomtabla='vencimiento_tipo_cliente').exclude(tg_estado='A'), to_field_name='tg_id', widget=forms.Select(
        attrs={'class': 'form-control select2', 'autocomplete': 'off'}), required=False)
    # ----
    # cpe_vencimiento     = forms.IntegerField(label="Vencimiento cliente", widget=forms.Select(attrs={'class': 'form-control', 'autocomplete': 'off'}), required=False)
    cpe_vencimiento = forms.ModelChoiceField(label="Vencimiento cliente", queryset=TablaGeneral.objects.filter(
        tg_nomtabla='vencimiento_tipo_proveedor').exclude(tg_estado='A'), to_field_name='tg_id', widget=forms.Select(
        attrs={'class': 'form-control select2', 'autocomplete': 'off'}), required=False)
    # ----
    banco = forms.ModelChoiceField(label="Banco", queryset=Bancos.objects.all(), to_field_name='ban_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    cpe_tipocuenta = forms.ChoiceField(label="Tipo de Cuenta", choices=ClienteProveedorEmpresa.TIPO_CTA_CHOICES,
                                       widget=forms.Select(
                                           attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
                                       required=False)
    cpe_ctacorriente = forms.CharField(label="Número de cuenta corriente",
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cpe_credautorizado = forms.DecimalField(label="Crédito autorizado",
                                            widget=forms.NumberInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ClienteProveedorEmpresa
        fields = [
            'empresa',
            'cpe_tipocliente',
            'cpe_tipoproveedor',
            'cpe_plazopago',
            'cpe_vencimiento',
            'banco',
            'cpe_tipocuenta',
            'cpe_ctacorriente',
            'cpe_credautorizado',
        ]
