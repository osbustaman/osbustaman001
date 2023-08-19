# -*- encoding: utf-8 -*-
from django.utils import timezone

import datetime
import time
import locale

import django.conf as conf

from datetime import datetime, timedelta

from bases.models import BaseEmpresa

#from recursos_humanos.models import Usuario

from configuracion.models import ClienteActivo

from jab.settings import RUTA_PDF, DATABASES, LOCALE_LANG

import re


# con esta funcion se asignara a un usuario a nivel de session
# de esa manera se podra manejar cualquier dato de usuario
# recibe objeto alumno
# def creacionUsuarioSesion(request, user):
#     try:
#         usuario = Usuario.objects.get(user=user)
#         usu_tipousuario = usuario.usu_tipousuario
#     except:
#         usu_tipousuario = ""
#
#     dicUsuario = {
#         'id': user.id,
#         'username': user.username,
#         'email': user.email,
#         'first_name': user.first_name,
#         'last_name': user.last_name,
#         'is_staff': user.is_staff,
#         'usu_tipousuario': usu_tipousuario,
#     }
#
#     request.session["dicUsuario"] = dicUsuario


def elige_choices(obj_choice, str):
    valor = ""
    for key, value in obj_choice:
        if key == str:
            valor = value
    return valor


def str_to_datetime(st, ft='%Y-%m-%d %H:%M:%S'):
    if not isinstance(st, str):
        st = str(st)
    return timezone.make_aware(datetime(*time.strptime(st, ft)[:6]), timezone.get_current_timezone())


def calculo_digito_verificador(el_rut):

    rut = el_rut.split('-')
    x_rut = rut[0]

    # si el largo del rut es menor a 8 se le agrega un 0 en el inicio
    # de la cadena
    if len(str(x_rut)) < 8:
        x_rut = "0{r}".format(r=x_rut)

    # recorrer la cadena
    secuencia = [3, 2, 7, 6, 5, 4, 3, 2]
    contador = 0
    acomulador = 0

    for c in list(x_rut):
        acomulador += int(c) * secuencia[contador]
        contador += 1

    mod = acomulador % 11
    dv = 11 - mod

    if dv == 10:
        dv = "k"

    if dv == 11:
        dv = 0

    return str(dv)


def valida_correo(el_mail):

    correo = el_mail

    if re.match('^[(a-z0-9\_\-\.)]+@[(a-z0-9\_\-\.)]+\.[(a-z)]{2,15}$', correo.lower()):
        return True
    else:
        return False


def thousands_separator(valor, decimales=0, defecto='SI'):
    """
    :param valor (int): Valor principal para formatear
    :param decimales (int): Cantidad de decimales a formatear
    :param defecto (varchar): Si se elige NO, pondra decimales y separadores de miles
    :return:
    """

    if valor is not None and decimales is not None and defecto == 'NO':
        if valor != '':
            return locale.format("%.*f", (decimales, valor), True)
        else:
            return 0
    else:
        if valor is not None:
            if valor != '':
                return locale.format("%d", valor, grouping=True)
            else:
                return 0
        else:
            return 0


def mesesDelAnio(mes):
    if mes == 1:
        return 'ENERO'

    if mes == 2:
        return 'FEBRERO'

    if mes == 3:
        return 'MARZO'

    if mes == 4:
        return 'ABRIL'

    if mes == 5:
        return 'MAYO'

    if mes == 6:
        return 'JUNIO'

    if mes == 7:
        return 'JULIO'

    if mes == 8:
        return 'AGOSTO'

    if mes == 9:
        return 'SEPTEIMBRE'

    if mes == 10:
        return 'OCTUBRE'

    if mes == 11:
        return 'NOVIEMBRE'

    if mes == 12:
        return 'DICIEMBRE'


def formateoAMilesConDecimal(monto, decimales):
    monto = locale.format('%.2f', monto, grouping=True, monetary=True)
    return float(monto)


def formatear_numero(numero, decimales):
    # Definimos el formato que deseamos
    locale.setlocale(locale.LC_ALL, LOCALE_LANG)

    format_numero = locale.format('%.{}f'.format(decimales), numero, grouping=True, monetary=True)

    return format_numero


def ultimoDiaDelMes(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)
    ultimoDiaMes = next_month - timedelta(days=next_month.day)

    # para obtener el numero de dia de la semana el cual va desde [0...6]
    cadena1 = int(ultimoDiaMes.strftime("%w"))

    if cadena1 == 6:
        dias = timedelta(days=1)
        ultimoDiaHabilDelMes = ultimoDiaMes - dias
    elif cadena1 == 0:
        dias = timedelta(days=2)
        ultimoDiaHabilDelMes = ultimoDiaMes - dias
    else:
        ultimoDiaHabilDelMes = ultimoDiaMes

    return ultimoDiaHabilDelMes


