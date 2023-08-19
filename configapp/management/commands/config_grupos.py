# -*- encoding: utf-8 -*-
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from perfil.models import Grupo

class Command(BaseCommand):


    def handle(self, *args, **options):


        print("Listando Grupos...")
        print("---------------------------")
        lst_grupos = [
            {
                'nombre_grupo':'SuperAdministrador'
            }
        ]

        print(" * Agregando:")
        for gr in lst_grupos:

            g = Grupo()
            g.gru_nombre = gr['nombre_grupo']
            g.save()
            print(" ** Grupo :", gr['nombre_grupo'].title())


        print("-----------------------------")
        print("Finalizada la carga")





