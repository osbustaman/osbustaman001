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

from clienteproveedor.models import ClienteProveedorEmpresa
from configuracion.forms import CargaLogoPorEmpresaForm
from jab.decoradores import existe_empresa, cargo_empresa, centro_costo_empresa
from jab.settings import UPLOAD_DIR_FOTO
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

from usuario.models import Empresa, Pais, Region, Comuna, AsociacionUsuarioEmpresa, \
    RelacionDeAfiliacion, Sucursal, Usuario, UsuarioEmpresa, Afp, Salud, Cargo, CargoEmpresa, CentroCosto, \
    GrupoCentroCosto, Haberes

from configuracion.models import Parametros, ClienteActivo

from perfil.models import Menu, MenuItem

from usuario.form import UsuarioForm, CargaFotoUsuario, HaberesForm, HaberesDescuentosForm

from empresa.forms import EmpresasForm, RelacionForm, SucursalForm, UserForm, UsuarioEmpresaForm, LeyesSocialesForm, \
    RemuneracionEmpleadoForm, MenuEmpleadoForm, CargoForm, CargoEmpresaForm, CentroCostoForm, GrupoCentroCostoForm, \
    DataCicloVidaCertificadoAmonestacionAnexosEquiposSeguridadForm, TerminoRelacionLaboralForm, OtrosForm

from documento.models import Documento, TipoDocumentos

from jab.views import elige_choices, formatear_numero


@login_required
def views_empresa(request):
    """
    Funcion que inicializa la vista que muestra la pantalla que muestra el listado de empresas
    :param request: variables de session
    :return: recursos_humanos/empresa.html
    """
    lst_empresas = Empresa.objects.all().exclude(emp_activa='N')

    data = {
        'las_empresas': lst_empresas,
    }
    return render(request, 'panelcontrol/empresa.html', data)


# -------------------------------------
@login_required
def add_empresa(request):
    """
    Funcion que agrega empresas
    :param variable de sesion
    :return data
        frmEmpresa: form para agregar empresa
        lista_err : listado con errores en el caso que existan
        error : variable que avisa que existe error
        add_emp : TRUE no permite mostrar los tabs
    """
    lista_err = []
    error = False
    if request.POST:

        la_empresa = Empresa.objects.all()

        # este if valida que no se agregue una empresa con mismo rut
        if la_empresa.filter(emp_rut=request.POST['emp_rut']).exists():
            lista_err.append('Rut empresa: El rut de esta empresa ya existe ')
            error = True
            frm = EmpresasForm(request.POST or None)
        else:
            frm = EmpresasForm(request.POST)
            if frm.is_valid():
                form = frm.save(commit=False)
                # form.usuario  = User.objects.get(id = request.POST['usuario_id'])
                form.pais = Pais.objects.get(pa_id=request.POST['pais'])
                form.region = Region.objects.get(re_id=request.POST['region'])
                form.comuna = Comuna.objects.get(com_id=request.POST['comuna'])

                # en el caso que exista una empresa madre, el input siempre se carga en N
                # ya que solo debe existir una empresa principal
                if la_empresa.filter(emp_isholding='S').exists():
                    form.emp_isholding = 'N'
                else:
                    form.emp_isholding = 'S'

                form.save()

                cambiarEmpresa(request, form.emp_id)

                s = Sucursal()

                s.suc_codigo = 'S110'
                s.suc_descripcion = 'Casa matriz'
                s.empresa = form
                s.suc_direccion = "{} {}".format(form.emp_direccion, form.emp_numero)
                s.pais = form.pais
                s.region = form.region
                s.comuna = form.comuna

                s.save()

                # crear_documentos_laborales(form)

                # aqui redirecciona al momento de crear un documento, se redirecciona a la funcion de edita
                return redirect('bases:views_empresa')
            else:
                error = True
                for field in frm:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)
                for er in lista_err:
                    print(er)
    else:
        frm = EmpresasForm()

        # en el caso que exista una empresa madre, el input siempre se carga en N
        # ya que solo debe existir una empresa principal
        is_principal = Empresa.objects.filter(emp_isholding='S').exists()
        if is_principal:
            frm.fields['emp_isholding'].initial = 'N'
            frm.fields['emp_isholding'].widget.attrs["disabled"] = True
        else:
            frm.fields['emp_isholding'].initial = 'S'

    data = {
        'frmEmpresa': frm,
        'lista_err': lista_err,
        'error': error,
        'add_emp': True
    }
    return render(request, 'panelcontrol/add_empresa.html', data)


