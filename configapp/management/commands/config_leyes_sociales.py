# -*- encoding: utf-8 -*-
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from usuario.models import Salud, Afp

class Command(BaseCommand):
    
    def add_arguments(self, parser):
        parser.add_argument('base', type=str, help='ingresa el nombre de la base')

    def handle(self, *args, **kwargs):


        lstSalud = [
            {'sa_nombre':'Fonasa', 'sa_codigo':'100', 'sa_tipo':'F'},
            {'sa_nombre':'Banmédica S.A.', 'sa_codigo':'99', 'sa_tipo':'I'},
            {'sa_nombre':'Chuquicamata Ltda.', 'sa_codigo':'65', 'sa_tipo':'I'},
            {'sa_nombre':'Colmena Golden Cross S.A.','sa_codigo':'67','sa_tipo':'I'},
            {'sa_nombre':'Consalud S.A.','sa_codigo':'107','sa_tipo':'I'},
            {'sa_nombre':'Cruz Blanca S.A.','sa_codigo':'78','sa_tipo':'I'},
            {'sa_nombre':'Cruz del Norte Ltda.','sa_codigo':'94','sa_tipo':'I'},
            {'sa_nombre':'Nueva Masvida S.A.','sa_codigo':'81','sa_tipo':'I'},
            {'sa_nombre':'Fundación Ltda.','sa_codigo':'76','sa_tipo':'I'},
            {'sa_nombre':'Fusat Ltda.','sa_codigo':'63','sa_tipo':'I'},
            {'sa_nombre':'Río Blanco Ltda.','sa_codigo':'68','sa_tipo':'I'},
            {'sa_nombre':'San Lorenzo Ltda.','sa_codigo':'62','sa_tipo':'I'},
            {'sa_nombre':'Vida Tres S.A.','sa_codigo':'80','sa_tipo':'I'},
        ]
        
        for salud in lstSalud:
            s = Salud()
            s.sa_nombre     = salud['sa_nombre']
            s.sa_codigo     = salud['sa_codigo']
            s.sa_tipo       = salud['sa_tipo']
            s.save(using=kwargs['base'])
            print(s)
            
            
        print('Entidades de salud creadas')
        print('***********************************************')
        
        

        lstPrevision = [
            {'afp_codigoprevired':'33', 'afp_nombre':'Capital', 'afp_tasatrabajadordependiente':11.44, 'afp_sis':1.53, 'afp_tasatrabajadorindependiente':12.97},
            {'afp_codigoprevired':'03', 'afp_nombre':'Cuprum', 'afp_tasatrabajadordependiente':11.44, 'afp_sis':1.53, 'afp_tasatrabajadorindependiente':12.97},
            {'afp_codigoprevired':'05', 'afp_nombre':'Habitat', 'afp_tasatrabajadordependiente':11.27, 'afp_sis':1.53, 'afp_tasatrabajadorindependiente':12.80},
            {'afp_codigoprevired':'29', 'afp_nombre':'PlanVital', 'afp_tasatrabajadordependiente':11.16, 'afp_sis':1.53, 'afp_tasatrabajadorindependiente':12.69},
            {'afp_codigoprevired':'08', 'afp_nombre':'ProVida', 'afp_tasatrabajadordependiente':11.45, 'afp_sis':1.53, 'afp_tasatrabajadorindependiente':12.98},
            {'afp_codigoprevired':'34', 'afp_nombre':'Modelo', 'afp_tasatrabajadordependiente':10.77, 'afp_sis':1.53, 'afp_tasatrabajadorindependiente':12.30},
        ]
        
        for prev in lstPrevision:
            a = Afp()
            a.afp_codigoprevired = prev['afp_codigoprevired']
            a.afp_nombre = prev['afp_nombre']
            a.afp_tasatrabajadordependiente = prev['afp_tasatrabajadordependiente']
            a.afp_sis = prev['afp_sis']
            a.afp_tasatrabajadorindependiente = prev['afp_tasatrabajadorindependiente']
            a.save(using=kwargs['base'])
            print(a)
            
            
        print('Entidades de prevision creadas')
        print('***********************************************')