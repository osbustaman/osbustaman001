# -*- encoding: utf-8 -*-
import xlwt
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
from django.utils import timezone

from importlib import import_module
from django.conf import settings

from django.contrib.sessions.backends.db import SessionStore
from django.core.exceptions import ObjectDoesNotExist

import xlrd
import xlwt
import collections
import shutil
import os
import time
import datetime
import sys
import locale
import calendar
import unicodedata
from django.contrib.auth.models import User
from datetime import datetime

from configuracion.models import ClienteActivo
from .models import Perfil, UsuarioLogeado
from usuario.models import Usuario, Empresa, UsuarioEmpresa, AsociacionUsuarioEmpresa


# con esta funcion se asignara a un usuario a nivel de session
# de esa manera se podra manejar cualquier dato de usuario
# recibe objeto alumno
def creacionUsuarioSesion(request, user, base):
    try:
        usuario = Usuario.objects.get(user=user)
        usu_tipousuario = usuario.usu_tipousuario
    except:
        usu_tipousuario = ""

    validar_usuario(user, request, base)

    dicUsuario = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_staff': user.is_staff,
        'usu_tipousuario': usu_tipousuario,
    }

    request.session["dicUsuario"] = dicUsuario

    if not base == 'LB':
        dataEmpresaSession(request, user.id, user.is_staff)


def dataEmpresaSession(request, id_usuario, is_user_staf=False):
    la_empresa = ""
    razon_social = ""

    if is_user_staf:
        try:
            emp = Empresa.objects.all()
            la_empresa = emp[0].emp_id
            razon_social = emp[0].emp_razonsocial
        except:
            la_empresa = ""
            razon_social = ""
    else:
        user = User.objects.get(id=id_usuario)
        emp = AsociacionUsuarioEmpresa.objects.filter(user=user)
        la_empresa = emp[0].empresa.emp_id
        razon_social = emp[0].empresa.emp_razonsocial

    ca = ClienteActivo.objects.all()

    request.session['la_empresa'] = la_empresa
    request.session['razon_social'] = razon_social
    request.session['cliente_activo'] = ca[0].cac_id
    request.session['x_ruta_imagen'] = "/static/{}/{}".format(ca[0].cac_nombrebase, ca[0].cac_nombreimagenlogo)
    request.session['rutas'] = {
        'cac_rutabase': ca[0].cac_rutabase,
        'cac_rutadocumentos': ca[0].cac_rutadocumentos,
        'cac_rutausuarios': ca[0].cac_rutausuarios,
    }


def obtener_logo_login():
    ca = ClienteActivo.objects.all()
    return "/static/{}/{}".format(ca[0].cac_nombrebase, ca[0].cac_nombreimagenlogo)


def validar_usuario(user, request, base):
    """
    Función que se ejecuta cuando se da pie al logueo de un
    usuario nuevo. Tiene como finalidad almacenar la session_key
    actual del usuario, logrando así, 'desloguear' a otros
    que hayan ingresado con las mismas credenciales
    :param sender:
    :param user:
    :param request:
    :param kwargs:
    :return:
    """

    if request:
        try:
            ## Se agrega esta validación ya que cuando ocurre una autenticación a través de la api
            ## la variable `request.user` es un AnonymousUser y se cambia por la variable `user`
            n_user = request.user.is_anonymous and user or request.user
            ##Se busca un registro acerca de la sesión del usuario
            registro = UsuarioLogeado.objects.get(usuario=n_user)
            ##Si nadie ha ingresado antes, se genera el registro del actual usuario en la pagina
            registro.ul_sessionid = request.session.session_key
            registro.save()
        except ObjectDoesNotExist:
            ##En caso de no encontrar el registro se genera uno
            ul = UsuarioLogeado()
            ul.usuario = request.user
            ul.ul_sessionid = request.session.session_key
            ul.ul_sistema = base
            ul.save()

    return True
