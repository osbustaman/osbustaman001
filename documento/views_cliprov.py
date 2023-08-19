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

from clienteproveedor.models import ClienteProveedor, ClienteProveedorEmpresa
from configuracion.models import Parametros, ClienteActivo, Moneda
from documento.forms import SubirDocumentoForm, DocumentoEncabezadoForm, DocumentoEncabezadoDetalleForm

from jab.decoradores import existe_empresa
from jab.settings import RUTA_PDF, WKHTMLTOPDF_BIN_PATH, STATICFILES_DIRS
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

from documento.models import TipoDocumentos, Documento, DocumentoEmpleado, DocumentoEmpresa, DocumentoEncabezado, \
    DocumentoEncabezadoDetalle
from jab.views import formatear_numero
from usuario.models import Empresa


@existe_empresa
@login_required
def listadoDocumentosCliente(request):
    lst_docEmpresa = []

    doc_emp = Documento.objects.filter(tipoDocumentos__tdl_filtrodoc__in=['CLI']).annotate(
        cantidad_docs=Count('documentoencabezado__documento'),
        docempr_id=F('documentoencabezado__empresa_id'))

    contador = 0
    for x in doc_emp:
        contador += 1

        lst_docEmpresa.append({
            'contador': contador,
            'docempr_id': x.docempr_id,
            'doc_id': x.doc_id,
            'doc_nombre': x.doc_nombre,
            'cantidad_doc': x.cantidad_docs,
            'tipoDoc': x.tipoDocumentos.tdl_filtrodoc,
        })

    data = {
        'lst_docEmpresa': lst_docEmpresa,

    }
    return render(request, 'panelcontrol/listado_documentos_cliente_proveedor.html', data)


@existe_empresa
@login_required
def listadoDocumentosProveedor(request):
    lst_docEmpresa = []
    doc_emp = Documento.objects.filter(tipoDocumentos__tdl_filtrodoc__in=['PRO']).annotate(
        cantidad_docs=Count('documentoencabezado__documento'),
        docempr_id=F('documentoencabezado__empresa_id'))

    contador = 0
    for x in doc_emp:
        contador += 1
        lst_docEmpresa.append({
            'contador': contador,
            'docempr_id': x.docempr_id,
            'doc_id': x.doc_id,
            'doc_nombre': x.doc_nombre,
            'cantidad_doc': x.cantidad_docs,
            'tipoDoc': x.tipoDocumentos.tdl_filtrodoc,
        })

    data = {
        'lst_docEmpresa': lst_docEmpresa,
    }
    return render(request, 'panelcontrol/listado_documentos_cliente_proveedor.html', data)


@login_required
def cantidad_documentos(request, doc_id, tipoDoc):
    lst_docEmpresa = []
    object_documento = Documento.objects.get(doc_id=doc_id)
    object_empresa = Empresa.objects.get(emp_id=request.session['la_empresa'])

    object_doc_enc = DocumentoEncabezado.objects.filter(documento=object_documento, empresa=object_empresa)
    if tipoDoc == 'PRO':
        ruta = reverse('bases:listadoDocumentosProveedor', args=[])
        titulo = 'Proveedor'

    elif tipoDoc == 'CLI':
        ruta = reverse('bases:listadoDocumentosCliente', args=[])
        titulo = 'Cliente'

    contador = 0
    for x in object_doc_enc:
        contador += 1

        doc_det = DocumentoEncabezadoDetalle.objects.select_related('documentoEncabezado').filter(
            documentoEncabezado=x)

        lst_docEmpresa.append({
            'contador': contador,
            'num_doc': x.docenc_numerodoc,
            'docenc_id': x.docenc_id,
            'cp_razonsocial': x.clienteProveedor.cp_razonsocial.title(),
            'docenc_fechaemision': x.docenc_fechaemision,
            'cant_detalles': doc_det.count(),
        })

    data = {
        'ruta': ruta,
        'doc_id': doc_id,
        'tipoDoc': tipoDoc,
        'doc_nombre': object_documento.doc_nombre.lower(),
        'titulo': titulo,
        'lst_docEmpresa': lst_docEmpresa,
    }
    return render(request, 'panelcontrol/cantidad_documentos.html', data)


