#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import requests


APIKEY_SBIF = '0eb328d624ae90b536baadfe747ecafb74830841'

# *****************************************************************************
# API DOLAR
# *****************************************************************************
def api_dolar(tipo_dato='AMBOS'):
    """
    funcion solo para ver los valores al dia actual
    @param tipo_dato: FECHA, VALOR, AMBOS
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/dolar?apikey={}&formato={}'.format(APIKEY_SBIF, 'json')
    fecha=""
    valor=""
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_dolar = response_json['Dolares']
        
        for dolar in data_dolar:
            fecha = dolar['Fecha']
            valor = dolar['Valor']
            
    if tipo_dato == 'FECHA':
        return fecha  
    
    if tipo_dato == 'VALOR':
        return valor
    
    if tipo_dato == 'AMBOS':
        ambos = "{}: {}".format(fecha, valor)
        return ambos  



def api_dolar_anio_especifico(anio):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param Integer: anio solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/dolar/{}?apikey={}&formato={}'.format(anio, APIKEY_SBIF, 'json')
    lst_dolar = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_dolar = response_json['Dolares']
        
        for dolar in data_dolar:
            lst_dolar.append({
                'fecha':dolar['Fecha'],
                'valor':dolar['Valor']
                })
            
    return lst_dolar

def api_dolar_anio_mes_especifico(anio, mes):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param anio: Integer anio solicitado
    @param mes: Integer mes solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/dolar/{}/{}?apikey={}&formato={}'.format(anio, mes, APIKEY_SBIF, 'json')
    lst_dolar = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_dolar = response_json['Dolares']
        
        for dolar in data_dolar:
            lst_dolar.append({
                'fecha':dolar['Fecha'],
                'valor':dolar['Valor']
                })
            
    return lst_dolar

# *****************************************************************************
# API UF
# *****************************************************************************
def api_uf(tipo_dato='AMBOS'):
    """
    funcion solo para ver los valores al dia actual
    @param tipo_dato: FECHA, VALOR, AMBOS
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/uf?apikey={}&formato={}'.format(APIKEY_SBIF, 'json')
    fecha=""
    valor=""
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_uf = response_json['UFs']
        
        for uf in data_uf:
            fecha = uf['Fecha']
            valor = uf['Valor']
            
    if tipo_dato == 'FECHA':
        return fecha  
    
    if tipo_dato == 'VALOR':
        return valor
    
    if tipo_dato == 'AMBOS':
        ambos = "{}: {}".format(fecha, valor)
        return ambos
    
def api_uf_anio_especifico(anio):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param Integer: anio solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/uf/{}?apikey={}&formato={}'.format(anio, APIKEY_SBIF, 'json')
    lst_uf = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_uf = response_json['UFs']
        
        for uf in data_uf:
            lst_uf.append({
                'fecha':uf['Fecha'],
                'valor':uf['Valor']
                })
            
    return lst_uf

def api_uf_anio_mes_especifico(anio, mes):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param anio: Integer anio solicitado
    @param mes: Integer mes solicitado
    """

    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/uf/{}/{}?apikey={}&formato={}'.format(anio, mes, APIKEY_SBIF, 'json')
    lst_uf = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_uf = response_json['UFs']
        
        for uf in data_uf:
            lst_uf.append({
                'fecha':uf['Fecha'],
                'valor':uf['Valor']
                })
            
    return lst_uf


def api_uf_dia_especifico(anio, mes, dia):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param anio: Integer anio solicitado
    @param mes: Integer mes solicitado
    """

    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/uf/{}/{}/dias/{}?apikey={}&formato={}'.format(anio, mes, dia, APIKEY_SBIF, 'json')

    lst_uf = []

    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)

    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json()  # Dic
        data_uf = response_json['UFs']

        for uf in data_uf:
            lst_uf.append({
                'fecha': uf['Fecha'],
                'valor': uf['Valor']
            })

    return lst_uf

# *****************************************************************************
# API IPC
# *****************************************************************************
def api_ipc(tipo_dato='AMBOS'):
    """
    funcion solo para ver los valores al dia actual
    @param tipo_dato: FECHA, VALOR, AMBOS
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/ipc?apikey={}&formato={}'.format(APIKEY_SBIF, 'json')
    fecha=""
    valor=""
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_ipc = response_json['IPCs']
        
        for ipc in data_ipc:
            fecha = ipc['Fecha']
            valor = ipc['Valor']
            
    if tipo_dato == 'FECHA':
        return fecha  
    
    if tipo_dato == 'VALOR':
        return valor
    
    if tipo_dato == 'AMBOS':
        ambos = "{}: {}".format(fecha, valor)
        return ambos  


def api_ipc_anio_especifico(anio):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param Integer: anio solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/ipc/{}?apikey={}&formato={}'.format(anio, APIKEY_SBIF, 'json')
    lst_ipc = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_ipc = response_json['IPCs']
        
        for ipc in data_ipc:
            lst_ipc.append({
                'fecha':ipc['Fecha'],
                'valor':ipc['Valor']
                })
            
    return lst_ipc

def api_ipc_anio_mes_especifico(anio, mes):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param anio: Integer anio solicitado
    @param mes: Integer mes solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/ipc/{}/{}?apikey={}&formato={}'.format(anio, mes, APIKEY_SBIF, 'json')
    lst_ipc = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_ipc = response_json['IPCs']
        
        for ipc in data_ipc:
            lst_ipc.append({
                'fecha':ipc['Fecha'],
                'valor':ipc['Valor']
                })
            
    return lst_ipc


# *****************************************************************************
# API UTM
# *****************************************************************************
def api_utm(tipo_dato='AMBOS'):
    """
    funcion solo para ver los valores al dia actual
    @param tipo_dato: FECHA, VALOR, AMBOS
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/utm?apikey={}&formato={}'.format(APIKEY_SBIF, 'json')
    fecha=""
    valor=""
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_utm = response_json['UTMs']
        
        for utm in data_utm:
            fecha = utm['Fecha']
            valor = utm['Valor']
            
    if tipo_dato == 'FECHA':
        return fecha  
    
    if tipo_dato == 'VALOR':
        return valor
    
    if tipo_dato == 'AMBOS':
        ambos = "{}: {}".format(fecha, valor)
        return ambos  


def api_utm_anio_especifico(anio):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param Integer: anio solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/utm/{}?apikey={}&formato={}'.format(anio, APIKEY_SBIF, 'json')
    lst_utm = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_utm = response_json['UTMs']
        
        for utm in data_utm:
            lst_utm.append({
                'fecha':utm['Fecha'],
                'valor':utm['Valor']
                })
            
    return lst_utm

def api_utm_anio_mes_especifico(anio, mes):
    """
    funcion solo para ver los valores de todos los dias de unio especifico
    @param anio: Integer anio solicitado
    @param mes: Integer mes solicitado
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/utm/{}/{}?apikey={}&formato={}'.format(anio, mes, APIKEY_SBIF, 'json')
    lst_utm = []
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_utm = response_json['UTMs']
        
        for utm in data_utm:
            lst_utm.append({
                'fecha':utm['Fecha'],
                'valor':utm['Valor']
                })
            
    return lst_utm

if __name__ == '__main__':
    print("DOLAR:", api_dolar())
    print("-------------------------")
    print("UTM:", api_utm())
    print("-------------------------")
    print("IPC:", api_ipc())
    print("-------------------------")
    print("UF:", api_uf())
    
    #https://api.sbif.cl/documentacion/index.html
        