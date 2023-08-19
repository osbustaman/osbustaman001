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

from django.contrib.auth.models import User
from datetime import timedelta

from jab.decoradores import existe_empresa
from jab.settings import BASE_DIR, STATICFILES_DIRS
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
import stat

from configuracion.models import Parametros, ClienteActivo, Moneda

from configuracion.forms import ParametrosForm, CargaLogoEmpresaForm, MonedaForm

from usuario.models import Empresa, Usuario, Pais

from documento.models import Documento, TipoDocumentos

from documento.forms import TipoDocumentosForm, DocumentoForm

from jab.views import elige_choices


@login_required
def views_parametros(request):
    """
    debe mostrar todos los parametros del sistema
    """
    lst_parametros = []
    los_parametros = Parametros.objects.all()

    contador = 0
    for p in los_parametros:
        contador += 1
        lst_parametros.append({
            'contador': contador,
            'param_id': p.param_id,
            'param_codigo': p.param_codigo,
            'param_descripcion': p.param_descripcion,
            'param_valor': p.param_valor,
            'param_factor': p.param_factor,
            'param_activo': p.param_activo,
            'is_activo': elige_choices(Parametros.OPCIONES, p.param_activo),
        })
    data = {
        'lst_parametros': lst_parametros,
        'contador': contador,
    }
    return render(request, 'panelcontrol/parametros.html', data)


@login_required
def addParametros(request):
    lista_err = []
    error = False

    frmParametrosForm = ParametrosForm(request.POST or None)

    if frmParametrosForm.is_valid():
        frm = frmParametrosForm.save(commit=False)
        frm.save()
        return redirect('bases:views_parametros')
    else:
        error = True
        for field in frmParametrosForm:
            for error in field.errors:
                lista_err.append(field.label + ': ' + error)
        for er in lista_err:
            print(er)

    data = {
        'error': error,
        'lista_err': lista_err,
        'frmParametrosForm': frmParametrosForm,
    }
    return render(request, 'panelcontrol/add_parametros.html', data)


@login_required
def editarParametros(request, parametro_id):
    lista_err = []
    error = False

    parametro = Parametros.objects.get(param_id=parametro_id)

    activo = parametro.param_activo

    frmParametrosForm = ParametrosForm(request.POST or None, instance=parametro)

    if frmParametrosForm.is_valid():
        frm = frmParametrosForm.save(commit=False)
        frm.save()
        return redirect('bases:views_parametros')
    else:
        error = True
        for field in frmParametrosForm:
            for error in field.errors:
                lista_err.append(field.label + ': ' + error)
        for er in lista_err:
            print(er)

    data = {
        'error': error,
        'lista_err': lista_err,
        'frmParametrosForm': frmParametrosForm,
        'activo': activo,
        'is_edit': True,
    }
    return render(request, 'panelcontrol/add_parametros.html', data)


@login_required
def borrarParametros(request, parametro_id, estado):
    param = Parametros.objects.get(param_id=parametro_id)
    if estado == 'S':
        param.param_activo = 'N'
    elif estado == 'N':
        param.param_activo = 'S'
    param.save()
    return redirect('bases:views_parametros')


@login_required
def errorcuatrocientostres(request):
    data = {
        'mensaje': 'la petición es correcta pero el servidor se niega a ofrecerle el recurso o página web. Ya que debe existir a lo menos una empresa ingresada'
    }
    return render(request, 'panelcontrol/error/error_403.html', data)


@login_required
def decoradorCentroCostoError403(request):
    data = {
        'mensaje': 'la petición es correcta pero el servidor se niega a ofrecerle el recurso o página web. Ya que debe existir a lo menos un centro coste asociado a la empresa'
    }
    return render(request, 'panelcontrol/error/error_403.html', data)


@login_required
def decoradorCargoError403(request):
    data = {
        'errorc': 'la petición es correcta pero el servidor se niega a ofrecerle el recurso o página web. Ya que debe existir a lo menos un cargo asociado a la empresa'
    }
    return render(request, 'panelcontrol/error/error_403_cargo.html', data)


@login_required
def errorcuatrocientoscuatro(request):
    data = {
        'mensaje': ''
    }
    return render(request, 'panelcontrol/error/error_404.html', data)