# -------------------------------------
@login_required
def edit_empresa(request, id_emp):
    """
    Funcion para editar una empresa
    :param id_emp id de la empresa que se desea editar, el funcionamiento es similar al de add_empresa
    :return data
        frmEmpresa: form para agregar empresa
        lista_err : listado con errores en el caso que existan
        error : variable que avisa que existe error
        add_emp : FALSE permite mostrar los tabs
        lst_relaciones: listado el cual entrega las relaciones de entidades que estan asociadas a la empresa
    """

    lista_err = []
    lst_relaciones = []
    error = False

    empresa = Empresa.objects.get(emp_id=id_emp)
    rutaImagen = empresa.emp_generadorrutalogo.replace('\\', '/')

    frm = EmpresasForm(request.POST or None, instance=empresa)
    if request.POST:
        if frm.is_valid():
            form = frm.save(commit=False)
            # form.usuario  = User.objects.get(id = request.POST['usuario_id'])
            form.pais = Pais.objects.get(pa_id=request.POST['pais'])
            form.region = Region.objects.get(re_id=request.POST['region'])
            form.comuna = Comuna.objects.get(com_id=request.POST['comuna'])
            form.save()
            # aqui redirecciona al momento de crear un documento, se redirecciona a la funcion de edita
            return redirect('bases:views_empresa')
        else:
            error = True
            for field in frm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
    else:

        # en el caso que exista una empresa madre, el input siempre se carga en N
        # ya que solo debe existir una empresa principal
        is_principal = Empresa.objects.filter(emp_isholding='S', emp_activa='S').exists()
        if is_principal:
            frm.fields['emp_isholding'].initial = 'N'
            frm.fields['emp_isholding'].widget.attrs["disabled"] = True
        else:
            frm.fields['emp_isholding'].initial = 'S'

    relaciones = RelacionDeAfiliacion.objects.filter(empresa=empresa)
    contador = 0
    for r in relaciones:
        contador += 1
        if r.rda_tipoafiliacion == 'IPS':
            nombre = r.rda_inp.title()
        if r.rda_tipoafiliacion == 'MUT':
            nombre = elige_choices(RelacionDeAfiliacion.MUTUALES, r.rda_tipoatipomutual)
        if r.rda_tipoafiliacion == 'CCAF':
            nombre = r.cajascompensacion.cc_nombre.title()

        lst_relaciones.append({
            'rda_tipoafiliacion': elige_choices(RelacionDeAfiliacion.TIPO_AFILIACION, r.rda_tipoafiliacion),
            'nombre': nombre,
            'contador': contador,
            'rda_id': r.rda_id,
            'id_emp': r.empresa_id
        })

    las_sucursales = Sucursal.objects.filter(empresa=empresa).exclude(suc_estado='N')

    """
    debe mostrar todos los usuarios incluyendo usuario con estado E con
    excepción el super-usuario
    """
    lst_usuarios = []
    los_usuarios = AsociacionUsuarioEmpresa.objects.filter(empresa=empresa).exclude(aue_activo='N')

    contador = 0
    for u in los_usuarios:
        if not u.user.is_staff:
            contador += 1

            el_u = Usuario.objects.get(user=u.user)

            lst_usuarios.append({
                'contador': contador,
                'first_name': u.user.first_name.title(),
                'last_name': u.user.last_name.title(),
                'email': u.user.email,
                'usu_rut': el_u.usu_rut,
                'id': u.user.id,
                'id_emp': u.empresa.emp_id,
                'nombre_emp': u.empresa.emp_razonsocial.title(),
            })

    request.session['ruta_volver_p'] = reverse('bases:edit_empresa', args=[empresa.emp_id])

    lst_cargos = []
    emp = Empresa.objects.get(emp_id=request.session['la_empresa'])
    los_cargos = CargoEmpresa.objects.filter(empresa=emp)

    contador = 0
    for c in los_cargos:
        contador += 1
        lst_cargos.append({
            'car_id': c.cargo.car_id,
            'car_nombre': c.cargo.car_nombre,
            'care_empresa_id': c.empresa.emp_id,
            'care_nombre_emp': c.empresa.emp_razonsocial,
            'contador': contador,
        })

    lst_GrupoCentroCosto = []
    emp = Empresa.objects.get(emp_id=request.session['la_empresa'])
    gCentroCostos = GrupoCentroCosto.objects.filter(empresa=emp).exclude(gcencost_activo='N')

    contador = 0
    for g in gCentroCostos:
        contador += 1
        lst_GrupoCentroCosto.append({
            'gcencost_id': g.gcencost_id,
            'gcencost_nombre': g.gcencost_nombre,
            'gcencost_codigo': g.gcencost_codigo,
            'gcencost_activo': elige_choices(GrupoCentroCosto.OPCIONES, g.gcencost_activo),
            'empresa': g.empresa.emp_razonsocial,
            'contador': contador,
        })
    frmCargaLogoPorEmpresaForm = CargaLogoPorEmpresaForm()
    data = {
        'frmEmpresa': frm,
        'frmCargaLogoPorEmpresaForm': frmCargaLogoPorEmpresaForm,
        'lista_err': lista_err,
        'error': error,
        'add_emp': False,
        'lst_relaciones': lst_relaciones,
        'id_emp': id_emp,
        'emp_razonsocial': empresa.emp_razonsocial.title(),
        'las_sucursales': las_sucursales,
        'lst_usuarios': lst_usuarios,
        'contador': contador,
        'lst_cargos': lst_cargos,
        'lst_GrupoCentroCosto': lst_GrupoCentroCosto,
        'rutaImagen': rutaImagen,
    }
    return render(request, 'panelcontrol/add_empresa.html', data)


