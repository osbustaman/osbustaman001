# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import datetime

from usuario.models import Empresa


# --------------------------------------------------------------
class ClienteActivo(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    cac_id = models.AutoField("Key", primary_key=True)
    cac_activo = models.CharField("Cliente activo?", max_length=1, choices=OPCIONES, default="S")
    cac_cantempleados = models.IntegerField("Cantidad de empleados", null=True, blank=True, default=10)
    cac_rutabase = models.CharField("Ruta base", max_length=255, null=True, blank=True, default='')
    cac_rutadocumentos = models.CharField("Ruta documentos", max_length=255, null=True, blank=True, default='')
    cac_rutadstatic = models.CharField("Ruta archivos static", max_length=255, null=True, blank=True, default='')
    cac_rutausuarios = models.CharField("Ruta usuarios", max_length=255, null=True, blank=True, default='')
    cac_nombrebase = models.CharField("Nombre base", max_length=255, null=True, blank=True, default='')
    cac_nombreimagenlogo = models.CharField("Nombre imagen logo", max_length=255, null=True, blank=True, default='')

    def __int__(self):
        return self.cac_id

    def __str__(self):
        return "{n}".format(n=self.cac_id)

    def __ruta_documentos_completa__(self):
        return "/{}/{}/".format(self.cac_rutabase, self.cac_rutadocumentos)

    ruta_base = property(__ruta_documentos_completa__)

    def __ruta_usuarios_completa__(self):
        return "/{}/{}/".format(self.cac_rutabase, self.cac_rutausuarios)

    ruta_usuarios = property(__ruta_usuarios_completa__)

    def save(self, *args, **kwargs):
        super(ClienteActivo, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_cliente_activo"
        ordering = ['cac_id']


class ClienteActivoAdmin(admin.ModelAdmin):
    list_display = ('cac_activo', 'cac_activo')


# --------------------------------------------------------------
class Parametros(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    param_id = models.AutoField("Key", primary_key=True)
    param_codigo = models.CharField("Código del parámetro", max_length=10)
    param_descripcion = models.TextField("Descripción", max_length=255)
    param_valor = models.CharField("Valor", max_length=50, null=True, blank=True, default=0)
    param_rangoini = models.DecimalField("Desde $", max_digits=15, decimal_places=6, null=True, blank=True, default=0)
    param_rangofin = models.DecimalField("Hasta $", max_digits=15, decimal_places=6, null=True, blank=True, default=0)
    param_factor = models.CharField("Factor", max_length=50)
    param_activo = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.param_id

    def __str__(self):
        return "{n}-{cc}".format(n=self.param_id, cc=self.param_descripcion)

    def save(self, *args, **kwargs):
        super(Parametros, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_parametros"
        ordering = ['param_id']


class ParametrosAdmin(admin.ModelAdmin):
    list_display = (
    'param_id', 'param_codigo', 'param_descripcion', 'param_valor', 'param_rangoini', 'param_rangofin', 'param_activo')


class TablaGeneral(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    tg_id = models.AutoField(primary_key=True)
    tg_nomtabla = models.CharField("Nombre tabla", max_length=255)
    tg_codigo = models.CharField("Código", max_length=15)
    tg_cod_ext = models.CharField("Código externo", blank=True, null=True, default='', max_length=15)
    tg_descripcion = models.CharField("Descripción", max_length=150)
    tg_num_aux = models.IntegerField("Número auxiliar", blank=True, null=True)
    tg_fecha_aux = models.DateField("Fecha auxiliar", blank=True, null=True)
    tg_text_aux = models.CharField("Texto auxiliar", max_length=200, blank=True, null=True)
    tg_valor = models.DecimalField("Valor", max_digits=15, decimal_places=2, blank=True, null=True)
    # user_cre = models.IntegerField(verbose_name='Usuario Creador', default=0)
    # fecha_cre = models.DateTimeField(verbose_name='Fecha Creacion', default=timezone.now)
    # user_mod = models.IntegerField(verbose_name='Usuario Modificador', default=0)
    # fecha_mod = models.DateTimeField(verbose_name='Fecha Modificacion', default=timezone.now)
    tg_estado = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.tg_id

    def __str__(self):
        return "{}-{}".format(self.tg_codigo, self.tg_descripcion)

    def save(self, *args, **kwargs):
        super(TablaGeneral, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_tabla_general"
        ordering = ['tg_id']


class TablaGeneralAdmin(admin.ModelAdmin):
    list_display = ('tg_id', 'tg_nomtabla', 'tg_codigo', 'tg_descripcion', 'tg_estado')


# --------------------------------------------------------------
class Moneda(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    CANTIDAD_DECIMALES = (
        (0, 0),
        (1, 1),
        (2, 2),
        (3, 3),
    )

    mon_id = models.CharField("Key", primary_key=True, max_length=3)
    mon_simbolo = models.CharField("Simbolo", max_length=3)
    mon_cantidaddecimales = models.IntegerField("Cantidad d decimales", choices=CANTIDAD_DECIMALES, default=0)
    mon_descripcion = models.CharField("Descripción", max_length=255)
    mon_activa = models.CharField("Moneda activa", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.mon_id

    def __str__(self):
        return "%s" % self.mon_simbolo

    def save(self, *args, **kwargs):
        super(Moneda, self).save(*args, **kwargs)

    class Meta:
        db_table = "conf_moneda"
        ordering = ['mon_id']


class MonedaAdmin(admin.ModelAdmin):
    list_display = ('mon_id', 'mon_simbolo', 'mon_cantidaddecimales', 'mon_descripcion', 'mon_activa')
