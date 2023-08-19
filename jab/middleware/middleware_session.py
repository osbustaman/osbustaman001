from django.contrib.auth import logout
from django.contrib.sessions.models import Session
from django.shortcuts import redirect
from django.utils import timezone

from django.core.exceptions import ObjectDoesNotExist
from perfil.models import UsuarioLogeado
from jab.views import elige_choices


def middleware_active_session(get_response):
    """
    Middleware que tiene como función validar en cada request
    que el usuario tenga permiso para navegar mediante la verificacipon
    de un registro, de lo contrario se realizara un logout y se
    redireccionar al login.
    :param get_response:
    :return:
    """
    # One-time configuration and initialization.
    def middleware(request):
        ##Sólo se hace uso del middleware cuando el usuario esta logueado

        try:

            if request.user.is_authenticated:
                ##Usuario registrado dentro de la plataforma
                try:
                    ##Se busca un registro acerca de la sesión del usuario
                    ##para saber si tiene permitido navegar en la plataforma
                    registro = UsuarioLogeado.objects.get(usuario=request.user)

                    ##Si esta en el registro de la db, puede continuar navegando
                    if request.session.session_key == registro.ul_sessionid:
                        response = get_response(request)

                    else:
                        ##Si ya no tiene permiso se hace una desconexión automática
                        logout(request)
                        request.session['error_login'] = 'Este usuario se ha conectado desde otro equipo'
                        if request:
                            print('salida:{}-{}'.format(request, request.session['error_login']))

                        response = redirect(elige_choices(UsuarioLogeado.SISTEMA, registro.ul_sistema))

                except ObjectDoesNotExist:
                    ##Si ya no tiene permiso se hace una desconexión automática
                    logout(request)
                    request.session['error_login'] = 'Este usuario se ha conectado desde otro equipo_2'
                    if request:
                        print('salida:{}-{}'.format(request, request.session['error_login']))

                    response = redirect(elige_choices(UsuarioLogeado.SISTEMA, registro.ul_sistema))
            else:
                response = get_response(request)

            return response
        except:
            response = get_response(request)
            return response

    return middleware