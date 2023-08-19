#!/usr/bin/env python
#  -*- coding: utf-8 -*-
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

from configuracion.models import ClienteActivo
from documento.views_print import reimprimir_doc_pdf
from jab.decoradores import existe_empresa
from jab.settings import UPLOAD_DIR, BASE_COMMAND, WKHTMLTOPDF_BIN_PATH, RUTA_PDF, STATIC_ROOT
from jab.threadlocal import get_thread_local
from jab.views import mesesDelAnio, formatear_numero
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

from jab.views import elige_choices

from documento.models import Documento, TipoDocumentos, DocumentoEmpresa, DocumentoEmpleado
from documento.forms import DocumentoForm, TipoDocumentosForm, DocumentoEmpresaForm, FiltroPorDocForm

from usuario.models import Empresa, Usuario, UsuarioEmpresa, AsociacionUsuarioEmpresa, Haberes

from clienteproveedor.models import ClienteProveedor, ClienteProveedorEmpresa

from jab.settings import STATICFILES_DIRS


@login_required
def viewsDocumentos(request, todas=''):
    """
    Funcion que inicializa la vista que muestra la pantalla que muestra el listado de empresas
    :param request: variables de session
    :return: recursos_humanos/empresa.html
    """
    lst_documentos = []
    contador = 0

    try:
        if todas == 'S':
            docs = Documento.objects.all().exclude(doc_activo='N')

        else:
            docs = Documento.objects.filter(empresa_id=request.session['la_empresa'])
    except:
        docs = Documento.objects.all().exclude(doc_activo='N')

    for x in docs:
        contador += 1
        lst_documentos.append({
            'contador': contador,
            'doc_tipodoc': x.tipoDocumentos.tdl_descripcion,
            'doc_nombre': x.doc_nombre.title(),
            'doc_activo': elige_choices(Documento.OPCIONES, x.doc_activo),
            'empresa': x.empresa.emp_razonsocial,
            'emp_id': x.empresa.emp_id,
            'doc_id': x.doc_id,
        })

    data = {
        'lst_documentos': lst_documentos,

    }
    return render(request, 'panelcontrol/listado_documentos.html', data)


# *************************************************************************************
# Documentos
# *************************************************************************************
@login_required
@existe_empresa
def listadoDocumentos(request, filtro=''):
    """
    Configuracion documentos
    :param request:
    :return:
    """
    lstTipoDocumentos = []

    # se obtiene los tipos de documentos, el cual pasan a ser grupos de documentos
    xTipoDoc = TipoDocumentos.objects.filter(tdl_filtrodoc__in=['DOC', 'DEF'])
    if len(filtro) > 0:
        xTipoDoc = xTipoDoc.filter(tdl_filtrodoc=filtro)
    xTipoDoc = xTipoDoc.exclude(tdl_activo='N')

    contador = 0
    for x in xTipoDoc:
        contador += 1
        lstTipoDocumentos.append({
            'contador': contador,
            'tdl_id': x.tdl_id,
            'tdl_codigo': x.tdl_codigo,
            'tdl_descripcion': x.tdl_descripcion,
            'tdl_activo': elige_choices(TipoDocumentos.OPCIONES, x.tdl_activo),
            'estado': x.tdl_activo,
            'tdl_pordefecto': x.tdl_pordefecto
        })

    data = {
        'lstTipoDocumentos': lstTipoDocumentos,
        'filtro': filtro,
    }
    return render(request, 'panelcontrol/tipo_documentos_laborales.html', data)


@login_required
def addGrupoDocumento(request):
    """
    formulario para agregar un grupo de documento
    :param request:
    :return:
    """
    lista_err = []
    error = False

    frmTipoDocumentosForm = TipoDocumentosForm(request.POST or None)

    if frmTipoDocumentosForm.is_valid():
        frm = frmTipoDocumentosForm.save(commit=False)
        frm.tdl_descripcion = "{}".format(request.POST['tdl_descripcion'])
        frm.tdl_pordefecto = 'N'
        frm.tdl_filtrodoc = 'DOC'
        frm.save()
        return redirect('bases:listadoDocumentos')
    else:
        error = True
        for field in frmTipoDocumentosForm:
            for error in field.errors:
                lista_err.append(field.label + ': ' + error)
        for er in lista_err:
            print(er)

    data = {
        'error': error,
        'lista_err': lista_err,
        'frmTipoDocumentosLaboralesForm': frmTipoDocumentosForm,
    }
    return render(request, 'panelcontrol/add_tipo_documento_laboral.html', data)