def ruta_informes(request):
    host = request.get_host().split(':')[0]
    subdominio = host.split('.')[0]
    ruta = RUTA_PDF + subdominio + '/'
    return ruta


def load_data_base():
    # lista = {}
    lista = BaseEmpresa.objects.using('default').all()

    for base in lista:

        domain = base.ba_link
        subdomain = (domain.split('.')[0]).split('//')[1]

        nueva_base = {}
        nueva_base['ENGINE'] = conf.settings.DATABASES['default']['ENGINE']
        nueva_base['HOST'] = base.ba_host
        nueva_base['NAME'] = base.ba_name
        nueva_base['USER'] = base.ba_user
        nueva_base['PASSWORD'] = base.ba_password
        nueva_base['PORT'] = base.ba_port

        conf.settings.DATABASES[subdomain] = nueva_base



def load_one_database(base):

    try:
        nueva_base = {}
        nueva_base['ENGINE'] = base.ba_engine
        nueva_base['HOST'] = base.ba_host
        nueva_base['NAME'] = base.ba_name
        nueva_base['USER'] = base.ba_user
        nueva_base['PASSWORD'] = base.ba_password
        nueva_base['PORT'] = base.ba_port

        DATABASES[base.ba_conexion] = nueva_base


    except:
        pass


def validaEmpresaActiva():

    cActivo = ClienteActivo.objects.all()

    if cActivo[0].cac_activo == 'S':
        return True
    else:
        return False


# -------------------------------------------------------------------------------------------
# CONVERSION DE NUMERO A LETRAS
# -------------------------------------------------------------------------------------------

def numero_to_letras(numero):
    indicador = [("", ""), ("MIL", "MIL"), ("MILLON", "MILLONES"), ("MIL", "MIL"), ("BILLON", "BILLONES")]
    entero = int(numero)

    contador = 0
    numero_letras = ""
    while entero > 0:
        a = entero % 1000
        if contador == 0:
            en_letras = convierte_cifra(a, 1).strip()
        else:
            en_letras = convierte_cifra(a, 0).strip()
        if a == 0:
            numero_letras = en_letras + " " + numero_letras
        elif a == 1:
            if contador in (1, 3):
                numero_letras = indicador[contador][0] + " " + numero_letras
            else:
                numero_letras = en_letras + " " + indicador[contador][0] + " " + numero_letras
        else:
            numero_letras = en_letras + " " + indicador[contador][1] + " " + numero_letras
        numero_letras = numero_letras.strip()
        contador = contador + 1
        entero = int(entero / 1000)
    numero_letras = numero_letras
    # print('numero: ', numero)
    # print(numero_letras)
    return numero_letras


def convierte_cifra(numero, sw):
    lista_centana = ["", ("CIEN", "CIENTO"), "DOSCIENTOS", "TRESCIENTOS", "CUATROCIENTOS", "QUINIENTOS", "SEISCIENTOS",
                     "SETECIENTOS", "OCHOCIENTOS", "NOVECIENTOS"]
    lista_decena = ["", (
        "DIEZ", "ONCE", "DOCE", "TRECE", "CATORCE", "QUINCE", "DIECISEIS", "DIECISIETE", "DIECIOCHO", "DIECINUEVE"),
                    ("VEINTE", "VEINTI"), ("TREINTA", "TREINTA Y"), ("CUARENTA", "CUARENTA Y"),
                    ("CINCUENTA", "CINCUENTA Y"), ("SESENTA", "SESENTA Y"),
                    ("SETENTA", "SETENTA Y"), ("OCHENTA", "OCHENTA Y"),
                    ("NOVENTA", "NOVENTA Y")
                    ]
    lista_unidad = ["", ("UN", "UNO"), "DOS", "TRES", "CUATRO", "CINCO", "SEIS", "SIETE", "OCHO", "NUEVE"]
    centena = int(numero / 100)
    decena = int((numero - (centena * 100)) / 10)
    unidad = int(numero - (centena * 100 + decena * 10))
    # print "centena: ",centena, "decena: ",decena,'unidad: ',unidad

    texto_unidad = ""

    # Validad las centenas
    texto_centena = lista_centana[centena]
    if centena == 1:
        if (decena + unidad) != 0:
            texto_centena = texto_centena[1]
        else:
            texto_centena = texto_centena[0]

    # Valida las decenas
    texto_decena = lista_decena[decena]
    if decena == 1:
        texto_decena = texto_decena[unidad]
    elif decena > 1:
        if unidad != 0:
            texto_decena = texto_decena[1]
        else:
            texto_decena = texto_decena[0]
    # Validar las unidades
    # print "texto_unidad: ",texto_unidad
    if decena != 1:
        texto_unidad = lista_unidad[unidad]
        if unidad == 1:
            texto_unidad = texto_unidad[sw]

    return "%s %s %s" % (texto_centena, texto_decena, texto_unidad)
