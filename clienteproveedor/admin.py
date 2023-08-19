# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from clienteproveedor.models import *

admin.site.register(ClienteProveedor, ClienteProveedorAdmin)
admin.site.register(ClienteProveedorEmpresa, ClienteProveedorEmpresaAdmin)