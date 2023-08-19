# -*- encoding: utf-8 -*-
from django.shortcuts import render_to_response, render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

# from .function import creacionUsuarioSesion
from clienteproveedor.models import ClienteProveedor
from configuracion.models import ClienteActivo
from usuario.models import Empresa, Usuario
from .forms import SignUpForm, LoginForm
from perfil.function import creacionUsuarioSesion, obtener_logo_login
from django.db.models import Case, When, Max, F, Count, Value, Q, Sum, BooleanField, TextField, IntegerField, EmailField

from jab.views import validaEmpresaActiva

import datetime


# -------------- INICIO --------------
# funciones que validan el logeo para el admini de bases
def index_bases(request):
    """
    :param request:
    :return: pagina de logeo
    """

    data = {
        'form': LoginForm,
    }
    return render(request, 'bases/bases_login.html', data)


def login_user_bases(request):
    """
    Esta funcion carga el templatedel login, y a su vez carga el login de django
    para poder ingresar al sistema
    :param request:
    :return:
    """
    username = request.POST['username']
    password = request.POST['password']

    request.session['error'] = None

    user = authenticate(username=username, password=password)
    if user is not None:
        if user.is_active:
            login(request, user)
            creacionUsuarioSesion(request, user, 'LB')
            return redirect('panel_bases')
        else:
            mensaje = "El usuario no esta activo, porfavor comunicarse con el administrador"
            pagina = 'bases/bases_login.html'
            error = True
    else:
        mensaje = "El usuario no existe"
        pagina = 'bases/bases_login.html'
        error = True

    request.session['error'] = error
    request.session['mensaje'] = mensaje

    return redirect('index_bases')


@login_required(login_url='/login/')
def panel_bases(request):
    """
    Funcion para cerrar sesion, mata las sesiones activas
    :param request:
    :return:
    """
    request.session['tipo_sistema'] = 'bases'
    return render(request, 'bases/base.html', {})


# -------------- FINAL --------------

def index(request):
    """
    :param request:
    :return: pagina de logeo
    """
    ahora = datetime.datetime.now()

    data = {
        'form': LoginForm,
        'anio': ahora.year,
        'ruta_imagen': obtener_logo_login(),
    }
    return render(request, 'panelcontrol/login.html', data)


def login_user(request):
    username = request.POST['username']
    password = request.POST['password']

    if validaEmpresaActiva():

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                creacionUsuarioSesion(request, user, 'L')
                return redirect('panel')
            else:
                mensaje = "El usuario no esta activo, porfavor comunicarse con el administrador"
                pagina = 'panelcontrol/login.html'
                datos = {
                    'form': LoginForm(),
                    'mensaje': mensaje,
                    'error': True
                }

                return render(request, pagina, datos)
        else:
            mensaje = "El usuario no existe"
            pagina = 'panelcontrol/login.html'
            datos = {
                'form': LoginForm(),
                'mensaje': mensaje,
                'error': True
            }

            return render(request, pagina, datos)

    else:
        mensaje = "Temporalmente fuera de servicio. Contactese con el administrador "
        pagina = 'panelcontrol/login.html'
        datos = {
            'form': LoginForm(),
            'mensaje': mensaje,
            'error': True
        }

        return render(request, pagina, datos)


@login_required(login_url='/login/')
def panel_control(request):
    request.session['tipo_sistema'] = 'empresas'

    cantEmpresas = Empresa.objects.count()

    cp = ClienteProveedor.objects.all()
    cant_clientes = cp.filter(cp_tipoentidad__in=['C', 'A']).count()
    cant_proveedor = cp.filter(cp_tipoentidad__in=['P', 'A']).count()

    xUser = Usuario.objects.all()

    cant_hombres = xUser.filter(usu_sexo='M').count()
    cant_mujeres = xUser.filter(usu_sexo='F').count()
    cant_ambos = xUser.filter(usu_sexo='PD').count()
    todos = xUser.count()

    datos = {
        'cantEmpresas': cantEmpresas,
        'cant_hombres': cant_hombres,
        'cant_mujeres': cant_mujeres,
        'cant_ambos': cant_ambos,
        'todos': todos,
        'cant_clientes': cant_clientes,
        'cant_proveedor': cant_proveedor,
    }

    return render(request, 'panelcontrol/index.html', datos)
