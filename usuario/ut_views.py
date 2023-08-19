# -*- encoding: utf-8 -*-
import distutils.core
from django.shortcuts import render_to_response, render, redirect
from django.template import RequestContext, Context
from django.http import HttpResponseRedirect
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
from datetime import datetime, date
from django.utils import timezone
from django.contrib import auth
from decimal import *

from hashlib import sha1
from jab.settings import UPLOAD_DIR_FOTO, BASE_COMMAND, STATICFILES_DIRS
from jab.threadlocal import get_thread_local
from django.db import transaction
import json
import xlrd
import xlwt
import collections
import shutil
import os
import time
import datetime
import sys
import locale

from configuracion.models import Parametros, ClienteActivo
from jab.views import formatear_numero, elige_choices

from usuario.models import Usuario, Empresa, AsociacionUsuarioEmpresa, Afp, Salud, UsuarioEmpresa, Pais, \
    Region, Comuna, Cargo, CentroCosto, Sucursal, Haberes

from perfil.models import Item, Menu, MenuItem

from usuario.form import UsuarioForm, CargaFotoUsuario, HaberesDescuentosForm

from empresa.forms import UserForm, UsuarioEmpresaForm, LeyesSocialesForm, RemuneracionEmpleadoForm, MenuEmpleadoForm, \
    DataCicloVidaCertificadoAmonestacionAnexosEquiposSeguridadForm, TerminoRelacionLaboralForm, OtrosForm


@csrf_exempt
@login_required
def ajaxObtenerAsignacioFamiliar(request, is_ajax='N'):
    pValor = Parametros.objects.filter(param_codigo__startswith='ASIGNFAMT')
    montoAsignacion = 0
    promedio = request.POST['valor']

    for a in pValor:

        if a.param_codigo == 'ASIGNFAMT1':
            if int(promedio) <= int(a.param_rangofin):
                montoAsignacion = a.param_valor

        if a.param_codigo == 'ASIGNFAMT2':
            if int(promedio) > int(a.param_rangoini) and int(promedio) <= int(a.param_rangofin):
                montoAsignacion = a.param_valor

        if a.param_codigo == 'ASIGNFAMT3':
            if int(promedio) > int(a.param_rangoini) and int(promedio) <= int(a.param_rangofin):
                montoAsignacion = a.param_valor

        if a.param_codigo == 'ASIGNFAMT4':
            if int(promedio) > int(a.param_rangoini):
                montoAsignacion = a.param_valor

    if is_ajax == 'S':

        html = {
            'montoAsignacion': montoAsignacion.replace('.', '').replace(',', '')
        }
        response = json.dumps(html)
        return HttpResponse(response, content_type='application/json')

    else:
        return montoAsignacion


