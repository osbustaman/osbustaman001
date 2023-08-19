# -*- encoding: utf-8 -*-
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from usuario.models import Bancos
from jab.api_bancos import listado_bancos

class Command(BaseCommand):

    help = 'ingresa el nombre de la nueva base'

    def add_arguments(self, parser):
        parser.add_argument('base', type=str, help='ingresa el nombre de la nueva base')

    def handle(self, *args, **kwargs):

        print("Listando Bancos...")
        print("---------------------------")
        print(" * Agregando:")
        for b in listado_bancos():
            
            if b['CodigoInstitucion'] != '061':
            
                print(b)
                ba = Bancos()
                ba.ban_nombre = b['NombreInstitucion'].title()
                ba.ban_codigo = b['CodigoInstitucion']
                ba.save(using=kwargs['base'])


        print("-----------------------------")
        print("Finalizada la carga")