# -------------------------------------
@csrf_exempt
@login_required
def remove_empresa(request):
    """
    funcion que cambia el estado de la empresa a no activa, de esa forma no se borra y no se muestra en
    la lista
    :param id_emp (int): id de la empresa
    """
    is_error = 0
    mensaje = ''
    empresa = Empresa.objects.get(emp_id=request.POST['id_emp'])
    cantidad_usuario = AsociacionUsuarioEmpresa.objects.filter(empresa=empresa).count()
    cantidad_cliente_proveedor = ClienteProveedorEmpresa.objects.filter(empresa=empresa).count()

    if (int(cantidad_usuario) + int(cantidad_cliente_proveedor)) > 0:

        mensaje = "No se puede borrar la empresa, ya que tiene empleados o clientes/proveedores o ambas entidades asociadas"
        is_error = 1
    else:
        empresa.emp_activa = 'N'
        empresa.save()
        return redirect('recursos_humanos_namespace:views_empresa')

    html = {
        'mensaje': mensaje,
        'is_error': is_error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def subirLogoPorEmpresa(request, emp_id):
    ca = ClienteActivo.objects.get(cac_id=request.session['cliente_activo'])
    lista_err = []
    error = False
    frmCargaLogoPorEmpresaForm = CargaLogoPorEmpresaForm(request.POST or None)

    if request.method == "POST":

        empresa = Empresa.objects.get(emp_id=emp_id)

        archivoUpload = request.FILES['archivo']
        fileName, fileExtension = os.path.splitext(request.FILES['archivo'].name)
        fileName = str(fileName).replace('-', '').split(' ')
        fileName = '{}_{}{}'.format(empresa.emp_rut, time.strftime("%H%M%S"), fileExtension)
        contenido_file = (ca.cac_rutadstatic + '/' + fileName).replace('\\', '/')

        empresa.emp_rutalogo = "/static/{}/".format(ca.cac_nombrebase)
        empresa.emp_nombreimagen = fileName
        empresa.save()

        with open(contenido_file, 'wb+') as destination:
            for chunk in request.FILES['archivo'].chunks():
                destination.write(chunk)
        destination.close()

    return redirect('bases:edit_empresa', emp_id)


# -------------------------------------
@login_required
def bajarExcelEmpresas(request):
    hoy = datetime.datetime.now()

    filename = "listados_de_empresas_{}.xls".format(hoy.strftime("%d%m%Y_%H%M%S"))
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Hoja 1')
    # Sheet header, first row
    row_num = 0
    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    text_style = xlwt.Style.easyxf("font: bold on; align: wrap on, vert centre, horiz center")

    ws.write(row_num, 0, 'Código', font_style)
    ws.write(row_num, 1, 'Rut', font_style)
    ws.write(row_num, 2, 'Razón social', font_style)
    ws.write(row_num, 3, 'Giro', font_style)
    ws.write(row_num, 4, 'Dirección', font_style)
    ws.write(row_num, 5, 'Número', font_style)
    ws.write(row_num, 6, 'Piso', font_style)
    ws.write(row_num, 7, 'Dpto/Oficina', font_style)
    ws.write(row_num, 8, 'Pais', font_style)
    ws.write(row_num, 9, 'Region', font_style)
    ws.write(row_num, 10, 'Comuna', font_style)
    ws.write(row_num, 11, 'Mail', font_style)
    ws.write(row_num, 12, 'Fono', font_style)

    xEmpresa = Empresa.objects.all().exclude(emp_activa='N')

    for x in xEmpresa:
        row_num += 1
        ws.write(row_num, 0, x.emp_codigo)
        ws.write(row_num, 1, x.emp_rut)
        ws.write(row_num, 2, x.emp_razonsocial)
        ws.write(row_num, 3, x.emp_giro)
        ws.write(row_num, 4, x.emp_direccion)
        ws.write(row_num, 5, x.emp_numero)
        ws.write(row_num, 6, x.emp_piso)
        ws.write(row_num, 7, x.emp_dptooficina)
        ws.write(row_num, 8, x.pais.pa_nombre)
        ws.write(row_num, 9, x.region.re_nombre)
        ws.write(row_num, 10, x.comuna.com_nombre)
        ws.write(row_num, 11, x.emp_mailuno)
        ws.write(row_num, 12, x.emp_fonodos)

    wb.save(response)
    return response


# -------------------------------------
@login_required
def cambiarEmpresa(request, id_emp):
    # **************************************************
    # AREA DE LAS SESSIONES
    # **************************************************
    empresa = Empresa.objects.get(emp_id=id_emp)

    request.session['la_empresa'] = empresa.emp_id
    request.session['razon_social'] = empresa.emp_razonsocial

    next = request.META.get('HTTP_REFERER', None) or '/'
    response = HttpResponseRedirect(next)

    view, args, kwargs = resolve(urlparse(next)[2])
    kwargs['request'] = request

    try:
        view(*args, **kwargs)
    except Http404:
        return HttpResponseRedirect('/')
    return response


# -------------------------------------
@login_required
def add_relacion(request, id_emp):
    """
    la relacion es la entidad que se asocia a la empresa, en dopnde se definen las mutuales,
    cajas de compensacion e INP (IPS)
    :param id_emp (int): id de la empresa
    """
    lista_err = []
    error = False
    eleccion = ''

    frm = RelacionForm(request.POST or None)
    la_empresa = Empresa.objects.get(emp_id=id_emp)
    if request.POST:

        if request.POST['nosave'] == 'off':
            eleccion = request.POST['rda_tipoafiliacion']

            if eleccion == 'IPS':
                frm.fields['rda_inp'].required = True

            if eleccion == 'MUT':
                frm.fields['rda_tipoatipomutual'].required = True
                frm.fields['rda_porcentajemutual'].required = True

            if eleccion == 'CCAF':
                frm.fields['cajascompensacion'].required = True
        else:
            if frm.is_valid():
                form = frm.save(commit=False)
                form.empresa = la_empresa
                form.save()
                # aqui redirecciona al momento de crear un documento, se redirecciona a la funcion de edita
                return redirect('bases:edit_empresa', id_emp)
            else:
                error = True
                for field in frm:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)

    data = {
        'id_emp': id_emp,
        'frmRelacion': frm,
        'eleccion': eleccion,
        'lista_err': lista_err,
        'error': error,
        'emp_razonsocial': la_empresa.emp_razonsocial.title()
    }
    return render(request, 'panelcontrol/add_relacion.html', data)


# -------------------------------------
@login_required
def edit_relacion(request, id_emp, id_relacion):
    lista_err = []
    error = False
    eleccion = ''

    relacion = RelacionDeAfiliacion.objects.get(rda_id=id_relacion)
    frm = RelacionForm(request.POST or None, instance=relacion)
    la_empresa = Empresa.objects.get(emp_id=id_emp)

    if request.POST:

        if request.POST['nosave'] == 'off':
            eleccion = request.POST['rda_tipoafiliacion']

            if eleccion == 'IPS':
                frm.fields['rda_inp'].required = True

            if eleccion == 'MUT':
                frm.fields['rda_tipoatipomutual'].required = True
                frm.fields['rda_porcentajemutual'].required = True

            if eleccion == 'CCAF':
                frm.fields['cajascompensacion'].required = True
        else:
            if frm.is_valid():
                form = frm.save(commit=False)
                form.empresa = la_empresa
                form.save()
                # aqui redirecciona al momento de crear un documento, se redirecciona a la funcion de edita
                return redirect('bases:edit_empresa', id_emp)
            else:
                error = True
                for field in frm:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)

    eleccion = relacion.rda_tipoafiliacion

    data = {
        'id_emp': id_emp,
        'frmRelacion': frm,
        'eleccion': eleccion,
        'lista_err': lista_err,
        'error': error,
        'emp_razonsocial': la_empresa.emp_razonsocial.title()
    }
    return render(request, 'panelcontrol/add_relacion.html', data)


