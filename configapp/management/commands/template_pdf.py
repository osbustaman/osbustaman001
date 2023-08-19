# -*- encoding: utf-8 -*-
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError
from jab.settings import BASE_COMMAND

class Command(BaseCommand):

    def handle(self, *args, **kwargs):

        print("Buscando carpeta...")
        print("Leyendo ruta...")
        print("{}/static/documentoshtmltopdf/...".format(BASE_COMMAND))






