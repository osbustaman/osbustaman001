#!/usr/bin/env python
#  -*- coding: utf-8 -*-
from django.db import models
from django.contrib import admin


# Create your models here.
class BaseEmpresa(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    ENGINE = (
        ('P', 'django.db.backends.postgresql_psycopg2'),
    )

    ba_id = models.AutoField("Key", primary_key=True)

    # -------------------------------------------------------------------------------
    ba_conexion = models.CharField("ALIAS", max_length=255)
    ba_engine = models.CharField("ENGINE", max_length=255, choices=OPCIONES, default="P")
    ba_esquema = models.CharField("'options': '-c search_path='", max_length=255, null=True, blank=True)
    ba_name = models.CharField("NAME", max_length=255)
    ba_user = models.CharField("USER", max_length=255, default='jab')
    ba_password = models.CharField("PASSWORD", max_length=255, default='nEgWJvX";00mCFJ~mAKL')
    ba_host = models.CharField("HOST", max_length=255, default='localhost')
    ba_port = models.CharField("PORT", max_length=255, default='5432')
    # -------------------------------------------------------------------------------

    ba_nameemp = models.CharField("Nombre de la empresa", max_length=255)
    ba_activa = models.CharField("Base activa", max_length=1, choices=OPCIONES, default="N")
    ba_fechaingreso = models.DateField("Fecha creación de la base", null=True, blank=True)
    ba_fechatermino = models.DateField(verbose_name='Fecha termino de la base', null=True, blank=True)
    ba_link = models.CharField("Link base", max_length=255, default='')

    ba_adddprc = models.CharField("Parametros generales (pais, región, comuna, etc.)", max_length=1, choices=OPCIONES, default="N")
    ba_additm = models.CharField("Creacion de menu", max_length=1, choices=OPCIONES, default="N")
    ba_armada = models.CharField("Estuctura de la base armada", max_length=1, choices=OPCIONES, default="N")
    ba_creada = models.CharField("Base creada", max_length=1, choices=OPCIONES, default="N")
    ba_idclienteactivo = models.IntegerField("ID base cliente activo", null=True, blank=True)
    ba_cantidadusuarios = models.IntegerField("Cantidad usuarios", null=True, blank=True)

    def __int__(self):
        return self.ba_id

    def __str__(self):
        return "{n}".format(n=self.ba_name.title())

    def __migrate(self):
        return "migrate --database {NOMBRE_BASE_DE_DATOS}".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    el_migrate = property(__migrate)

    def __config_data_generic(self):
        return "config_data_generic {NOMBRE_BASE_DE_DATOS}".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    config_data_generic = property(__config_data_generic)

    def __config_ruta(self):
        return "login/empresa/{NOMBRE_BASE_DE_DATOS}/".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    config_ruta = property(__config_ruta)

    def __config_super_user(self):
        return "createsuperuser --database {NOMBRE_BASE_DE_DATOS}".format(NOMBRE_BASE_DE_DATOS=self.ba_name)

    config_super_user = property(__config_super_user)

    def save(self, *args, **kwargs):
        self.ba_conexion = self.ba_conexion.lower()
        self.ba_esquema = self.ba_esquema.lower()
        self.ba_name = self.ba_name.lower()
        self.ba_nameemp = self.ba_nameemp.lower()
        self.ba_link = self.ba_link.lower()
        super(BaseEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'bases_bases'
        ordering = ['ba_id']


class BaseEmpresaAdmin(admin.ModelAdmin):
    list_display = ('ba_id', 'ba_nameemp', 'ba_name', 'ba_password', 'ba_host', 'ba_port', 'ba_activa', 'el_migrate')