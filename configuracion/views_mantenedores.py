# -*- encoding: utf-8 -*-
import distutils.core
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context
from django.http import Http404, HttpResponseRedirect
from urllib.parse import urlparse
from django.urls import resolve

from django.core.urlresolvers import reverse
from django.views.decorators.csrf import csrf_exempt
from django.core.validators import validate_email
from django.template.loader import get_template
from django.http import HttpResponse
from slugify import slugify
from django import template
from django.conf import settings
from django.db.models import Q
from threading import Thread
from django.template.loader import get_template
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.db.models import Case, When, Max, F, Count, Value, Q, Sum, BooleanField, TextField, IntegerField, EmailField
from django.contrib.auth.views import logout, password_reset, password_reset_done, password_reset_complete

from datetime import timedelta

from clienteproveedor.models import ClienteProveedor, ClienteProveedorEmpresa
from configuracion.models import ClienteActivo
from jab.decoradores import existe_empresa
from jab.threadlocal import get_thread_local
from django.db import transaction
import json

from django.utils import timezone
from django.contrib import auth

from xlwt import Workbook
from xlwt import Font
from xlwt import XFStyle
from xlwt import Borders

import json
import xlrd
import xlwt
import collections
import shutil
import os
import time
import math
import datetime

import sys
import decimal
import locale
import csv

from django.contrib.auth.models import User
from usuario.models import Usuario, UsuarioEmpresa, AsociacionUsuarioEmpresa, Pais, Region, Comuna, Cargo, CentroCosto, \
    Afp, Salud, Bancos, Empresa

from configuracion.forms import ExportadorForm, CamposExtrasForm

from jab.views import calculo_digito_verificador, valida_correo, elige_choices


