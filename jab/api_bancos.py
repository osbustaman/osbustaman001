#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import requests

APIKEY_SBIF = '0eb328d624ae90b536baadfe747ecafb74830841'

# *****************************************************************************
# API LISTADO BANCOS
# *****************************************************************************
def listado_bancos():
    
    """
    funcion solo para ver el listado de los bancos
    """
    url = 'https://api.sbif.cl/api-sbifv3/recursos_api/perfil/instituciones?apikey={}&formato={}'.format(APIKEY_SBIF, 'json')
    lst_bancos=[]
    
    # debe recibir un parametro en donde se indica la url
    response = requests.get(url)
    
    # condion para saber que estoy bien conectado
    if response.status_code == 200:
        response_json = response.json() #Dic
        data_bancos = response_json['Perfiles']
        
        for bancos in data_bancos:
            lst_bancos.append(bancos['Institucion'])
    
    return lst_bancos


if __name__ == '__main__':
    print(listado_bancos())
    
    #https://api.sbif.cl/documentacion/index.html