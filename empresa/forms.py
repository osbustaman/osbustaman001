#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django import forms
from django.core.exceptions import ObjectDoesNotExist
from django.forms import ModelForm, TextInput, Select, PasswordInput, Textarea, HiddenInput, NumberInput, DateInput
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User

from jab.views import calculo_digito_verificador
from usuario.models import Empresa, Comuna, Region, Pais, RelacionDeAfiliacion, CajasCompensacion, Sucursal, \
    Usuario, UsuarioEmpresa, Cargo, GrupoCentroCosto, CentroCosto, Bancos, Afp, Salud, CargoEmpresa

from perfil.models import Item

import datetime
from _datetime import date


class EmpresasForm(ModelForm):
    emp_codigo = forms.CharField(label="Código", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autofocus': 'autofocus', 'autocomplete': 'off'}))
    emp_rut = forms.CharField(label="Rut empresa", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off', 'maxlength': '10'}))
    emp_nombrerepresentante = forms.CharField(label="Representante legal", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    emp_rutrepresentante = forms.CharField(label="Rut representante", widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength': '10', 'autocomplete': 'off'}))
    emp_isestatal = forms.ChoiceField(initial='S', label="Es estatal?", choices=Empresa.OPCIONES,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    emp_razonsocial = forms.CharField(label="Razón social",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    emp_giro = forms.CharField(label="Giro",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    emp_direccion = forms.CharField(label="Calle",
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    emp_numero = forms.CharField(label="N°",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    emp_piso = forms.CharField(label="Piso",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                               required=False)
    emp_dptooficina = forms.CharField(label="N° departamento/oficina",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                      required=False)
    pais = forms.ModelChoiceField(queryset=Pais.objects.all(), label='Pais', to_field_name='pa_id',
                                  widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    region = forms.ModelChoiceField(queryset=Region.objects.all(), label='Region', to_field_name='re_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    comuna = forms.ModelChoiceField(queryset=Comuna.objects.all(), label='Comuna', to_field_name='com_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    emp_cospostal = forms.CharField(label="Código postal",
                                    widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                    required=False)
    emp_fonouno = forms.CharField(label="teléfono principal", widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-inputmask': '"mask": "9-9999-9999"', 'data-mask': '',
               'autocomplete': 'off'}))
    emp_mailuno = forms.EmailField(label="Mail principal",
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    emp_fonodos = forms.CharField(label="teléfono secundario", widget=forms.TextInput(
        attrs={'class': 'form-control', 'data-inputmask': '"mask": "9-9999-9999"', 'data-mask': '',
               'autocomplete': 'off'}), required=False)
    emp_maildos = forms.EmailField(label="Mail secundario",
                                   widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                   required=False)
    emp_fechaingreso = forms.DateField(input_formats=["%d/%m/%Y"], label="Fecha de inicio de actividades",
                                          widget=forms.DateInput(format="%d/%m/%Y",
                                                                 attrs={'class': 'form-control pull-right',
                                                                        'placeholder': 'Ej: 31/12/1999'}))
    emp_isholding = forms.ChoiceField(initial='N', label="Empresa principal", choices=Empresa.OPCIONES,
                                      widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    emp_activa = forms.ChoiceField(initial='S', label="Empresa activa", choices=Empresa.OPCIONES,
                                   widget=forms.Select(attrs={'class': 'form-control'}))
    emp_rutcontador = forms.CharField(label="Rut contador", widget=forms.TextInput(
        attrs={'class': 'form-control', 'maxlength': '10', 'autocomplete': 'off'}), required=False)
    emp_nombrecontador = forms.CharField(label="Nombre contador",
                                         widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                         required=False)

    def clean(self, *args, **kwargs):

        emp_rut = self.cleaned_data.get('emp_rut')
        emp_rutcontador = self.cleaned_data.get('emp_rutcontador')
        emp_rutrepresentante = self.cleaned_data.get('emp_rutrepresentante')

        x_emp_rut = emp_rut.split('-')
        x_emp_rutcontador = emp_rutcontador.split('-')
        x_emp_rutrepresentante = emp_rutrepresentante.split('-')

        dv_rut = calculo_digito_verificador(emp_rut)
        if not str(dv_rut).lower() == str(x_emp_rut[1]).lower():
            self.add_error('emp_rut', "Rut empresa no valido")

        dv_rutcontador = calculo_digito_verificador(emp_rutcontador)
        if not str(dv_rutcontador).lower() == str(x_emp_rutcontador[1]).lower():
            self.add_error('emp_rutcontador', "Rut del contador no valido")

        dv_rutrepresentante = calculo_digito_verificador(emp_rutrepresentante)
        if not str(dv_rutrepresentante).lower() == str(x_emp_rutrepresentante[1]).lower():
            self.add_error('emp_rutrepresentante', "Rut representante no valido")

    class Meta:
        model = Empresa
        fields = [
            'emp_codigo',
            'emp_rut',
            'emp_nombrerepresentante',
            'emp_rutrepresentante',
            'emp_isestatal',
            'emp_razonsocial',
            'emp_giro',
            'emp_direccion',
            'emp_numero',
            'emp_piso',
            'emp_dptooficina',
            'pais',
            'region',
            'comuna',
            'emp_cospostal',
            'emp_fonouno',
            'emp_mailuno',
            'emp_fonodos',
            'emp_maildos',
            'emp_fechaingreso',
            'emp_isholding',
            'emp_activa',
            'emp_rutcontador',
            'emp_nombrecontador',
        ]


class RelacionForm(ModelForm):
    rda_tipoafiliacion = forms.ChoiceField(label="Tipo de afiliación", initial='',
                                           choices=RelacionDeAfiliacion.TIPO_AFILIACION,
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    cajascompensacion = forms.ModelChoiceField(label='Caja de Compensacion', queryset=CajasCompensacion.objects.all(),
                                               to_field_name='cc_id', widget=forms.Select(
            attrs={'class': 'form-control select2', 'style': 'width: 100%'}), required=False)
    rda_inp = forms.CharField(label="Nombre INP",
                              widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                              required=False)
    rda_tipoatipomutual = forms.ChoiceField(label="Mutual", initial='', choices=RelacionDeAfiliacion.MUTUALES,
                                            widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    rda_porcentajemutual = forms.DecimalField(label='% Mutual', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}), required=False)

    class Meta:
        model = RelacionDeAfiliacion
        fields = [
            'rda_tipoafiliacion',
            'cajascompensacion',
            'rda_inp',
            'rda_tipoatipomutual',
            'rda_porcentajemutual',
        ]


class SucursalForm(ModelForm):
    suc_codigo = forms.CharField(label="Código de la sucursal", widget=forms.TextInput(attrs={'class': 'form-control'}))
    suc_descripcion = forms.CharField(label="Descripción", widget=forms.TextInput(attrs={'class': 'form-control'}))
    suc_direccion = forms.CharField(label="Dirección", widget=forms.TextInput(attrs={'class': 'form-control'}))
    pais = forms.ModelChoiceField(label='Pais', queryset=Pais.objects.all(), to_field_name='pa_id',
                                  widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    region = forms.ModelChoiceField(label='Region', queryset=Region.objects.all(), to_field_name='re_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    comuna = forms.ModelChoiceField(label='Comuna', queryset=Comuna.objects.all(), to_field_name='com_id',
                                    widget=forms.Select(
                                        attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    suc_estado = forms.ChoiceField(label="Sucursal activa?", initial='S', choices=Sucursal.OPCIONES,
                                   widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = Sucursal
        fields = [
            'suc_codigo',
            'suc_descripcion',
            'suc_direccion',
            'pais',
            'region',
            'comuna',
            'suc_estado',
        ]


class UserForm(UserCreationForm):
    TIPO_USUARIO = (
        ('', '-- seleccione --'),
        (2, 'Administrador'),
        (3, 'Usuario-Sistema'),
    )

    username = forms.CharField(label="Rut",
                               widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    first_name = forms.CharField(label="Nombres",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    last_name = forms.CharField(label="Apellidos",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    email = forms.EmailField(label="Email",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    password1 = forms.CharField(label="Contraseña",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    password2 = forms.CharField(label="Repite la contraseña",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    usu_tipousuario = forms.ChoiceField(initial='', label="Tipo de usuario", choices=TIPO_USUARIO,
                                        widget=forms.Select(attrs={'class': 'form-control '}))
    empresa = forms.CharField(widget=forms.HiddenInput())

    def clean(self, *args, **kwargs):
        username = self.cleaned_data.get('username')

        x_username = username.split('-')

        dv_rut = calculo_digito_verificador(username)
        if not str(dv_rut).lower() == str(x_username[1]).lower():
            self.add_error('username', "Rut no valido")

    class Meta:
        model = User
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]


class UsuarioEmpresaForm(ModelForm):
    sucursal = forms.ModelChoiceField(label='Sucursal', queryset=Sucursal.objects.all().exclude(suc_estado='N'),
                                      to_field_name='suc_id',
                                      widget=forms.Select(
                                          attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
                                      required=False)
    cargo = forms.ModelChoiceField(label='Cargo', queryset=Cargo.objects.all(), to_field_name='car_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    centrocosto = forms.ModelChoiceField(label='Centro de costo',
                                         queryset=CentroCosto.objects.all().exclude(
                                             grupocentrocosto__gcencost_activo='N').exclude(cencost_activo='N'),
                                         to_field_name='cencost_id', widget=forms.Select(
            attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    banco = forms.ModelChoiceField(label='Banco', queryset=Bancos.objects.all().exclude(ban_activo='N'),
                                   to_field_name='ban_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}),
                                   required=False)
    ue_tipocontrato = forms.ChoiceField(label="Tipo de contrato", initial='', choices=UsuarioEmpresa.TIPO_CONTRATO,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    ue_tipotrabajdor = forms.ChoiceField(label="Tipo trabajador", initial='D', choices=UsuarioEmpresa.TIPO_TRABAJADOR,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    ue_formapago = forms.ChoiceField(label="Forma de pago", initial='', choices=UsuarioEmpresa.FORMA_PAGO,
                                     widget=forms.Select(attrs={'class': 'form-control'}))
    ue_fechacontratacion = forms.DateField(input_formats=["%d/%m/%Y"], label="Fecha de contratacion",
                                           widget=forms.DateInput(format="%d/%m/%Y",
                                                                  attrs={'class': 'form-control pull-right',
                                                                         'placeholder': 'Ej: 31/12/1999'}))
    ue_fecharenovacioncontrato = forms.DateField(input_formats=["%d/%m/%Y"], label="Fecha término de contrato",
                                                 widget=forms.DateInput(format="%d/%m/%Y",
                                                                        attrs={'class': 'form-control',
                                                                               'placeholder': 'Ej: 31/12/1999'}),
                                                 required=False)
    ue_fecharetiro = forms.DateField(input_formats=["%d/%m/%Y"], label="Fecha finiquito",
                                     widget=forms.DateInput(format="%d/%m/%Y", attrs={'class': 'form-control',
                                                                                      'placeholder': 'Ej: 31/12/1999'}),
                                     required=False)
    ue_horassemanales = forms.IntegerField(label='Horas semanales', initial=45,
                                           widget=forms.NumberInput(attrs={'class': 'form-control'}))
    ue_asignacionfamiliar = forms.ChoiceField(label="Tiene asignación familiar", initial='',
                                              choices=UsuarioEmpresa.OPCIONES,
                                              widget=forms.Select(attrs={'class': 'form-control'}))
    ue_cargasfamiliares = forms.IntegerField(label='Cargas familiares', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': True}), required=False)
    ue_montoasignacionfamiliar = forms.DecimalField(label='Monto asignacion familiar', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': True}), required=False)

    ue_cuentabancaria = forms.CharField(label="Cuenta bancaria", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off', 'readonly': 'readonly'}), required=False)

    ue_jornadalaboral = forms.CharField(label='Jornada de trabajo',
                                        widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                        required=False)

    def clean_ue_fecharenovacioncontrato(self):

        """
        Validar fecha ue_fecharenovacioncontrato
        """
        ue_fecharenovacioncontrato = self.cleaned_data.get('ue_fecharenovacioncontrato')
        ue_fechacontratacion = self.cleaned_data.get('ue_fechacontratacion')

        if ue_fecharenovacioncontrato == "" or not ue_fecharenovacioncontrato:
            pass
        else:
            dateFechaContratacion = ue_fechacontratacion
            dateFechaRenovacionContrato = ue_fecharenovacioncontrato

            if dateFechaRenovacionContrato < dateFechaContratacion:
                self.add_error('ue_fecharenovacioncontrato',
                               'La fecha de la renovación no puede ser menor a la fecha de contratación')
                ue_fecharenovacioncontrato = ""
            return ue_fecharenovacioncontrato

    def clean_ue_fecharetiro(self):

        """
        Validar fecha ue_fecharetiro
        """
        ue_fecharetiro = self.cleaned_data.get('ue_fecharetiro')
        ue_fechacontratacion = self.cleaned_data.get('ue_fechacontratacion')

        if not ue_fecharetiro or not ue_fechacontratacion:
            pass
        else:
            dateFechaContratacion = ue_fechacontratacion
            dateFecharetiro = ue_fecharetiro

            if dateFecharetiro < dateFechaContratacion:
                self.add_error('ue_fecharetiro', 'La fecha de retiro no puede ser menor a la fecha de contratación')
                ue_fecharetiro = ""
            return ue_fecharetiro

    class Meta:
        model = UsuarioEmpresa
        fields = [
            # 'sucursal',
            'cargo',
            'centrocosto',
            'ue_tipocontrato',
            'ue_formapago',
            'ue_fechacontratacion',
            'ue_fecharenovacioncontrato',
            'ue_fecharetiro',
            'ue_horassemanales',
            'ue_asignacionfamiliar',
            'ue_cargasfamiliares',
            'ue_montoasignacionfamiliar',
            'banco',
            'ue_cuentabancaria',
            'ue_jornadalaboral',
        ]


class LeyesSocialesForm(ModelForm):
    afp = forms.ModelChoiceField(label='AFP', queryset=Afp.objects.all(), to_field_name='afp_id',
                                 widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    afp_apv = forms.ModelChoiceField(label='AFP', queryset=Afp.objects.all(), to_field_name='afp_id',
                                     widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                                'disabled': True}), required=False)
    salud = forms.ModelChoiceField(label='Salud ', queryset=Salud.objects.all(), to_field_name='sa_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    afp_porcentaje = forms.CharField(label="Cotización obligatoria",
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                     required=False)
    ue_sis = forms.CharField(label="Seguro de Invalidez y Sobrevivencia (SIS)",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                             required=False)
    afp_codigo = forms.CharField(label="Código",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                 required=False)
    sa_codigo = forms.CharField(label="Código",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                required=False)
    ue_ufisapre = forms.FloatField(label="UF a pagar", widget=forms.TextInput(attrs={'class': 'form-control', }),
                                   required=False)
    ue_funisapre = forms.IntegerField(label="FUN de la isapre",
                                      widget=forms.TextInput(attrs={'class': 'form-control', }), required=False)
    ue_cotizacion = forms.FloatField(label='Cotización', initial='0',
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                     required=False)

    ue_tieneapv = forms.ChoiceField(label="Tiene APV", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                    widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    ue_tipomontoapv = forms.ChoiceField(label="Tipo monto APV", choices=UsuarioEmpresa.TIPO_MONTO,
                                        widget=forms.Select(attrs={'class': 'form-control', 'disabled': True}),
                                        required=False)
    ue_tieneahorrovoluntario = forms.ChoiceField(label="Tiene Ahorro voluntario", initial='N',
                                                 choices=UsuarioEmpresa.OPCIONES,
                                                 widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    ue_ahorrovoluntario = forms.DecimalField(label="Ahorro voluntario", widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': True}), required=False)
    ue_cotizacionvoluntaria = forms.DecimalField(label='Cotización voluntaria', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': True}), required=False)

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_ufisapre',
            'ue_funisapre',
            'ue_cotizacion',
            'ue_tieneahorrovoluntario',
            'ue_tieneapv',
            'ue_tipomontoapv',
            'ue_ahorrovoluntario',
            'ue_cotizacionvoluntaria',
        ]


class RemuneracionEmpleadoForm(ModelForm):
    ue_movilizacion = forms.DecimalField(label='Movilización', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_colacion = forms.DecimalField(label='Colación', initial='0',
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_sueldobase = forms.DecimalField(label='Sueldo base', initial='0',
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_gratificacion = forms.ChoiceField(label="Tiene gratificación?", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    ue_tipogratificacion = forms.ChoiceField(label="Tipo de gratificación", initial='M',
                                             choices=UsuarioEmpresa.TIPO_GRATIFICACION,
                                             widget=forms.Select(attrs={'class': 'form-control'}))
    ue_segurodesempleo = forms.ChoiceField(label="Tiene seguro de desempleo?", choices=UsuarioEmpresa.SEGURO_DESEMPLEO,
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    ue_porempleado = forms.FloatField(label="Empleado", initial='0',
                                      widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                      required=False)
    ue_porempleador = forms.FloatField(label="Empleador", initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    ue_trabajopesado = forms.ChoiceField(label="Trabajo pesado?", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    ue_comiciones = forms.ChoiceField(label="Tiene comiciones?", initial='N', choices=UsuarioEmpresa.SEGURO_DESEMPLEO,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    ue_porcentajecomicion = forms.DecimalField(label='Porcentaje comociones', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_anticipo = forms.ChoiceField(label="Tiene anticipo?", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    ue_montonticipo = forms.DecimalField(label='Monto anticipo', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_movilizacion',
            'ue_colacion',
            'ue_sueldobase',
            'ue_gratificacion',
            'ue_tipogratificacion',
            'ue_segurodesempleo',
            'ue_porempleado',
            'ue_porempleador',
            'ue_trabajopesado',
            'ue_comiciones',
            'ue_porcentajecomicion',
            'ue_anticipo',
            'ue_montonticipo',
        ]


class MenuEmpleadoForm(forms.Form):
    me_items = forms.ModelChoiceField(label='Items del menú', queryset=Item.objects.all(), to_field_name='item_id',
                                      widget=forms.Select(
                                          attrs={'class': 'form-control select-multiple', 'multiple': 'multiple',
                                                 'style': 'width: 100%'}))


class CargoForm(ModelForm):
    car_nombre = forms.CharField(label="Cargo",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))

    class Meta:
        model = Cargo
        fields = [
            'car_nombre',
        ]


class CargoEmpresaForm(ModelForm):
    empresa = forms.ModelChoiceField(label='Empresa', queryset=Empresa.objects.all().exclude(emp_activa='N'),
                                     to_field_name='emp_id', widget=forms.Select(
            attrs={'class': 'form-control select2', 'style': 'width: 100%'}), required=False)

    class Meta:
        model = CargoEmpresa
        fields = [
            'empresa',
        ]


class LeyesSocialesForm(ModelForm):
    afp = forms.ModelChoiceField(label='AFP', queryset=Afp.objects.all(), to_field_name='afp_id',
                                 widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    afp_apv = forms.ModelChoiceField(label='AFP', queryset=Afp.objects.all(), to_field_name='afp_id',
                                     widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%',
                                                                'disabled': True}), required=False)
    salud = forms.ModelChoiceField(label='Salud ', queryset=Salud.objects.all(), to_field_name='sa_id',
                                   widget=forms.Select(attrs={'class': 'form-control select2', 'style': 'width: 100%'}))
    afp_porcentaje = forms.CharField(label="Cotización obligatoria",
                                     widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                     required=False)
    ue_sis = forms.CharField(label="Seguro de Invalidez y Sobrevivencia (SIS)",
                             widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                             required=False)
    afp_codigo = forms.CharField(label="Código",
                                 widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                 required=False)
    sa_codigo = forms.CharField(label="Código",
                                widget=forms.TextInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                required=False)
    ue_ufisapre = forms.FloatField(label="UF a pagar", widget=forms.TextInput(attrs={'class': 'form-control', }),
                                   required=False)
    ue_funisapre = forms.IntegerField(label="FUN de la isapre",
                                      widget=forms.TextInput(attrs={'class': 'form-control', }), required=False)
    ue_cotizacion = forms.FloatField(label='Cotización', initial='0',
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                     required=False)

    ue_tieneapv = forms.ChoiceField(label="Tiene APV", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                    widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    ue_tipomontoapv = forms.ChoiceField(label="Tipo monto APV", choices=UsuarioEmpresa.TIPO_MONTO,
                                        widget=forms.Select(attrs={'class': 'form-control', 'disabled': True}),
                                        required=False)
    ue_tieneahorrovoluntario = forms.ChoiceField(label="Tiene Ahorro voluntario", initial='N',
                                                 choices=UsuarioEmpresa.OPCIONES,
                                                 widget=forms.Select(attrs={'class': 'form-control'}), required=False)
    ue_ahorrovoluntario = forms.DecimalField(label="Ahorro voluntario", widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': True}), required=False)
    ue_cotizacionvoluntaria = forms.DecimalField(label='Cotización voluntaria', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': True}), required=False)

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_ufisapre',
            'ue_funisapre',
            'ue_cotizacion',
            'ue_tieneahorrovoluntario',
            'ue_tieneapv',
            'ue_tipomontoapv',
            'ue_ahorrovoluntario',
            'ue_cotizacionvoluntaria',
        ]


class RemuneracionEmpleadoForm(ModelForm):
    ue_movilizacion = forms.DecimalField(label='Movilización', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_colacion = forms.DecimalField(label='Colación', initial='0',
                                     widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_sueldobase = forms.DecimalField(label='Sueldo base', initial='0',
                                       widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_gratificacion = forms.ChoiceField(label="Tiene gratificación?", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    ue_tipogratificacion = forms.ChoiceField(label="Tipo de gratificación", initial='M',
                                             choices=UsuarioEmpresa.TIPO_GRATIFICACION,
                                             widget=forms.Select(attrs={'class': 'form-control'}))
    ue_segurodesempleo = forms.ChoiceField(label="Tiene seguro de desempleo?", choices=UsuarioEmpresa.SEGURO_DESEMPLEO,
                                           widget=forms.Select(attrs={'class': 'form-control'}))
    ue_porempleado = forms.FloatField(label="Empleado", initial='0',
                                      widget=forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
                                      required=False)
    ue_porempleador = forms.FloatField(label="Empleador", initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'readonly': 'readonly'}), required=False)
    ue_trabajopesado = forms.ChoiceField(label="Trabajo pesado?", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                         widget=forms.Select(attrs={'class': 'form-control'}))
    ue_comiciones = forms.ChoiceField(label="Tiene comiciones?", initial='N', choices=UsuarioEmpresa.SEGURO_DESEMPLEO,
                                      widget=forms.Select(attrs={'class': 'form-control'}))
    ue_porcentajecomicion = forms.DecimalField(label='Porcentaje comociones', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    ue_anticipo = forms.ChoiceField(label="Tiene anticipo?", initial='N', choices=UsuarioEmpresa.OPCIONES,
                                    widget=forms.Select(attrs={'class': 'form-control'}))
    ue_montonticipo = forms.DecimalField(label='Monto anticipo', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_movilizacion',
            'ue_colacion',
            'ue_sueldobase',
            'ue_gratificacion',
            'ue_tipogratificacion',
            'ue_segurodesempleo',
            'ue_porempleado',
            'ue_porempleador',
            'ue_trabajopesado',
            'ue_comiciones',
            'ue_porcentajecomicion',
            'ue_anticipo',
            'ue_montonticipo',
        ]


class DataCicloVidaCertificadoAmonestacionAnexosEquiposSeguridadForm(ModelForm):
    ue_prestamo = forms.DecimalField(label='Monto', initial='0', widget=forms.NumberInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}), required=False)
    ue_cuotas = forms.CharField(label='Cuotas', initial='0',
                                widget=forms.NumberInput(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                required=False)

    ue_certificado = forms.CharField(label='Certificado',
                                     widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                     required=False)

    ue_amonestacion = forms.CharField(label='Motivo de amonestación',
                                      widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                      required=False)

    ue_entregaequiposeguridad = forms.CharField(label='Entrega de equipos de seguridad',
                                                widget=forms.Textarea(
                                                    attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                                required=False)

    ue_anexocontrato = forms.CharField(label='Anexo de contrato',
                                       widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                       required=False)

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_prestamo',
            'ue_prestamo',
            'ue_certificado',
            'ue_amonestacion',
            'ue_entregaequiposeguridad',
            'ue_anexocontrato',
        ]


class TerminoRelacionLaboralForm(ModelForm):
    ue_fechanotificacioncartaaviso = forms.DateField(input_formats=["%d/%m/%Y"],
                                                     label="Fecha de notificacion carta aviso",
                                                     widget=forms.DateInput(format="%d/%m/%Y",
                                                                            attrs={'class': 'form-control pull-right',
                                                                                   'placeholder': 'Ej: 31/12/1999'}),
                                                     required=False)

    ue_fechatermino = forms.DateField(input_formats=["%d/%m/%Y"], label="Fecha de termino relacion laboral",
                                      widget=forms.DateInput(format="%d/%m/%Y",
                                                             attrs={'class': 'form-control pull-right',
                                                                    'placeholder': 'Ej: 31/12/1999'}), required=False)

    ue_cuasal = forms.CharField(label='Causal',
                                widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                required=False)

    ue_fundamento = forms.CharField(label='Fundamento',
                                    widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                                    required=False)

    ue_tiponoticacion = forms.ChoiceField(label="Tipo de notificación", initial='',
                                          choices=UsuarioEmpresa.NOTIFICACION,
                                          widget=forms.Select(attrs={'class': 'form-control'}), required=False)

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_fechanotificacioncartaaviso',
            'ue_fechatermino',
            'ue_cuasal',
            'ue_fundamento',
            'ue_tiponoticacion',
        ]


class OtrosForm(ModelForm):
    ue_otros = forms.CharField(label='Otro',
                               widget=forms.Textarea(attrs={'class': 'form-control', 'autocomplete': 'off'}),
                               required=False)

    class Meta:
        model = UsuarioEmpresa
        fields = [
            'ue_otros',
        ]


# class CentroCostoForm(ModelForm):
#     cencost_nombre = forms.CharField(label="Nombre Centro de costo",
#                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
#     cencost_codigo = forms.CharField(label="Código Centro de costo",
#                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
#     cencost_activo = forms.ChoiceField(label="Centro costo activo?", initial='S', choices=CentroCosto.OPCIONES,
#                                        widget=forms.Select(attrs={'class': 'form-control'}))
#
#     class Meta:
#         model = CentroCosto
#         fields = [
#             'cencost_nombre',
#             'cencost_codigo',
#             'cencost_activo',
#         ]


class GrupoCentroCostoForm(ModelForm):
    gcencost_nombre = forms.CharField(label="Nombre grupo centro de costo",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    gcencost_codigo = forms.CharField(label="Código ",
                                      widget=forms.TextInput(attrs={'class': 'form-control', 'autocomplete': 'off'}))
    gcencost_activo = forms.ChoiceField(label="Grupo activo?", initial='S', choices=CentroCosto.OPCIONES,
                                        widget=forms.Select(attrs={'class': 'form-control'}))
    empresa = forms.ModelChoiceField(label='Empresa', queryset=Empresa.objects.all().exclude(emp_activa='N'),
                                     to_field_name='emp_id', widget=forms.Select(
            attrs={'class': 'form-control select2', 'style': 'width: 100%'}), required=False)

    class Meta:
        model = GrupoCentroCosto
        fields = [
            'gcencost_nombre',
            'gcencost_codigo',
            'gcencost_activo',
            'empresa',
        ]


class CentroCostoForm(ModelForm):
    cencost_nombre = forms.CharField(label="Nombre Centro de costo", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cencost_codigo = forms.CharField(label="Código Centro de costo", widget=forms.TextInput(
        attrs={'class': 'form-control', 'autocomplete': 'off'}))
    cencost_activo = forms.ChoiceField(label="Centro costo activo?", initial='S', choices=CentroCosto.OPCIONES,
                                       widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CentroCosto
        fields = [
            'cencost_nombre',
            'cencost_codigo',
            'cencost_activo',
        ]