@csrf_exempt
@login_required
def borrarTipoDocumento(request):
    """
    borrar grupo documento laboral
    :param request:
    :param tdl_id: id del grupo de documentos
    :param estado:
    :return:
    """
    tdl = TipoDocumentos.objects.get(tdl_id=request.POST['tdl_id'])
    can_doc = Documento.objects.filter(tipoDocumentos=tdl).count()

    if not can_doc > 0:
        if request.POST['estado'] == 'S':
            tdl.tdl_activo = 'N'
        elif request.POST['estado'] == 'N':
            tdl.tdl_activo = 'S'
        tdl.save()
        return redirect('bases:listadoDocumentos')

    html = {
        'error_mensaje': 'No se puede borrar ya que este grupo tiene documentos asociados'
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def editGrupoDocumento(request, tdl_id):
    """
    Editar el grupo de documento y a su vez muestra otra pestaña en donde esta el listado
    de documentos que tiene el grupo
    :param request:
    :param tdl_id:
    :return:
    """
    lista_err = []
    error = False

    tdl = TipoDocumentos.objects.get(tdl_id=tdl_id)
    tipoDocumento = tdl.tdl_descripcion

    lstDocumentos = []

    frmTipoDocumentosForm = TipoDocumentosForm(request.POST or None, instance=tdl)
    if request.POST:
        if frmTipoDocumentosForm.is_valid():
            frm = frmTipoDocumentosForm.save(commit=False)
            frm.tdl_descripcion = "{}".format(request.POST['tdl_descripcion'])
            frm.save()

            return redirect('bases:listadoDocumentos')
        else:
            error = True
            for field in frmTipoDocumentosForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
                for er in lista_err:
                    print(er)

    xDocumentos = Documento.objects.filter(tipoDocumentos=tdl)
    contador = 0
    for x in xDocumentos:
        contador += 1
        lstDocumentos.append({
            'contador': contador,
            'activo': elige_choices(Documento.OPCIONES, x.doc_activo),
            'doc_activo': x.doc_activo,
            'doc_defecto': x.doc_defecto,
            'doc_nombre': x.doc_nombre.upper(),
            'doc_texto': x.doc_texto,
            'doc_id': x.doc_id,
        })

    frmTipoDocumentosForm.fields['tdl_codigo'].widget.attrs["readonly"] = True

    if tdl.tdl_pordefecto == 'S':
        frmTipoDocumentosForm.fields['tdl_codigo'].widget.attrs["readonly"] = True
        frmTipoDocumentosForm.fields['tdl_descripcion'].widget.attrs["readonly"] = True
        frmTipoDocumentosForm.fields['tdl_activo'].widget.attrs["readonly"] = True

    data = {
        'is_edit': True,
        'error': error,
        'lista_err': lista_err,
        'tipoDocumento': tipoDocumento.lower(),
        'frmTipoDocumentosLaboralesForm': frmTipoDocumentosForm,
        'lstDocumentos': lstDocumentos,
        'tdl_id': tdl_id,
        'tdl_pordefecto': tdl.tdl_pordefecto,
    }

    return render(request, 'panelcontrol/add_tipo_documento_laboral.html', data)


@login_required
def addNuevoDocumento(request, tdl_id):
    lista_err = []
    error = False

    tdl = TipoDocumentos.objects.get(tdl_id=tdl_id)
    formDoc = DocumentoForm(request.POST or None)

    if request.POST:

        if formDoc.is_valid():

            name_template = "%s.html" % request.POST['doc_nombre']

            form = formDoc.save(commit=False)
            form.tipoDocumentos = tdl
            form.doc_template = name_template.replace(' ', '_')
            form.doc_defecto = 'N'
            form.doc_fechacreacion = datetime.datetime.now()
            form.save()

            x_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])
            de = DocumentoEmpresa()
            de.documento = form
            de.empresa = x_empresa
            de.save()

            cli_act = ClienteActivo.objects.all().first()

            logo = '{}{}'.format(cli_act.cac_rutadstatic, cli_act.cac_nombreimagenlogo)

            html_logo = '{}\n'.format("{% include 'docpdf/style.html' %}")
            html_logo += '<table width="100%" border="0" cellspacing="0" cellpadding="0">\n'
            html_logo += '<tr>\n'
            html_logo += '<td>\n<img class="img-responsive" width="151" height="48" src="{{logo}}">\n</td>\n'
            html_logo += '<td></td>\n'
            html_logo += '</tr>\n'
            html_logo += '<tr>\n'
            html_logo += '<td colspan="2">\n<br/>\n<br/>\n<br/>{}\n</td>\n'.format(form.doc_texto)
            html_logo += '</tr>\n'
            html_logo += '</table>'

            ruta_doc = "{}templates/{}/{}".format(BASE_COMMAND, cli_act.cac_nombrebase, form.doc_template)

            file = open(ruta_doc, "w")
            file.write(html_logo)
            file.close()

            return redirect('bases:editGrupoDocumento', tdl_id)

        else:
            error = True
            for field in formDoc:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    if tdl.tdl_filtrodoc in ['CLI', 'PRO']:
        lstVariables = listadoVariableClienteProveedorEmpresa()
    else:
        lstVariables = listadoVariableUsuarioEmpesa()

    data = {
        'frmDocumentoForm': formDoc,
        'lstVariables': lstVariables,
        'lista_err': lista_err,
        'error': error,
        'doc_id': tdl_id,
        'tdl_id': tdl_id,
        'tipoDocumento': tdl.tdl_descripcion.lower(),
    }
    return render(request, 'panelcontrol/add_documento.html', data)


@login_required
def editDocumento(request, tdl_id):
    lstDocumentoEmpresa = []

    elDocumento = Documento.objects.get(doc_id=tdl_id)
    formDoc = DocumentoForm(request.POST or None, instance=elDocumento)

    if request.POST:
        if formDoc.is_valid():
            form = formDoc.save(commit=False)
            form.save()

            x_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])
            de = DocumentoEmpresa()
            de.documento = form
            de.empresa = x_empresa
            de.save()

            cli_act = ClienteActivo.objects.all().first()

            html_logo = '{}\n'.format("{% include 'docpdf/style.html' %}")
            html_logo += '<table width="100%" border="0" cellspacing="0" cellpadding="0">\n'
            html_logo += '<tr>\n'
            html_logo += '<td><img class="img-responsive" width="151" height="48" src="{{logo}}"></td>\n'
            html_logo += '<td></td>\n'
            html_logo += '</tr>\n'
            html_logo += '<tr>\n'
            html_logo += '<td colspan="2">\n<br/>\n<br/>\n<br/>{}\n</td>\n'.format(form.doc_texto)
            html_logo += '</tr>\n'
            html_logo += '</table>'

            ruta_doc = "{}templates/{}/{}".format(BASE_COMMAND, cli_act.cac_nombrebase, form.doc_template)

            file = open(ruta_doc, "w")
            file.write(html_logo)
            file.close()

            return redirect('bases:editGrupoDocumento', elDocumento.tipoDocumentos_id)

    xDocumentoEmpresa = DocumentoEmpresa.objects.all()

    contador = 0
    for x in xDocumentoEmpresa.filter(documento_id=tdl_id):
        contador += 1
        lstDocumentoEmpresa.append({
            'contador': contador,
            'docempr_id': x.docempr_id,
            'documento': x.documento.doc_id,
            'empresa': x.empresa.emp_razonsocial,
            'docempr_activo': x.docempr_activo,
            'activo': elige_choices(DocumentoEmpresa.OPCIONES, x.docempr_activo),
        })

    if elDocumento.tipoDocumentos.tdl_filtrodoc in ['CLI', 'PRO']:
        lstVariables = listadoVariableClienteProveedorEmpresa()
    else:
        lstVariables = listadoVariableUsuarioEmpesa()

    tdl_filtrodoc = True
    if elDocumento.tipoDocumentos.tdl_filtrodoc in ['CLI', 'PRO']:
        tdl_filtrodoc = False

    data = {
        'frmDocumentoForm': formDoc,
        'lstVariables': lstVariables,
        'tdl_id': elDocumento.tipoDocumentos.tdl_id,
        'tipoDocumento': elDocumento.tipoDocumentos.tdl_descripcion.lower(),
        'is_edit': True,
        'lstDocumentoEmpresa': lstDocumentoEmpresa,
        'doc_id': elDocumento.doc_id,
        'tdl_filtrodoc': tdl_filtrodoc,
    }
    return render(request, 'panelcontrol/add_documento.html', data)


