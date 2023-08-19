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

from documento.forms import SubirDocumentoForm
from documento.models import TipoDocumentos, Documento, DocumentoEmpleado
from jab.decoradores import existe_empresa
from jab.settings import WKHTMLTOPDF_BIN_PATH, RUTA_PDF
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
import pdfkit

from usuario.models import Empresa, Pais, Region, Comuna, AsociacionUsuarioEmpresa, \
    RelacionDeAfiliacion, Sucursal, Usuario, UsuarioEmpresa, Afp, Salud, Cargo, CargoEmpresa, CentroCosto, \
    GrupoCentroCosto

from configuracion.models import Parametros, ClienteActivo

from perfil.models import Menu, MenuItem

from usuario.form import UsuarioForm

from empresa.forms import EmpresasForm, RelacionForm, SucursalForm, UserForm, UsuarioEmpresaForm, LeyesSocialesForm, \
    RemuneracionEmpleadoForm, MenuEmpleadoForm, CargoForm, CargoEmpresaForm, CentroCostoForm, GrupoCentroCostoForm

from jab.views import elige_choices


@login_required
@existe_empresa
def views_empleados(request):
    """
    debe mostrar todos los usuarios incluyendo usuario con estado E con
    excepción el super-usuario
    """
    lst_usuarios = []

    try:
        los_usuarios = AsociacionUsuarioEmpresa.objects.filter(empresa_id=request.session['la_empresa'])
    except:
        los_usuarios = AsociacionUsuarioEmpresa.objects.all()

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
                'emp_id': u.empresa.emp_id,
                'usu_usuarioactivo': el_u.usu_usuarioactivo,
                'estado_usuario': elige_choices(Usuario.ESTADO_USUARIO, el_u.usu_usuarioactivo),

            })

    request.session['ruta_volver_p'] = reverse('bases:views_empleados', args=[])

    data = {
        'lst_usuarios': lst_usuarios,
        'contador': contador,
        'id_emp': request.session['la_empresa'],
    }
    return render(request, 'panelcontrol/listado_empleados.html', data)


