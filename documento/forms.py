#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, Select, PasswordInput, Textarea, HiddenInput, NumberInput, DateInput
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

import datetime

from clienteproveedor.models import ClienteProveedor
from configuracion.models import Moneda
from documento.models import Documento, DocumentoEmpleado, TipoDocumentos, DocumentoEmpresa, DocumentoEncabezado, \
    DocumentoEncabezadoDetalle

from usuario.models import Empresa


class DocumentoForm(ModelForm):
    doc_activo = forms.ChoiceField(label="Documento activo?", initial='', choices=Documento.OPCIONES,
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    doc_nombre = forms.CharField(label="Nombre documento",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    doc_texto = forms.CharField(label="Texto del documento",
                                widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    class Meta:
        model = Documento
        fields = [
            'doc_activo',
            'doc_nombre',
            'doc_texto',
        ]


class TipoDocumentosForm(ModelForm):
    tdl_codigo = forms.CharField(label="Código", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': True, 'autocomplete': 'off'}))
    tdl_descripcion = forms.CharField(label="Descripción", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': True, 'autocomplete': 'off'}))
    tdl_activo = forms.ChoiceField(label="Activo?", choices=TipoDocumentos.OPCIONES, initial='S',
                                   widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = TipoDocumentos
        fields = [
            'tdl_codigo',
            'tdl_descripcion',
            'tdl_activo',
        ]


class DocumentoEmpresaForm(ModelForm):
    documento = forms.ModelChoiceField(label='Documento', queryset=Documento.objects.all(), to_field_name='doc_id',
                                       widget=forms.Select(
                                           attrs={'class': 'form-control', 'style': 'width: 100%', 'disabled': True}))

    empresa = forms.ModelChoiceField(label='Empresa', queryset=Empresa.objects.all(), to_field_name='emp_id',
                                     widget=forms.Select(
                                         attrs={'class': 'form-control select2', 'style': 'width: 100%'}))

    class Meta:
        model = DocumentoEmpresa
        fields = [
            'documento',
            'empresa',
        ]


# INPUTS PARA FILTROS
class FiltroPorDocForm(forms.Form):
    tipoDocumentos = forms.ChoiceField(label="Activo?", choices=TipoDocumentos.FILTRO_DOCS, initial='DOC',
                                       widget=forms.Select(attrs={'class': 'form-control'}), required=False)


class SubirDocumentoForm(forms.Form):
    archivo = forms.FileField(label="Archivo a subir", widget=forms.FileInput(
        attrs={'class': 'filestyle col-md-12 col-sm-12 col-xs-12', 'data-buttonText': 'Buscar archivo',
               'data-placeholder': 'Sin archivos...', 'data-iconName': 'fa fa-file'}), required=False)

    class Meta:
        fields = [
            'archivo'
        ]

    def clean_archivo(self):
        file = self.cleaned_data['archivo']

        if not file.name.endswith('.pdf'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .pdf .jpg .jpeg .png")

        if not file.name.endswith('.jpg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .pdf .jpg .jpeg .png")

        if not file.name.endswith('.jpeg'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .pdf .jpg .jpeg .png")

        if not file.name.endswith('.png'):
            raise forms.ValidationError("Sólo está permitido importar archivos tipo .pdf .jpg .jpeg .png")


class DocumentoEncabezadoForm(ModelForm):
    docenc_numerodoc = forms.IntegerField(label="N° de documento",
                                          widget=forms.NumberInput({'class': 'form-control', 'autocomplete': 'off'}))
    clienteProveedor = forms.IntegerField(label='Cliente/Proveedor', widget=forms.HiddenInput(
        attrs={'class': 'form-control', 'style': 'width: 100%'}))
    docenc_fechaemision = forms.CharField(label="Fecha de emisión",
                                          widget=forms.TextInput(attrs={'class': 'form-control', }))
    docenc_fechavencimiento = forms.CharField(label="Fecha de vencimiento",
                                              widget=forms.TextInput(attrs={'class': 'form-control', }))
    docenc_tipodescuento = forms.ChoiceField(label="Tipo de descuento", choices=DocumentoEncabezado.TIPO_DESCUENTO,
                                             initial='M', widget=forms.Select(attrs={'class': 'form-control'}),
                                             required=False)
    docenc_descuento = forms.FloatField(label="Descuento", initial=0.00,
                                        widget=forms.NumberInput({'class': 'form-control', 'autocomplete': 'off'}))
    docenc_descripcionadicional = forms.CharField(label="Descripción adicional",
                                                  widget=forms.Textarea({'class': 'form-control', 'rows': '5'}),
                                                  required=False)

    def clean_docenc_fechavencimiento(self):

        """
        Validar fecha ue_fecharetiro
        """
        docenc_fechaemision = self.cleaned_data.get('docenc_fechaemision')
        docenc_fechavencimiento = self.cleaned_data.get('docenc_fechavencimiento')

        datefechaemision = datetime.datetime.strptime(docenc_fechaemision, '%Y-%m-%d')
        datefechavencimiento = datetime.datetime.strptime(docenc_fechavencimiento, '%Y-%m-%d')

        if datefechavencimiento < datefechaemision:
            self.add_error('docenc_fechavencimiento',
                           'La fecha de vencimiento no puede ser menor a la fecha de emisión')
            docenc_fechavencimiento = ""
        return docenc_fechavencimiento

    def clean_docenc_descripcionadicional(self):

        """
        Valida la cantidad de caracters
        """
        docenc_descripcionadicional = self.cleaned_data.get('docenc_descripcionadicional')

        if len(docenc_descripcionadicional) > 250:
            self.add_error('docenc_descripcionadicional',
                           'La cantidad de caracteres no es valida, puede agregar hasta 250 caracteres, el texto tiene {} caracteres.'.format(
                               len(docenc_descripcionadicional)))
            docenc_descripcionadicional = ""
        return docenc_descripcionadicional

    class Meta:
        model = DocumentoEncabezado
        fields = [
            'docenc_numerodoc',
            'docenc_fechaemision',
            'docenc_fechavencimiento',
            'docenc_tipodescuento',
            'docenc_tipodescuento',
            'docenc_descripcionadicional',
        ]


class DocumentoEncabezadoDetalleForm(ModelForm):
    docdet_numdetalle = forms.IntegerField(label="N° de detalle", widget=forms.NumberInput(
        {'class': 'form-control', 'autocomplete': 'off', 'readonly': True}))  #
    docdet_isiva = forms.ChoiceField(label="IVA", choices=DocumentoEncabezadoDetalle.OPCIONES, initial='N',
                                     widget=forms.Select(attrs={'class': 'form-control'}))  #
    docdet_cantidad = forms.DecimalField(label="Cantidad", initial=0,
                                         widget=forms.NumberInput({'class': 'form-control', 'autocomplete': 'off'}))  #
    docdet_producto = forms.CharField(label="Producto", widget=forms.TextInput(attrs={'class': 'form-control', }))  #
    docdet_preciounitario = forms.DecimalField(label="Precio unitario", initial=0, widget=forms.NumberInput(
        {'class': 'form-control', 'autocomplete': 'off'}))  #
    docdet_preciototal = forms.DecimalField(label="Total", initial=0, widget=forms.NumberInput(
        {'class': 'form-control', 'autocomplete': 'off', 'readonly': True}))
    docdet_tipodescuento = forms.ChoiceField(label="Tipo de descuento",
                                             choices=DocumentoEncabezadoDetalle.TIPO_DESCUENTO, initial='',
                                             widget=forms.Select(attrs={'class': 'form-control'}), required=False)  #
    docdet_descuento = forms.DecimalField(label="Descuento", initial=0,
                                          widget=forms.NumberInput({'class': 'form-control', 'autocomplete': 'off'}))  #
    docdet_montoiva = forms.DecimalField(label="Monto IVA", initial=0, widget=forms.NumberInput(
        {'class': 'form-control', 'autocomplete': 'off', 'readonly': True}))  #
    docdet_tasadecambio = forms.DecimalField(label="Tasa de cambio", initial=0, widget=forms.NumberInput(
        {'class': 'form-control', 'autocomplete': 'off'}))  #
    moneda = forms.ModelChoiceField(label='Moneda', queryset=Moneda.objects.all(), to_field_name='mon_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
                                    required=False)

    def clean_docdet_preciounitario(self):
        docdet_preciounitario = self.cleaned_data.get('docdet_preciounitario')
        if docdet_preciounitario <= 0:
            self.add_error('docdet_preciounitario', 'El precio unitario debe ser mayor a 0')
            docdet_preciounitario = 0
        return docdet_preciounitario

    def clean_docdet_cantidad(self):
        docdet_cantidad = self.cleaned_data.get('docdet_cantidad')
        if docdet_cantidad <= 0:
            self.add_error('docdet_cantidad', 'La cantidad debe ser mayor a 0')
            docdet_cantidad = 0
        return docdet_cantidad

    # def clean_docdet_descuento(self):
    #     docdet_descuento = self.cleaned_data.get('docdet_descuento')
    #     if docdet_descuento <= 0:
    #         self.add_error('docdet_descuento', 'El descuento debe ser mayor a 0')
    #         docdet_descuento = 0
    #     return docdet_descuento

    class Meta:
        model = DocumentoEncabezadoDetalle
        fields = [
            'docdet_numdetalle',
            'docdet_isiva',
            'docdet_cantidad',
            'docdet_producto',
            'docdet_preciounitario',
            'docdet_preciototal',
            'docdet_tipodescuento',
            'docdet_descuento',
            'docdet_montoiva',
            'docdet_tasadecambio',
            'moneda',
        ]