@csrf_exempt
@login_required
def consultarBorrarDocumento(request):
    """
    borrar documento laboral
    :param request:
    :return:
    """
    doc = Documento.objects.get(doc_id=request.POST['doc_id'])
    can_doc_emp = DocumentoEmpresa.objects.filter(documento=doc).count()

    error_mensaje = ""
    error = False
    if can_doc_emp > 0:
        error_mensaje = 'No se puede borrar ya que este documento tiene empresas asociadas'
        error = True

    html = {
        'error_mensaje': error_mensaje,
        'error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def borrarDocumento(request, doc_id, estado):
    """
    borrar documento laboral
    :param request:
    :return:
    """
    doc = Documento.objects.get(doc_id=doc_id)
    can_doc_emp = DocumentoEmpresa.objects.filter(documento=doc).count()

    if not can_doc_emp > 0:
        if estado == 'S':
            doc.doc_activo = 'N'
        elif estado == 'N':
            doc.doc_activo = 'S'
        doc.save()
        return redirect('bases:editGrupoDocumento', doc.tipoDocumentos.tdl_id)


@login_required
def documentoEmpresa(request, tdl_id):
    lista_err = []
    error = False

    formDoc = DocumentoEmpresaForm(request.POST or None)
    elDocumento = Documento.objects.get(doc_id=tdl_id)

    formDoc.fields['documento'].initial = tdl_id

    if request.POST:

        doc_emp = DocumentoEmpresa.objects.filter(documento=elDocumento, empresa_id=request.POST['empresa'])
        if doc_emp.exists():
            error = True
            lista_err.append(
                'Ya existe asociación del documento {} con la empresa {}'.format(doc_emp[0].documento.doc_nombre,
                                                                                 doc_emp[0].empresa.emp_razonsocial))
        else:
            if formDoc.is_valid():
                form = formDoc.save(commit=False)
                form.documento = Documento.objects.get(doc_id=request.POST['documento'])
                form.empresa = Empresa.objects.get(emp_id=request.POST['empresa'])
                form.save()

                return redirect('bases:editDocumento', tdl_id)

            else:
                error = True
                for field in formDoc:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)
                for er in lista_err:
                    print(er)

    data = {
        'formDoc': formDoc,
        'tdl_id': tdl_id,
        'error': error,
        'lista_err': lista_err,
        'tipoDocumento': elDocumento.tipoDocumentos.tdl_descripcion.lower() + " - " + elDocumento.doc_nombre.lower(),

    }
    return render(request, 'panelcontrol/add_documento_empresa.html', data)


@login_required
def editDocumentoEmpresa(request, docempr_id):
    lista_err = []
    error = False

    doc_emp = DocumentoEmpresa.objects.get(docempr_id=docempr_id)

    formDoc = DocumentoEmpresaForm(request.POST or None, instance=doc_emp)
    formDoc.fields['documento'].initial = doc_emp.documento.tipoDocumentos.tdl_id
    formDoc.fields['empresa'].initial = doc_emp.empresa.emp_id

    if request.POST:

        if formDoc.is_valid():
            form = formDoc.save(commit=False)
            form.documento = Documento.objects.get(doc_id=request.POST['documento'])
            form.empresa = Empresa.objects.get(emp_id=request.POST['empresa'])
            form.save()

            return redirect('bases:editDocumento', doc_emp.documento.tipoDocumentos.tdl_id)
        else:
            error = True
            for field in formDoc:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)

    data = {
        'formDoc': formDoc,
        'tdl_id': doc_emp.documento.doc_id,
        'error': error,
        'lista_err': lista_err,
        'tipoDocumento': doc_emp.documento.tipoDocumentos.tdl_descripcion.lower() + " - " + doc_emp.documento.doc_nombre.lower(),

    }
    return render(request, 'panelcontrol/add_documento_empresa.html', data)


