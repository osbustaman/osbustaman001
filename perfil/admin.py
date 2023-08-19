# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from perfil.models import *

admin.site.register(Menu, MenuAdmin)
admin.site.register(Item, ItemAdmin)
admin.site.register(MenuItem, MenuItemAdmin)
admin.site.register(SubItem, SubItemAdmin)
admin.site.register(Grupo, GrupoAdmin)
admin.site.register(GrupoUsuario, GrupoUsuarioAdmin)
admin.site.register(UsuarioLogeado, UsuarioLogeadoAdmin)
