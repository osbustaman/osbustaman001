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

from clienteproveedor.forms import ClienteProveedorForm, ClienteProveedorEmpresaForm
from configuracion.models import TablaGeneral
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

from jab.views import elige_choices

from clienteproveedor.models import ClienteProveedor, ClienteProveedorEmpresa
from usuario.models import Empresa


@login_required
def viewsClientesProveedores(request, entidad=''):
    """
    debe mostrar todos los clientes proveedores del sistema
    """
    lstClientesProveedores = []

    if entidad in ['C', 'P']:
        xClienteProveedor = ClienteProveedor.objects.filter(cp_tipoentidad=entidad).exclude(cp_estado='N')
    else:
        xClienteProveedor = ClienteProveedor.objects.all().exclude(cp_estado='N')

    contador = 0
    for x in xClienteProveedor:
        contador += 1
        lstClientesProveedores.append({
            'contador': contador,
            'cp_id': x.cp_id,
            'cp_rut': x.cp_rut,
            'cp_razonsocial': x.cp_razonsocial,
            'estado': elige_choices(ClienteProveedor.OPCIONES, x.cp_estado),
            'cp_estado': x.cp_estado,
            'cp_tipoentidad': elige_choices(ClienteProveedor.TIPO_ENTIDAD, x.cp_tipoentidad),
        })
    data = {
        'lstClientesProveedores': lstClientesProveedores,
        'filtro': entidad,
    }
    return render(request, 'panelcontrol/viewsClientesProveedores.html', data)


@login_required
def addClienteProveedor(request):
    """
    formulario para crear un cliente/proveedor
    """

    lista_err = []
    error = False
    form = ClienteProveedorForm(request.POST or None)

    if request.POST:

        if form.is_valid():
            frm = form.save(commit=False)
            frm.save()
            return redirect('bases:viewsClientesProveedores')

        else:
            error = True
            for field in form:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    data = {
        'form': form,
        'error': error,
        'lista_err': lista_err,
    }
    return render(request, 'panelcontrol/add_cliente_proveedor.html', data)


@login_required
def editClienteProveedor(request, cp_id):
    """
    formulario para crear un cliente/proveedor
    """

    lista_err = []
    lstClientesProveedoresEmpresa = []
    error = False
    objectCliProv = ClienteProveedor.objects.get(cp_id=cp_id)
    nombre_empresa = objectCliProv.cp_razonsocial
    form = ClienteProveedorForm(request.POST or None, instance=objectCliProv)

    if request.POST:

        if form.is_valid():
            frm = form.save(commit=False)
            frm.save()

        else:
            error = True
            for field in form:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    xClienteProveedorEmpresa = ClienteProveedorEmpresa.objects.filter(clienteProveedor=objectCliProv).exclude(
        cpe_estado='N')

    contador = 0
    for x in xClienteProveedorEmpresa:
        contador += 1
        lstClientesProveedoresEmpresa.append({
            'contador': contador,
            'cpe_id': x.cpe_id,
            'empresa': x.empresa.emp_razonsocial,
            'cpe_tipocliente': elige_choices(ClienteProveedorEmpresa.TIPO_CLI_CHOICES, x.cpe_tipocliente),
            'cpe_tipoproveedor': elige_choices(ClienteProveedorEmpresa.TIPO_PROV_CHOICES, x.cpe_tipoproveedor),
            'estado': elige_choices(ClienteProveedorEmpresa.OPCIONES, x.cpe_estado),
            'cpe_estado': x.cpe_estado,
        })

    data = {
        'form': form,
        'error': error,
        'lista_err': lista_err,
        'is_edit': True,
        'lstClientesProveedoresEmpresa': lstClientesProveedoresEmpresa,
        'cp_id': cp_id,
        'nombre_empresa': nombre_empresa,
        'contador': contador,
    }
    return render(request, 'panelcontrol/add_cliente_proveedor.html', data)