def listadoVariableUsuarioEmpesa():
    lstVariables = []

    fecha = datetime.datetime.now()

    dia = fecha.day
    mes = mesesDelAnio(int(fecha.month)).title()
    anio = fecha.year

    lstVariables.append({
        'variable': '{{dia}}',
        'descripcion': 'dia',
    })
    lstVariables.append({
        'variable': '{{mes}}',
        'descripcion': 'mes',
    })
    lstVariables.append({
        'variable': '{{anio}}',
        'descripcion': 'año',
    })

    # ** ** ** ** *EMPLEADO ** ** ** ** *

    lstVariables.append({
        'variable': '{{usu_rut}}',
        'descripcion': 'Rut empleado',
    })
    lstVariables.append({
        'variable': '{{usu_nombre}}',  # nombre completo
        'descripcion': 'Nombre completo',
    })
    lstVariables.append({
        'variable': '{{usu_mail}}',
        'descripcion': 'Mail de empleado',
    })
    lstVariables.append({
        'variable': '{{usu_estadocivil}}',
        'descripcion': 'Estado civil',
    })
    lstVariables.append({
        'variable': '{{usu_tiporut}}',
        'descripcion': 'Tipo de rut',
    })
    lstVariables.append({
        'variable': '{{usu_sexo}}',
        'descripcion': 'Sexo',
    })
    lstVariables.append({
        'variable': '{{usu_fono}}',
        'descripcion': 'Teléfono empleado',
    })
    lstVariables.append({
        'variable': '{{usu_fechanacimiento}}',
        'descripcion': 'Fecha de nacimiento',
    })
    lstVariables.append({
        'variable': '{{usu_pais}}',
        'descripcion': 'País empleado',
    })
    lstVariables.append({
        'variable': '{{usu_region}}',
        'descripcion': 'Región empleado',
    })
    lstVariables.append({
        'variable': '{{usu_comuna}}',
        'descripcion': 'Comuna empleado',
    })
    lstVariables.append({
        'variable': '{{usu_direccion}}',
        'descripcion': 'Dirección empleado',
    })
    lstVariables.append({
        'variable': '{{usu_profesion}}',
        'descripcion': 'Profesión',
    })
    lstVariables.append({
        'variable': '{{usu_licenciaconducir}}',
        'descripcion': 'Licencia de conducir',
    })
    # ********* EMPLEADO *********

    # ********* EMPRESA *********
    lstVariables.append({
        'variable': '{{emp_rut}}',
        'descripcion': 'Rut empresa',
    })
    lstVariables.append({
        'variable': '{{emp_razonsocial}}',
        'descripcion': 'Razón social',
    })
    lstVariables.append({
        'variable': '{{emp_giro}}',
        'descripcion': 'Giro empresa',
    })
    lstVariables.append({
        'variable': '{{emp_pais}}',
        'descripcion': 'País empresa',
    })
    lstVariables.append({
        'variable': '{{emp_region}}',
        'descripcion': 'Región empresa',
    })
    lstVariables.append({
        'variable': '{{emp_comuna}}',
        'descripcion': 'Comuna empresa',
    })
    lstVariables.append({
        'variable': '{{emp_direccion}}',  # direccion completa emp_direccion + emp_numero + emp_dptooficina
        'descripcion': 'Dirección empresa',
    })
    lstVariables.append({
        'variable': '{{emp_fono}}',  # emp_fonouno + emp_fonodos
        'descripcion': 'Fono empresa',
    })
    lstVariables.append({
        'variable': '{{emp_mail}}',  # emp_mailuno + emp_maildos
        'descripcion': 'Fono empresa',
    })
    lstVariables.append({
        'variable': '{{emp_fechainiactividades}}',
        'descripcion': 'Inicio de actividades',
    })
    lstVariables.append({
        'variable': '{{emp_isholding}}',
        'descripcion': 'Es holding',
    })
    lstVariables.append({
        'variable': '{{emp_nombrerepresentante}}',
        'descripcion': 'Nombre representante emp.',
    })
    lstVariables.append({
        'variable': '{{emp_rutrepresentante}}',
        'descripcion': 'Rut representante emp.',
    })
    lstVariables.append({
        'variable': '{{emp_nombrecontador}}',
        'descripcion': 'Nombre contador',
    })
    lstVariables.append({
        'variable': '{{emp_rutcontador}}',
        'descripcion': 'Rut contador',
    })
    lstVariables.append({
        'variable': '{{emp_isestatal}}',
        'descripcion': 'Empresa estatal',
    })
    # ********* EMPRESA *********

    # ********* USUARIO EMPRESA *********
    lstVariables.append({
        'variable': '{{cargo}}',
        'descripcion': 'Cargo empleado',
    })
    lstVariables.append({
        'variable': '{{ue_tipocontrato}}',
        'descripcion': 'Tipo de contrato',
    })
    lstVariables.append({
        'variable': '{{ue_tipotrabajdor}}',
        'descripcion': 'Tipo de trabajador',
    })
    lstVariables.append({
        'variable': '{{ue_fechacontratacion}}',
        'descripcion': 'Fecha de contratación',
    })
    lstVariables.append({
        'variable': '{{ue_fecharenovacioncontrato}}',
        'descripcion': 'Fecha renovación contrato',
    })
    lstVariables.append({
        'variable': '{{ue_fecharetiro}}',
        'descripcion': 'Fecha de retiro',
    })
    lstVariables.append({
        'variable': '{{ue_formapago}}',
        'descripcion': 'Forma de pago',
    })
    lstVariables.append({
        'variable': '{{centrocosto}}',
        'descripcion': 'Centro de costo',
    })
    lstVariables.append({
        'variable': '{{ue_horassemanales}}',
        'descripcion': 'Horas semanales',
    })
    lstVariables.append({
        'variable': '{{ue_movilizacion}}',
        'descripcion': 'Movilización',
    })
    lstVariables.append({
        'variable': '{{ue_colacion}}',
        'descripcion': 'Colación',
    })
    lstVariables.append({
        'variable': '{{ue_montonticipo}}',
        'descripcion': 'Anticipo',
    })
    lstVariables.append({
        'variable': '{{ue_cargasfamiliares}}',
        'descripcion': 'Cargas familiares',
    })
    lstVariables.append({
        'variable': '{{ue_montoasignacionfamiliar}}',
        'descripcion': 'Monto asignación familiar',
    })
    lstVariables.append({
        'variable': '{{ue_sueldobase}}',
        'descripcion': 'Sueldo base',
    })
    lstVariables.append({
        'variable': '{{ue_gratificacion}}',
        'descripcion': 'Gratificación',
    })
    lstVariables.append({
        'variable': '{{ue_tipogratificacion}}',
        'descripcion': 'Tipo de gratificación',
    })
    lstVariables.append({
        'variable': '{{ue_comiciones}}',
        'descripcion': 'Comiciones',
    })
    lstVariables.append({
        'variable': '{{ue_porcentajecomicion}}',
        'descripcion': 'Porcentaje comisión',
    })
    lstVariables.append({
        'variable': '{{ue_cotizacionvoluntaria}}',
        'descripcion': 'Cotización voluntaria',
    })
    lstVariables.append({
        'variable': '{{afp}}',
        'descripcion': 'AFP',
    })
    lstVariables.append({
        'variable': '{{afp_porcentaje}}',
        'descripcion': 'Porcentaje AFP',
    })
    lstVariables.append({
        'variable': '{{ue_tipomontoapv}}',
        'descripcion': 'Tipo monto APV',
    })
    lstVariables.append({
        'variable': '{{afp_apv}}',
        'descripcion': 'APV (AFP)',
    })
    lstVariables.append({
        'variable': '{{ue_ahorrovoluntario}}',
        'descripcion': 'Ahorro Voluntario',
    })
    lstVariables.append({
        'variable': '{{salud}}',
        'descripcion': 'Salud',
    })
    lstVariables.append({
        'variable': '{{ue_ufisapre}}',
        'descripcion': 'UF isapre',
    })
    lstVariables.append({
        'variable': '{{ue_funisapre}}',
        'descripcion': 'FUN isapre',
    })
    lstVariables.append({
        'variable': '{{ue_cotizacion}}',
        'descripcion': 'Cotizacion fonasa/isapre',
    })
    lstVariables.append({
        'variable': '{{ue_segurodesempleo}}',
        'descripcion': 'Seguro de desmpleo',
    })
    lstVariables.append({
        'variable': '{{ue_porempleado}}',
        'descripcion': 'Porcentaje seguro desempleo por empleado',
    })
    lstVariables.append({
        'variable': '{{ue_porempleador}}',
        'descripcion': 'Porcentaje seguro desempleo por empleador',
    })
    lstVariables.append({
        'variable': '{{ue_trabajopesado}}',
        'descripcion': 'Porcentaje seguro trabajo pesado',
    })
    lstVariables.append({
        'variable': '{{ue_prestamo}}',
        'descripcion': 'Préstamo',
    })
    lstVariables.append({
        'variable': '{{ue_cuotas}}',
        'descripcion': 'Cuotas préstamo',
    })
    lstVariables.append({
        'variable': '{{ue_certificado}}',
        'descripcion': 'Descripción de certificado',
    })
    lstVariables.append({
        'variable': '{{ue_amonestacion}}',
        'descripcion': 'Amonestación',
    })
    lstVariables.append({
        'variable': '{{ue_anexocontrato}}',
        'descripcion': 'Anexo de contrato',
    })
    lstVariables.append({
        'variable': '{{ue_entregaequiposeguridad}}',
        'descripcion': 'Entrega equipos de seguridad y otros',
    })
    lstVariables.append({
        'variable': '{{ue_fechanotificacioncartaaviso}}',
        'descripcion': 'Fecha de notificacion carta aviso',
    })
    lstVariables.append({
        'variable': '{{ue_fechatermino}}',
        'descripcion': 'Fecha de termino relación laboral',
    })
    lstVariables.append({
        'variable': '{{ue_causal}}',
        'descripcion': 'Causal',
    })
    lstVariables.append({
        'variable': '{{ue_fundamento}}',
        'descripcion': 'Fundamento',
    })
    lstVariables.append({
        'variable': '{{ue_tiponoticacion}}',
        'descripcion': 'Tipo de notificacion',
    })
    lstVariables.append({
        'variable': '{{ue_otros}}',
        'descripcion': 'Otros',
    })

    lstVariables.append({
        'variable': '{{banco}}',
        'descripcion': 'Banco',
    })
    lstVariables.append({
        'variable': '{{ue_cuentabancaria}}',
        'descripcion': 'Cuenta bancaria',
    })
    lstVariables.append({
        'variable': '{{ue_jornadalaboral}}',
        'descripcion': 'Jornada de trabajo',
    })
    # ********* USUARIO EMPRESA *********

    # ********* CICLOS *********
    lstVariables.append({
        'variable': '{{ciclo_haberes_descuentos|safe}}',
        'descripcion': 'Listado de haberes y descuentos',
    })
    lstVariables.append({
        'variable': '{{ciclo_habres_imponibles_no_imponibles|safe}}',
        'descripcion': 'Listado de haberes imponibles y no imponibles',
    })
    # ********* CICLOS *********

    return lstVariables


