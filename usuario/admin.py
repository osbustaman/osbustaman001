# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.contrib import admin
from usuario.models import *

admin.site.register(Bancos, BancosAdmin)
admin.site.register(CentroCosto, CentroCostoAdmin)
admin.site.register(CajasCompensacion, CajasCompensacionAdmin)
admin.site.register(Salud, SaludAdmin)
admin.site.register(Afp, AfpAdmin)
admin.site.register(Pais, PaisAdmin)
admin.site.register(Region, RegionAdmin)
admin.site.register(Comuna, ComunaAdmin)
admin.site.register(Empresa, EmpresaAdmin)
admin.site.register(Sucursal, SucursalAdmin)
admin.site.register(Cargo, CargoAdmin)
admin.site.register(CargoEmpresa, CargoEmpresaAdmin)
admin.site.register(Usuario, UsuarioAdmin)
admin.site.register(UsuarioEmpresa, UsuarioEmpresaAdmin)
admin.site.register(RelacionDeAfiliacion, RelacionDeAfiliacionAdmin)
admin.site.register(AsociacionUsuarioEmpresa, AsociacionUsuarioEmpresaAdmin)
admin.site.register(Haberes, HaberesAdmin)