# ------------------------------------
@login_required
def viewsFichaEmpleado(request, id_usuario, id_empresa, accion):
    request.session['boton_volver_ver_ficha_empleado'] = False

    formSubirDocumentoForm = SubirDocumentoForm()

    is_documentos = True

    # *** DATA USUARIO ***

    dataUser = User.objects.get(id=id_usuario)
    # dataEmpresa = Empresa.objects.get(emp_id=request.session['la_empresa'])
    dataEmpresa = Empresa.objects.get(emp_id=id_empresa)

    elUsuario = Usuario.objects.get(user=dataUser)

    aoe = AsociacionUsuarioEmpresa.objects.get(user=dataUser, empresa=dataEmpresa)

    nombreCompleto = "{} {}".format(dataUser.first_name.title(), dataUser.last_name.title())

    try:
        direccion = "{}, {}, {}".format(elUsuario.usu_direccion.title(), elUsuario.region.re_nombre.title(),
                                        elUsuario.comuna.com_nombre.title())
    except:
        direccion = "-- no se a definido dirección --"

    if elUsuario.usu_profesion is None or len(elUsuario.usu_profesion) == 0:
        titulo = '-- Profesión por definir --'
    else:
        titulo = elUsuario.usu_profesion.title()

    empresa = aoe.empresa.emp_razonsocial.title()
    sexo = elUsuario.usu_sexo

    rutaImagen = "/static"+elUsuario.usu_rutafoto
    # *** DATA USUARIO ***

    # *** DATA TIPO DOCUMENTOS ***

    lstTipoDocumentos = []
    tDocumentos = TipoDocumentos.objects.filter(tdl_filtrodoc__in=['DOC', 'DEF']).exclude(tdl_activo='N').order_by(
        '-tdl_descripcion')

    for d in tDocumentos:
        lstTipoDocumentos.append({
            'tdl_id': d.tdl_id,
            'tdl_descripcion': d.tdl_descripcion.upper(),
        })

    xDocumentos = []
    nombreGrupoDoc = ''
    try:

        if not accion == 'FIS':

            tipoDocs = TipoDocumentos.objects.get(tdl_id=int(accion))
            nombreGrupoDoc = tipoDocs.tdl_descripcion.title()

            for doc in Documento.objects.filter(tipoDocumentos=tipoDocs).exclude(doc_activo='N'):
                xDocumentos.append({
                    'doc_id': doc.doc_id,
                    'doc_nombre': doc.doc_nombre,
                })

        else:
            contador = 0
            # for doc in DocumentoEmpleado.objects.filter(user=dataUser).exclude(docemp_estado='N'):
            #     contador += 1
            #     xDocumentos.append({
            #         'contador': contador,
            #         'doc_id': doc.docemp_id,
            #         'tdl_descripcion': "-",
            #         'doc_nombre': doc.documento.doc_nombre.upper(),
            #         'docemp_nombrearchivo': doc.docemp_nombrearchivo,
            #         'docemp_rutaarchivo': doc.docemp_rutaarchivo,
            #     })
            xDocumentos = DocumentoEmpleado.objects.filter(user=dataUser).exclude(docemp_estado='N')


    except:
        pass

    if accion == 'FIS':
        nombreGrupoDoc = 'Subir documentos'

    if accion == 'ERROR-01':
        nombreGrupoDoc = 'faltan datos del empleado para imprimir la ficha, por favor revise los datos.'

    data = {
        'is_edit': True,
        'id_usuario': id_usuario,
        'id_empresa': id_empresa,
        'nombreCompleto': nombreCompleto,
        'direccion': direccion,
        'titulo': titulo,
        'empresa': empresa,
        'sexo': sexo,
        'rutaImagen': rutaImagen,
        'is_documentos': is_documentos,
        'lstTipoDocumentos': lstTipoDocumentos,
        'nombreGrupoDoc': nombreGrupoDoc,
        'xDocumentos': xDocumentos,
        'formSubirDocumentoForm': formSubirDocumentoForm,
        'accion': accion,
    }

    return render(request, 'panelcontrol/views_ficha_empleado.html', data)