def listadoVariableClienteProveedorEmpresa():
    lstVariables = []

    # ********* CLIENTE PROVEEDOR *********
    lstVariables.append({
        'variable': '{{cp_rut}}',
        'descripcion': 'Rut cliente/proveedor',
    })
    lstVariables.append({
        'variable': '{{cp_razonsocial}}',  # nombre completo
        'descripcion': 'Razón comercial',
    })
    lstVariables.append({
        'variable': '{{cp_nombrefantasia}}',
        'descripcion': 'Nombre de fantasía',
    })
    lstVariables.append({
        'variable': '{{cp_giro}}',
        'descripcion': 'Giro',
    })
    lstVariables.append({
        'variable': '{{cp_direccion}}',
        'descripcion': 'Dirección',
    })
    lstVariables.append({
        'variable': '{{cp_numero}}',
        'descripcion': 'Número',
    })
    lstVariables.append({
        'variable': '{{cp_piso}}',
        'descripcion': 'Piso',
    })
    lstVariables.append({
        'variable': '{{cp_dptooficina}}',
        'descripcion': 'Dpto/Oficina',
    })
    lstVariables.append({
        'variable': '{{pais}}',
        'descripcion': 'País',
    })
    lstVariables.append({
        'variable': '{{region}}',
        'descripcion': 'Región',
    })
    lstVariables.append({
        'variable': '{{comuna}}',
        'descripcion': 'Comuna',
    })
    lstVariables.append({
        'variable': '{{cp_email}}',
        'descripcion': 'Email cliente/proveedor',
    })
    lstVariables.append({
        'variable': '{{cp_comentario}}',
        'descripcion': 'Comentario',
    })
    lstVariables.append({
        'variable': '{{cp_estado}}',
        'descripcion': 'Estado',
    })
    # ********* CLIENTE PROVEEDOR *********

    # ********* CLIENTE PROVEEDOR EMPRESA*********
    lstVariables.append({
        'variable': '{{clienteProveedor}}',
        'descripcion': 'Cliente/Proveedor',
    })
    lstVariables.append({
        'variable': '{{empresa}}',
        'descripcion': 'Empresa',
    })
    lstVariables.append({
        'variable': '{{cpe_tipoentidad}}',
        'descripcion': 'Tipo entidad',
    })
    lstVariables.append({
        'variable': '{{cpe_tipocliente}}',
        'descripcion': 'Tipo cliente',
    })
    lstVariables.append({
        'variable': '{{cpe_tipoproveedor}}',
        'descripcion': 'Tipo proveedor',
    })
    lstVariables.append({
        'variable': '{{cpe_plazopago}}',
        'descripcion': 'Plazo pago',
    })
    lstVariables.append({
        'variable': '{{cpe_vencimiento}}',
        'descripcion': 'Fecha vencimiento',
    })
    lstVariables.append({
        'variable': '{{banco}}',  # emp_fonouno + emp_fonodos
        'descripcion': 'Banco',
    })
    lstVariables.append({
        'variable': '{{cpe_tipocuenta}}',  # emp_mailuno + emp_maildos
        'descripcion': 'Tipo de cuenta',
    })
    lstVariables.append({
        'variable': '{{cpe_ctacorriente}}',
        'descripcion': 'Número de cuenta',
    })
    lstVariables.append({
        'variable': '{{cpe_credautorizado}}',
        'descripcion': 'Crédito autorizado',
    })
    lstVariables.append({
        'variable': '{{cpe_estado}}',
        'descripcion': 'Estado',
    })
    # ********* EMPRESA *********0

    return lstVariables


