#!/usr/bin/env python
#  -*- coding: utf-8 -*-
import os

from jab.settings import BASE_COMMAND

if __name__ == '__main__':

    print("Buscando carpeta...")
    print("Leyendo ruta...")


    directorio_base = "{}templates/documentoshtmltopdf/".format(BASE_COMMAND)

    print(directorio_base)

    try:
        os.stat(directorio_base)
    except:
        os.mkdir(directorio_base)

    print("Directorio creado correctamente...")
    print("Creando documentos por defecto...")

    lstDocumentos = [
        {
            'documento':'contrato jornada normal',
            'texto':''

        },{
            'documento':'contrato jornada parcial',
            'texto':''
        },{
            'documento':'contrato por obra',
            'texto': ''
        },{
            'documento':'contrato part time',
            'texto': ''
        },{
            'documento':'contrato extranjeros',
            'texto': ''
        },{
            'documento':'contrato jefaturas art 22 clausulas especiales',
            'texto': ''
        },{
            'documento':'anexo contratos extension plazo',
            'texto': ''
        },{
            'documento':'anexo contratos cambio sueldo',
            'texto': ''
        },{
            'documento':'anexo contrato otro articulo',
            'texto': ''
        },{
            'documento':'entrega reglamento interno',
            'texto': ''
        },{
            'documento':'politica seguridad',
            'texto': ''
        },{
            'documento':'riesgos laborales',
            'texto': ''
        },{
            'documento':'das',
            'texto': ''
        },{
            'documento':'formulario vacaciones',
            'texto': ''
        },{
            'documento':'formulario prestamo',
            'texto': ''
        },{
            'documento':'formulario hrs extras',
            'texto': ''
        },{
            'documento':'evaluacion desempeno',
            'texto': ''
        },{
            'documento':'carta amonestacion',
            'texto': ''
        },{
            'documento':'certificados antiguedad y vigencia',
            'texto': ''
        },{
            'documento':'entrega de equipos y elementos',
            'texto': ''
        },{
            'documento':'calculo finiquito',
            'texto': ''
        },{
            'documento':'carta aviso segun causal correo o personal',
            'texto': ''
        },{
            'documento':'finiquito',
            'texto': ''
        }
    ]

    for x in lstDocumentos:
        cadena_file = "{}{}.html".format(directorio_base, x['documento'].replace(' ', '_'))
        print("Creando {}".format(cadena_file))
        file = open(cadena_file, "w")
        file.write(x['texto'])
    file.close()