# -------------------------------------
@login_required
def remove_relacion(request, id_emp, id_relacion):
    relacion = RelacionDeAfiliacion.objects.get(rda_id=id_relacion)
    relacion.delete()
    return redirect('bases:edit_empresa', id_emp)


# -------------------------------------
@login_required
def add_sucursal(request, id_emp):
    frm_sucursalForm = SucursalForm(request.POST or None)
    la_empresa = Empresa.objects.get(emp_id=id_emp)
    if request.POST:
        if frm_sucursalForm.is_valid():
            form = frm_sucursalForm.save(commit=False)
            form.empresa = la_empresa
            form.save()
            return redirect('bases:edit_empresa', id_emp)
        else:
            lista_err = []
            for field in frm_sucursalForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)
    data = {
        'frm_sucursalForm': frm_sucursalForm,
        'id_emp': id_emp,
        'emp_razonsocial': la_empresa.emp_razonsocial.title()
    }
    return render(request, 'panelcontrol/add_sucursal.html', data)


# -------------------------------------
@login_required
def edit_sucursal(request, id_emp, suc_id):
    s = Sucursal.objects.get(suc_id=suc_id)
    frm_sucursalForm = SucursalForm(request.POST or None, instance=s)
    la_empresa = Empresa.objects.get(emp_id=id_emp)
    if request.POST:
        if frm_sucursalForm.is_valid():
            form = frm_sucursalForm.save(commit=False)
            form.save()
            return redirect('bases:edit_empresa', id_emp)
        else:
            lista_err = []
            for field in frm_sucursalForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)

    data = {
        'frm_sucursalForm': frm_sucursalForm,
        'id_emp': id_emp,
        'emp_razonsocial': la_empresa.emp_razonsocial.title()
    }
    return render(request, 'panelcontrol/add_sucursal.html', data)


# -------------------------------------
@login_required
def delete_sucursal(request, id_emp, id_suc):
    s = Sucursal.objects.get(suc_id=id_suc)
    s.suc_estado = 'N'
    s.save()
    return redirect('bases:edit_empresa', id_emp)


# -------------------------------------
@login_required
@cargo_empresa
@centro_costo_empresa
def add_personal(request, id_emp):
    request.session['boton_volver_ver_ficha_empleado'] = False
    lista_err = []
    error = False
    frmUserForm = UserForm(request.POST or None)

    # frmUserForm.fields['username'].widget.attrs["data-inputmask"] = False
    # frmUserForm.fields['username'].widget.attrs["data-inputmask"] = '"mask": "99.999.999-*"'
    frmUserForm.fields['empresa'].initial = id_emp

    la_empresa = Empresa.objects.get(emp_id=id_emp)

    data = {
        'frmUserForm': frmUserForm,
        'lista_err': lista_err,
        'is_edit': False,
        'error': error,
        'funcion': 'addDatosUsuario()',
        'empresa_id': id_emp,
        'emp_razonsocial': la_empresa.emp_razonsocial.title(),

    }

    return render(request, 'panelcontrol/add_empleado.html', data)