@csrf_exempt
@login_required
def ajaxDeleteDocumento(request):
    try:
        doc_cab = DocumentoEncabezado.objects.get(docenc_id=int(request.POST['docenc_id']))
        DocumentoEncabezadoDetalle.objects.filter(documentoEncabezado=doc_cab).delete()
        doc_cab.delete()
        mensaje = "Documento borrado exitosamente"
        error = 0

    except Exception as inst:
        print(type(inst))
        print(inst.args)
        print(inst)
        mensaje = (str(type(inst)))
        error = 1

    html = {
        'mensaje': mensaje,
        'is_error': error,
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def addNuevoDocumentosCP(request, doc_id, tipoDoc):
    lstClienteProveedor = []
    lista_err = []
    error = False

    object_documento = Documento.objects.get(doc_id=doc_id)
    cliente_proveedor = ClienteProveedorEmpresa.objects.filter(empresa_id=int(request.session['la_empresa']))

    formDocumentoEncabezadoForm = DocumentoEncabezadoForm(request.POST or None)

    if tipoDoc == 'CLI':
        formDocumentoEncabezadoForm.fields['clienteProveedor'].label = 'Clientes'
        cliente_proveedor = cliente_proveedor.filter(clienteProveedor__cp_tipoentidad__in=['C', 'A'])
    if tipoDoc == 'PRO':
        formDocumentoEncabezadoForm.fields['clienteProveedor'].label = 'Proveedores'
        cliente_proveedor = cliente_proveedor.filter(clienteProveedor__cp_tipoentidad__in=['P', 'A'])

    formDocumentoEncabezadoForm.fields['docenc_fechaemision'].initial = datetime.datetime.now()

    if request.POST:
        using_db = get_thread_local('using_db', 'default')
        with transaction.atomic(using=using_db):

            if formDocumentoEncabezadoForm.is_valid():
                form = formDocumentoEncabezadoForm.save(commit=False)
                form.clienteProveedor = ClienteProveedor.objects.get(cp_id=int(request.POST['clienteProveedor']))
                form.documento = Documento.objects.get(doc_id=int(doc_id))
                form.empresa = Empresa.objects.get(emp_id=int(request.session['la_empresa']))
                form.user = User.objects.get(id=int(request.session["dicUsuario"]['id']))
                form.docenc_descuento = request.POST['docenc_descuento']
                form.save()

                return redirect('bases:editNuevoDocumentosCP', doc_id, form.docenc_id, tipoDoc)

            else:
                for field in formDocumentoEncabezadoForm:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)
                for er in lista_err:
                    print(er)

                error = True

    contador = 0
    for x in cliente_proveedor:
        contador += 1
        lstClienteProveedor.append({
            'contador': contador,
            'cp_id': x.clienteProveedor.cp_id,
            'cp_razonsocial': x.clienteProveedor.cp_razonsocial,
        })

    data = {
        'doc_id': doc_id,
        'tipoDoc': tipoDoc,
        'doc_nombre': object_documento.doc_nombre.lower(),
        'formDocumentoEncabezadoForm': formDocumentoEncabezadoForm,
        'lstClienteProveedor': lstClienteProveedor,
        'lista_err': lista_err,
        'error': error,
    }
    return render(request, 'panelcontrol/add_documento_cp.html', data)


