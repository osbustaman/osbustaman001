# -*- encoding: utf-8 -*-
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from configuracion.models import Parametros

class Command(BaseCommand):

    help = 'ingresa el nombre de la nueva base'

    def add_arguments(self, parser):
        parser.add_argument('base', type=str, help='ingresa el nombre de la nueva base')

    def handle(self, *args, **kwargs):


        print("Listando Parametros...")
        print("---------------------------")
        lst_parametros = [
            {
                'param_codigo':'FONASA',
                'param_descripcion':'Fondo nacional de salud (fonasa)',
                'param_valor':'7',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'IVA',
                'param_descripcion':'Impuesto valor agregado (IVA)',
                'param_valor':'19',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'SMINIMO',
                'param_descripcion':'Sueldo mínimo',
                'param_valor':'301000',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'RTIAFP',
                'param_descripcion':'Para afiliados a una AFP (UF)',
                'param_valor':'79.2',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'RTIIPS',
                'param_descripcion':'Para afiliados al IPS (ex INP) (UF)',
                'param_valor':'60',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'RTIAFC',
                'param_descripcion':'Para Seguro de Cesantía (UF)',
                'param_valor':'118.9',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'APVMENSUAL',
                'param_descripcion':'Tope Mensual (UF)',
                'param_valor':'50',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'APVANUAL',
                'param_descripcion':'Tope Anual (UF)',
                'param_valor':'600',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'DEPCONV',
                'param_descripcion':'Depósito Convenido Tope Anual (UF)',
                'param_valor':'900',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'CPIEMP',
                'param_descripcion':'Contrato Plazo Indefinido empleador',
                'param_valor':'2,4',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'CPITRAB',
                'param_descripcion':'Contrato Plazo Indefinido Trabajador',
                'param_valor':'0,6',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'CPFEMP',
                'param_descripcion':'Contrato Plazo Fijo Empleador',
                'param_valor':'3,0',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'CPF11',
                'param_descripcion':'Contrato Plazo Indefinido 11 años o más',
                'param_valor':'0,8',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'TPEMP',
                'param_descripcion':'Trabajo pesado empleador',
                'param_valor':'2,0',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'TPTRAB',
                'param_descripcion':'Trabajo pesado trabajador',
                'param_valor':'2,0',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'TMPEMP',
                'param_descripcion':'Trabajo menos pesado empleador',
                'param_valor':'1,0',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'TMPTRAB',
                'param_descripcion':'Trabajo menos pesado trabajador',
                'param_valor':'1,0',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'GRATIF',
                'param_descripcion':'Factor para calcular gratificación',
                'param_valor':'4,75',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'DIASMES',
                'param_descripcion':'Días del mes',
                'param_valor':'30',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'HORASLAB',
                'param_descripcion':'Horas laborales',
                'param_valor':'45',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'RECLEGHOEX',
                'param_descripcion':'Recargo legal hora extra',
                'param_valor':'1,5',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'ASIGNFAMT1',
                'param_descripcion':'Asignación familiar tramo 1',
                'param_valor': '12.364',
                'param_rangoini':0,
                'param_rangofin':315841,
                'param_factor':'0',
            },{
                'param_codigo':'ASIGNFAMT2',
                'param_descripcion':'Asignación familiar tramo 2',
                'param_valor': '7.587',
                'param_rangoini':315841,
                'param_rangofin':461320,
                'param_factor':'0',
            },{
                'param_codigo':'ASIGNFAMT3',
                'param_descripcion':'Asignación familiar tramo 3',
                'param_valor': '2.398',
                'param_rangoini':461320,
                'param_rangofin':719502,
                'param_factor':'0',
            },{
                'param_codigo':'ASIGNFAMT4',
                'param_descripcion':'Asignación familiar tramo 4',
                'param_valor': '0',
                'param_rangoini':719502,
                'param_rangofin':0,
                'param_factor':'0',
            },{
                'param_codigo':'SMINIM3165',
                'param_descripcion':'Menores de 18 y Mayores de 65',
                'param_valor':'224704',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'SUMINIMOCP',
                'param_descripcion':'Trabajadores de Casa Particular',
                'param_valor':'301000',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo':'FINESNOREM',
                'param_descripcion':'Para fines no remuneracionales',
                'param_valor':'194164',
                'param_rangoini': 0,
                'param_rangofin': 0,
                'param_factor':'0',
            },{
                'param_codigo': 'IMPSEGC1',
                'param_descripcion': 'Segmento 1',
                'param_valor': '0',
                'param_rangoini': 0,
                'param_rangofin': 13.5,
                'param_factor': '0',
            },{
                'param_codigo': 'IMPSEGC2',
                'param_descripcion': 'Segmento 2',
                'param_valor': '4',
                'param_rangoini': 13.5,
                'param_rangofin': 30,
                'param_factor': '0.54',
            },{
                'param_codigo': 'IMPSEGC3',
                'param_descripcion': 'Segmento 3',
                'param_valor': '8',
                'param_rangoini': 30,
                'param_rangofin': 50,
                'param_factor': '1.78',
            },{
                'param_codigo': 'IMPSEGC4',
                'param_descripcion': 'Segmento 4',
                'param_valor': '13.5',
                'param_rangoini': 50,
                'param_rangofin': 70,
                'param_factor': '4.48',
            },{
                'param_codigo': 'IMPSEGC5',
                'param_descripcion': 'Segmento 5',
                'param_valor': '23',
                'param_rangoini': 70,
                'param_rangofin': 90,
                'param_factor': '11.14',
            },{
                'param_codigo': 'IMPSEGC6',
                'param_descripcion': 'Segmento 6',
                'param_valor': '30.4',
                'param_rangoini': 90,
                'param_rangofin': 120,
                'param_factor': '17.8',
            },{
                'param_codigo': 'IMPSEGC7',
                'param_descripcion': 'Segmento 7',
                'param_valor': '35',
                'param_rangoini': 120,
                'param_rangofin': 150,
                'param_factor': '23.32',
            },{
                'param_codigo': 'IMPSEGC8',
                'param_descripcion': 'Segmento 8',
                'param_valor': '40',
                'param_rangoini': 150,
                'param_rangofin': 0,
                'param_factor': '30.82',
            },
            
        ]

        print(" * Agregando:")
        for pr in lst_parametros:
            
            try:
                p = Parametros.objects.get(param_codigo = pr['param_codigo'])
            except:                
                p = Parametros()
            p.param_codigo = pr['param_codigo']
            p.param_descripcion = pr['param_descripcion']
            p.param_valor  = pr['param_valor']
            p.param_rangoini  = pr['param_rangoini']
            p.param_rangofin  = pr['param_rangofin']
            p.param_factor = pr['param_factor']
            p.save(using=kwargs['base'])
            print(" ** Parametros :", pr['param_codigo'].title())


        print("-----------------------------")
        print("Finalizada la carga")