# ------------------------------------
@login_required
def pdfFichaEmpleado(request, id_usuario, id_empresa):
    try:
        cli_act = ClienteActivo.objects.all().first()

        # *** DATA USUARIO ***
        dataUser = User.objects.get(id=id_usuario)
        email = dataUser.email
        dataEmpresa = Empresa.objects.get(emp_id=id_empresa)
        elUsuario = Usuario.objects.get(user=dataUser)
        aoe = AsociacionUsuarioEmpresa.objects.get(user=dataUser, empresa=dataEmpresa)

        nombreCompleto = "{} {}".format(dataUser.first_name.title(), dataUser.last_name.title())
        try:
            direccion = "{}, {}, {}".format(elUsuario.usu_direccion.title(), elUsuario.region.re_nombre.title(),
                                            elUsuario.comuna.com_nombre.title())
        except:
            direccion = "-- no se a definido dirección --"

        if elUsuario.usu_profesion is None or len(elUsuario.usu_profesion) == 0:
            titulo = '-- Profesión por definir --'
        else:
            titulo = elUsuario.usu_profesion.title()

        empresa = aoe.empresa.emp_razonsocial.title()
        sexo = elUsuario.usu_sexo

        rutaImagen = "{}/{}/{}".format(cli_act.cac_rutausuarios, elUsuario.usu_rut, elUsuario.usu_nombrefoto).replace('\\', '/')

        uEmpresa = UsuarioEmpresa.objects.get(user=dataUser)
        try:
            sucursal = aoe.sucursal.suc_descripcion
        except:
            sucursal = '-- sin sucursal --'

        if uEmpresa.ue_tipotrabajdor == 'D':
            afp_tasatrabajador = uEmpresa.afp.afp_tasatrabajadordependiente
        else:
            afp_tasatrabajador = uEmpresa.afp.afp_tasatrabajadorindependiente

        ue_fecharenovacioncontrato = uEmpresa.ue_fecharenovacioncontrato
        if not uEmpresa.ue_fecharenovacioncontrato:
            ue_fecharenovacioncontrato = ''

        ue_fecharetiro = uEmpresa.ue_fecharetiro
        if not uEmpresa.ue_fecharetiro:
            ue_fecharetiro = ''

        entidad = ''
        cotizacion = 0
        if uEmpresa.salud.sa_tipo == 'F':
            cotizacion = uEmpresa.ue_cotizacion

        elif uEmpresa.salud.sa_tipo == 'I':
            cotizacion = uEmpresa.ue_ufisapre

    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)

        return redirect('bases:viewsFichaEmpleado', id_usuario, id_empresa, 'ERROR-01')

    lst_datosUsuario = {
        'nombreCompleto': nombreCompleto,
        'usu_tiporut': elige_choices(Usuario.TIPO_RUT, elUsuario.usu_tiporut),
        'usu_rut': elUsuario.usu_rut,
        'usu_sexo': elige_choices(Usuario.SEXO, elUsuario.usu_sexo),
        'usu_fono': elUsuario.usu_fono,
        'usu_fechanacimiento': elUsuario.usu_fechanacimiento,
        'usu_estadocivil': elige_choices(Usuario.ESTADO_CIVIL, elUsuario.usu_estadocivil),
        'direccion': direccion,
        'email': email,
        'rutaImagen': rutaImagen,
        'titulo': titulo,

        'empresa': empresa,

        'cargo': uEmpresa.cargo.car_nombre,
        'sucursal': sucursal,
        'centrocosto': uEmpresa.centrocosto.cencost_nombre,
        'ue_tipotrabajdor': elige_choices(UsuarioEmpresa.TIPO_TRABAJADOR, uEmpresa.ue_tipotrabajdor),
        'ue_tipocontrato': elige_choices(UsuarioEmpresa.TIPO_CONTRATO, uEmpresa.ue_tipocontrato).title(),
        'ue_fechacontratacion': uEmpresa.ue_fechacontratacion,
        'ue_fecharenovacioncontrato': ue_fecharenovacioncontrato,
        'ue_fecharetiro': ue_fecharetiro,

        'afp': uEmpresa.afp.afp_nombre,
        'afp_tasatrabajador': afp_tasatrabajador,

        'salud': uEmpresa.salud.sa_nombre,
        'ue_cotizacion': cotizacion,
        'sa_tipo': uEmpresa.salud.sa_tipo,

    }

    # *** DATA USUARIO ***
    # https://stackoverflow.com/questions/34479040/how-to-install-wkhtmltopdf-with-patched-qt
    file_template = 'docpdf/ficha_empleado_pdf.html'

    filename = "ficha_empleado_pdf.pdf"

    data = {
        'logo': '{}{}'.format(cli_act.cac_rutadstatic, cli_act.cac_nombreimagenlogo),
        'lst_datosUsuario': lst_datosUsuario,
    }
    template = get_template(file_template)
    html = template.render(data)

    options = {
        'page-size': 'Letter',
        'margin-top': '0.20in',
        'margin-right': '0.50in',
        'margin-bottom': '0.20in',
        'margin-left': '0.50in',
        'encoding': "UTF-8",
        'quiet': '',
        'no-outline': None,

    }

    ruta = RUTA_PDF
    ruta_template = ruta + filename

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_BIN_PATH)
    pdfkit.from_string(html, ruta_template, configuration=config, options=options)
    pdf = open(ruta_template, "rb").read()
    response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename=' + filename
    os.remove(ruta_template)

    return response


# ------------------------------------
@login_required
def editDataEmpleado(request, id_usuario, id_empresa):
    request.session['boton_volver_ver_ficha_empleado'] = True

    return redirect('bases:edit_personal', id_usuario, id_empresa)