@login_required
@existe_empresa
def viewsExportador(request, accion=''):
    url_formato = ''
    lst_validaciones = []
    lista_err = []
    form = ExportadorForm(request.POST or None, request.FILES or None)
    error = False
    tipoArchivo = ''
    lista_uno = ''
    lista_dos = ''

    if accion == 'E':
        url_formato = reverse('bases:camposPersonal', args=[])

        lst_validaciones = [
            {'contador': 1, 'key': 'username', 'value': 'obligatorio, debe ser el rut del empleado sin puntos'},
            {'contador': 2, 'key': 'email', 'value': ' obligatorio'},
            {'contador': 3, 'key': 'first_name', 'value': ' obligatorio'},
            {'contador': 4, 'key': 'last_name', 'value': ' obligatorio'},
            {'contador': 5, 'key': 'usu_tiporut', 'value': ' obligatorio,  valor:1=Rut - 2=Extranjero,  numero'},
            {'contador': 6, 'key': 'usu_sexo',
             'value': ' obligatorio,  valor: M=masculino - F=femenino -  PD=Por definir,  2 caracteres,  texto'},
            {'contador': 7, 'key': 'usu_fono', 'value': 'no obligatorio,  20 caracteres'},
            {'contador': 8, 'key': 'usu_fechanacimiento', 'value': ' obligatorio,  mm/dd/AAAA,  10 caracteres'},
            {'contador': 9, 'key': 'pais', 'value': ' obligatorio,  numero'},
            {'contador': 10, 'key': 'region', 'value': ' obligatorio,  numero'},
            {'contador': 11, 'key': 'comuna', 'value': ' obligatorio,  numero'},
            {'contador': 12, 'key': 'usu_direccion', 'value': ' obligatorio,  texto'},
            {'contador': 13, 'key': 'usu_estadocivil',
             'value': ' obligatorio,  valor: S=Solter@ - C=Casad@ - D=Divorsiad@ - V=Viaud@,  1 caracteres,  texto'},
            {'contador': 14, 'key': 'usu_tipousuario',
             'value': ' obligatorio,  valor: 2=Administrador - 3=Usuario-Sistema,  numero'},
            {'contador': 15, 'key': 'usu_profesion', 'value': 'no obligatorio,  50 carateres'},
            {'contador': 16, 'key': 'cargo', 'value': ' obligatorio,  numero'},
            {'contador': 17, 'key': 'ue_tipocontrato',
             'value': ' obligatorio,  valor: CI=Contrato indefinido - CPF=Contrato plazo fijo - CIT=Contrato individual de trabajo,  3 caracteres,  texto'},
            {'contador': 18, 'key': 'ue_tipotrabajdor',
             'value': ' obligatorio,  valor: D=Dependiente - I=Independiente,  1 caracteres,  texto'},
            {'contador': 19, 'key': 'ue_fechacontratacion', 'value': ' obligatorio,  mm/dd/AAAA,  10 caracteres'},
            {'contador': 20, 'key': 'ue_fecharenovacioncontrato',
             'value': 'no obligatorio,  mm/dd/AAAA,  10 caracteres'},
            {'contador': 21, 'key': 'centrocosto', 'value': ' obligatorio,  numero'},
            {'contador': 22, 'key': 'ue_movilizacion',
             'value': 'obligatorio,  numero, en el caso que no tenga colocar 0'},
            {'contador': 23, 'key': 'ue_colacion', 'value': ' obligatorio,  numero, en el caso que no tenga colocar 0'},
            {'contador': 24, 'key': 'ue_anticipo', 'value': ' obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 25, 'key': 'ue_montonticipo',
             'value': 'no obligatorio, numero, en el caso que no tenga colocar 0'},
            {'contador': 26, 'key': 'ue_asignacionfamiliar', 'value': 'no obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 27, 'key': 'ue_cargasfamiliares',
             'value': 'obligatorio en el caso que tenga asignacion familiar, numero, en el caso que no tenga colocar 0'},
            {'contador': 28, 'key': 'ue_montoasignacionfamiliar',
             'value': 'obligatorio en el caso que tenga asignacion familiar, numero, en el caso que no tenga colocar 0'},
            {'contador': 29, 'key': 'ue_sueldobase', 'value': ' obligatorio,  numero'},
            {'contador': 30, 'key': 'ue_gratificacion', 'values': 'obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 31, 'key': 'ue_tipogratificacion',
             'value': ' no obligatorio,  valor: A=Anual - M=Mensual,  texto'},
            {'contador': 32, 'key': 'ue_comiciones', 'value': ' obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 33, 'key': 'ue_porcentajecomicion', 'value': ' no obligatorio,  numero'},
            {'contador': 34, 'key': 'afp', 'value': ' obligatorio,  numero'},
            {'contador': 35, 'key': 'ue_tieneapv', 'value': 'obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 36, 'key': 'ue_tipomontoapv',
             'value': ' obligatorio,  valor: P=Porcentaje - M=Monto, texto, en el caso que no tenga apv dejar vacio'},
            {'contador': 37, 'key': 'afp_apv',
             'value': 'no obligatorio,  numero, en el caso que no tenga apv dejar vacio'},
            {'contador': 38, 'key': 'ue_cotizacionvoluntaria',
             'value': 'no obligatorio,  numero, en el caso que no tenga apv dejar vacio'},
            {'contador': 39, 'key': 'ue_tieneahorrovoluntario', 'value': 'obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 40, 'key': 'ue_ahorrovoluntario',
             'value': 'obligatorio en el caso que tenga ahorro voluntario, numero, en el caso que no tenga debe quedar en 0'},
            {'contador': 41, 'key': 'salud', 'value': ' obligatorio,  numero'},
            {'contador': 42, 'key': 'ue_ufisapre',
             'value': 'no obligatorio,  numero, en el caso que no tenga debe quedar vacio'},
            {'contador': 43, 'key': 'ue_funisapre',
             'value': 'no obligatorio,  numero, en el caso que no tenga debe quedar vacio'},
            # {'contador': 49, 'key': 'ue_cotizacion', 'value': ' no obligatorio,  numero'},
            {'contador': 44, 'key': 'ue_trabajopesado', 'value': 'obligatorio,  valor: S=Si - N=No,  texto'},
            {'contador': 45, 'key': 'banco', 'value': ' obligatorio,  numero'},
            {'contador': 46, 'key': 'ue_formapago',
             'value': ' obligatorio,  valor: 1=Efectivo - 2=Cheque - 3=Depósito directo,  numero'},
            {'contador': 47, 'key': 'ue_cuentabancaria',
             'value': 'no obligatorio,  50 caracteres,  texto, en el caso que no tenga debe quedar vacio'},
        ]

        if request.method == "POST":
            lista_uno, lista_dos = uploadPersonal(request, form)
            tipoArchivo = request.POST['tipo-archivo']

    if accion in ['C', 'P', 'A']:
        url_formato = reverse('bases:camposClienteProveedor', args=[accion])

        if accion == 'C':
            key_tipo = 'cpe_tipocliente'
            value_tipo = 'obligatorio,  valor: N=No - C=Nacional - P=Prospecto - E=Extranjero,  texto'

        if accion == 'P':
            key_tipo = 'cpe_tipoproveedor'
            value_tipo = 'obligatorio,  valor: N=No - P=Nacional - H=Honorario - E=Extranjero - A=Agente de Aduana,  texto'

        lst_validaciones = [
            {'contador': 1, 'key': 'cp_rut', 'value': 'obligatorio, Debe ser el rut sin puntos ejemplo 12345678-9'},
            {'contador': 2, 'key': 'cp_razonsocial', 'value': ' obligatorio, 50 caracteres, texto'},
            {'contador': 3, 'key': 'cp_nombrefantasia', 'value': ' obligatorio, 150 caracteres, texto'},
            {'contador': 4, 'key': 'cp_giro', 'value': ' obligatorio, 150 caracteres, texto'},
            {'contador': 5, 'key': 'cp_direccion', 'value': ' obligatorio, texto'},
            {'contador': 6, 'key': 'cp_numero', 'value': ' obligatorio, numero'},
            {'contador': 7, 'key': 'cp_piso', 'value': ' no obligatorio,  12 caracteres,  texto'},
            {'contador': 8, 'key': 'cp_dptooficina', 'value': 'no obligatorio, 25 caracteres,  texto'},
            {'contador': 9, 'key': 'pais', 'value': 'obligatorio, numero'},
            {'contador': 10, 'key': 'region', 'value': 'obligatorio, numero'},
            {'contador': 11, 'key': 'comuna', 'value': 'obligatorio, numero'},
            {'contador': 12, 'key': 'cp_email', 'value': 'obligatorio, 50 caracteres,  texto'},
            {'contador': 13, 'key': 'cp_fono', 'value': 'obligatorio, 25 caracteres,  texto'},
            {'contador': 14, 'key': key_tipo, 'value': value_tipo},
            {'contador': 15, 'key': 'banco', 'value': ' obligatorio,  numero'},
            {'contador': 16, 'key': 'cpe_tipocuenta',
             'value': 'obligatorio,  valor: 1=Cuenta vista - 2=Cuenta de ahorro - 3=Cuenta corriente - 4=Vale vista,  numero'},

        ]

        if request.method == "POST":
            lista_uno, lista_dos = uploadClienteProveedor(request, form, accion)
            tipoArchivo = request.POST['tipo-archivo']

    lstDataExport = [
        {
            'key': 'E',
            'value': 'Personal',
        }, {
            'key': 'C',
            'value': 'Cliente',
        }, {
            'key': 'P',
            'value': 'Proveedor',
        }
    ]

    data = {
        'lstDataExport': lstDataExport,
        'filtro': accion,
        'url_formato': url_formato,
        'lst_validaciones': lst_validaciones,
        'form': form,
        'error': error,
        'lista_err': lista_err,
        'tipoArchivo': tipoArchivo,
        'lista_uno': lista_uno,
        'lista_dos': lista_dos,
        'frmExtras': CamposExtrasForm(),
    }
    return render(request, 'panelcontrol/exportador.html', data)


@login_required
def modal_ids(request):
    data = {
        'frmExtras': CamposExtrasForm(),
    }
    return render(request, 'panelcontrol/popup_ids.html', data)


@login_required
def camposPersonal(request):
    hoy = datetime.datetime.now()

    filename = "upload_campos_personal_{}.xls".format(hoy.strftime("%d%m%Y_%H%M%S"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Hoja 1')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    text_style = xlwt.Style.easyxf("font: bold on; align: wrap on, vert centre, horiz center")

    ws.write(row_num, 0, 'rut', font_style)
    ws.write(row_num, 1, 'email', font_style)
    ws.write(row_num, 2, 'first_name', font_style)
    ws.write(row_num, 3, 'last_name', font_style)
    ws.write(row_num, 4, 'usu_tiporut', font_style)
    ws.write(row_num, 5, 'usu_sexo', font_style)
    ws.write(row_num, 6, 'usu_fono', font_style)
    ws.write(row_num, 7, 'usu_fechanacimiento', font_style)
    ws.write(row_num, 8, 'pais', font_style)
    ws.write(row_num, 9, 'region', font_style)
    ws.write(row_num, 10, 'comuna', font_style)
    ws.write(row_num, 11, 'usu_direccion', font_style)
    ws.write(row_num, 12, 'usu_estadocivil', font_style)
    ws.write(row_num, 13, 'usu_tipousuario', font_style)
    ws.write(row_num, 14, 'usu_profesion', font_style)
    ws.write(row_num, 15, 'cargo', font_style)
    ws.write(row_num, 16, 'ue_tipocontrato', font_style)
    ws.write(row_num, 17, 'ue_tipotrabajdor', font_style)
    ws.write(row_num, 18, 'ue_fechacontratacion', font_style)
    ws.write(row_num, 19, 'ue_fecharenovacioncontrato', font_style)
    ws.write(row_num, 20, 'centrocosto', font_style)
    ws.write(row_num, 21, 'ue_movilizacion', font_style)
    ws.write(row_num, 22, 'ue_colacion', font_style)
    ws.write(row_num, 23, 'ue_anticipo', font_style)
    ws.write(row_num, 24, 'ue_montonticipo', font_style)
    ws.write(row_num, 25, 'ue_asignacionfamiliar', font_style)
    ws.write(row_num, 26, 'ue_cargasfamiliares', font_style)
    ws.write(row_num, 27, 'ue_montoasignacionfamiliar', font_style)
    ws.write(row_num, 28, 'ue_sueldobase', font_style)
    ws.write(row_num, 29, 'ue_gratificacion', font_style)
    ws.write(row_num, 30, 'ue_tipogratificacion', font_style)
    ws.write(row_num, 31, 'ue_comiciones', font_style)
    ws.write(row_num, 32, 'ue_porcentajecomicion', font_style)
    ws.write(row_num, 33, 'afp', font_style)
    ws.write(row_num, 34, 'ue_tieneapv', font_style)
    ws.write(row_num, 35, 'ue_tipomontoapv', font_style)
    ws.write(row_num, 36, 'afp_apv', font_style)
    ws.write(row_num, 37, 'ue_cotizacionvoluntaria', font_style)
    ws.write(row_num, 38, 'ue_tieneahorrovoluntario', font_style)
    ws.write(row_num, 39, 'ue_ahorrovoluntario', font_style)
    ws.write(row_num, 40, 'salud', font_style)
    ws.write(row_num, 41, 'ue_ufisapre', font_style)
    ws.write(row_num, 42, 'ue_funisapre', font_style)
    # ws.write(row_num, 44, 'ue_cotizacion', font_style)
    ws.write(row_num, 43, 'ue_trabajopesado', font_style)
    ws.write(row_num, 44, 'banco', font_style)
    ws.write(row_num, 45, 'ue_formapago', font_style)
    ws.write(row_num, 46, 'ue_cuentabancaria', font_style)

    wb.save(response)
    return response


@login_required
def camposClienteProveedor(request, accion):
    hoy = datetime.datetime.now()

    filename = "cliente_proveedor_{}.xls".format(hoy.strftime("%d%m%Y_%H%M%S"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Hoja 1')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    text_style = xlwt.Style.easyxf("font: bold on; align: wrap on, vert centre, horiz center")

    ws.write(row_num, 0, 'cp_rut', font_style)
    ws.write(row_num, 1, 'cp_razonsocial', font_style)
    ws.write(row_num, 2, 'cp_nombrefantasia', font_style)
    ws.write(row_num, 3, 'cp_giro', font_style)
    ws.write(row_num, 4, 'cp_direccion', font_style)
    ws.write(row_num, 5, 'cp_numero', font_style)
    ws.write(row_num, 6, 'cp_piso', font_style)
    ws.write(row_num, 7, 'cp_dptooficina', font_style)
    ws.write(row_num, 8, 'pais', font_style)
    ws.write(row_num, 9, 'region', font_style)
    ws.write(row_num, 10, 'comuna', font_style)
    ws.write(row_num, 11, 'cp_email', font_style)
    ws.write(row_num, 12, 'cp_fono', font_style)

    if accion == 'C':
        ws.write(row_num, 13, 'cpe_tipocliente', font_style)
    elif accion == 'P':
        ws.write(row_num, 13, 'cpe_tipoproveedor', font_style)

    ws.write(row_num, 14, 'banco', font_style)
    ws.write(row_num, 15, 'cpe_tipocuenta', font_style)

    wb.save(response)
    return response


@login_required
def uploadPersonal(request, form):
    lista_err = []
    error = False
    separacion = ''

    if request.POST['tipo-archivo'] == '1':
        separacion = ';'
    if request.POST['tipo-archivo'] == '2':
        separacion = ','
    if request.POST['tipo-archivo'] == '3':
        pass

    if form.is_valid():
        # lee archivo
        data = request.FILES['archivo'].read()
        dat = data.decode(encoding='iso-8859-1', errors='strict')

        using_db = get_thread_local('using_db', 'default')
        with transaction.atomic(using=using_db):
            contador1 = 0

            dd = str(dat).split('\n')

            if dd[-1] == '':
                dd = dd[:-1]

            lst_fila_errores = []
            lst_fila_exitos = []

            # cantidad de usuarios registrados en el sistema
            x_cantidad_user = User.objects.all().count()

            # cantidad de usuarios que bienen en el archivo
            x_cantidad_usuarios_archivo = len(dd) - 1

            # cantidad usuarios asignados por defecto
            c_cantidad_usuario_default = ClienteActivo.objects.all()[0].cac_cantempleados

            diferencia_usuarios = c_cantidad_usuario_default - x_cantidad_user

            if diferencia_usuarios >= x_cantidad_usuarios_archivo:

                try:
                    for elemento in dd:

                        contador1 += 1
                        add_error = []
                        add_dato = []
                        is_error = False

                        if contador1 > 1:
                            el = elemento.split(separacion)

                            # -------------------------------------------------
                            # - el campo  es obligatorio
                            # - el rut no contiene puntos
                            # - digito verificador valido
                            if len(el[0]) > 0:
                                rut = el[0]
                                verifica_puntos = rut.split('.')
                                digito_verificador = rut.split('-')

                                if len(verifica_puntos) > 1:
                                    add_error.append('username: El rut contiene puntos')
                                    is_error = True
                                else:
                                    if str(calculo_digito_verificador(rut)).lower() != str(
                                            digito_verificador[1]).lower():
                                        add_error.append('username: El digito verifcador no es valido')
                                        is_error = True
                                    else:
                                        add_dato.append(rut)
                            else:
                                add_error.append('El campo username es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de un correo
                            if len(el[1]) > 0:
                                correo = el[1]
                                if not valida_correo(correo):
                                    add_error.append("email: Correo invalido")
                                else:
                                    add_dato.append(correo)
                            else:
                                add_error.append('email: El campo mail es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del primer nombre
                            if len(el[2]) > 0:
                                nombres = el[2]
                                add_dato.append(nombres)
                            else:
                                add_error.append('first_name: El campo mail es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del segundo nombre
                            if len(el[3]) > 0:
                                apellidos = el[3]
                                add_dato.append(apellidos)
                            else:
                                add_error.append('last_name: El campo mail es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion tipo_rut
                            # - 1 es rut nacional
                            # - 2 es rut extranjero
                            if len(el[4]) > 0:
                                try:
                                    tipo_rut = int(el[4])
                                    if tipo_rut in [1, 2]:
                                        add_dato.append(tipo_rut)
                                    else:
                                        add_error.append(
                                            'tipo_rut: el rango del tipo_rut debe ser entre 1: rut nacional o 2: rut extranjero')
                                        is_error = True
                                except:
                                    add_error.append('tipo_rut: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('tipo_rut: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion usu_sexo
                            if len(el[5]) > 0:
                                try:
                                    usu_sexo = str(el[5]).strip()

                                    if not len(usu_sexo) > 2:
                                        if usu_sexo in ['M', 'F', 'PD']:
                                            add_dato.append(usu_sexo)
                                        else:
                                            add_error.append(
                                                'usu_sexo: las opciones son M: masculino, F:femenino, PD: por definir')
                                            is_error = True
                                    else:
                                        add_error.append('usu_sexo: no deben ser mas de dos caracteres')
                                        is_error = True
                                except:
                                    add_error.append('usu_sexo: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('usu_sexo: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del usu_fono
                            if len(el[6]) == 0 or len(el[6] <= 20):
                                usu_fono = el[6]
                                add_dato.append(usu_fono)
                            else:
                                add_error.append('usu_fono: máximo 20 caracteres')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del usu_fechanacimiento
                            # - es obligatorio
                            # - el formato debe ser de m/d/A
                            # - maximo 10 caracteres
                            if len(el[7]) > 0 and len(el[7]) <= 10:
                                if '/' in el[7]:
                                    fecha_ini = "{}-{}-{}".format(el[7].split('/')[2], el[7].split('/')[1],
                                                                  el[7].split('/')[0])
                                    try:
                                        add_dato.append(datetime.datetime.strptime(fecha_ini, '%Y-%m-%d'))
                                    except:
                                        add_error.append(
                                            'usu_fechanacimiento: el formato debe ser: mm/dd/AAAA, máximo 10 caracteres')
                                        is_error = True
                                else:
                                    add_error.append(
                                        'usu_fechanacimiento: el formato debe ser: mm/dd/AAAA, máximo 10 caracteres')
                                    is_error = True
                            else:
                                add_error.append('usu_fechanacimiento: es un campo obligatorio, máximo 10 caracteres')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del pais
                            if len(el[8]) > 0:
                                try:
                                    pais = int(el[8])
                                    add_dato.append(pais)
                                except:
                                    add_error.append('pais: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('pais: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de la region
                            if len(el[9]) > 0:
                                try:
                                    pais = int(el[9])
                                    add_dato.append(pais)
                                except:
                                    add_error.append('region: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('region: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de la comuna
                            if len(el[10]) > 0:
                                try:
                                    comuna = int(el[10])
                                    add_dato.append(comuna)
                                except:
                                    add_error.append('comuna: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('comuna: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de la usu_direccion
                            if len(el[11]) > 0:
                                usu_direccion = el[11]
                                add_dato.append(usu_direccion)
                            else:
                                add_error.append('usu_direccion: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # usu_estadocivil
                            if len(el[12]) > 0:
                                try:
                                    usu_estadocivil = str(el[12]).strip()

                                    if not len(usu_estadocivil) > 1:
                                        if usu_estadocivil in ['S', 'C', 'D', 'V']:
                                            add_dato.append(usu_estadocivil)
                                        else:
                                            add_error.append(
                                                'usu_estadocivil: valor: S=Solter@ - C=Casad@ - D=Divorsiad@ - V=Viaud@')
                                            is_error = True
                                    else:
                                        add_error.append('usu_estadocivil: no deben ser mas de un caracteres')
                                        is_error = True
                                except:
                                    add_error.append('usu_estadocivil: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('usu_estadocivil: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # usu_tipousuario
                            if len(el[13]) > 0:
                                try:
                                    usu_tipousuario = int(el[13])
                                    if usu_tipousuario in [2, 3]:
                                        add_dato.append(usu_tipousuario)
                                    else:
                                        add_error.append(
                                            'usu_tipousuario: el rango del usu_tipousuario debe ser entre valor: 2=Administrador - 3=Usuario-Sistema, numero')
                                        is_error = True
                                except:
                                    add_error.append('usu_tipousuario: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('usu_tipousuario: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - usu_profesion
                            if len(el[14]) == 0 or len(el[14]) <= 50:
                                usu_profesion = el[14]
                                add_dato.append(usu_profesion)
                            else:
                                add_error.append('usu_profesion: máximo 50 caracteres')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del cargo
                            if len(el[15]) > 0:
                                try:
                                    cargo = int(el[15])
                                    add_dato.append(cargo)
                                except:
                                    add_error.append('cargo: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('cargo: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_tipocontrato
                            if len(el[16]) > 0:
                                try:
                                    ue_tipocontrato = str(el[16]).strip()

                                    if not len(ue_tipocontrato) > 3:
                                        if ue_tipocontrato in ['CI', 'CPF', 'CIT']:
                                            add_dato.append(ue_tipocontrato)
                                        else:
                                            add_error.append(
                                                'ue_tipocontrato: valor: CI=Contrato indefinido - CPF=Contrato plazo fijo - CIT=Contrato individual de trabajo')
                                            is_error = True
                                    else:
                                        add_error.append('ue_tipocontrato: no deben ser mas de tres caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_tipocontrato: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_tipocontrato: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_tipotrabajdor
                            if len(el[17]) > 0:
                                try:
                                    ue_tipotrabajdor = str(el[17]).strip()

                                    if not len(ue_tipotrabajdor) > 1:
                                        if ue_tipotrabajdor in ['D', 'I']:
                                            add_dato.append(ue_tipotrabajdor)
                                        else:
                                            add_error.append(
                                                'ue_tipotrabajdor: valor: D=Dependiente - I=Independiente')
                                            is_error = True
                                    else:
                                        add_error.append('ue_tipotrabajdor: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_tipotrabajdor: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_tipotrabajdor: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_fechacontratacion
                            # - es obligatorio
                            # - el formato debe ser de m/d/A
                            # - maximo 10 caracteres
                            if len(el[18]) > 0 and len(el[18]) <= 10:
                                if '/' in el[18]:
                                    ue_fechacontratacion = "{}-{}-{}".format(el[18].split('/')[2], el[18].split('/')[1],
                                                                             el[18].split('/')[0])
                                    try:
                                        add_dato.append(datetime.datetime.strptime(ue_fechacontratacion, '%Y-%m-%d'))
                                    except:
                                        add_error.append(
                                            'ue_fechacontratacion: el formato debe ser: mm/dd/AAAA, máximo 10 caracteres')
                                        is_error = True
                                else:
                                    add_error.append(
                                        'ue_fechacontratacion: el formato debe ser: mm/dd/AAAA, máximo 10 caracteres')
                                    is_error = True
                            else:
                                add_error.append('ue_fechacontratacion: es un campo obligatorio, máximo 10 caracteres')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_fecharenovacioncontrato
                            # - no es obligatorio
                            # - el formato debe ser de m/d/A
                            # - maximo 10 caracteres

                            if len(el[19]) == 0:
                                add_dato.append(None)
                            else:
                                if len(el[19]) > 0 and len(el[19]) <= 10:
                                    if '/' in el[19]:
                                        ue_fecharenovacioncontrato = "{}-{}-{}".format(el[19].split('/')[2],
                                                                                       el[19].split('/')[1],
                                                                                       el[19].split('/')[0])
                                        try:
                                            add_dato.append(
                                                datetime.datetime.strptime(ue_fecharenovacioncontrato, '%Y-%m-%d'))
                                        except:
                                            add_error.append(
                                                'ue_fecharenovacioncontrato: el formato debe ser: mm/dd/AAAA, máximo 10 caracteres')
                                            is_error = True
                                    else:
                                        add_error.append(
                                            'ue_fecharenovacioncontrato: el formato debe ser: mm/dd/AAAA, máximo 10 caracteres')
                                        is_error = True
                                else:
                                    add_error.append(
                                        'ue_fecharenovacioncontrato: es un campo obligatorio, máximo 10 caracteres')
                                    is_error = True

                            # -------------------------------------------------
                            # - validacion del centrocosto
                            if len(el[20]) > 0:
                                try:
                                    centrocosto = int(el[20])
                                    add_dato.append(centrocosto)
                                except:
                                    add_error.append('centrocosto: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('centrocosto: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_movilizacion
                            if len(el[21]) > 0:
                                try:
                                    ue_movilizacion = int(el[21])
                                    add_dato.append(ue_movilizacion)
                                except:
                                    add_error.append('ue_movilizacion: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append(
                                    'ue_movilizacion: El campo es obligatorio, si no tiene dato debe ir un 0')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_colacion
                            if len(el[22]) > 0:
                                try:
                                    ue_colacion = int(el[22])
                                    add_dato.append(ue_colacion)
                                except:
                                    add_error.append('ue_colacion: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('ue_colacion: El campo es obligatorio, si no tiene dato debe ir un 0')
                                is_error = True

                            # -------------------------------------------------
                            # ue_anticipo
                            if len(el[23]) > 0:
                                try:
                                    ue_anticipo = str(el[23]).strip()

                                    if not len(ue_anticipo) > 1:
                                        if ue_anticipo in ['S', 'N']:
                                            add_dato.append(ue_anticipo)
                                        else:
                                            add_error.append('ue_anticipo: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append('ue_anticipo: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_anticipo: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_anticipo: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_montonticipo
                            if len(el[24]) > 0:
                                try:
                                    ue_montonticipo = int(el[24])
                                    add_dato.append(ue_montonticipo)
                                except:
                                    add_error.append('ue_montonticipo: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append(
                                    'ue_montonticipo: El campo es obligatorio, si no tiene dato debe ir un 0')
                                is_error = True

                            # -------------------------------------------------
                            # ue_asignacionfamiliar
                            if len(el[25]) > 0:
                                try:
                                    ue_asignacionfamiliar = str(el[25]).strip()

                                    if not len(ue_asignacionfamiliar) > 1:
                                        if ue_asignacionfamiliar in ['S', 'N']:
                                            add_dato.append(ue_asignacionfamiliar)
                                        else:
                                            add_error.append('ue_asignacionfamiliar: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append('ue_asignacionfamiliar: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_asignacionfamiliar: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_asignacionfamiliar: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_cargasfamiliares
                            if len(el[26]) > 0:
                                try:
                                    ue_cargasfamiliares = int(el[26])
                                    add_dato.append(ue_cargasfamiliares)
                                except:
                                    add_error.append('ue_cargasfamiliares: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append(
                                    'ue_cargasfamiliares: El campo es obligatorio, si no tiene dato debe ir un 0')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_montoasignacionfamiliar
                            if len(el[27]) > 0:
                                try:
                                    ue_montoasignacionfamiliar = int(el[27])
                                    add_dato.append(ue_montoasignacionfamiliar)
                                except:
                                    add_error.append('ue_montoasignacionfamiliar: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append(
                                    'ue_montoasignacionfamiliar: El campo es obligatorio, si no tiene dato debe ir un 0')
                                is_error = True

                            # -------------------------------------------------
                            # ue_sueldobase
                            if len(el[28]) > 0:
                                try:
                                    ue_sueldobase = int(el[28])
                                    add_dato.append(ue_sueldobase)
                                except:
                                    add_error.append('ue_sueldobase: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('ue_montoasignacionfamiliar: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_gratificacion
                            if len(el[29]) > 0:
                                try:
                                    ue_gratificacion = str(el[29]).strip()

                                    if not len(ue_gratificacion) > 1:
                                        if ue_gratificacion in ['S', 'N']:
                                            add_dato.append(ue_gratificacion)
                                        else:
                                            add_error.append('ue_gratificacion: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append('ue_gratificacion: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_gratificacion: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_gratificacion: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_tipogratificacion
                            if len(el[30]) > 0:
                                try:
                                    ue_tipogratificacion = str(el[30]).strip()

                                    if not len(ue_tipogratificacion) > 1:
                                        if ue_tipogratificacion in ['A', 'M']:
                                            add_dato.append(ue_tipogratificacion)
                                        else:
                                            add_error.append('ue_tipogratificacion: valor: A=Anual - M=Mensual')
                                            is_error = True
                                    else:
                                        add_error.append('ue_tipogratificacion: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_tipogratificacion: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_tipogratificacion: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_comiciones
                            if len(el[31]) > 0:
                                try:
                                    ue_comiciones = str(el[31]).strip()
                                    if not len(ue_comiciones) > 1:
                                        if ue_comiciones in ['S', 'N']:
                                            add_dato.append(ue_comiciones)
                                        else:
                                            add_error.append('ue_comiciones: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append('ue_comiciones: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_comiciones: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_comiciones: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del ue_porcentajecomicion
                            if len(el[32]) > 0:
                                try:
                                    ue_porcentajecomicion = (el[32]).replace(',', '.')
                                    ue_porcentajecomicion = float(ue_porcentajecomicion)
                                    add_dato.append(ue_porcentajecomicion)
                                except:
                                    add_error.append('ue_porcentajecomicion: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('ue_porcentajecomicion: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion del afp
                            if len(el[33]) > 0:
                                try:
                                    afp = int(el[33])
                                    add_dato.append(afp)
                                except:
                                    add_error.append('afp: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('afp: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_tieneapv
                            if len(el[34]) > 0:
                                try:
                                    ue_tieneapv = str(el[34]).strip()
                                    if not len(ue_tieneapv) > 1:
                                        if ue_tieneapv in ['S', 'N']:
                                            add_dato.append(ue_tieneapv)
                                        else:
                                            add_error.append('ue_tieneapv: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append('ue_tieneapv: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_tieneapv: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_comiciones: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_tipomontoapv
                            if len(el[35]) > 0:
                                try:
                                    ue_tipomontoapv = str(el[35]).strip()
                                    if not len(ue_tipomontoapv) > 1:
                                        if ue_tipomontoapv in ['P', 'M']:
                                            add_dato.append(ue_tipomontoapv)
                                        else:
                                            add_error.append(
                                                'ue_tipomontoapv: valor: P=Porcentaje - M=Monto, en el caso que no tenga apv dejar vacio')
                                            is_error = True
                                    else:
                                        add_error.append('ue_tipomontoapv: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_tipomontoapv: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_dato.append(None)

                            # -------------------------------------------------
                            # - validacion del afp_apv
                            if len(el[36]) > 0:
                                try:
                                    afp_apv = int(el[36])
                                    add_dato.append(afp_apv)
                                except:
                                    add_error.append('afp_apv: debe ser un número')
                                    is_error = True
                            else:
                                add_dato.append(None)

                            # -------------------------------------------------
                            # - validacion del ue_cotizacionvoluntaria
                            if len(el[37]) > 0:
                                try:
                                    ue_cotizacionvoluntaria = int(el[37])
                                    add_dato.append(ue_cotizacionvoluntaria)
                                except:
                                    add_error.append('ue_cotizacionvoluntaria: debe ser un número')
                                    is_error = True
                            else:
                                add_dato.append(None)

                            # -------------------------------------------------
                            # ue_tieneahorrovoluntario
                            if len(el[38]) > 0:
                                try:
                                    ue_tieneahorrovoluntario = str(el[38]).strip()
                                    if not len(ue_tieneahorrovoluntario) > 1:
                                        if ue_tieneahorrovoluntario in ['S', 'N']:
                                            add_dato.append(ue_tieneahorrovoluntario)
                                        else:
                                            add_error.append('ue_tieneahorrovoluntario: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append('ue_tieneahorrovoluntario: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_tieneahorrovoluntario: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_tieneahorrovoluntario: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_ahorrovoluntario
                            if len(el[39]) > 0:
                                try:
                                    ue_ahorrovoluntario = int(el[39])
                                    add_dato.append(ue_ahorrovoluntario)
                                except:
                                    add_error.append('ue_ahorrovoluntario: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append(
                                    'ue_ahorrovoluntario: El campo es obligatorio, si no tiene dato debe ir un 0')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de la salud
                            if len(el[40]) > 0:
                                try:
                                    salud = int(el[40])
                                    add_dato.append(salud)
                                except:
                                    add_error.append('salud: debeeeee ser un número')
                                    is_error = True
                            else:
                                add_error.append('salud: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de la ue_ufisapre
                            if len(el[41]) > 0:
                                try:
                                    ue_ufisapre = (el[41]).replace(',', '.')
                                    ue_ufisapre = float(ue_ufisapre)
                                    add_dato.append(ue_ufisapre)
                                except:
                                    add_error.append('ue_ufisapre: debe ser un número')
                                    is_error = True
                            else:
                                add_dato.append(0)

                            # -------------------------------------------------
                            # - validacion de la ue_funisapre
                            if len(el[42]) > 0:
                                try:
                                    ue_funisapre = int(el[42])
                                    add_dato.append(ue_funisapre)
                                except:
                                    add_error.append('ue_funisapre: debe ser un número')
                                    is_error = True
                            else:
                                add_dato.append(None)

                            # -------------------------------------------------
                            # ue_trabajopesado
                            if len(el[43]) > 0:
                                try:
                                    ue_trabajopesado = str(el[43]).strip()
                                    if not len(ue_trabajopesado) > 1:
                                        if ue_trabajopesado in ['S', 'N']:
                                            add_dato.append(ue_trabajopesado)
                                        else:
                                            add_error.append('ue_trabajopesado: valor: S=Si - N=No')
                                            is_error = True
                                    else:
                                        add_error.append(
                                            'ue_trabajopesado: no deben ser mas de 1 caracteres')
                                        is_error = True
                                except:
                                    add_error.append('ue_trabajopesado: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('ue_trabajopesado: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # - validacion de la banco
                            if len(el[44]) > 0:
                                try:
                                    banco = int(el[44])
                                    add_dato.append(banco)
                                except:
                                    add_error.append('banco: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('banco: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_formapag
                            if len(el[45]) > 0:
                                try:
                                    ue_formapag = int(el[45])
                                    if ue_formapag in [1, 2, 3]:
                                        add_dato.append(ue_formapag)
                                    else:
                                        add_error.append(
                                            'ue_formapag: valor: 1=Efectivo - 2=Cheque - 3=Depósito directo, numero')
                                        is_error = True
                                except:
                                    add_error.append('ue_formapag: debe ser un número')
                                    is_error = True
                            else:
                                add_error.append('ue_formapag: El campo es obligatorio')
                                is_error = True

                            # -------------------------------------------------
                            # ue_cuentabancaria
                            if len(el[46]) == 0 or len(el[46]) <= 50:
                                ue_cuentabancaria = el[46]
                                add_dato.append(ue_cuentabancaria)
                            else:
                                add_error.append('ue_cuentabancaria: máximo 50 caracteres')
                                is_error = True

                            # ***************************************************************************
                            if is_error:
                                add_error.append(el[0].replace('.', ''))
                                lst_fila_errores.append(add_error)
                            else:
                                lst_fila_exitos.append(add_dato)

                    errores = []
                    for e in lst_fila_exitos:
                        if not len(e) == 0:

                            existe_usuario = AsociacionUsuarioEmpresa.objects.filter(user__username=e[0]).exists()
                            using_db = get_thread_local('using_db', 'default')
                            with transaction.atomic(using=using_db):
                                if not existe_usuario:
                                    try:
                                        # *** AREA USER INI ***
                                        u = User()
                                        u.username = e[0]
                                        u.email = e[1]
                                        u.first_name = e[2]
                                        u.last_name = e[3]
                                        u.set_password(e[0])
                                        u.is_staff = False
                                        if e[13] == 2:
                                            u.is_superuser = True
                                        elif e[13] == 3:
                                            u.is_superuser = False
                                        u.save()
                                        # *** AREA USER FIN ***

                                        # *** AREA USUARIO INI ***
                                        us = Usuario()
                                        us.user = u
                                        us.usu_tiporut = e[4]
                                        us.usu_rut = e[0]
                                        us.usu_sexo = e[5]
                                        us.usu_fono = e[6]
                                        us.usu_fechanacimiento = e[7]
                                        us.pais = Pais.objects.get(pa_id=e[8])
                                        us.region = Region.objects.get(re_id=e[9])
                                        us.comuna = Comuna.objects.get(com_id=e[10])
                                        us.usu_direccion = e[11]
                                        us.usu_estadocivil = e[12]
                                        us.usu_tipousuario = e[13]
                                        us.usu_profesion = e[14]
                                        us.usu_usuarioactivo = 'S'
                                        us.usu_nombreusuario = e[0]
                                        us.usu_passwordusuario = e[0]
                                        us.save()
                                        # *** AREA USUARIO FIN ***

                                        # *** AREA USUARIO EMPRESA INI ***
                                        ue = UsuarioEmpresa()
                                        ue.user = u
                                        ue.ue_fechacreacion = datetime.datetime.now()
                                        ue.cargo = Cargo.objects.get(car_id=e[15])
                                        ue.ue_tipocontrato = e[16]
                                        ue.ue_tipotrabajdor = e[17]
                                        ue.ue_fechacontratacion = e[18]
                                        ue.ue_fecharenovacioncontrato = e[19]
                                        ue.centrocosto = CentroCosto.objects.get(cencost_id=e[20])
                                        ue.ue_movilizacion = e[21]
                                        ue.ue_colacion = e[22]
                                        ue.ue_anticipo = e[23]
                                        ue.ue_montonticipo = e[24]
                                        ue.ue_asignacionfamiliar = e[25]

                                        if e[25] == 'S':
                                            ue.ue_cargasfamiliares = e[26]
                                            ue.ue_montoasignacionfamiliar = e[27]
                                        elif e[25] == 'N':
                                            ue.ue_cargasfamiliares = None
                                            ue.ue_montoasignacionfamiliar = None

                                        ue.ue_sueldobase = e[28]
                                        ue.ue_gratificacion = e[29]

                                        if e[29] == 'S':
                                            ue.ue_tipogratificacion = e[30]
                                        elif e[29] == 'N':
                                            ue.ue_tipogratificacion = None

                                        ue.ue_comiciones = e[31]
                                        if e[31] == 'S':
                                            ue.ue_porcentajecomicion = e[32]
                                        elif e[31] == 'N':
                                            ue.ue_porcentajecomicion = None
                                        # -----------------------------
                                        ue.afp = Afp.objects.get(afp_id=e[33])

                                        ue.ue_tieneapv = e[34]

                                        if e[34] == 'S':
                                            ue.ue_tipomontoapv = e[35]
                                            ue.afp_apv = Afp.objects.get(afp_id=e[36])
                                            ue.ue_cotizacionvoluntaria = e[37]
                                        elif e[34] == 'N':
                                            ue.ue_tipomontoapv = None
                                            ue.afp_apv = None
                                            ue.ue_cotizacionvoluntaria = None

                                        ue.ue_tieneahorrovoluntario = e[38]
                                        if e[38] == 'S':
                                            ue.ue_ahorrovoluntario = e[39]
                                        elif e[38] == 'N':
                                            ue.ue_ahorrovoluntario = None
                                        # -----------------------------
                                        ue.salud = Salud.objects.get(sa_id=e[40])

                                        if not e[40] == 1:
                                            ue.ue_ufisapre = e[41]
                                            ue.ue_funisapre = e[42]

                                        ue.ue_trabajopesado = e[43]

                                        ue.banco = Bancos.objects.get(ban_id=int(e[44]))
                                        ue.ue_formapag = e[45]
                                        if e[45] == 3:
                                            ue.ue_cuentabancaria = e[46]

                                        ue.save()
                                        # *** AREA USUARIO EMPRESA FIN ***

                                        # *** AREA ASOCIACION USUARIO EMPRESA INI ***
                                        aue = AsociacionUsuarioEmpresa()
                                        aue.user = u
                                        aue.empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])
                                        aue.save()
                                        # *** AREA ASOCIACION USUARIO EMPRESA FIN ***

                                        ca = ClienteActivo.objects.get(cac_id=request.session['cliente_activo'])
                                        ruta_usuario = ca.cac_rutausuarios + us.usu_rut + '/'
                                        try:
                                            os.stat(ruta_usuario)
                                        except:
                                            os.mkdir(ruta_usuario)

                                    except Exception as inst:
                                        errores.append({
                                            'rut': e[0],
                                            'error': str(inst)
                                        })
                                        transaction.set_rollback(True, using_db)
                                else:
                                    aue = AsociacionUsuarioEmpresa.objects.filter(user__username=e[0])
                                    errores.append({
                                        'rut': e[0],
                                        'error': 'El rut ya existe en la empresa {}'.format(
                                            aue[0].empresa.emp_razonsocial.title())
                                    })

                    for x in lst_fila_errores:
                        ultimo_valor = len(x) - 1
                        rut_error = x[ultimo_valor]
                        cadena_error = ', '.join(x[:ultimo_valor])
                        errores.append({
                            'rut': rut_error,
                            'error': cadena_error
                        })

                except IndexError:
                    errores = []
                    if separacion == ';':
                        nueva_separacion = ','
                    if separacion == ',':
                        nueva_separacion = ';'

                    errores.append({
                        'rut': 'Tipo formato',
                        'error': 'Revisa el formato del documento .csv, la separación debe ser con "{}" '.format(
                            nueva_separacion)
                    })

            else:

                errores = []

                errores.append({
                    'rut': 'Cantidad de usuarios',
                    'error': "El sistema permite una cantidad total entre la/las empresa(s) de {} empleados incluyendose los administradores del sistema, <br/>actualmente tiene agregados {} empleados, por favor revise el archivo a subir. <br/>Para el caso que necesita aumentar la cantidad de empleados debe ponerese en contacto con el proveedor del sistema".format(
                        c_cantidad_usuario_default, x_cantidad_user)
                })

        return errores, lst_fila_exitos

    else:
        lista_err = []
        error = True
        for field in form:
            for error in field.errors:
                lista_err.append(field.label + ': ' + error)
                print(field.label + ': ' + error)

        return lista_err, error


@login_required
def uploadClienteProveedor(request, form, accion):
    lista_err = []
    error = False
    separacion = ''

    if request.POST['tipo-archivo'] == '1':
        separacion = ';'
    if request.POST['tipo-archivo'] == '2':
        separacion = ','
    if request.POST['tipo-archivo'] == '3':
        pass

    if form.is_valid():
        # lee archivo
        data = request.FILES['archivo'].read()
        dat = data.decode(encoding='iso-8859-1', errors='strict')

        using_db = get_thread_local('using_db', 'default')
        with transaction.atomic(using=using_db):
            contador1 = 0

            dd = str(dat).split('\n')

            if dd[-1] == '':
                dd = dd[:-1]

            lst_fila_errores = []
            lst_fila_exitos = []
            try:
                for elemento in dd:

                    contador1 += 1
                    add_error = []
                    add_dato = []
                    is_error = False

                    if contador1 > 1:
                        el = elemento.split(separacion)

                        # -------------------------------------------------
                        # - cp_rut
                        if len(el[0]) > 0:
                            cp_rut = el[0]
                            verifica_puntos = cp_rut.split('.')
                            digito_verificador = cp_rut.split('-')

                            if len(verifica_puntos) > 1:
                                add_error.append('cp_rut: El rut contiene puntos')
                                is_error = True
                            else:
                                if str(calculo_digito_verificador(cp_rut)).lower() != str(
                                        digito_verificador[1]).lower():
                                    add_error.append('cp_rut: El digito verifcador no es valido')
                                    is_error = True
                                else:
                                    add_dato.append(cp_rut)
                        else:
                            add_error.append('cp_rut: es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_razonsocial
                        if len(el[1]) > 0:
                            if len(el[1]) == 0 or len(el[1]) <= 200:
                                cp_razonsocial = el[1]
                                add_dato.append(cp_razonsocial)
                            else:
                                add_error.append('cp_razonsocial: máximo 50 caracteres')
                                is_error = True
                        else:
                            add_error.append('cp_razonsocial: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_nombrefantasia
                        if len(el[2]) > 0:
                            if len(el[2]) == 0 or len(el[2]) <= 150:
                                cp_nombrefantasia = el[2]
                                add_dato.append(cp_nombrefantasia)
                            else:
                                add_error.append('cp_nombrefantasia: máximo 150 caracteres')
                                is_error = True
                        else:
                            add_error.append('cp_nombrefantasia: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_giro
                        if len(el[3]) > 0:
                            if len(el[3]) == 0 or len(el[3]) <= 150:
                                cp_giro = el[3]
                                add_dato.append(cp_giro)
                            else:
                                add_error.append('cp_giro: máximo 150 caracteres')
                                is_error = True
                        else:
                            add_error.append('cp_giro: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_direccion
                        if len(el[4]) > 0:
                            if len(el[4]) == 0 or len(el[4]) <= 150:
                                cp_direccion = el[4]
                                add_dato.append(cp_direccion)
                            else:
                                add_error.append('cp_direccion: máximo 150 caracteres')
                                is_error = True
                        else:
                            add_error.append('cp_direccion: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_numero
                        if len(el[5]) > 0:
                            try:
                                cp_numero = int(el[5])
                                add_dato.append(cp_numero)
                            except:
                                add_error.append('cp_numero: debe ser un número')
                                is_error = True
                        else:
                            add_error.append('cp_numero: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_piso
                        if len(el[6]) > 0:
                            if len(el[6]) == 0 or len(el[6]) <= 12:
                                cp_piso = el[6]
                                add_dato.append(cp_piso)
                            else:
                                add_error.append('cp_piso: máximo 12 caracteres')
                                is_error = True
                        else:
                            add_dato.append(None)

                        # -------------------------------------------------
                        # - cp_dptooficina
                        if len(el[7]) > 0:
                            if len(el[7]) == 0 or len(el[7]) <= 25:
                                cp_dptooficina = el[7]
                                add_dato.append(cp_dptooficina)
                            else:
                                add_error.append('cp_dptooficina: máximo 25 caracteres')
                                is_error = True
                        else:
                            add_dato.append(None)

                        # -------------------------------------------------
                        # - validacion del pais
                        if len(el[8]) > 0:
                            try:
                                pais = int(el[8])
                                add_dato.append(pais)
                            except:
                                add_error.append('pais: debe ser un número')
                                is_error = True
                        else:
                            add_error.append('pais: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - validacion de la region
                        if len(el[9]) > 0:
                            try:
                                pais = int(el[9])
                                add_dato.append(pais)
                            except:
                                add_error.append('region: debe ser un número')
                                is_error = True
                        else:
                            add_error.append('region: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - validacion de la comuna
                        if len(el[10]) > 0:
                            try:
                                comuna = int(el[10])
                                add_dato.append(comuna)
                            except:
                                add_error.append('comuna: debe ser un número')
                                is_error = True
                        else:
                            add_error.append('comuna: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - validacion de un correo
                        if len(el[11]) > 0:
                            cp_email = el[11]
                            if not valida_correo(cp_email):
                                add_error.append("cp_email: Correo invalido")
                            else:
                                add_dato.append(cp_email)
                        else:
                            add_error.append('cp_email: El campo mail es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cp_fono
                        if len(el[12]) == 0 or len(el[12]) <= 20:
                            cp_fono = el[12]
                            add_dato.append(cp_fono)
                        else:
                            add_error.append('cp_fono: máximo 25 caracteres')
                            is_error = True

                        if accion == 'C':
                            # -------------------------------------------------
                            # - cpe_tipocliente
                            if len(el[13]) > 0:
                                try:
                                    cpe_tipocliente = str(el[13]).strip()

                                    if not len(cpe_tipocliente) > 1:
                                        if cpe_tipocliente in ['N', 'C', 'P', 'E']:
                                            add_dato.append(cpe_tipocliente)
                                        else:
                                            add_error.append(
                                                'cpe_tipocliente: valor: N=No - C=Nacional - P=Prospecto - E=Extranjero,  texto')
                                            is_error = True
                                    else:
                                        add_error.append('cpe_tipocliente: no deben ser mas de un caracteres')
                                        is_error = True
                                except:
                                    add_error.append('cpe_tipocliente: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('cpe_tipocliente: El campo es obligatorio')
                                is_error = True

                        elif accion == 'P':
                            # -------------------------------------------------
                            # - cpe_tipoproveedor
                            if len(el[13]) > 0:
                                try:
                                    cpe_tipoproveedor = str(el[13]).strip()

                                    if not len(cpe_tipoproveedor) > 1:
                                        if cpe_tipoproveedor in ['N', 'P', 'H', 'E', 'A']:
                                            add_dato.append(cpe_tipoproveedor)
                                        else:
                                            add_error.append(
                                                'cpe_tipoproveedor: valor: N=No - P=Nacional - H=Honorario - E=Extranjero - A=Agente de Aduana,  texto')
                                            is_error = True
                                    else:
                                        add_error.append('cpe_tipoproveedor: no deben ser mas de un caracteres')
                                        is_error = True
                                except:
                                    add_error.append('cpe_tipoproveedor: debe ser tipo texto')
                                    is_error = True
                            else:
                                add_error.append('cpe_tipoproveedor: El campo es obligatorio')
                                is_error = True

                        elif accion == 'A':
                            add_dato.append('N')

                        # -------------------------------------------------
                        # - validacion de la banco
                        if len(el[14]) > 0:
                            try:
                                banco = int(el[14])
                                add_dato.append(banco)
                            except:
                                add_error.append('banco: debe ser un número')
                                is_error = True
                        else:
                            add_error.append('banco: El campo es obligatorio')
                            is_error = True

                        # -------------------------------------------------
                        # - cpe_tipocuenta
                        if len(el[15]) > 0:
                            try:
                                cpe_tipocuenta = str(el[15]).strip()

                                if not len(cpe_tipocuenta) > 1:
                                    if cpe_tipocuenta in ['1', '2', '3', '4']:
                                        add_dato.append(cpe_tipocuenta)
                                    else:
                                        add_error.append(
                                            'cpe_tipocuenta: valor: 1=Cuenta vista - 2=Cuenta de ahorro - 3=Cuenta corriente - 4=Vale vista,  numero')
                                        is_error = True
                                else:
                                    add_error.append('cpe_tipocuenta: no deben ser mas de un caracteres')
                                    is_error = True
                            except:
                                add_error.append('cpe_tipocuenta: debe ser tipo texto')
                                is_error = True
                        else:
                            add_error.append('cpe_tipocuenta: El campo es obligatorio')
                            is_error = True
                        # ***************************************************************************

                    if is_error:
                        add_error.append(el[0].replace('.', ''))
                        lst_fila_errores.append(add_error)
                    else:
                        lst_fila_exitos.append(add_dato)

                errores = []
                for e in lst_fila_exitos:
                    if not len(e) == 0:
                        try:
                            emp = Empresa.objects.get(emp_id=request.session['la_empresa'])
                            existe_cliente_proveedor_empresa = ClienteProveedorEmpresa.objects.filter(
                                clienteProveedor__cp_rut=e[0], empresa=emp,
                                clienteProveedor__cp_tipoentidad=accion).exists()
                            using_db = get_thread_local('using_db', 'default')
                            with transaction.atomic(using=using_db):
                                if not existe_cliente_proveedor_empresa:

                                    cp = ClienteProveedor()

                                    cp.cp_rut = e[0]
                                    cp.cp_razonsocial = e[1]
                                    cp.cp_nombrefantasia = e[2]
                                    cp.cp_giro = e[3]
                                    cp.cp_direccion = e[4]
                                    cp.cp_numero = e[5]
                                    cp.cp_piso = e[6]
                                    cp.cp_dptooficina = e[7]
                                    cp.pais = Pais.objects.get(pa_id=e[8])
                                    cp.region = Region.objects.get(re_id=e[9])
                                    cp.comuna = Comuna.objects.get(com_id=e[10])
                                    cp.cp_email = e[11]
                                    cp.cp_fono = e[12]
                                    cp.cp_tipoentidad = accion

                                    cp.save()

                                    cpe = ClienteProveedorEmpresa()
                                    cpe.clienteProveedor = cp
                                    cpe.empresa = emp
                                    if accion == 'C':
                                        cpe.cpe_tipocliente = e[13]
                                        cpe.cpe_tipoproveedor = None
                                    if accion == 'P':
                                        cpe.cpe_tipocliente = None
                                        cpe.cpe_tipoproveedor = e[13]
                                    if accion == 'A':
                                        cpe.cpe_tipocliente = None
                                        cpe.cpe_tipoproveedor = None
                                    cpe.banco = Bancos.objects.get(ban_id=int(e[14]))
                                    cpe.cpe_tipocuenta = e[15]
                                    cpe.save()
                                else:
                                    # raise Exception('El rut {} ya existe en esta empresa'.format(e[0]))
                                    errores.append({
                                        'rut': e[0],
                                        'error': 'El {} ya existe en la empresa {}'.format(
                                            elige_choices(ClienteProveedor.TIPO_ENTIDAD, accion).lower(),
                                            request.session['razon_social'])
                                    })
                                    transaction.set_rollback(True, using_db)

                        except Exception as inst:
                            errores.append({
                                'rut': e[0],
                                'error': str(inst)
                            })

                for x in lst_fila_errores:
                    ultimo_valor = len(x) - 1
                    rut_error = x[ultimo_valor]
                    cadena_error = ', '.join(x[:ultimo_valor])
                    errores.append({
                        'rut': rut_error,
                        'error': cadena_error
                    })
            except IndexError:
                errores = []
                if separacion == ';':
                    nueva_separacion = ','
                if separacion == ',':
                    nueva_separacion = ';'

                errores.append({
                    'rut': 'Tipo formato',
                    'error': 'Revisa el formato del documento .csv, la separación debe ser con "{}" '.format(
                        nueva_separacion)
                })
        return errores, lst_fila_exitos

    else:
        lista_err = []
        error = True
        for field in form:
            for error in field.errors:
                lista_err.append(field.label + ': ' + error)
                print(field.label + ': ' + error)

        return lista_err, error
