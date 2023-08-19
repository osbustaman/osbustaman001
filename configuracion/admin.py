# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from configuracion.models import *

admin.site.register(ClienteActivo, ClienteActivoAdmin)
admin.site.register(Parametros, ParametrosAdmin)
admin.site.register(TablaGeneral, TablaGeneralAdmin)
admin.site.register(Moneda, MonedaAdmin)