@login_required
def editNuevoDocumentosCP(request, doc_id, docenc_id, tipoDoc):
    lstClienteProveedor = []
    lstDocumentoDetalle = []
    lista_err = []
    error = False

    object_documento = Documento.objects.get(doc_id=doc_id)
    cliente_proveedor = ClienteProveedorEmpresa.objects.filter(empresa_id=int(request.session['la_empresa']))

    doc_enc = DocumentoEncabezado.objects.get(docenc_id=docenc_id)

    formDocumentoEncabezadoForm = DocumentoEncabezadoForm(request.POST or None, instance=doc_enc)
    formDocumentoEncabezadoDetalleForm = DocumentoEncabezadoDetalleForm(request.POST or None)

    if tipoDoc == 'CLI':
        formDocumentoEncabezadoForm.fields['clienteProveedor'].label = 'Clientes'
        cliente_proveedor = cliente_proveedor.filter(clienteProveedor__cp_tipoentidad__in=['C', 'A'])
    if tipoDoc == 'PRO':
        formDocumentoEncabezadoForm.fields['clienteProveedor'].label = 'Proveedores'
        cliente_proveedor = cliente_proveedor.filter(clienteProveedor__cp_tipoentidad__in=['P', 'A'])

    formDocumentoEncabezadoForm.fields['clienteProveedor'].initial = doc_enc.clienteProveedor_id
    formDocumentoEncabezadoForm.fields['docenc_descuento'].initial = doc_enc.docenc_descuento

    dDetalle = DocumentoEncabezadoDetalle.objects.filter(documentoEncabezado=doc_enc).order_by('docdet_numdetalle')

    for dd in dDetalle:

        monto_descuento = float(dd.docdet_descuento)
        if dd.docdet_tipodescuento == 'P':
            monto_descuento = float(dd.docdet_descuento) * (float(dd.docdet_valorcotizado) / 100)

        monto_neto = float(dd.docdet_valorcotizado) - monto_descuento

        lstDocumentoDetalle.append({
            'docdet_id': dd.docdet_id,
            'docdet_numdetalle': dd.docdet_numdetalle,
            'docdet_producto': dd.docdet_producto,
            'docdet_preciounitario': float(dd.docdet_preciounitario),
            'docdet_cantidad': formatear_numero(dd.docdet_cantidad, 0),
            'docdet_preciototal': formatear_numero(dd.docdet_preciototal, 0),
            'docdet_tipodescuento': dd.docdet_tipodescuento,
            'docdet_descuento': formatear_numero(dd.docdet_descuento, 0),
            'docdet_valorcotizado': formatear_numero(dd.docdet_valorcotizado, 0),
            'docdet_isiva': dd.docdet_isiva,
            'docdet_montoiva': formatear_numero(dd.docdet_montoiva, 0),
            'moneda': dd.moneda_id,
            'docdet_tasadecambio': formatear_numero(dd.docdet_tasadecambio, 0),
            'monto_neto': formatear_numero(monto_neto, 0),
            'monto_descuento': formatear_numero(monto_descuento, 0),
        })

    if request.POST:
        using_db = get_thread_local('using_db', 'default')
        with transaction.atomic(using=using_db):
            if formDocumentoEncabezadoForm.is_valid():
                form = formDocumentoEncabezadoForm.save(commit=False)
                form.clienteProveedor = ClienteProveedor.objects.get(cp_id=int(request.POST['clienteProveedor']))
                form.documento = Documento.objects.get(doc_id=int(doc_id))
                form.empresa = Empresa.objects.get(emp_id=int(request.session['la_empresa']))
                form.user = User.objects.get(id=int(request.session["dicUsuario"]['id']))
                form.docenc_descuento = request.POST['docenc_descuento']
                form.save()

            else:
                for field in formDocumentoEncabezadoForm:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)
                error = True

    contador = 0
    for x in cliente_proveedor:
        contador += 1
        lstClienteProveedor.append({
            'contador': contador,
            'cp_id': x.clienteProveedor.cp_id,
            'cp_razonsocial': x.clienteProveedor.cp_razonsocial,
        })

    iva = Parametros.objects.get(param_codigo='IVA')

    try:
        total_documento = prorrateo(doc_enc)
        xtotal_documento = formatear_numero(total_documento, 0)
    except ZeroDivisionError:
        xtotal_documento = 0

    try:
        total_iva = calcular_totales_documento(doc_enc)
        xtotal_iva = formatear_numero(total_iva, 0)
    except:
        xtotal_iva = 0

    data = {
        'doc_id': doc_id,
        'tipoDoc': tipoDoc,
        'doc_nombre': object_documento.doc_nombre.lower(),
        'formDocumentoEncabezadoForm': formDocumentoEncabezadoForm,
        'lstClienteProveedor': lstClienteProveedor,
        'is_edit': True,
        'razon_social': doc_enc.clienteProveedor.cp_razonsocial,
        'tipo_desc': doc_enc.docenc_tipodescuento,
        'num_doc': doc_enc.docenc_numerodoc,
        'formDocumentoEncabezadoDetalleForm': formDocumentoEncabezadoDetalleForm,
        'lista_err': lista_err,
        'error': error,
        'docenc_id': docenc_id,
        'iva': iva.param_valor,
        'lstDocumentoDetalle': lstDocumentoDetalle,
        'total_documento': xtotal_documento,
        'total_iva': xtotal_iva,
    }
    return render(request, 'panelcontrol/add_documento_cp.html', data)