@csrf_exempt
@login_required
def ajaxVerificarEmpleado(request):
    existeEnUser = False
    existeEnAsociacionUsuarioEmpresa = False

    username = (request.POST['rut']).replace('.', '')
    empresa = request.POST['empresa']
    id = ""
    lafuncion = ""
    try:
        # se verifica que exista en user
        elUser = User.objects.filter(username=username)
        id = elUser[0].id

        if elUser.exists():
            existeEnUser = True

            laEmpresa = Empresa.objects.get(emp_id=empresa)
            aue = AsociacionUsuarioEmpresa.objects.filter(usuario=elUser, empresa=laEmpresa).exists()

            if aue:
                existeEnAsociacionUsuarioEmpresa = True

            lafuncion = 'asociar_usuario_empresa({}, {})'.format(id, laEmpresa.emp_id)
    except:
        pass

    html = {
        'existeEnUser': existeEnUser,
        'existeEnAsociacionUsuarioEmpresa': existeEnAsociacionUsuarioEmpresa,
        'id': id,
        'lafuncion': lafuncion,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxCargaDatosUsuario(request):
    id = request.POST['pk']

    u = Usuario.objects.get(user__id=id)
    last_name = u.user.last_name
    first_name = u.user.first_name
    email = u.user.email
    usu_passwordusuario = u.usu_passwordusuario
    usu_tipousuario = u.usu_tipousuario

    html = {
        'id': id,
        'last_name': last_name,
        'first_name': first_name,
        'email': email,
        'usu_passwordusuario': usu_passwordusuario,
        'usu_tipousuario': usu_tipousuario,

    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_data_afp(request):
    la_afp = Afp.objects.get(afp_id=request.POST['pk'])

    html = {
        'afp_codigoprevired': la_afp.afp_codigoprevired,
        'afp_nombre': la_afp.afp_nombre,
        'afp_tasatrabajadordependiente': float(la_afp.afp_tasatrabajadordependiente),
        'afp_sis': float(la_afp.afp_sis),
        'afp_tasatrabajadorindependiente': float(la_afp.afp_tasatrabajadorindependiente),
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_salud(request):
    la_salud = Salud.objects.get(sa_id=request.POST['pk'])
    fonasa_param = Parametros.objects.get(param_codigo='FONASA')

    html = {
        'sa_nombre': la_salud.sa_nombre,
        'sa_codigo': la_salud.sa_codigo,
        'sa_tipo': la_salud.sa_tipo,
        'fonasa_param': fonasa_param.param_valor
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_seguro_desempleo(request):
    tipoContraro = request.POST['id_ue_tipocontrato']
    lstMontoSeguroDesempleo = []

    montoEmpleador = 0
    montoTrabajador = 0

    parametro = Parametros.objects.all()

    if tipoContraro == 'CI':

        montoTrabajador = parametro.get(param_codigo='CPITRAB')
        montoEmpleador = parametro.get(param_codigo='CPIEMP')

        lstMontoSeguroDesempleo = [
            {
                'valor': montoTrabajador.param_valor,
                'entidad': 'trabajador',
                'glosa': []
            }, {
                'valor': montoEmpleador.param_valor,
                'entidad': 'empleador',
                'glosa': [
                    {
                        'detalle': 'Cuenta individual de cesantia del trabajador',
                        'valor': 1.6
                    }, {
                        'detalle': 'Fondo solidario de cesantía',
                        'valor': 0.8
                    }

                ]
            }
        ]


    elif tipoContraro == 'CPF':

        montoEmpleador = parametro.get(param_codigo='CPFEMP')

        lstMontoSeguroDesempleo.append({
            'valor': montoEmpleador.param_valor,
            'entidad': 'empleador'
        })

    html = {
        'lstMontoSeguroDesempleo': lstMontoSeguroDesempleo
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxAsociarUsuarioEmpresa(request):
    error = False

    data_user = User.objects.get(id=request.POST['usuario_id'])
    data_empresa = Empresa.objects.get(emp_id=request.POST['empresa_id'])
    try:
        aue = AsociacionUsuarioEmpresa()
        aue.usuario = data_user
        aue.empresa = data_empresa
        aue.save()
    except:
        error = True

    html = {
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxCrearUsuarioEmpresa(request):
    """
    paso 1 para la creación de una persona
    @param request: POST
    """
    lista_err = []
    error = False
    pk_usuario = ""
    pk_empresa = ""
    ruta_usuario = ""

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):

        c_cliActivo = ClienteActivo.objects.all()
        x_user = User.objects.all().count()
        if c_cliActivo[0].cac_cantempleados == x_user:
            lista_err.append(
                "Cantidad de usuarios: El sistema permite una cantidad total entre la/las empresa(s) de {} empleados incluyendose los administradores del sistema. Para el caso que necesita aumentar la cantidad de empleados debe ponerese en contacto con el proveedor del sistema".format(
                    c_cliActivo[0].cac_cantempleados))
            error = True
        else:
            frmUserForm = UserForm(request.POST)

            if frmUserForm.is_valid():
                try:
                    form = frmUserForm.save(commit=False)

                    form.username = str(request.POST['username']).replace('.', '')
                    if request.POST['usu_tipousuario'] == '1':
                        form.is_staff = True
                        form.is_superuser = True
                    if request.POST['hdn_tipo_usuario'] == 'usr':
                        xpassword = request.POST['password1']
                        encoding = 'utf-8'
                        sha1(xpassword.encode(encoding)).hexdigest()
                        form.set_password(sha1(xpassword.encode(encoding)).hexdigest())

                    form.save()

                    u = Usuario()
                    u.user = form
                    date_str = '31/12/2999'
                    format_str = '%d/%m/%Y'
                    datetime_obj = datetime.datetime.strptime(date_str, format_str)

                    u.usu_rut = form.username
                    u.usu_tipousuario = request.POST['usu_tipousuario']
                    u.usu_fechanacimiento = datetime_obj
                    if request.POST['hdn_tipo_usuario'] == 'adm':
                        u.usu_nombreusuario = request.POST['username']
                        u.usu_passwordusuario = request.POST['password1']
                    u.save()
                    # ****************************
                    e = Empresa.objects.get(emp_id=request.POST['empresa'])
                    ue = UsuarioEmpresa()
                    ue.user = form
                    ue.save()
                    # ****************************
                    pk_usuario = form.id
                    pk_empresa = e.emp_id

                    aue = AsociacionUsuarioEmpresa()
                    aue.user = form
                    aue.empresa = e
                    aue.save()

                    ca = ClienteActivo.objects.get(cac_id=request.session['cliente_activo'])
                    ruta_usuario = "{}/{}".format((ca.cac_rutausuarios).replace('\\', '/'), form.username)

                    try:
                        os.stat(ruta_usuario)
                    except:
                        os.mkdir(ruta_usuario)

                except Exception as inst:
                    print(type(inst))  # la instancia de excepción
                    print(inst.args)  # argumentos guardados en .args
                    print(inst)  # __str__ permite imprimir args directamente,

                    lista_err.append("ERROR" + ': ' + str(inst))
                    error = True
                    transaction.set_rollback(True, using_db)
            else:
                for field in frmUserForm:
                    el_error = ''
                    for error in field.errors:

                        el_error = error
                        if error == 'This field is required.':
                            el_error = 'Este campo es requerido.'
                        if error == 'This password is too short. It must contain at least 8 characters.':
                            el_error = 'La contraseña debe tener un largo minimo de 8 caracteres.'

                        lista_err.append(field.label + ': ' + el_error)
                for er in lista_err:
                    print(er)

                error = True
    html = {
        'lista_err': lista_err,
        'error': error,
        'pk_empresa': pk_empresa,
        'pk_usuario': pk_usuario,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxEditarUsuarioEmpresa(request, id_usuario, id_empresa):
    """
    paso 1 para la edicion de una persona
    @param request: POST
    """
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmUserForm = UserForm(request.POST or None, instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmUserForm.is_valid():
            try:
                # ****************************
                data_user.username = (request.POST['username']).replace('.', '')
                data_user.first_name = request.POST['first_name']
                data_user.last_name = request.POST['last_name']
                data_user.email = request.POST['email']
                data_user.set_password(request.POST['password1'])
                if request.POST['usu_tipousuario'] == '1':
                    data_user.is_staff = True
                    data_user.is_superuser = True
                data_user.save()
                # ****************************
                data_usuario = Usuario.objects.get(user=data_user)
                data_usuario.usu_tipousuario = request.POST['usu_tipousuario']
                data_usuario.save()
                # ****************************

                # ****************************
            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmUserForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True
    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxAddDatosPersonales(request, usu_id):
    lista_err = []
    error = False
    data_usuario = Usuario.objects.get(user=usu_id)
    frmUsuarioForm = UsuarioForm(request.POST or None, instance=data_usuario)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmUsuarioForm.is_valid():
            try:
                form = frmUsuarioForm.save(commit=False)
                form.usu_rut = data_usuario.user.username

                if request.POST['usu_tiporut'] == '2':
                    form.usu_paisextranjeros = request.POST['usu_paisextranjeros']
                else:
                    form.pais = Pais.objects.get(pa_id=request.POST['pais'])

                form.region = Region.objects.get(re_id=request.POST['region'])
                form.comuna = Comuna.objects.get(com_id=request.POST['comuna'])
                form.save()
            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmUsuarioForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxAddDatosLaborales(request, id_usuario, id_empresa):
    lista_err = []
    error = False
    ue_tipocontrato_distinto = False

    data_user = User.objects.get(id=id_usuario)
    data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    if request.POST['ue_tipocontrato'] != data_user_emp.ue_tipocontrato:
        ue_tipocontrato_distinto = True

    frmUsuarioEmpresaForm = UsuarioEmpresaForm(request.POST or None, instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmUsuarioEmpresaForm.is_valid():
            try:
                form = frmUsuarioEmpresaForm.save(commit=False)
                try:
                    form.sucursal = Sucursal.objects.get(suc_id=request.POST['sucursal'])
                except:
                    form.sucursal = None
                form.cargo = Cargo.objects.get(car_id=request.POST['cargo'])
                form.centrocosto = CentroCosto.objects.get(cencost_id=request.POST['centrocosto'])
                form.save()

                if ue_tipocontrato_distinto:
                    if request.POST['ue_tipocontrato'] == 'CI':
                        data_user_emp.ue_porempleado = 0.6
                        data_user_emp.ue_porempleador = 2.4
                    elif request.POST['ue_tipocontrato'] == 'CPF':
                        data_user_emp.ue_porempleado = None
                        data_user_emp.ue_porempleador = 3
                    data_user_emp.save()

                aue = AsociacionUsuarioEmpresa.objects.get(user=data_user, empresa=data_empresa)
                aue.sucursal = Sucursal.objects.get(suc_id=request.POST['sucursal'])
                aue.save()

            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmUsuarioEmpresaForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxDatosLeyesSociales(request, id_usuario, id_empresa):
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    # data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmLeyesSocialesForm = LeyesSocialesForm(request.POST or None, instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmLeyesSocialesForm.is_valid():
            try:
                form = frmLeyesSocialesForm.save(commit=False)
                form.afp = Afp.objects.get(afp_id=request.POST['afp'])
                try:
                    form.afp_apv = Afp.objects.get(afp_id=request.POST['afp_apv'])
                except:
                    form.afp_apv = None
                form.salud = Salud.objects.get(sa_id=request.POST['salud'])
                form.save()
            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmLeyesSocialesForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxAddRemuneracionEmpleado(request, id_usuario, id_empresa):
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmRemuneracionEmpleadoForm = RemuneracionEmpleadoForm(request.POST or None, instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmRemuneracionEmpleadoForm.is_valid():
            try:

                form = frmRemuneracionEmpleadoForm.save(commit=False)
                form.save()

                xHaberes = Haberes.objects.filter(empresa=data_empresa, user=data_user)

                # Filtro para movilizacion
                movilizacion = xHaberes.filter(hab_nombre='Movilizacion')
                if not movilizacion.exists():
                    object_1 = Haberes()

                    object_1.hab_nombre = 'Movilizacion'
                    object_1.hab_monto = float(form.ue_movilizacion)
                    object_1.hab_tipo = 'HNI'
                    object_1.empresa = data_empresa
                    object_1.user = data_user
                    object_1.save()

                else:
                    object_1 = movilizacion.first()
                    object_1.hab_monto = float(form.ue_movilizacion)
                    object_1.save()

                # Filtro para colacion
                colacion = xHaberes.filter(hab_nombre='Colacion')
                if not colacion.exists():
                    object_2 = Haberes()

                    object_2.hab_nombre = 'Colacion'
                    object_2.hab_monto = float(form.ue_colacion)
                    object_2.hab_tipo = 'HNI'
                    object_2.empresa = data_empresa
                    object_2.user = data_user
                    object_2.save()
                else:
                    object_2 = colacion.first()
                    object_2.hab_monto = float(form.ue_colacion)
                    object_2.save()

            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmRemuneracionEmpleadoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxAddMenuEmpleado(request, id_usuario, id_empresa):
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmMenuEmpleadoForm = MenuEmpleadoForm(request.POST or None)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmMenuEmpleadoForm.is_valid():
            try:
                list = request.POST.getlist("me_items")
                elMenu = Menu.objects.filter(usuario=data_user)

                if elMenu.exists():
                    for i in list:

                        mItem = MenuItem.objects.filter(menu=elMenu[0], item=Item.objects.get(item_id=i))
                        if mItem.exists():
                            mItem[0].men_ite_estado = 'S'
                            mItem[0].save()
                        else:
                            mItem = MenuItem()
                            mItem.menu = elMenu[0]
                            mItem.item = Item.objects.get(item_id=i)
                            mItem.save()
                else:
                    elMenu = Menu()
                    elMenu.usuario = data_user
                    elMenu.menu_nombre = "{}_{}_{}".format(data_user.username, data_user.email, data_empresa.emp_codigo)
                    elMenu.save()

                    for i in list:
                        if len(i) > 0:
                            mItem = MenuItem()
                            mItem.menu = elMenu
                            mItem.item = Item.objects.get(item_id=i)
                            mItem.save()
            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmMenuEmpleadoForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


def removeItems(request, id_usuario, empresa_id, men_ite_id):
    mItems = MenuItem.objects.get(men_ite_id=men_ite_id)

    if mItems.men_ite_estado == 'S':
        mItems.men_ite_estado = 'N'
    else:
        mItems.men_ite_estado = 'S'
    mItems.save()
    return redirect('bases:edit_personal', id_usuario, empresa_id)


@csrf_exempt
@login_required
def ajaxAddImagenPerfilUSuario(request, id_usuario, id_empresa):
    lista_err = []
    error = False
    contenido_file = UPLOAD_DIR_FOTO
    imagen_template = ''

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        # hEmpresa = Empresa.objects.get(emp_id=id_empresa)
        data_user = User.objects.get(id=id_usuario)
        data_usuario = Usuario.objects.get(user=data_user)

        data_cliente_activo = ClienteActivo.objects.get(cac_id=request.session['cliente_activo'])
        try:
            archivoUpload = request.FILES['archivo']
            fileName, fileExtension = os.path.splitext(request.FILES['archivo'].name)
            fileName = str(fileName).replace('-', '').split(' ')
            fileName = '{}_{}{}'.format(data_usuario.usu_rut, time.strftime("%H%M%S"), fileExtension)
            contenido_file = BASE_COMMAND + 'static/' + data_cliente_activo.cac_nombrebase + '/usuarios/' + data_usuario.usu_rut + '/' + fileName
            imagen_template = '/' + UPLOAD_DIR_FOTO + data_cliente_activo.cac_nombrebase + '/usuarios/' + data_usuario.usu_rut + '/' + fileName

            data_usuario.usu_rutafoto = imagen_template
            data_usuario.usu_nombrefoto = fileName
            data_usuario.save()

            with open(contenido_file, 'wb+') as destination:
                for chunk in request.FILES['archivo'].chunks():
                    destination.write(chunk)
            destination.close()
        except IOError:
            os.remove(contenido_file)

    html = {
        'lista_err': lista_err,
        'error': error,
        'imagen_template': imagen_template,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_ciclo(request, id_usuario):
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    # data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmDCVCAAES = DataCicloVidaCertificadoAmonestacionAnexosEquiposSeguridadForm(request.POST or None,
                                                                                 instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmDCVCAAES.is_valid():
            try:
                form = frmDCVCAAES.save(commit=False)
                form.ue_prestamo = request.POST['ue_prestamo']
                form.ue_cuotas = request.POST['ue_cuotas']
                form.ue_certificado = request.POST['ue_certificado']
                form.ue_amonestacion = request.POST['ue_amonestacion']
                form.ue_entregaequiposeguridad = request.POST['ue_entregaequiposeguridad']
                form.ue_anexocontrato = request.POST['ue_anexocontrato']
                form.save()

            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmDCVCAAES:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_termino_laboral(request, id_usuario):
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    # data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmTerminoRelacionLaboralForm = TerminoRelacionLaboralForm(request.POST or None, instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmTerminoRelacionLaboralForm.is_valid():
            try:
                form = frmTerminoRelacionLaboralForm.save(commit=False)
                form.save()

            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmTerminoRelacionLaboralForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_otro(request, id_usuario):
    lista_err = []
    error = False

    data_user = User.objects.get(id=id_usuario)
    # data_empresa = Empresa.objects.get(emp_id=id_empresa)
    data_user_emp = UsuarioEmpresa.objects.get(user=data_user)

    frmOtrosForm = OtrosForm(request.POST or None, instance=data_user_emp)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmOtrosForm.is_valid():
            try:
                form = frmOtrosForm.save(commit=False)
                form.ue_otros = request.POST['ue_otros']
                form.save()

            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmOtrosForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_add_haber_descuento(request, user_id, emp_id):
    lista_err = []
    error = False
    hab_nombre = ''
    haber = 0
    descuento = 0
    hab_id = 0
    ue_totalhaberes = 0
    ue_totaldescuentos = 0
    ue_totalfinalhaberesdescuentos = 0

    frmHaberesDescuentosForm = HaberesDescuentosForm(request.POST)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmHaberesDescuentosForm.is_valid():
            try:
                data_user = User.objects.get(id=user_id)
                data_empresa = Empresa.objects.get(emp_id=emp_id)
                data_usuario_empresa = UsuarioEmpresa.objects.get(user=data_user)

                form = frmHaberesDescuentosForm.save(commit=False)
                form.hab_tipo = 'F'
                form.empresa = data_empresa
                form.user = data_user
                form.save()

                hab_id = form.hab_id
                hab_nombre = form.hab_nombre.upper()

                if form.hab_tipohaberdescuento == 'H':
                    haber = formatear_numero(form.hab_monto, 0)
                    data_usuario_empresa.ue_totalhaberes = float(data_usuario_empresa.ue_totalhaberes) + float(
                        form.hab_monto)

                elif form.hab_tipohaberdescuento == 'D':
                    descuento = formatear_numero(form.hab_monto, 0)
                    data_usuario_empresa.ue_totaldescuentos = float(data_usuario_empresa.ue_totaldescuentos) + float(
                        form.hab_monto)

                data_usuario_empresa.save()

                data_usuario_empresa.ue_totalfinalhaberesdescuentos = float(
                    data_usuario_empresa.ue_totalhaberes) - float(data_usuario_empresa.ue_totaldescuentos)
                data_usuario_empresa.save()

                ue_totalhaberes = float(data_usuario_empresa.ue_totalhaberes)
                ue_totaldescuentos = float(data_usuario_empresa.ue_totaldescuentos)
                ue_totalfinalhaberesdescuentos = data_usuario_empresa.ue_totalfinalhaberesdescuentos


            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmHaberesDescuentosForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
        'hab_nombre': hab_nombre,
        'haber': haber,
        'descuento': descuento,
        'hab_id': hab_id,
        'ue_totalhaberes': formatear_numero(ue_totalhaberes, 0),
        'ue_totaldescuentos': formatear_numero(ue_totaldescuentos, 0),
        'ue_totalfinalhaberesdescuentos': formatear_numero(ue_totalfinalhaberesdescuentos, 0),
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajax_delete_haber_descuento(request, hab_id):
    dHaber = Haberes.objects.get(hab_id=hab_id)

    data_empresa = dHaber.empresa
    data_user = dHaber.user

    dHaber.delete()

    xHaberesDescuentos = Haberes.objects.filter(empresa=data_empresa, user=data_user,
                                                hab_tipo='F').exclude(hab_activo='N').order_by(
        'hab_id')

    suma_haberes = 0
    suma_descuentos = 0
    for y in xHaberesDescuentos:

        if y.hab_tipohaberdescuento == 'H':
            haberes = formatear_numero(y.hab_monto, 0)
            suma_haberes += float(haberes.replace(',', '').replace('.', ''))
        else:
            descuentos = formatear_numero(y.hab_monto, 0)
            suma_descuentos += float(descuentos.replace(',', '').replace('.', ''))

    total_haberes_descuentos = suma_haberes - suma_descuentos

    uEmpresa = UsuarioEmpresa.objects.get(user=data_user)
    uEmpresa.ue_totalhaberes = suma_haberes
    uEmpresa.ue_totaldescuentos = suma_descuentos
    uEmpresa.ue_totalfinalhaberesdescuentos = total_haberes_descuentos
    uEmpresa.save()

    html = {
        'hab_id': hab_id,
        'suma_haberes': formatear_numero(suma_haberes, 0),
        'suma_descuentos': formatear_numero(suma_descuentos, 0),
        'total_haberes_descuentos': formatear_numero(total_haberes_descuentos, 0),
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')