# -------------------------------------
def edit_personal(request, id_usuario, id_empresa):
    """
    :param id_emp: id de la empresa
    :param id_usuario: id del usuario
    :return: retorna un diccionario con datos como el formulario
    """
    lista_err = []
    error = False
    tipoEntidad = ""
    formaPago = ""

    data_user = User.objects.get(id=id_usuario)
    nombre_usuario = ("{} {}".format(data_user.first_name, data_user.last_name)).title()

    data_empresa = Empresa.objects.get(emp_id=id_empresa)

    data_usuario = Usuario.objects.get(user=data_user)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    data_asociacion = AsociacionUsuarioEmpresa.objects.filter(user=data_user, empresa=data_empresa)

    isApv = data_user_emp.ue_tieneapv
    isAhorroVoluntario = data_user_emp.ue_tieneahorrovoluntario

    tieneAignacionFamiliar = data_user_emp.ue_asignacionfamiliar

    # **********************************************
    # DATOS PERSONALES
    frmDatosPersonales = UsuarioForm(request.POST or None, instance=data_usuario)

    # **********************************************
    # DATOS PRIMERA PESTANIA
    frmUserForm = UserForm(request.POST or None, instance=data_user)
    frmUserForm.fields['username'].widget.attrs["readonly"] = True

    frmUserForm.fields['password1'].initial = data_usuario.usu_passwordusuario
    frmUserForm.fields['password1'].require = False

    frmUserForm.fields['password2'].initial = data_usuario.usu_passwordusuario
    frmUserForm.fields['password2'].require = False

    frmUserForm.fields['usu_tipousuario'].initial = data_usuario.usu_tipousuario

    notPassword = False
    if data_usuario.usu_tipousuario == 3:
        frmUserForm.fields['password1'].widget.attrs["readonly"] = True
        frmUserForm.fields['password2'].widget.attrs["readonly"] = True
        notPassword = True

    frmUserForm.fields['empresa'].initial = data_empresa.emp_id

    frmUserForm.fields['username'].widget.attrs["data-inputmask"] = False
    frmUserForm.fields['username'].widget.attrs["data-inputmask"] = '"mask": "99.999.999-*"'

    frmUserForm.fields['empresa'].initial = id_empresa

    # **********************************************
    # DATOS EMPRESA

    # **********************************************
    # DATOS LABORALES
    frmUsuarioEmpresaForm = UsuarioEmpresaForm(request.POST or None, instance=data_user_emp)

    frmUsuarioEmpresaForm.fields['sucursal'].initial = data_asociacion[0].sucursal

    if data_user_emp.ue_formapago == 3:
        frmUsuarioEmpresaForm.fields['banco'].widget.attrs["disabled"] = False
        frmUsuarioEmpresaForm.fields['ue_cuentabancaria'].widget.attrs["readonly"] = False
        frmUsuarioEmpresaForm.fields['cargo'].queryset = CargoEmpresa.objects.filter(empresa=data_empresa)
        frmUsuarioEmpresaForm.fields['cargo'].to_field_name = 'care_id'
        formaPago = data_user_emp.ue_formapago

    # **********************************************
    # DATOS LEYES SOCIALES
    frmLeyesSocialesForm = LeyesSocialesForm(request.POST or None, instance=data_usuario)

    try:
        frmLeyesSocialesForm.fields['afp'].initial = data_user_emp.afp
        frmLeyesSocialesForm.fields['salud'].initial = data_user_emp.salud

        data_afp = Afp.objects.get(afp_id=data_user_emp.afp)

        frmLeyesSocialesForm.fields['ue_sis'].initial = data_afp.afp_sis
        frmLeyesSocialesForm.fields['afp_porcentaje'].initial = data_afp.afp_tasatrabajadordependiente
        frmLeyesSocialesForm.fields['afp_codigo'].initial = data_afp.afp_codigoprevired

        data_salud = Salud.objects.get(sa_id=data_user_emp.salud)
        frmLeyesSocialesForm.fields['sa_codigo'].initial = data_salud.sa_codigo

        if data_salud.sa_tipo == 'F':
            tipoEntidad = 'FONASA'
            parametros = Parametros.objects.get(param_codigo='FONASA')
            frmLeyesSocialesForm.fields['ue_cotizacion'].initial = parametros.param_valor

        else:
            tipoEntidad = 'ISAPRE'
            frmLeyesSocialesForm.fields['ue_ufisapre'].initial = data_user_emp.ue_ufisapre
            frmLeyesSocialesForm.fields['ue_funisapre'].initial = data_user_emp.ue_funisapre
            frmLeyesSocialesForm.fields['ue_cotizacion'].initial = data_user_emp.ue_cotizacion

        frmLeyesSocialesForm.fields['ue_ahorrovoluntario'].initial = data_user_emp.ue_ahorrovoluntario
        frmLeyesSocialesForm.fields['ue_cotizacionvoluntaria'].initial = data_user_emp.ue_cotizacionvoluntaria

        if data_user_emp.ue_tieneapv == 'S':
            frmLeyesSocialesForm.fields['afp_apv'].widget.attrs["disabled"] = False
            frmLeyesSocialesForm.fields['ue_tipomontoapv'].widget.attrs["disabled"] = False
            frmLeyesSocialesForm.fields['ue_cotizacionvoluntaria'].widget.attrs["readonly"] = False

            frmLeyesSocialesForm.fields['ue_tieneapv'].initial = data_user_emp.ue_tieneapv
            frmLeyesSocialesForm.fields['afp_apv'].initial = data_user_emp.afp_apv
            frmLeyesSocialesForm.fields['ue_tipomontoapv'].initial = data_user_emp.ue_tipomontoapv

        if data_user_emp.ue_tieneahorrovoluntario == 'S':
            frmLeyesSocialesForm.fields['ue_ahorrovoluntario'].widget.attrs["readonly"] = False

            frmLeyesSocialesForm.fields['ue_tieneahorrovoluntario'].initial = data_user_emp.ue_tieneahorrovoluntario
            frmLeyesSocialesForm.fields['ue_ahorrovoluntario'].initial = data_user_emp.ue_ahorrovoluntario
    except:
        pass

    # **********************************************
    # DATOS REMUNERACION EMPLEADO
    frmRemuneracionEmpleadoForm = RemuneracionEmpleadoForm(request.POST or None, instance=data_usuario)
    frmHaberes = HaberesForm()

    frmRemuneracionEmpleadoForm.fields['ue_movilizacion'].initial = int(data_user_emp.ue_movilizacion)
    frmRemuneracionEmpleadoForm.fields['ue_colacion'].initial = int(data_user_emp.ue_colacion)
    frmRemuneracionEmpleadoForm.fields['ue_sueldobase'].initial = int(data_user_emp.ue_sueldobase)
    frmRemuneracionEmpleadoForm.fields['ue_gratificacion'].initial = data_user_emp.ue_gratificacion
    frmRemuneracionEmpleadoForm.fields['ue_segurodesempleo'].initial = data_user_emp.ue_segurodesempleo
    frmRemuneracionEmpleadoForm.fields['ue_porempleado'].initial = data_user_emp.ue_porempleado
    frmRemuneracionEmpleadoForm.fields['ue_porempleador'].initial = data_user_emp.ue_porempleador
    frmRemuneracionEmpleadoForm.fields['ue_comiciones'].initial = data_user_emp.ue_comiciones
    frmRemuneracionEmpleadoForm.fields['ue_porcentajecomicion'].initial = data_user_emp.ue_porcentajecomicion
    frmRemuneracionEmpleadoForm.fields['ue_anticipo'].initial = data_user_emp.ue_anticipo
    frmRemuneracionEmpleadoForm.fields['ue_montonticipo'].initial = data_user_emp.ue_montonticipo

    frmMenuEmpleadoForm = MenuEmpleadoForm()

    # **********************************************
    # DATOS IMAGEN EMPLEADO
    frmCargaFotoUsuario = CargaFotoUsuario()

    # **********************************************
    # CICLO DE VIDA Y OTROS
    data_dcpvcaaes = DataCicloVidaCertificadoAmonestacionAnexosEquiposSeguridadForm(request.POST or None,
                                                                                    instance=data_usuario)

    data_dcpvcaaes.fields['ue_prestamo'].initial = data_user_emp.ue_prestamo
    data_dcpvcaaes.fields['ue_cuotas'].initial = data_user_emp.ue_cuotas
    data_dcpvcaaes.fields['ue_certificado'].initial = data_user_emp.ue_certificado
    data_dcpvcaaes.fields['ue_amonestacion'].initial = data_user_emp.ue_amonestacion
    data_dcpvcaaes.fields['ue_entregaequiposeguridad'].initial = data_user_emp.ue_entregaequiposeguridad
    data_dcpvcaaes.fields['ue_anexocontrato'].initial = data_user_emp.ue_anexocontrato

    # **********************************************
    # TERMINO RELACION LABORAL

    frmTerminoRelacionLaboralForm = TerminoRelacionLaboralForm(request.POST or None, instance=data_usuario)

    frmTerminoRelacionLaboralForm.fields[
        'ue_fechanotificacioncartaaviso'].initial = data_user_emp.ue_fechanotificacioncartaaviso
    frmTerminoRelacionLaboralForm.fields['ue_fechatermino'].initial = data_user_emp.ue_fechatermino
    frmTerminoRelacionLaboralForm.fields['ue_cuasal'].initial = data_user_emp.ue_cuasal
    frmTerminoRelacionLaboralForm.fields['ue_fundamento'].initial = data_user_emp.ue_fundamento
    frmTerminoRelacionLaboralForm.fields['ue_tiponoticacion'].initial = data_user_emp.ue_tiponoticacion

    # **********************************************
    # OTROS
    frmOtrosForm = OtrosForm(request.POST or None, instance=data_usuario)

    frmOtrosForm.fields['ue_otros'].initial = data_user_emp.ue_otros

    # **********************************************
    # HABERE Y DESCUENTOS
    frmHaberesDescuentosForm = HaberesDescuentosForm(request.POST)

    lstMenuItemes = []
    try:
        elMenu = Menu.objects.get(usuario=data_user)
        mItems = MenuItem.objects.filter(menu=elMenu)
        contador = 1
        for m in mItems:
            lstMenuItemes.append({
                'contador': contador,
                'men_ite_id': m.men_ite_id,
                'item': m.item,
                'estado': m.men_ite_estado
            })
            contador += 1
    except:
        pass

    # fecha de hoy
    anio = datetime.datetime.now().year

    lstHaberes = []
    xHaberes = Haberes.objects.filter(empresa=data_empresa, user=data_user).exclude(hab_activo='N').order_by('-hab_id')
    contador = 0
    for x in xHaberes:
        contador += 1
        lstHaberes.append({
            'contador': contador,
            'hab_id': x.hab_id,
            'hab_nombre': x.hab_nombre,
            'hab_monto': formatear_numero(x.hab_monto, 0),
            'hab_tipo': elige_choices(Haberes.TIPO, x.hab_tipo),
            'hab_tipo_clave': x.hab_tipo,
        })

    lstHaberesDescuentos = []
    xHaberesDescuentos = Haberes.objects.filter(empresa=data_empresa, user=data_user,
                                                hab_tipo='F').exclude(hab_activo='N').order_by(
        'hab_id')
    contador = 0
    suma_haberes = 0
    suma_descuentos = 0
    for y in xHaberesDescuentos:
        haberes = 0
        descuentos = 0
        if y.hab_tipohaberdescuento == 'H':
            haberes = formatear_numero(y.hab_monto, 0)
            suma_haberes += float(haberes.replace(',', '').replace('.', ''))
        else:
            descuentos = formatear_numero(y.hab_monto, 0)
            suma_descuentos += float(descuentos.replace(',', '').replace('.', ''))

        contador += 1
        lstHaberesDescuentos.append({
            'contador': contador,
            'hab_id': y.hab_id,
            'hab_nombre': y.hab_nombre,
            'haberes': haberes,
            'descuentos': descuentos,
            'hab_tipo': elige_choices(Haberes.FINIQUITO, y.hab_tipohaberdescuento),
            'hab_tipo_clave': y.hab_tipohaberdescuento,
        })

    total_haberes_descuentos = suma_haberes - suma_descuentos

    data = {
        'is_edit': True,
        'user_id': data_user.id,
        'id_usuario': id_usuario,
        'empresa_id': data_empresa.emp_id,
        'frmUserForm': frmUserForm,
        'frmDatosPersonales': frmDatosPersonales,
        'frmUsuarioEmpresaForm': frmUsuarioEmpresaForm,
        'frmLeyesSocialesForm': frmLeyesSocialesForm,
        'frmRemuneracionEmpleadoForm': frmRemuneracionEmpleadoForm,
        'frmMenuEmpleadoForm': frmMenuEmpleadoForm,
        'frmCargaFotoUsuario': frmCargaFotoUsuario,
        'funcion': 'editDatosUsuario({}, {})'.format(id_usuario, id_empresa),
        'nombre_usuario': nombre_usuario,
        'tipoEntidad': tipoEntidad,
        'formaPago': formaPago,
        'lstMenuItemes': lstMenuItemes,
        'emp_razonsocial': data_empresa.emp_razonsocial.title(),
        'anioActual': anio,
        'anioAnterior': int(anio - 1),
        'tieneAignacionFamiliar': tieneAignacionFamiliar,
        'notPassword': notPassword,
        'frmHaberes': frmHaberes,
        'lstHaberes': lstHaberes,
        'data_dcpvcaaes': data_dcpvcaaes,
        'frmTerminoRelacionLaboralForm': frmTerminoRelacionLaboralForm,
        'frmOtrosForm': frmOtrosForm,
        'frmHaberesDescuentosForm': frmHaberesDescuentosForm,
        'lstHaberesDescuentos': lstHaberesDescuentos,
        'total_haberes_descuentos': formatear_numero(total_haberes_descuentos, 0),
        'suma_haberes': formatear_numero(suma_haberes, 0),
        'suma_descuentos': formatear_numero(suma_descuentos, 0),
        'usu_tiporut': data_usuario.usu_tiporut,
    }

    return render(request, 'panelcontrol/add_empleado.html', data)


