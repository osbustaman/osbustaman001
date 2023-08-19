# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from documento.models import *

admin.site.register(Documento, DocumentoAdmin)
admin.site.register(DocumentoEmpleado, DocumentoEmpleadoAdmin)
admin.site.register(TipoDocumentos, TipoDocumentosAdmin)
admin.site.register(DocumentoEmpresa, DocumentoEmpresaAdmin)
admin.site.register(DocumentoEncabezado, DocumentoEncabezadoAdmin)
admin.site.register(DocumentoEncabezadoDetalle, DocumentoEncabezadoDetalleAdmin)