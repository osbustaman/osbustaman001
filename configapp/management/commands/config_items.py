# -*- encoding: utf-8 -*-
import os
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

from perfil.models import Item, SubItem


class Command(BaseCommand):

    help = 'ingresa el nombre de la nueva base'

    def add_arguments(self, parser):
        parser.add_argument('base', type=str, help='ingresa el nombre de la nueva base')

    def handle(self, *args, **kwargs):

        print("Listando Items...")
        print("Listando Sub-Items...")
        print("---------------------------")
        lst_items = [
            {
                'item_nombre':'Empresa',
                'item_css_img':'fa fa-university',
                'item_orden':1,
                'sub_items': [
                    {
                        'subitem_nombre': 'Datos empresa',
                        'subitem_orden': 1,
                        'subitem_namespace_link': 'views_empresa',
                    },{
                        'subitem_nombre': 'Cargos',
                        'subitem_orden': 2,
                        'subitem_namespace_link': 'views_cargos',
                    }
                    ,{
                        'subitem_nombre': 'Centro de costo',
                        'subitem_orden': 3,
                        'subitem_namespace_link': 'views_grupos_centro_costo',
                    }
                ]
            },{
                'item_nombre':'Personal',
                'item_css_img':'fa fa-users',
                'item_orden':2,
                'sub_items': [
                    {
                        'subitem_nombre': 'Ver fichas',
                        'subitem_orden': 1,
                        'subitem_namespace_link': 'views_empleados',
                    }
                ]
            },{
                'item_nombre':'Remuneraciones',
                'item_css_img':'fa fa-money',
                'item_orden':3,
                'sub_items': [
                    {
                        'subitem_nombre': 'Libro de remuneraciones',
                        'subitem_orden': 1,
                        'subitem_namespace_link': '#',
                    }, {
                        'subitem_nombre': 'Haberes y descuentos',
                        'subitem_orden': 2,
                        'subitem_namespace_link': 'viewsHaberesDescuentos',
                    }, {
                        'subitem_nombre': 'Exportar datos',
                        'subitem_orden': 3,
                        'subitem_namespace_link': 'exportarDatos',
                    }
                ]
            },{
                'item_nombre':'Solicitudes',
                'item_css_img':'fa fa-pencil-square-o',
                'item_orden':4,
                'sub_items': [
                    {
                        'subitem_nombre': 'Solicitar vacaciones',
                        'subitem_orden': 1,
                        'subitem_namespace_link': '#',
                    }, {
                        'subitem_nombre': 'Aprobar vacaciones',
                        'subitem_orden': 1,
                        'subitem_namespace_link': '#',
                    }, {
                        'subitem_nombre': 'Aprobar solicitud vacaciones',
                        'subitem_orden': 2,
                        'subitem_namespace_link': '#',
                    }
                ]
            },{
                'item_nombre':'Documentos',
                'item_css_img':'fa fa-file-text',
                'item_orden':5,
                'sub_items': [
                    {
                        'subitem_nombre': 'Contratos',
                        'subitem_orden': 1,
                        'subitem_namespace_link': '#',
                    }
                ]
            },{
                'item_nombre':'Mantenedores',
                'item_css_img':'fa fa-upload',
                'item_orden':6,
                'sub_items': [
                    {
                        'subitem_nombre': 'Exportador',
                        'subitem_orden': 1,
                        'subitem_namespace_link': '#',
                    }
                ]
            },{
                'item_nombre':'Configuración',
                'item_css_img':'fa fa-cog',
                'item_orden':7,
                'sub_items': [
                    {
                        'subitem_nombre': 'Impuestos',
                        'subitem_orden': 1,
                        'subitem_namespace_link': '#',
                    },{
                        'subitem_nombre': 'Parámetros',
                        'subitem_orden': 2,
                        'subitem_namespace_link': 'views_parametros',
                    }
                ]
            }
        ]

        print(" * Agregando:")
        for it in lst_items:
            try:
                i = Item.objects.get(item_nombre = it['item_nombre'])
                print("El item :", it['item_nombre'], ", ya se encuentra cargado...")
                print("-----------------------------")
            except:

                i = Item()
                i.item_nombre = it['item_nombre']
                i.item_css_img = it['item_css_img']
                i.item_orden = it['item_orden']
                i.save(using=kwargs['base'])
                print(" ** Item :", it['item_nombre'].title())
                
                for su in it['sub_items']:
                    s = SubItem()
                    s.item = i
                    s.subitem_nombre = su['subitem_nombre']
                    s.subitem_orden  = su['subitem_orden']
                    s.subitem_namespace_link = su['subitem_namespace_link']
                    s.save(using=kwargs['base'])
                    print(" ****** Sub-Items :", su['subitem_nombre'].title())

        print("Finalizada la carga")
        print("-----------------------------")