# -------------------------------------
@csrf_exempt
@login_required
def ajax_add_haberes(request, usu_id):
    lista_err = []
    xerror = False
    cantidad = 0

    if request.POST:
        frmHaberes = HaberesForm(request.POST)
        if frmHaberes.is_valid():

            xEmpresa = Empresa.objects.get(emp_id=request.session['la_empresa'])
            xUser = User.objects.get(id=usu_id)

            form = frmHaberes.save(commit=False)
            form.empresa = xEmpresa
            form.user = xUser
            form.save()
            cantidad = Haberes.objects.filter(empresa=xEmpresa, user=xUser).order_by('-hab_id')
            cantidad = cantidad.count()
        else:
            xerror = True
            for field in frmHaberes:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
    html = {
        'error': xerror,
        'lista_err': lista_err,
        'cantidad': cantidad,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


# -------------------------------------
@csrf_exempt
@login_required
def ajax_edit_haberes(request, hab_id):
    lista_err = []
    xerror = False
    tipo = ''
    xtipo = ''

    if request.POST:
        xHaber = Haberes.objects.get(hab_id=hab_id)
        frmHaberes = HaberesForm(request.POST or None, instance=xHaber)
        if frmHaberes.is_valid():
            form = frmHaberes.save(commit=False)
            form.save()

            tipo = form.hab_tipo
            xtipo = elige_choices(Haberes.TIPO, tipo).upper()

        else:
            xerror = True
            for field in frmHaberes:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
    html = {
        'error': xerror,
        'lista_err': lista_err,
        'tipo': tipo,
        'xtipo': xtipo,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


# -------------------------------------
@csrf_exempt
@login_required
def ajax_delete_haberes(request, hab_id):
    xHaber = Haberes.objects.get(hab_id=hab_id)
    xHaber.hab_activo = 'N'
    xHaber.save()

    html = {
        'mensaje': 'OK'
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


# -------------------------------------
def remove_personal(request, id_usuario, id_emp):
    usuario = Usuario.objects.get(user=id_usuario)
    usuario.usu_usuarioactivo = 'E'
    usuario.save()

    aue = AsociacionUsuarioEmpresa.objects.get(user=id_usuario, empresa=id_emp)
    aue.aue_activo = 'N'
    aue.save()
    return redirect('bases:edit_empresa', id_emp)


# -------------------------------------
@login_required
def add_cargo(request, id_emp):
    lista_err = []
    frm_cargoForm = CargoForm(request.POST or None)
    frm_cargoEmpresaForm = CargoEmpresaForm(request.POST or None)

    frm_cargoEmpresaForm.fields['empresa'].initial = request.session['la_empresa']
    frm_cargoEmpresaForm.fields['empresa'].widget.attrs["disabled"] = True

    if request.POST:
        if frm_cargoForm.is_valid() and frm_cargoEmpresaForm.is_valid():

            la_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])

            form1 = frm_cargoForm.save(commit=False)
            form1.save()

            form2 = frm_cargoEmpresaForm.save(commit=False)
            form2.cargo = form1
            form2.empresa = la_empresa
            form2.save()
            return redirect('bases:edit_empresa', id_emp)
        else:
            for field in frm_cargoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for field in frm_cargoEmpresaForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)
    data = {
        'frm_cargoForm': frm_cargoForm,
        'frm_cargoEmpresaForm': frm_cargoEmpresaForm,
        'id_emp': id_emp,
    }
    return render(request, 'panelcontrol/add_cargo.html', data)