@login_required
def addClienteProveedorEmpresa(request, cp_id):
    """
    formulario para crear un cliente/proveedor empresa
    """

    lista_err = []
    error = False
    cliProv = ClienteProveedor.objects.get(cp_id=cp_id)
    form = ClienteProveedorEmpresaForm(request.POST or None)

    if request.POST:

        if form.is_valid():
            frm = form.save(commit=False)
            frm.clienteProveedor = ClienteProveedor.objects.get(cp_id=cp_id)
            frm.empresa = Empresa.objects.get(emp_id=request.POST['empresa'])
            frm.cpe_estado = 'S'
            frm.save()
            return redirect('bases:editClienteProveedor', cp_id)

        else:
            error = True
            for field in form:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    data = {
        'form': form,
        'error': error,
        'lista_err': lista_err,
        'cp_id': cp_id,
        'tipo_cliente': cliProv.cp_tipoentidad,
        'cp_razonsocial': cliProv.cp_razonsocial.lower(),
        'cp_tipoentidad': elige_choices(ClienteProveedor.TIPO_ENTIDAD, cliProv.cp_tipoentidad),
    }
    return render(request, 'panelcontrol/add_cliente_proveedor_empresa.html', data)


@login_required
def editClienteProveedorEmpresa(request, cp_id, cpe_id):
    """
    formulario para crear un cliente/proveedor empresa
    """

    lista_err = []
    error = False
    cliProv = ClienteProveedor.objects.get(cp_id=cp_id)

    cliProvEmp = ClienteProveedorEmpresa.objects.get(cpe_id=cpe_id)

    form = ClienteProveedorEmpresaForm(request.POST or None, instance=cliProvEmp)

    if request.POST:

        if form.is_valid():
            frm = form.save(commit=False)
            frm.clienteProveedor = ClienteProveedor.objects.get(cp_id=cp_id)
            frm.empresa = Empresa.objects.get(emp_id=request.POST['empresa'])
            frm.cpe_estado = 'S'
            frm.save()
            return redirect('bases:editClienteProveedor', cp_id)

        else:
            error = True
            for field in form:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    data = {
        'form': form,
        'error': error,
        'lista_err': lista_err,
        'cp_id': cp_id,
        'tipo_cliente': cliProv.cp_tipoentidad,
        'cp_razonsocial': cliProv.cp_razonsocial.lower(),
        'cp_tipoentidad': elige_choices(ClienteProveedor.TIPO_ENTIDAD, cliProv.cp_tipoentidad),
    }
    return render(request, 'panelcontrol/add_cliente_proveedor_empresa.html', data)


@csrf_exempt
@login_required
def borrarClienteProveedor(request):
    """
    borrar cliente proveedor
    :param request:
    :param cp_id: id del cliente proveedor
    :param estado:
    :return:
    """
    cp_id = request.POST['cp_id']
    estado = request.POST['estado']
    error = False
    textoError = ""

    cp = ClienteProveedor.objects.get(cp_id=cp_id)
    objectClienteProveedorEmpresa = ClienteProveedorEmpresa.objects.filter(clienteProveedor=cp, cpe_estado='S')
    existAsociacion = objectClienteProveedorEmpresa.exists()
    can_cp_emp = objectClienteProveedorEmpresa.count()

    if not existAsociacion:
        cp.cp_estado = 'N'
        cp.save()
    else:
        textoError = 'No se puede borrar ya que el {} {} tiene empresas asociadas'.format(
            elige_choices(ClienteProveedor.TIPO_ENTIDAD, cp.cp_tipoentidad).lower(), cp.cp_razonsocial.lower())
        error = True

    html = {
        'error_mensaje': textoError,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def borrarClienteProveedorEmpresa(request, cpe_id, estado):
    """
    borrar cliente proveedor
    :param request:
    :param cp_id: id del cliente proveedor
    :param estado:
    :return:
    """
    cpem = ClienteProveedorEmpresa.objects.get(cpe_id=cpe_id)

    if estado == 'S':
        cpem.cpe_estado = 'N'
    elif estado == 'N':
        cpem.cpe_estado = 'S'
    cpem.save()
    return redirect('bases:editClienteProveedor', cpem.clienteProveedor_id)
