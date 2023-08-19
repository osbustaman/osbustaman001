# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse

from jab.threadlocal import thread_local

import os


class menu_middleware_items(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        try:
            if 'panecontrol/views/empresa/' in request.path:
                request.session['item'] = 'configuracion'
                request.session['sub_item'] = 'empresa'

            if 'panecontrol/edit/empresa/' in request.path:
                request.session['item'] = 'configuracion'
                request.session['sub_item'] = 'empresa'

            if '/panecontrol/views/personal/' in request.path:
                request.session['item'] = 'personal'
                request.session['sub_item'] = 'ver_listado'

            if '/panecontrol/views/ficha/empleado/' in request.path:
                request.session['item'] = 'personal'
                request.session['sub_item'] = 'ver_fichas'

            if '/panecontrol/views/documentos/' in request.path:
                request.session['item'] = 'documentos'
                request.session['sub_item'] = 'contratos'

            if '/panecontrol/agregar/nuevo/documentos/' in request.path:
                request.session['item'] = 'documentos'
                request.session['sub_item'] = 'ver_documentos'

            if '/panecontrol/views/parametros/' in request.path:
                request.session['item'] = 'configuracion'
                request.session['sub_item'] = 'parametros'

            if '/panecontrol/listado/documentos/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'configuracion_documentos'

            if 'add/grupo/documento/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'configuracion_documentos'

            if '/panecontrol/edit/grupo/documento/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'configuracion_documentos'

            if '/panecontrol/add/nuevo/documento/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'configuracion_documentos'

            if '/panecontrol/editar/nuevo/documentos/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'configuracion_documentos'

            if '/panecontrol/views/cliente/proveedor/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'cliente/proveedor'

            if '/panecontrol/add/cliente/proveedor/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'cliente_proveedor'

            if '/panecontrol/edit/cliente/proveedor/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'cliente_proveedor'

            if '/panecontrol/cliente/proveedor/empresa/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'cliente_proveedor'

            if '/panecontrol/exportador/' in request.path:
                request.session['item'] = 'mantenedores'
                request.session['sub_item'] = 'exportador'

            if '/doc/cliente/' in request.path:
                request.session['item'] = 'documentos'
                request.session['sub_item'] = 'clientes'

            if '/doc/proveedor/' in request.path:
                request.session['item'] = 'documentos'
                request.session['sub_item'] = 'proveedores'

            if '/panecontrol/views/config/empresa/' in request.path:
                request.session['item'] = 'configuracion'
                request.session['sub_item'] = 'config._empresa'

            if '/bases/' in request.path:
                request.session['item'] = 'bases'
                request.session['sub_item'] = 'ver_bases'

            if '/editar/base/' in request.path:
                request.session['item'] = 'bases'
                request.session['sub_item'] = 'ver_bases'

            if '/default/' in request.path:
                request.session['item'] = 'configuracion_entorno'
                request.session['sub_item'] = 'documentos_por_defecto'

            if '/add/nuevo/tipo/documento/' in request.path:
                request.session['item'] = 'configuracion_entorno'
                request.session['sub_item'] = 'documentos_por_defecto'

            if '/agregar/documento/standart/' in request.path:
                request.session['item'] = 'configuracion_entorno'
                request.session['sub_item'] = 'documentos_por_defecto'
        except:
            pass