@csrf_exempt
@login_required
def ajaxAddFileUsuario(request, id_usuario):
    lista_err = []
    error = False
    contenido_file = UPLOAD_DIR
    name_template = []

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        data_user = User.objects.get(id=id_usuario)
        data_cliente_activo = ClienteActivo.objects.get(cac_id=request.session['cliente_activo'])
        try:
            archivoUpload = request.FILES['archivo']
            fileName, fileExtension = os.path.splitext(request.FILES['archivo'].name)
            fileName = str(fileName).replace('-', '').split(' ')
            fileName = '{}_{}{}'.format(data_user.username, time.strftime("%H%M%S"), fileExtension)
            contenido_file = (data_cliente_activo.cac_rutadstatic + '/usuarios/' + data_user.username + '/' + fileName).replace('\\', '/')
            with open(contenido_file, 'wb+') as destination:
                for chunk in request.FILES['archivo'].chunks():
                    destination.write(chunk)
            destination.close()

            user = User.objects.get(id=id_usuario)

            de = DocumentoEmpleado()
            de.user = user
            de.docemp_rutaarchivo = '/static/' + data_cliente_activo.cac_nombrebase + '/usuarios/' + data_user.username + '/' + fileName
            de.docemp_nombrearchivo = fileName
            de.docemp_fechacreacion = datetime.datetime.now()
            de.save()

            # name_template.append({
            #     'tdl_descripcion': de.documento.tipoDocumentos.tdl_descripcion,
            #     'doc_nombre': de.documento.doc_nombre,
            #     'contenido_file': contenido_file,
            #     'docemp_id': de.docemp_id,
            #     'doc_id': de.documento.doc_id,
            # })

            # name_template.append({
            #     'docemp_fechacreacion': de.docemp_fechacreacion,
            #     'doc_nombre': de.docemp_nombrearchivo,
            #     'contenido_file': contenido_file,
            #     'docemp_id': de.docemp_id,
            # })
        except IOError:
            os.remove(contenido_file)

    html = {
        'lista_err': lista_err,
        'error': error,
        # 'name_template': name_template,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxBuscarDocumento(request):
    lstLosDocumentos = []
    losDocumentos = Documento.objects.filter(tipoDocumentos__tdl_id=request.POST['documento'])
    for d in losDocumentos:
        lstLosDocumentos.append({
            'doc_id': d.doc_id,
            'doc_nombre': d.doc_nombre,
        })
    html = {
        'lstLosDocumentos': lstLosDocumentos
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


# ------------------------------------
@login_required
def borrarDocumentoEmpleado(request, docemp_id, accion):
    de = DocumentoEmpleado.objects.get(docemp_id=docemp_id)
    de.docemp_estado = 'N'
    de.save()

    return redirect('bases:viewsFichaEmpleado', de.user.id, request.session['la_empresa'], accion)


@login_required
def pdfDocumento(request, doc_id, id_usuario):
    dict_detalle = []
    tipo_documento = None
    id_emp = request.session['la_empresa']

    usr = User.objects.get(id=id_usuario)
    usu = Usuario.objects.get(user=usr)
    ase = AsociacionUsuarioEmpresa.objects.filter(user=usr).first()
    usu_emp = UsuarioEmpresa.objects.get(user=usr)

    docPrintToPdf = Documento.objects.get(doc_id=doc_id)

    if docPrintToPdf.doc_defecto == 'N':
        cli_act = ClienteActivo.objects.all().first()
        file_template = "{}templates/{}/{}".format(BASE_COMMAND, cli_act.cac_nombrebase, docPrintToPdf.doc_template)
    elif docPrintToPdf.doc_defecto == 'S':

        file_template = "{}/docpdf/{}".format(STATICFILES_DIRS[1], docPrintToPdf.doc_template)
        print("file_template: ", file_template)

    filename = docPrintToPdf.doc_template

    try:
        afp_nombre = usu_emp.afp_apv.afp_nombre
    except:
        afp_nombre = ""

    ue_montoasignacionfamiliar = 0
    if usu_emp.ue_montoasignacionfamiliar:
        ue_montoasignacionfamiliar = formatear_numero(usu_emp.ue_montoasignacionfamiliar, 0)

    ue_porcentajecomicion = 0
    if usu_emp.ue_porcentajecomicion:
        ue_porcentajecomicion = formatear_numero(float(usu_emp.ue_porcentajecomicion), 3)

    ue_ahorrovoluntario = 0
    if usu_emp.ue_ahorrovoluntario:
        ue_ahorrovoluntario = formatear_numero(float(usu_emp.ue_ahorrovoluntario), 0)

    # ciclo haberes imponibles y no imponibles
    ciclo_habres_imponibles_no_imponibles = "<table class='table table-condensed'>"
    ciclo_habres_imponibles_no_imponibles += "<thead>"
    ciclo_habres_imponibles_no_imponibles += "<tr>"
    ciclo_habres_imponibles_no_imponibles += "<th>Haber</th>"
    ciclo_habres_imponibles_no_imponibles += "<th>Tipo</th>"
    ciclo_habres_imponibles_no_imponibles += "<th>Monto</th>"
    ciclo_habres_imponibles_no_imponibles += "</tr>"
    ciclo_habres_imponibles_no_imponibles += "</thead>"
    ciclo_habres_imponibles_no_imponibles += "<tbody>"

    x_haberes = Haberes.objects.filter(empresa_id=id_emp, user=usr).exclude(hab_tipo='F', hab_activo='N')
    x_contador = 0
    for xh in x_haberes:
        x_contador += 1
        ciclo_habres_imponibles_no_imponibles += "<tr>"
        ciclo_habres_imponibles_no_imponibles += "<td>{}</td>".format(xh.hab_nombre).lower()
        ciclo_habres_imponibles_no_imponibles += "<td>{}</td>".format(
            elige_choices(Haberes.TIPO, xh.hab_tipo)).lower()
        ciclo_habres_imponibles_no_imponibles += "<td>{}</td>".format(formatear_numero(xh.hab_monto, 0))
        ciclo_habres_imponibles_no_imponibles += "</tr>"

    ciclo_habres_imponibles_no_imponibles += "</tbody>"
    ciclo_habres_imponibles_no_imponibles += "</table>"

    # ciclo haberes y descuentos
    ciclo_haberes_descuentos = "<table class='table table-condensed'>"
    ciclo_haberes_descuentos += "<thead>"
    ciclo_haberes_descuentos += "<tr>"
    ciclo_haberes_descuentos += "<th>Haber</th>"
    ciclo_haberes_descuentos += "<th>Tipo</th>"
    ciclo_haberes_descuentos += "<th>Monto haber</th>"
    ciclo_haberes_descuentos += "<th>Monto descuento</th>"
    ciclo_haberes_descuentos += "</tr>"
    ciclo_haberes_descuentos += "</thead>"
    ciclo_haberes_descuentos += "<tbody>"

    y_haberes = Haberes.objects.filter(empresa_id=id_emp, user=usr, hab_tipo='F').exclude(hab_activo='N')
    y_contador = 0
    total_y_haberes = 0
    total_y_descuentos = 0

    for yh in y_haberes:
        y_contador += 1
        xy_haberes = 0
        xy_descuento = 0
        if yh.hab_tipohaberdescuento == 'H':
            xy_haberes = yh.hab_monto
        elif yh.hab_tipohaberdescuento == 'D':
            xy_descuento = yh.hab_monto

        total_y_haberes += xy_haberes
        total_y_descuentos += xy_descuento

        ciclo_haberes_descuentos += "<tr>\n"
        ciclo_haberes_descuentos += "<td>{}</td>\n".format(yh.hab_nombre).lower()
        ciclo_haberes_descuentos += "<td>{}</td>\n".format(
            elige_choices(Haberes.FINIQUITO, yh.hab_tipohaberdescuento)).lower()
        ciclo_haberes_descuentos += "<td>{}</td>\n".format(formatear_numero(xy_haberes, 0))
        ciclo_haberes_descuentos += "<td>{}</td>\n".format(formatear_numero(xy_descuento, 0))
        ciclo_haberes_descuentos += "</tr>\n"

    ciclo_haberes_descuentos += "</tbody>\n"
    ciclo_haberes_descuentos += "</table>\n"

    total_final = float(total_y_haberes) - float(total_y_descuentos)
    ciclo_haberes_descuentos += "<table class='table table-condensed'>\n"
    ciclo_haberes_descuentos += "<tr>\n"
    ciclo_haberes_descuentos += "<td></td>\n"
    ciclo_haberes_descuentos += "<td>Total haber: {}</td>\n".format(formatear_numero(float(total_y_haberes), 0))
    ciclo_haberes_descuentos += "<td>Total descuento: {}</td>\n".format(formatear_numero(float(total_y_descuentos), 0))
    ciclo_haberes_descuentos += "<td>Total: {}</td>\n".format(formatear_numero(float(total_final), 0))
    ciclo_haberes_descuentos += "</tr>\n"
    ciclo_haberes_descuentos += "</table>\n"

    cli_act = ClienteActivo.objects.all().first()

    # if cli_act.cac_nombreimagenlogo:
    #     logo = '{}/{}'.format(cli_act.cac_rutadstatic, cli_act.cac_nombreimagenlogo)
    # else:
    #     logo = ''

    try:
        ban_nombre = usu_emp.banco.ban_nombre
    except:
        ban_nombre = ''

    try:
        usu_pais = usu.pais.pa_nombre.title()
    except:
        usu_pais = ''

    try:
        usu_region = usu.region.re_nombre.title()
    except:
        usu_region = ''

    try:
        usu_comuna = usu.comuna.com_nombre.title()
    except:
        usu_comuna = ''

    try:
        usu_direccion = usu.usu_direccion.title()
    except:
        usu_direccion = ''

    try:
        usu_profesion = usu.usu_profesion.title()
    except:
        usu_profesion = ''

    try:
        usu_cargo = usu_emp.cargo.car_nombre.title()
    except:
        usu_cargo = ''

    try:
        usu_centrocosto = usu_emp.centrocosto.cencost_nombre.title()
    except:
        usu_centrocosto = ''

    try:
        usu_afp = usu_emp.afp.afp_nombre.title()
    except:
        usu_afp = ''

    try:
        afp_tasatrabajadordependiente = usu_emp.afp.afp_tasatrabajadordependiente,
    except:
        afp_tasatrabajadordependiente = ''

    try:
        sa_nombre = usu_emp.salud.sa_nombre.title()
    except:
        sa_nombre = ''

    data = {
        'usu_rut': usr.username,
        'usu_nombre': "{} {}".format(usr.first_name, usr.last_name).title(),
        'usu_mail': usr.email,
        'usu_estadocivil': elige_choices(Usuario.ESTADO_CIVIL, usu.usu_estadocivil),
        'usu_tiporut': elige_choices(Usuario.TIPO_RUT, usu.usu_tiporut),
        'usu_sexo': elige_choices(Usuario.SEXO, usu.usu_sexo),
        'usu_fono': usu.usu_fono,
        'usu_fechanacimiento': usu.usu_fechanacimiento,
        'usu_pais': usu_pais,
        'usu_region': usu_region,
        'usu_comuna': usu_comuna,
        'usu_direccion': usu_direccion,
        'usu_profesion': usu_profesion,
        'usu_licenciaconducir': elige_choices(Usuario.OPCIONES, usu.usu_licenciaconducir.title()),
        'emp_rut': ase.empresa.emp_rut.title(),
        'emp_razonsocial': ase.empresa.emp_razonsocial.title(),
        'emp_giro': ase.empresa.emp_giro.title(),
        'emp_pais': ase.empresa.pais.pa_nombre.title(),
        'emp_region': ase.empresa.region.re_nombre.title(),
        'emp_comuna': ase.empresa.comuna.com_nombre.title(),
        'emp_direccion': ase.empresa.emp_direccion.title(),
        'emp_fono': ase.empresa.emp_fonouno,
        'emp_mail': ase.empresa.emp_mailuno,
        'emp_fechainiactividades': ase.empresa.emp_fechaingreso,
        'emp_isholding': elige_choices(Empresa.OPCIONES, ase.empresa.emp_isholding),
        'emp_nombrerepresentante': ase.empresa.emp_nombrerepresentante,
        'emp_rutrepresentante': ase.empresa.emp_rutrepresentante,
        'emp_nombrecontador': ase.empresa.emp_nombrecontador,
        'emp_rutcontador': ase.empresa.emp_rutcontador,
        'emp_isestatal': elige_choices(Empresa.OPCIONES, ase.empresa.emp_isestatal).lower(),
        'cargo': usu_cargo,
        'ue_tipocontrato': elige_choices(UsuarioEmpresa.TIPO_CONTRATO, usu_emp.ue_tipocontrato),
        'ue_tipotrabajdor': elige_choices(UsuarioEmpresa.TIPO_TRABAJADOR, usu_emp.ue_tipotrabajdor),
        'ue_fechacontratacion': usu_emp.ue_fechacontratacion,
        'ue_fecharenovacioncontrato': usu_emp.ue_fecharenovacioncontrato,
        'ue_fecharetiro': usu_emp.ue_fecharetiro,
        'ue_formapago': elige_choices(UsuarioEmpresa.FORMA_PAGO, usu_emp.ue_formapago),
        'centrocosto': usu_centrocosto,
        'ue_horassemanales': usu_emp.ue_horassemanales,
        'ue_movilizacion': formatear_numero(usu_emp.ue_movilizacion, 0),
        'ue_colacion': formatear_numero(usu_emp.ue_colacion, 0),
        'ue_montonticipo': formatear_numero(usu_emp.ue_montonticipo, 0),
        'ue_cargasfamiliares': usu_emp.ue_cargasfamiliares,
        'ue_montoasignacionfamiliar': ue_montoasignacionfamiliar,
        'ue_sueldobase': formatear_numero(usu_emp.ue_sueldobase, 0),
        'ue_gratificacion': elige_choices(UsuarioEmpresa.OPCIONES, usu_emp.ue_gratificacion),
        'ue_tipogratificacion': elige_choices(UsuarioEmpresa.TIPO_GRATIFICACION, usu_emp.ue_tipogratificacion),
        'ue_comiciones': elige_choices(UsuarioEmpresa.OPCIONES, usu_emp.ue_comiciones),
        'ue_porcentajecomicion': ue_porcentajecomicion,
        'ue_cotizacionvoluntaria': usu_emp.ue_cotizacionvoluntaria,
        'afp': usu_afp,
        'afp_porcentaje': afp_tasatrabajadordependiente,
        'ue_tipomontoapv': elige_choices(UsuarioEmpresa.TIPO_MONTO, usu_emp.ue_tipomontoapv),
        'afp_apv': afp_nombre.title(),
        'ue_ahorrovoluntario': ue_ahorrovoluntario,
        'salud': sa_nombre,
        'ue_ufisapre': usu_emp.ue_ufisapre,
        'ue_funisapre': usu_emp.ue_funisapre,
        'ue_cotizacion': formatear_numero(float(usu_emp.ue_cotizacion), 0),
        'ue_segurodesempleo': elige_choices(UsuarioEmpresa.OPCIONES, usu_emp.ue_segurodesempleo),
        'ue_porempleado': formatear_numero(float(usu_emp.ue_porempleado), 2),
        'ue_porempleador': formatear_numero(float(usu_emp.ue_porempleador), 2),
        'ue_trabajopesado': elige_choices(UsuarioEmpresa.OPCIONES, usu_emp.ue_trabajopesado),
        'ue_prestamo': formatear_numero(float(usu_emp.ue_prestamo), 0),
        'ue_cuotas': usu_emp.ue_cuotas,
        'ue_certificado': usu_emp.ue_certificado,
        'ue_amonestacion': usu_emp.ue_amonestacion,
        'ue_anexocontrato': usu_emp.ue_anexocontrato,
        'ue_entregaequiposeguridad': usu_emp.ue_entregaequiposeguridad,
        'ue_fechanotificacioncartaaviso': usu_emp.ue_fechanotificacioncartaaviso,
        'ue_fechatermino': usu_emp.ue_fechatermino,
        'ue_causal': usu_emp.ue_cuasal,
        'ue_fundamento': usu_emp.ue_fundamento,
        'ue_tiponoticacion': elige_choices(UsuarioEmpresa.NOTIFICACION, usu_emp.ue_tiponoticacion),
        'ue_otros': usu_emp.ue_otros,
        'banco': ban_nombre,
        'ue_cuentabancaria': usu_emp.ue_cuentabancaria,
        'ue_jornadalaboral': usu_emp.ue_jornadalaboral,
        'ciclo_habres_imponibles_no_imponibles': ciclo_habres_imponibles_no_imponibles,
        'ciclo_haberes_descuentos': ciclo_haberes_descuentos,
        #'logo': logo

    }

    template = get_template(file_template)
    html = template.render(data)

    options = {
        'page-size': 'Letter',
        'margin-top': '0.20in',
        'margin-right': '0.50in',
        'margin-bottom': '0.50in',
        'margin-left': '0.50in',
        'encoding': "UTF-8",
        'quiet': '',
        'no-outline': None,
    }

    ruta = RUTA_PDF
    # ruta = ruta_informes(request)
    ruta_template = ruta + "doc_generales/" + filename

    config = pdfkit.configuration(wkhtmltopdf=WKHTMLTOPDF_BIN_PATH)

    pdfkit.from_string(html, ruta_template, configuration=config, options=options)

    pdf = open(ruta_template, "rb").read()
    response = HttpResponse(pdf, content_type='application/pdf')
    # response['Content-Disposition'] = 'attachment; filename=' + filename
    os.remove(ruta_template)

    return response