# -------------------------------------
@login_required
def edit_cargo(request, car_id, id_emp):
    lista_err = []

    la_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])
    el_cargo = Cargo.objects.get(car_id=car_id)

    el_cargo_empresa = CargoEmpresa.objects.get(cargo=el_cargo, empresa=la_empresa)

    frm_cargoForm = CargoForm(request.POST or None, instance=el_cargo)
    frm_cargoEmpresaForm = CargoEmpresaForm(request.POST or None, instance=el_cargo_empresa)

    frm_cargoEmpresaForm.fields['empresa'].initial = request.session['la_empresa']
    frm_cargoEmpresaForm.fields['empresa'].widget.attrs["disabled"] = True

    if request.POST:
        if frm_cargoForm.is_valid() and frm_cargoEmpresaForm.is_valid():
            form1 = frm_cargoForm.save(commit=False)
            form1.save()

            el_cargo_empresa.cargo = el_cargo
            el_cargo_empresa.empresa = la_empresa
            el_cargo_empresa.save()

            return redirect('bases:edit_empresa', id_emp)
    data = {
        'frm_cargoForm': frm_cargoForm,
        'frm_cargoEmpresaForm': frm_cargoEmpresaForm,
        'id_emp': id_emp,
    }
    return render(request, 'panelcontrol/add_cargo.html', data)


# -------------------------------------
@login_required
def delete_cargo(request, car_id, id_emp):
    la_empresa = Empresa.objects.get(emp_id=id_emp)
    el_cargo = Cargo.objects.get(car_id=car_id)
    c = CargoEmpresa.objects.get(cargo=el_cargo, empresa=la_empresa)
    c.delete()
    return redirect('bases:edit_empresa', id_emp)


# -------------------------------------
@existe_empresa
@login_required
def views_grupos_centro_costo(request):
    lst_GrupoCentroCosto = []
    emp = Empresa.objects.get(emp_id=request.session['la_empresa'])
    gCentroCostos = GrupoCentroCosto.objects.filter(empresa=emp).exclude(gcencost_activo='N')

    contador = 0
    for g in gCentroCostos:
        contador += 1
        lst_GrupoCentroCosto.append({
            'gcencost_id': g.gcencost_id,
            'gcencost_nombre': g.gcencost_nombre,
            'gcencost_codigo': g.gcencost_codigo,
            'gcencost_activo': elige_choices(GrupoCentroCosto.OPCIONES, g.gcencost_activo),
            'empresa': g.empresa.emp_razonsocial,
            'contador': contador,
        })

    data = {
        'lst_GrupoCentroCosto': lst_GrupoCentroCosto,
        'contador': contador,
    }
    return render(request, 'panelcontrol/grupo_centro_costo.html', data)