@csrf_exempt
@login_required
def ajaxFiltroPorEmpresa(request):
    lst_empresas = []

    docEmpresas = Documento.objects.filter(empresa__emp_id=request.POST['pk'],
                                           tipoDocumentos__tdl_id=request.POST['doc'])

    for x in docEmpresas:
        lst_empresas.append({
            'emp_id': x.empresa.emp_id,
            'doc_id': x.doc_id,
            'emp_codigo': x.empresa.emp_codigo,
            'emp_razonsocial': x.empresa.emp_razonsocial.upper(),
            'doc_nombre': x.doc_nombre.upper(),
        })

    html = {
        'lst_empresas': lst_empresas,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def views_config_empresa(request):
    ca = ClienteActivo.objects.get(cac_id=request.session['cliente_activo'])

    ruta_imagen = "/static/{}/{}".format(ca.cac_nombrebase, ca.cac_nombreimagenlogo)
    request.session['x_ruta_imagen'] = ruta_imagen

    frmCargaLogoEmpresa = CargaLogoEmpresaForm(request.POST or None)

    if request.method == "POST":
        archivoUpload = request.FILES['archivo']
        fileName, fileExtension = os.path.splitext(request.FILES['archivo'].name)
        fileName = str(fileName).replace('-', '').split(' ')
        fileName = '{}_{}{}'.format(ca.cac_nombrebase, time.strftime("%H%M%S"), fileExtension)
        contenido_file = (ca.cac_rutadstatic + '/' + fileName).replace('\\', '/')

        ca.cac_nombreimagenlogo = fileName
        ca.save()

        with open(contenido_file, 'wb+') as destination:
            for chunk in request.FILES['archivo'].chunks():
                destination.write(chunk)
        destination.close()

        return redirect('bases:views_config_empresa')

    frmCargaLogoEmpresa.fields['cac_rutabase'].initial = ca.cac_rutabase
    frmCargaLogoEmpresa.fields['cac_rutadocumentos'].initial = ca.cac_rutadocumentos
    frmCargaLogoEmpresa.fields['cac_rutausuarios'].initial = ca.cac_rutausuarios

    lstMonedas = []
    for x in Moneda.objects.all().exclude(mon_activa='N'):
        lstMonedas.append({
            'mon_id': x.mon_id,
            'mon_simbolo': x.mon_simbolo,
            'mon_cantidaddecimales': x.mon_cantidaddecimales,
            'mon_descripcion': x.mon_descripcion,
            'mon_activa': elige_choices(Moneda.OPCIONES, x.mon_activa),
        })

    lstPaises = []
    contador_p = 0
    for x in Pais.objects.all():
        contador_p += 1
        lstPaises.append({
            'contador_p': contador_p,
            'pa_id': x.pa_id,
            'pa_nombre': x.pa_nombre,
            'pa_codigo': x.pa_codigo,
        })

    data = {
        'frmCargaLogoEmpresa': frmCargaLogoEmpresa,
        'ruta_imagen': ruta_imagen,
        'lstMonedas': lstMonedas,
        'lstPaises': lstPaises,
    }
    return render(request, 'panelcontrol/configuracion_empresa.html', data)


@login_required
def views_add_moneda(request):
    lista_err = []
    is_error = False

    if request.POST:
        frmMoneda = MonedaForm(request.POST or None)

        if frmMoneda.is_valid():
            frm = frmMoneda.save(commit=False)
            frm.save()
            return redirect('bases:views_edit_moneda', frm.mon_id, '1')
        else:
            is_error = True
            for field in frmMoneda:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
    else:
        frmMoneda = MonedaForm()

    data = {
        'frmMoneda': frmMoneda,
        'error': is_error,
        'lista_err': lista_err,
    }
    return render(request, 'panelcontrol/add_moneda.html', data)


@login_required
def views_edit_moneda(request, mon_id, flag):
    lista_err = []
    error = False
    is_save = False

    xMoneda = Moneda.objects.get(mon_id=mon_id)
    frmMoneda = MonedaForm(request.POST or None, instance=xMoneda)

    if request.POST:
        if frmMoneda.is_valid():
            frm = frmMoneda.save(commit=False)
            frm.save()
            is_save = True
        else:
            error = True
            for field in frmMoneda:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    data = {
        'frmMoneda': frmMoneda,
        'error': error,
        'lista_err': lista_err,
        'is_save': is_save,
        'is_edit': True,
        'flag': flag,
    }
    return render(request, 'panelcontrol/add_moneda.html', data)