@login_required
def pdfDocumentoClienteProveedor(request, doc_id, docenc_id, tipoDoc):
    doc = Documento.objects.get(doc_id=doc_id)
    doc_enc = DocumentoEncabezado.objects.get(docenc_id=docenc_id)
    doc_det = DocumentoEncabezadoDetalle.objects.filter(documentoEncabezado=doc_enc)
    cli_act = ClienteActivo.objects.all().first()

    contador = 0
    lst_docDet = []
    total_iva = 0

    try:
        total_documento = prorrateo(doc_enc)
    except ZeroDivisionError:
        total_documento = 0

    for dd in doc_det:
        contador += 1

        total_iva += float(dd.docdet_montoiva)

        monto_descuento = float(dd.docdet_descuento)
        if dd.docdet_tipodescuento == 'P':
            monto_descuento = float(dd.docdet_descuento) * (float(dd.docdet_valorcotizado) / 100)

        monto_neto = float(dd.docdet_valorcotizado) - monto_descuento

        lst_docDet.append({
            'contador': contador,
            'docdet_producto': dd.docdet_producto,
            'docdet_preciounitario': float(dd.docdet_preciounitario),
            'monto_neto': formatear_numero(monto_neto, 0),
            'docdet_cantidad': formatear_numero(dd.docdet_cantidad, 0),
            'docdet_descuento': formatear_numero(monto_descuento, 0),
            'docdet_montoiva': formatear_numero(dd.docdet_montoiva, 0),
            'docdet_preciototal': formatear_numero(dd.docdet_preciototal, 0),
        })

    if tipoDoc == 'CLI':
        x_tipoDoc = 'cliente'
    else:
        x_tipoDoc = 'proveedor'

    if doc_enc.docenc_tipodescuento == 'M':
        monto = "{}".format(formatear_numero(doc_enc.docenc_descuento, 0))
    else:
        x_monto = (float(doc_enc.docenc_descuento) * float(doc_enc.docenc_totalprecio)) / 100
        monto = "{} <small>({}%)</small>".format(formatear_numero(x_monto, 0),
                                                 formatear_numero(doc_enc.docenc_descuento, 0))

    lst_documento = {
        'doc_nombre': doc.doc_nombre,
        'docenc_numerodoc': doc_enc.docenc_numerodoc,
        'docenc_fechaemision': doc_enc.docenc_fechaemision,
        'docenc_fechavencimiento': doc_enc.docenc_fechavencimiento,
        'total_documento': formatear_numero(total_documento, 0),
        'total_iva': formatear_numero(total_iva, 0),
        'total_descuento_doc': monto,
        'docenc_descripcionadicional': doc_enc.docenc_descripcionadicional,

        'emp_razonsocial': doc_enc.empresa.emp_razonsocial,
        'emp_direccion': "{} #{}, piso {}, dpto/oficina {} ".format(doc_enc.empresa.emp_direccion,
                                                                    doc_enc.empresa.emp_numero,
                                                                    doc_enc.empresa.emp_piso,
                                                                    doc_enc.empresa.emp_dptooficina),
        'emp_comuna': "{}".format(doc_enc.empresa.comuna.com_nombre),
        'emp_region': "{}".format(doc_enc.empresa.region.re_nombre),
        'emp_pais': "{}".format(doc_enc.empresa.pais.pa_nombre),
        'emp_fonouno': "{}".format(doc_enc.empresa.emp_fonouno),
        'emp_mailuno': "{}".format(doc_enc.empresa.emp_mailuno),

        'cp_tipoentidad': "{}".format(x_tipoDoc),
        'cp_rut': "{}".format(doc_enc.clienteProveedor.cp_rut),
        'cp_razonsocial': "{}".format(doc_enc.clienteProveedor.cp_razonsocial),
        'cp_direccion': "{} #{}, piso {}, dpto/oficina {} ".format(doc_enc.clienteProveedor.cp_direccion,
                                                                   doc_enc.clienteProveedor.cp_numero,
                                                                   doc_enc.clienteProveedor.cp_piso,
                                                                   doc_enc.clienteProveedor.cp_dptooficina),
        'cp_comuna': "{}".format(doc_enc.clienteProveedor.comuna.com_nombre),
        'cp_region': "{}".format(doc_enc.clienteProveedor.region.re_nombre),
        'cp_pais': "{}".format(doc_enc.clienteProveedor.pais.pa_nombre),
        'cp_fono': "{}".format(doc_enc.clienteProveedor.cp_fono),
        'cp_email': "{}".format(doc_enc.clienteProveedor.cp_email),

        'doc_det': lst_docDet,
    }

    # https://stackoverflow.com/questions/34479040/how-to-install-wkhtmltopdf-with-patched-qt
    file_template = "{}/docpdf/docpdfcliprov.html".format(STATICFILES_DIRS[1])
    filename = "{}.pdf".format(doc.doc_template.split('.')[0])

    if doc_enc.empresa.emp_nombreimagen == '':
        logo = ''
    else:
        logo = '{}/{}'.format(cli_act.cac_rutadstatic, doc_enc.empresa.emp_nombreimagen)

    data = {
        'lst_documento': lst_documento,
        'logo': logo.replace('\\', '/'),
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


@csrf_exempt
@login_required
def ajaxAddDetalle(request, docenc_id):
    lista_err = []
    error = False
    docdet_id = False
    isIva = ''
    total_valor = 0
    total_iva = 0
    total_doc = 0
    moneda = ''
    tasacambio = 0
    valorcotizado = 0
    tipoDescuento = ''
    monto_descuento = 0
    monto_neto = 0

    x_monedas = Moneda.objects.all()
    if x_monedas.count() <= 0:
        error = True
        lista_err.append("ERROR" + ': Para agregar un detalle debe configurar una moneda en el sistema. Debe ir a Otras configuraciones > Agregar nueva moneda')
    else:

        frmDocumentoEncabezadoDetalleForm = DocumentoEncabezadoDetalleForm(request.POST or None)

        using_db = get_thread_local('using_db', 'default')
        with transaction.atomic(using=using_db):
            if frmDocumentoEncabezadoDetalleForm.is_valid():
                try:

                    doc_cab = DocumentoEncabezado.objects.get(docenc_id=docenc_id)

                    form = frmDocumentoEncabezadoDetalleForm.save(commit=False)
                    form.documentoEncabezado = doc_cab
                    form.save()

                    docdet_id = form.docdet_id
                    isIva = form.docdet_isiva
                    tipoDescuento = form.docdet_tipodescuento
                    moneda = form.moneda_id
                    tasacambio = form.docdet_tasadecambio
                    valorcotizado = form.docdet_valorcotizado

                    doc_cab.docenc_totalprecio = float(doc_cab.docenc_totalprecio) + float(form.docdet_preciototal)
                    doc_cab.save()

                    total_valor = prorrateo(doc_cab)
                    total_iva = calcular_totales_documento(doc_cab)

                    monto_descuento = float(form.docdet_descuento)
                    if form.docdet_tipodescuento == 'P':
                        monto_descuento = float(form.docdet_descuento) * (float(form.docdet_valorcotizado) / 100)

                    monto_neto = float(form.docdet_valorcotizado) - monto_descuento

                except Exception as inst:
                    print(type(inst))  # la instancia de excepción
                    print(inst.args)  # argumentos guardados en .args
                    print(inst)  # __str__ permite imprimir args directamente,

                    lista_err.append("ERROR" + ': ' + str(inst))
                    error = True
                    transaction.set_rollback(True, using_db)
            else:
                for field in frmDocumentoEncabezadoDetalleForm:
                    for error in field.errors:
                        lista_err.append(field.label + ': ' + error)
                for er in lista_err:
                    print(er)
                error = True

    html = {
        'lista_err': lista_err,
        'error': error,
        'docdet_id': docdet_id,
        'isIva': isIva,
        'tipoDescuento': tipoDescuento,
        'total_valor': formatear_numero(total_valor, 0),
        'total_iva': formatear_numero(total_iva, 0),
        'moneda': moneda,
        'tasacambio': formatear_numero(tasacambio, 0),
        'valorcotizado': formatear_numero(valorcotizado, 0),
        'monto_descuento': formatear_numero(monto_descuento, 0),
        'monto_neto': formatear_numero(monto_neto, 0),
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxEditDetalle(request, docenc_id, docdet_id):
    lista_err = []
    error = False
    docdetid = False
    isIva = ''
    tipoDescuento = ''
    total_valor = 0
    total_iva = 0

    moneda = ''
    tasacambio = 0
    valorcotizado = 0

    monto_descuento = 0
    monto_neto = 0

    doc_cab = DocumentoEncabezado.objects.get(docenc_id=docenc_id)
    object_detalle = DocumentoEncabezadoDetalle.objects.get(docdet_id=docdet_id)
    frmDocumentoEncabezadoDetalleForm = DocumentoEncabezadoDetalleForm(request.POST or None, instance=object_detalle)

    using_db = get_thread_local('using_db', 'default')
    with transaction.atomic(using=using_db):
        if frmDocumentoEncabezadoDetalleForm.is_valid():
            try:

                form = frmDocumentoEncabezadoDetalleForm.save(commit=False)
                form.documentoEncabezado = doc_cab
                form.save()
                docdetid = form.docdet_id
                isIva = form.docdet_isiva
                tipoDescuento = form.docdet_tipodescuento
                moneda = form.moneda_id
                tasacambio = form.docdet_tasadecambio
                valorcotizado = form.docdet_valorcotizado

                doc_cab.docenc_totalprecio = float(doc_cab.docenc_totalprecio) + float(form.docdet_preciototal)
                doc_cab.save()

                total_valor = prorrateo(doc_cab)
                total_iva = calcular_totales_documento(doc_cab)

                monto_descuento = float(form.docdet_descuento)
                if form.docdet_tipodescuento == 'P':
                    monto_descuento = float(form.docdet_descuento) * (float(form.docdet_valorcotizado) / 100)

                monto_neto = float(form.docdet_valorcotizado) - monto_descuento

            except Exception as inst:
                print(type(inst))  # la instancia de excepción
                print(inst.args)  # argumentos guardados en .args
                print(inst)  # __str__ permite imprimir args directamente,

                lista_err.append("ERROR" + ': ' + str(inst))
                error = True
                transaction.set_rollback(True, using_db)
        else:
            for field in frmDocumentoEncabezadoDetalleForm:
                for error in field.errors:
                    lista_err.append(field.label + ': ' + error)
            for er in lista_err:
                print(er)
            error = True

    html = {
        'lista_err': lista_err,
        'error': error,
        'docdet_id': docdetid,
        'isIva': isIva,
        'tipoDescuento': tipoDescuento,
        'total_valor': total_valor,
        'total_iva': float(total_iva),

        'moneda': moneda,
        'tasacambio': formatear_numero(tasacambio, 0),
        'valorcotizado': formatear_numero(valorcotizado, 0),
        'monto_descuento': formatear_numero(monto_descuento, 0),
        'monto_neto': formatear_numero(monto_neto, 0),
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@csrf_exempt
@login_required
def ajaxDelDetalle(request, docdet_id, docenc_id):
    error_detalle = False

    doc_cab = DocumentoEncabezado.objects.get(docenc_id=docenc_id)

    doc_det = DocumentoEncabezadoDetalle.objects.filter(docdet_id=docdet_id)
    monto_detalle = float(doc_det[0].docdet_preciototal)
    doc_det.delete()

    new_doc_det = DocumentoEncabezadoDetalle.objects.filter(documentoEncabezado=doc_cab)
    contador = 1
    for dd in new_doc_det:
        DocumentoEncabezadoDetalle.objects.filter(docdet_id=dd.docdet_id).order_by('docdet_id').update(
            docdet_numdetalle=contador)
        contador = contador + 1

    doc_cab.docenc_totalprecio = float(doc_cab.docenc_totalprecio) - monto_detalle
    doc_cab.save()

    try:
        monto_total = prorrateo(doc_cab)
    except ZeroDivisionError:
        monto_total = 0
    except:
        monto_total = 0

    try:
        total_iva = calcular_totales_documento(doc_cab)
        if total_iva == None:
            total_iva = 0
    except:
        total_iva = 0

    html = {
        'error_detalle': error_detalle,
        'monto_total': monto_total,
        'total_iva': float(total_iva),
    }
    response = json.dumps(html)
    return HttpResponse(response, content_type='application/json')


@login_required
def calcular_totales_documento(doc_cab):
    totales = DocumentoEncabezadoDetalle.objects.select_related('documentoEncabezado').filter(
        documentoEncabezado=doc_cab)

    # total_doc = totales.aggregate(total_doc = Sum('docdet_preciototal'))['total_doc']
    total_iva = totales.aggregate(total_iva=Sum('docdet_montoiva'))['total_iva']

    return total_iva


@login_required
def prorrateo(doc_cab):
    # se obtiene el factor del prorrateo

    total_documento = 0
    doc_det = DocumentoEncabezadoDetalle.objects.select_related('documentoEncabezado').filter(
        documentoEncabezado=doc_cab)

    if doc_cab.docenc_tipodescuento == 'P':
        total_descuento = (float(doc_cab.docenc_totalprecio) * float(doc_cab.docenc_descuento)) / 100
    elif doc_cab.docenc_tipodescuento == 'M':
        total_descuento = float(doc_cab.docenc_descuento)

    factor = total_descuento / float(doc_cab.docenc_totalprecio)

    for x in doc_det:
        descuento = factor * float(x.docdet_preciototal)
        nuevo_precio = float(x.docdet_preciototal) - descuento
        total_documento += nuevo_precio

    print("total_doc: {}".format(total_documento))

    return total_documento