@login_required
def add_grupo_centro_costo(request, id_emp):
    lista_err = []
    frm_gCentrocCostoForm = GrupoCentroCostoForm(request.POST or None)

    frm_gCentrocCostoForm.fields['empresa'].initial = request.session['la_empresa']
    frm_gCentrocCostoForm.fields['empresa'].widget.attrs["disabled"] = True

    if request.POST:
        print("request.POST:", request.POST)
        la_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])

        if frm_gCentrocCostoForm.is_valid():
            form = frm_gCentrocCostoForm.save(commit=False)
            form.empresa = la_empresa
            form.save()

            return redirect('bases:edit_empresa', id_emp)
        else:
            for field in frm_gCentrocCostoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)
    data = {
        'frm_gCentrocCostoForm': frm_gCentrocCostoForm,
        'lista_err': lista_err,
        'id_emp': id_emp,
    }
    return render(request, 'panelcontrol/add_grupocentrocosto.html', data)


# -------------------------------------
@login_required
def edit_grupo_centro_costo(request, gcencost_id, id_emp):
    lista_err = []
    gcc = GrupoCentroCosto.objects.get(gcencost_id=gcencost_id)

    frm_gCentrocCostoForm = GrupoCentroCostoForm(request.POST or None, instance=gcc)

    frm_gCentrocCostoForm.fields['empresa'].initial = request.session['la_empresa']
    frm_gCentrocCostoForm.fields['empresa'].widget.attrs["disabled"] = True

    if request.POST:

        la_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])

        if frm_gCentrocCostoForm.is_valid():
            form = frm_gCentrocCostoForm.save(commit=False)
            form.empresa = la_empresa
            form.save()

            return redirect('bases:edit_empresa', id_emp)
        else:
            for field in frm_gCentrocCostoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)

    lst_CentroCosto = []
    cCostos = CentroCosto.objects.filter(grupocentrocosto=gcc).exclude(cencost_activo='N')

    contador = 0
    for c in cCostos:
        contador += 1
        lst_CentroCosto.append({
            'cencost_id': c.cencost_id,
            'cencost_nombre': c.cencost_nombre,
            'cencost_codigo': c.cencost_codigo,
            'cencost_activo': elige_choices(CentroCosto.OPCIONES, c.cencost_activo),
            'contador': contador,
        })

    data = {
        'frm_gCentrocCostoForm': frm_gCentrocCostoForm,
        'lista_err': lista_err,
        'is_edit': True,
        'lst_CentroCosto': lst_CentroCosto,
        'nombre_gcce': "Grupo centro costo " + gcc.gcencost_nombre.title(),
        'gcencost_id': gcc.gcencost_id,
        'id_emp': id_emp,
    }
    return render(request, 'panelcontrol/add_grupocentrocosto.html', data)


# -------------------------------------
@login_required
def delete_grupo_centro_costo(request, gcencost_id, id_emp):
    el_gCentroCosto = GrupoCentroCosto.objects.get(gcencost_id=gcencost_id)
    el_gCentroCosto.gcencost_activo = 'N'
    el_gCentroCosto.save()
    return redirect('bases:edit_empresa', id_emp)


# -------------------------------------
@login_required
def add_centro_costo(request, gcencost_id):
    lista_err = []
    frm_cCostoForm = CentroCostoForm(request.POST or None)
    gcc = GrupoCentroCosto.objects.get(gcencost_id=gcencost_id)

    if request.POST:

        if frm_cCostoForm.is_valid():
            form = frm_cCostoForm.save(commit=False)
            form.grupocentrocosto = gcc
            form.save()

            return redirect('bases:edit_grupo_centro_costo', gcc.gcencost_id, gcc.empresa.emp_id)
        else:
            for field in frm_cCostoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)
    data = {
        'frm_cCostoForm': frm_cCostoForm,
        'gcencost_id': gcc.gcencost_id,
        'nombre_gcce': "Grupo centro costo " + gcc.gcencost_nombre.title(),
        'id_emp': gcc.empresa.emp_id,
    }
    return render(request, 'panelcontrol/add_ccosto.html', data)


# -------------------------------------
@login_required
def edit_centro_costo(request, gcencost_id, cencost_id):
    lista_err = []

    gcc = GrupoCentroCosto.objects.get(gcencost_id=gcencost_id)
    el_cCosto = CentroCosto.objects.get(cencost_id=cencost_id)
    frm_cCostoForm = CentroCostoForm(request.POST or None, instance=el_cCosto)

    if request.POST:
        if frm_cCostoForm.is_valid():

            form = frm_cCostoForm.save(commit=False)
            form.grupocentrocosto = gcc
            form.save()

            return redirect('bases:edit_grupo_centro_costo', gcc.gcencost_id, gcc.empresa.emp_id)
        else:
            for field in frm_cCostoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)

            for er in lista_err:
                print(er)
    data = {
        'frm_cCostoForm': frm_cCostoForm,
        'gcencost_id': gcc.gcencost_id,
        'nombre_gcce': "Grupo centro costo " + gcc.gcencost_nombre.title(),
        'id_emp': gcc.empresa.emp_id,
    }
    return render(request, 'panelcontrol/add_ccosto.html', data)


# -------------------------------------
@login_required
def delete_centro_costo(request, gcencost_id, cencost_id):
    el_cCosto = CentroCosto.objects.get(cencost_id=cencost_id)
    el_cCosto.cencost_activo = 'N'
    el_cCosto.save()
    return redirect('bases:edit_grupo_centro_costo', gcencost_id)


# ------------------------------------
@existe_empresa
@login_required
def views_cargos(request):
    lst_cargos = []
    emp = Empresa.objects.get(emp_id=request.session['la_empresa'])
    los_cargos = CargoEmpresa.objects.filter(empresa=emp)

    contador = 0
    for c in los_cargos:
        contador += 1
        lst_cargos.append({
            'car_id': c.cargo.car_id,
            'car_nombre': c.cargo.car_nombre,
            'care_empresa_id': c.empresa.emp_id,
            'care_nombre_emp': c.empresa.emp_razonsocial,
            'contador': contador,
        })

    data = {
        'lst_cargos': lst_cargos,
        'contador': contador,
    }
    return render(request, 'panelcontrol/cargos.html', data)
