#!/usr/bin/env python
#  -*- coding: utf-8 -*-

import django
import xlwt
from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin
from django.http import JsonResponse, HttpResponse

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from django.template.defaultfilters import default


# Create your models here.
# --------------------------------------------------------------
class Bancos(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    ban_id = models.AutoField("Key", primary_key=True)
    ban_nombre = models.CharField("Nombre del banco", max_length=150)
    ban_codigo = models.CharField("Código", max_length=10)
    ban_activo = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.ban_id

    def __str__(self):
        return "{n}-{cc}".format(n=self.ban_nombre, cc=self.ban_codigo)

    def save(self, *args, **kwargs):
        super(Bancos, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_bancos"
        ordering = ['ban_id']


class BancosAdmin(admin.ModelAdmin):
    list_display = ('ban_id', 'ban_nombre', 'ban_codigo', 'ban_activo')


# --------------------------------------------------------------
class CajasCompensacion(models.Model):
    cc_id = models.AutoField("Key", primary_key=True)
    cc_nombre = models.CharField("Nombre", max_length=100)
    cc_codigo = models.CharField("Código", max_length=100)

    def __int__(self):
        return self.cc_id

    def __str__(self):
        return "{n}".format(n=self.cc_nombre)

    def save(self, *args, **kwargs):
        super(CajasCompensacion, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_cajas_compensacion"
        ordering = ['cc_id']


class CajasCompensacionAdmin(admin.ModelAdmin):
    list_display = ('cc_id', 'cc_nombre', 'cc_codigo')


# --------------------------------------------------------------
class Salud(models.Model):
    TIPO = (
        ('F', 'FONASA'),
        ('I', 'ISAPRE'),
    )

    sa_id = models.AutoField("Key", primary_key=True)
    sa_nombre = models.CharField("Nombre", max_length=100)
    sa_codigo = models.CharField("Código", max_length=100)
    sa_tipo = models.CharField("Tipo", max_length=1, choices=TIPO, default='I')

    def __int__(self):
        return self.sa_id

    def __str__(self):
        return "{n}".format(n=self.sa_nombre)

    def __porcentaje_fonasa(self):
        if self.sa_tipo == 'F':
            return 7
        else:
            return 0

    porcentajeFonasa = property(__porcentaje_fonasa)

    def save(self, *args, **kwargs):
        super(Salud, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_salud"
        ordering = ['sa_id']


class SaludAdmin(admin.ModelAdmin):
    list_display = ('sa_id', 'sa_nombre', 'sa_codigo', 'sa_tipo')


# --------------------------------------------------------------afp.afp_nombre
class Afp(models.Model):
    afp_id = models.AutoField("Key", primary_key=True)
    afp_codigoprevired = models.CharField("Código previred", max_length=100)
    afp_nombre = models.CharField("Nombre", max_length=100)
    afp_tasatrabajadordependiente = models.FloatField("Tasa traba. dependiente", default=0)
    afp_sis = models.FloatField("Seguro de Invalidez y Sobrevivencia (SIS)", default=0)
    afp_tasatrabajadorindependiente = models.FloatField("Tasa traba. independiente", default=0)

    def __int__(self):
        return self.afp_id

    def __str__(self):
        return "{n}".format(n=self.afp_nombre)

    def save(self, *args, **kwargs):
        super(Afp, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_afp"
        ordering = ['afp_id']


class AfpAdmin(admin.ModelAdmin):
    list_display = ('afp_id', 'afp_codigoprevired', 'afp_nombre', 'afp_tasatrabajadordependiente', 'afp_sis',
                    'afp_tasatrabajadorindependiente')


# --------------------------------------------------------------
class Pais(models.Model):
    pa_id = models.AutoField("Key", primary_key=True)
    pa_nombre = models.CharField("Nombre país", max_length=255)
    pa_codigo = models.IntegerField("Código area país", unique=True)

    def __int__(self):
        return self.pa_id

    def __str__(self):
        return "{n}".format(n=self.pa_nombre.title())

    def save(self, *args, **kwargs):
        # print "save cto"
        super(Pais, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_pais'
        ordering = ['pa_id']


class PaisAdmin(admin.ModelAdmin):
    list_display = ('pa_id', 'pa_nombre', 'pa_codigo')


# ------------
class Region(models.Model):
    re_id = models.AutoField("Key", primary_key=True)
    re_nombre = models.CharField("Nombre región", max_length=255)
    pais = models.ForeignKey(Pais, verbose_name="País", blank=True, null=True, on_delete=models.PROTECT,
                             db_column="re_pais")
    re_numeroregion = models.CharField("Sigla de región", blank=True, null=True, max_length=5)
    re_numero = models.IntegerField("Número de región", db_index=True)

    def __int__(self):
        return self.re_id

    def __str__(self):
        return "{n}".format(n=self.re_nombre.title())

    def save(self, *args, **kwargs):
        # print "save cto"
        super(Region, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_region'
        ordering = ['re_id']


class RegionAdmin(admin.ModelAdmin):
    list_display = ('re_id', 're_nombre', 're_numeroregion', 'pais')


# ------------
class Comuna(models.Model):
    com_id = models.AutoField("Key", primary_key=True)
    com_nombre = models.CharField("Nombre comuna", max_length=255)
    com_numero = models.IntegerField("Numero comuna", default=0)
    region = models.ForeignKey(Region, verbose_name="Región", blank=True, null=True, on_delete=models.PROTECT,
                               db_column="com_region")

    def __int__(self):
        return self.com_id

    def __str__(self):
        return "{n}".format(n=self.com_nombre.title())

    def save(self, *args, **kwargs):
        # print "save cto"
        super(Comuna, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_comuna'
        ordering = ['com_id']


class ComunaAdmin(admin.ModelAdmin):
    list_display = ('com_id', 'com_nombre', 'region', 'region')


# ------------
class Empresa(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    emp_id = models.AutoField("Key", primary_key=True)
    emp_codigo = models.CharField("Código de la empresa", max_length=150)
    emp_rut = models.CharField("Rut", max_length=25)
    emp_nombrerepresentante = models.CharField("Nombre representante", max_length=255, null=True, blank=True)
    emp_rutrepresentante = models.CharField("Rut representante", max_length=25)
    emp_isestatal = models.CharField("Es estatal", max_length=1, choices=OPCIONES, default="N")
    emp_razonsocial = models.CharField("Razón social", max_length=150)
    emp_giro = models.CharField("Giro", max_length=150)
    emp_direccion = models.TextField("Calle")
    emp_numero = models.IntegerField("N°")
    emp_piso = models.CharField("Piso", max_length=25, null=True, blank=True)
    emp_dptooficina = models.CharField("Departamento/oficina", max_length=25, null=True, blank=True)
    pais = models.ForeignKey(Pais, verbose_name="País", db_column="emp_pais")
    region = models.ForeignKey(Region, verbose_name="Región", db_column="emp_region")
    comuna = models.ForeignKey(Comuna, verbose_name="Comuna", db_column="emp_comuna")
    emp_cospostal = models.CharField("Código postal", max_length=25, null=True, blank=True)
    emp_fonouno = models.CharField("Télefono 1", max_length=25)
    emp_mailuno = models.CharField("Email 1", max_length=150)
    emp_fonodos = models.CharField("Télefono 2", max_length=25, null=True, blank=True)
    emp_maildos = models.CharField("Email 2", max_length=150, null=True, blank=True)
    emp_fechaingreso = models.DateField(verbose_name='Fecha inicio de actividades', null=True, blank=True)
    emp_isholding = models.CharField("Es sub-empresa", max_length=1, choices=OPCIONES, default="S")
    emp_idempresamadre = models.ForeignKey('self', db_column="emp_idempresamadre", null=True, blank=True, default=None,
                                           on_delete=models.PROTECT)
    emp_activa = models.CharField("Empresa activa", max_length=1, choices=OPCIONES, default="S")
    emp_rutcontador = models.CharField("Rut contador", max_length=12, null=True, blank=True)
    emp_nombrecontador = models.CharField("Razón social", max_length=150, null=True, blank=True)
    emp_rutalogo = models.CharField("Ruta logo", max_length=250, null=True, blank=True, default='')
    emp_nombreimagen = models.CharField("Nombre imagen", max_length=250, null=True, blank=True, default='')

    def __int__(self):
        return self.emp_id

    def __str__(self):
        return self.emp_razonsocial


    def __generador_ruta_logo(self):
        rutaLogo = "{a}/{b}".format(a=self.emp_rutalogo, b=self.emp_nombreimagen)
        return rutaLogo

    emp_generadorrutalogo = property(__generador_ruta_logo)

    def save(self, *args, **kwargs):
        self.emp_razonsocial = self.emp_razonsocial.title()
        super(Empresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_empresa'
        ordering = ['emp_id']


class EmpresaAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    search_fields = ['emp_rut', 'emp_mailuno']
    list_display = (
        'emp_id', 'emp_codigo', 'emp_rut', 'emp_isestatal', 'emp_razonsocial', 'pais', 'region', 'comuna',
        'emp_mailuno',
        'emp_fechaingreso', 'emp_isholding', 'emp_activa')
    raw_id_fields = ('pais', 'region', 'comuna')
    list_filter = ('emp_activa', 'pais', 'region', 'comuna', 'emp_fechaingreso')


# ------------
class Sucursal(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    suc_id = models.AutoField("Key", primary_key=True)
    suc_codigo = models.CharField("Código de la unidad", max_length=50, null=True, blank=True)
    suc_descripcion = models.CharField("Descripción de la unidad", max_length=255, null=True, blank=True)
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', db_column='suc_empresa', default=0,
                                on_delete=models.PROTECT)
    suc_direccion = models.CharField("Direccion de la unidad", max_length=255, default='')
    pais = models.ForeignKey(Pais, verbose_name="País", db_column="suc_pais", null=True, blank=True)
    region = models.ForeignKey(Region, verbose_name="Región", db_column="suc_region", null=True, blank=True)
    comuna = models.ForeignKey(Comuna, verbose_name="Comuna", db_column="suc_comuna", null=True, blank=True)
    # unineg_usercre = models.IntegerField(verbose_name='Usuario Creador', default=0)
    # unineg_fechacre = models.DateTimeField(verbose_name='Fecha Creacion', default=timezone.now)
    # unineg_usermod = models.IntegerField(verbose_name='Usuario Modificador', default=0)
    # unineg_fechamod = models.DateTimeField(verbose_name='Fecha Modificacion', default=timezone.now)
    suc_estado = models.CharField("Sucursal activa", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.suc_id

    def __str__(self):
        return self.suc_codigo

    def save(self, *args, **kwargs):
        # print "save cto"
        super(Sucursal, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_sucursal"


class SucursalAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    search_fields = ['pais', 'region', 'comuna']
    list_display = ('suc_id', 'suc_codigo', 'empresa', 'region', 'comuna', 'suc_estado')
    raw_id_fields = ('pais', 'region', 'comuna')
    list_filter = ('suc_estado', 'pais', 'region', 'comuna')


# ------------
class Cargo(models.Model):
    car_id = models.AutoField("Key", primary_key=True)
    car_nombre = models.CharField("Nombre cargo", max_length=255)

    def __int__(self):
        return self.car_id

    def __str__(self):
        return "{n}".format(n=self.car_nombre.title())

    def save(self, *args, **kwargs):
        # print "save cto"
        super(Cargo, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_cargo'
        ordering = ['car_id']


class CargoAdmin(admin.ModelAdmin):
    list_display = ('car_id', 'car_nombre')


# ------------
class CargoEmpresa(models.Model):
    care_id = models.AutoField("Key", primary_key=True)
    cargo = models.ForeignKey(Cargo, verbose_name="Cargo", db_column="care_cargo", on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="care_empresa", on_delete=models.PROTECT)
    care_fechacreacion = models.DateTimeField("Fecha-Hora creación", default=timezone.now)

    def __int__(self):
        return self.care_id

    def __str__(self):
        return "{c}-{e}".format(c=str(self.cargo).title(), e=str(self.empresa).title())

    def save(self, *args, **kwargs):
        # print "save cto"
        super(CargoEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_cargo_empresa'
        ordering = ['care_id']


class CargoEmpresaAdmin(admin.ModelAdmin):
    list_display = ('care_id', 'cargo', 'empresa', 'care_fechacreacion')


# ------------
class Usuario(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    ESTADO_USUARIO = (
        ('A', 'Activo'),
        ('E', 'Eliminado'),
        ('C', 'Candidato'),
        ('P', 'Pendiente'),
        ('X', 'Externo'),
    )

    TIPO_RUT = (
        (1, 'Rut'),
        (2, 'Extranjero(a)')
    )

    SEXO = (
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('PD', 'Por definir'),
    )

    ESTADO_CIVIL = (
        ('S', 'Soltero(a)'),
        ('C', 'Casado(a)'),
        ('D', 'Divorsiado(a)'),
        ('V', 'Viudo(a)'),
    )

    TIPO_USUARIO = (
        (1, 'Super-Admin'),
        (2, 'Administrador'),
        (3, 'Usuario-Sistema'),
    )

    TIPO_CREACION_USUARIO = (
        (1, 'Nuevo empleado'),
        (2, 'Crear empleado a través de otro'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    usu_tiporut = models.IntegerField("Tipo de rut", default=1, choices=TIPO_RUT, null=True, blank=True)  #
    usu_rut = models.CharField("Rut", max_length=12, db_index=True, null=True, blank=True)  #
    usu_sexo = models.CharField("Sexo", max_length=2, choices=SEXO, default="PD", null=True, blank=True)  #
    usu_fono = models.CharField("Fono", max_length=20, null=True, blank=True)  #
    usu_fechanacimiento = models.DateField(verbose_name='Fecha de nacimiento', null=True, blank=True)  ##
    pais = models.ForeignKey(Pais, verbose_name="País", db_column="usu_pais", null=True, blank=True, default=None)  #
    region = models.ForeignKey(Region, verbose_name="Región", db_column="usu_region", null=True, blank=True)  #
    comuna = models.ForeignKey(Comuna, verbose_name="Comuna", db_column="usu_comuna", null=True, blank=True)  #
    usu_direccion = models.TextField("Dirección", null=True, blank=True)  ##
    usu_estadocivil = models.CharField("Estado civil", max_length=1, choices=ESTADO_CIVIL, null=True, blank=True,
                                       default='C')  #
    usu_tipousuario = models.IntegerField("Tipo usuario", choices=TIPO_USUARIO, null=True, blank=True, default="")  #
    usu_profesion = models.CharField("Profesión", max_length=255, null=True, blank=True)  ##
    usu_extranjero = models.CharField("Es extranjero?", max_length=1, choices=OPCIONES, null=True, blank=True,
                                      default="N")  #
    usu_usuarioactivo = models.CharField("Estado del usuario", max_length=1, choices=ESTADO_USUARIO, null=True,
                                         blank=True, default="P")  #
    usu_licenciaconducir = models.CharField("Licencia de conducir", max_length=1, choices=OPCIONES, null=True,
                                            blank=True, default="N")  #
    usu_nombreusuario = models.CharField("Nombre usuario", max_length=20, null=True, blank=True)
    usu_passwordusuario = models.CharField("Clave usuario", max_length=20, null=True, blank=True)
    usu_fechacreacion = models.DateField("Fecha creación usuario", default=timezone.now)  #
    usu_tipocreacionusuario = models.IntegerField("Tipo creación de usuario", choices=TIPO_CREACION_USUARIO, null=True,
                                                  blank=True, default=1)  #

    usu_rutafoto = models.CharField("Ruta de la foto", max_length=220, null=True, blank=True, default='')
    usu_nombrefoto = models.CharField("Nombre de la foto", max_length=220, null=True, blank=True, default='')
    usu_paisextranjeros = models.CharField("País extranjero", max_length=220, null=True, blank=True, default='')

    def __int__(self):
        return int(self.usu_rut)

    def __str__(self):
        return self.usu_rut

    def save(self, *args, **kwargs):
        super(Usuario, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_usuario'
        ordering = ['usu_rut']


class UsuarioAdmin(admin.ModelAdmin):
    search_fields = ['usu_sexo', 'usu_mail', 'usu_generadorrut']
    list_display = ('usu_rut', 'pais', 'region', 'comuna', 'usu_tipousuario', 'usu_extranjero', 'usu_usuarioactivo')
    raw_id_fields = ('pais', 'region', 'comuna')
    list_filter = ('usu_fechanacimiento', 'usu_fechacreacion', 'usu_extranjero', 'usu_usuarioactivo', 'usu_tipousuario')


# --------------------------------------------------------------
class GrupoCentroCosto(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    gcencost_id = models.AutoField("Key", primary_key=True)
    gcencost_nombre = models.CharField("Nombre", max_length=100)
    gcencost_codigo = models.CharField("Código", max_length=100)
    gcencost_activo = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")
    empresa = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="gcencost_empresa")

    def __int__(self):
        return self.gcencost_id

    def __str__(self):
        return "{n}".format(n=self.gcencost_nombre)

    def save(self, *args, **kwargs):
        super(GrupoCentroCosto, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_grupo_centro_costo"
        ordering = ['gcencost_id']


class GrupoCentroCostoAdmin(admin.ModelAdmin):
    list_display = ('gcencost_id', 'gcencost_nombre', 'gcencost_codigo', 'gcencost_activo')


# --------------------------------------------------------------
class CentroCosto(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    cencost_id = models.AutoField("Key", primary_key=True)
    grupocentrocosto = models.ForeignKey(GrupoCentroCosto, verbose_name="Grupo Centro costo",
                                         db_column="ec_grupocentrocosto")
    cencost_nombre = models.CharField("Nombre", max_length=100)
    cencost_codigo = models.CharField("Código", max_length=100)
    cencost_activo = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.cencost_id

    def __str__(self):
        return "{n}".format(n=self.cencost_nombre)

    def save(self, *args, **kwargs):
        super(CentroCosto, self).save(*args, **kwargs)

    class Meta:
        db_table = "usu_centro_costo"
        ordering = ['cencost_id']


class CentroCostoAdmin(admin.ModelAdmin):
    list_display = ('cencost_id', 'cencost_nombre', 'cencost_codigo', 'cencost_activo')


# ------------
class UsuarioEmpresa(models.Model):
    TIPO_CONTRATO = (
        ('', '-- OPCIONES --'),
        ('CI', 'Contrato duración indefinida'),
        ('CPF', 'Contrato plazo fijo'),
        ('CIT', 'Contrato individual de trabajo'),
        ('CPO', 'Contrato por obra'),
        ('CJP', 'Contrato jornada parcial'),
        ('CPT', 'Contrato part-time'),
        ('CE', 'Contrato especial'),
        ('INA', 'Inactivo'),
    )

    TIPO_TRABAJADOR = (
        ('', '-- OPCIONES --'),
        ('D', 'Dependiente'),
        ('I', 'Independiente'),
    )

    FORMA_PAGO = (
        (1, 'Efectivo'),
        (2, 'Cheque'),
        (3, 'Depósito directo'),
    )

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    NOTIFICACION = (
        ('', '-- OPCIONES --'),
        ('E', 'Email'),
        ('C', 'Carta'),
    )

    TIPO_MONTO = (
        ('', '-- OPCIONES --'),
        ('P', 'Porcentaje'),
        ('M', 'Monto'),
    )

    SEGURO_DESEMPLEO = (
        ('', '-- OPCIONES --'),
        ('S', 'SI'),
        ('N', 'NO'),
    )

    TIPO_GRATIFICACION = (
        ('', '-- OPCIONES --'),
        ('A', 'Anual'),
        ('M', 'Mensual'),
    )

    ue_id = models.AutoField("Key", primary_key=True)
    user = models.ForeignKey(User, verbose_name="Usuario", db_column="ue_usuario")
    ue_fechacreacion = models.DateTimeField("Fecha-Hora creación", null=True, blank=True)

    # ---------------------------
    # FORM DATOS LABORALES
    # ---------------------------
    # empresa          = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="ue_empresa")
    # sucursal         = models.ForeignKey(Sucursal, verbose_name="Sucursal", db_column="ue_sucursal", null=True, blank=True)
    cargo = models.ForeignKey(Cargo, verbose_name="Cargo", db_column="ue_cargo", null=True, blank=True)
    ue_tipocontrato = models.CharField("Tipo de contrato", max_length=4, choices=TIPO_CONTRATO, default="CPF")  #
    ue_tipotrabajdor = models.CharField("Tipo de trabajador", max_length=1, choices=TIPO_TRABAJADOR, default="D")  #
    ue_fechacontratacion = models.DateField("Fecha de contratacion del usuario", null=True, blank=True)  #
    ue_fecharenovacioncontrato = models.DateField("Fecha termino de contrato", null=True, blank=True)  #
    ue_fecharetiro = models.DateField("Fecha de finiquito", null=True, blank=True)  #
    ue_formapago = models.IntegerField("Forma de pago", choices=FORMA_PAGO, null=True, blank=True, default=1)  #
    centrocosto = models.ForeignKey(CentroCosto, verbose_name="Centro de costo ", db_column="ue_contro_costo",
                                    null=True, blank=True)

    ue_horassemanales = models.IntegerField("Horas trabajadas", null=True, blank=True, default=45)  #
    ue_movilizacion = models.DecimalField("Movilización", max_digits=15, decimal_places=6, null=True, blank=True,
                                          default=0)
    ue_colacion = models.DecimalField("Colación", max_digits=15, decimal_places=6, null=True, blank=True, default=0)
    ue_anticipo = models.CharField("Anticipo?", choices=OPCIONES, max_length=1, null=True, blank=True, default="N")
    ue_montonticipo = models.DecimalField("Monto anticipo", max_digits=15, decimal_places=2, null=True, blank=True,
                                          default=0)

    ue_asignacionfamiliar = models.CharField("Asignación familiar", choices=OPCIONES, max_length=1, null=True,
                                             blank=True, default="N")  #
    ue_cargasfamiliares = models.IntegerField("Cargas familiares", null=True, blank=True, default=0)  #
    ue_montoasignacionfamiliar = models.DecimalField("Monto asignación familiar", max_digits=15, decimal_places=2,
                                                     null=True, blank=True, default=0)

    ue_sueldobase = models.DecimalField("Sueldo base", max_digits=15, decimal_places=6, null=True, blank=True,
                                        default=0)
    ue_gratificacion = models.CharField("Tiene gratificación", choices=OPCIONES, max_length=1, null=True, blank=True,
                                        default="")
    ue_tipogratificacion = models.CharField("Tipo de gratificación", choices=TIPO_GRATIFICACION, max_length=1,
                                            null=True, blank=True, default="")

    ue_comiciones = models.CharField("Tiene comociones", choices=OPCIONES, max_length=1, null=True, blank=True,
                                     default="")
    ue_porcentajecomicion = models.DecimalField("Porcentaje comociones", max_digits=15, decimal_places=2, null=True,
                                                blank=True, default=0)
    # -----------------------------
    # AFP
    # -----------------------------
    afp = models.ForeignKey(Afp, verbose_name="AFP", db_column="ue_afp", null=True, blank=True)
    ue_tieneapv = models.CharField("Tiene APV", choices=OPCIONES, max_length=1, default="N")
    ue_tipomontoapv = models.CharField("Tipo de monto", choices=TIPO_MONTO, null=True, blank=True, max_length=1,
                                       default="M")
    afp_apv = models.ForeignKey(Afp, verbose_name='AFP APV', db_column='ue_afp_apv', related_name="afp_apv", null=True,
                                blank=True, on_delete=models.PROTECT)
    ue_cotizacionvoluntaria = models.DecimalField("Cotización voluntaria", max_digits=15, decimal_places=2, null=True,
                                                  blank=True, default=0)
    ue_tieneahorrovoluntario = models.CharField("Tiene ahorro voluntario", choices=OPCIONES, max_length=1, default="N")
    ue_ahorrovoluntario = models.DecimalField("Ahorro Voluntario", max_digits=15, decimal_places=2, null=True,
                                              blank=True, default=0)
    # -----------------------------
    # -----------------------------
    # SALUD
    # -----------------------------
    salud = models.ForeignKey(Salud, verbose_name="Salud", db_column="ue_salud", null=True, blank=True)
    ue_ufisapre = models.FloatField("Valor en UF isapre", null=True, blank=True, default=0)
    ue_funisapre = models.IntegerField("Fun isapre", null=True, blank=True, default=0)
    ue_cotizacion = models.FloatField("Cotizacion fonasa/isapre", null=True, blank=True, default=0)
    # -----------------------------
    # -----------------------------
    # SEGURO DE DESEMPLEO
    # -----------------------------
    ue_segurodesempleo = models.CharField("Seguro de desmpleo", max_length=1, choices=SEGURO_DESEMPLEO, null=True,
                                          blank=True, default="")  #
    ue_porempleado = models.FloatField("porcentaje por empleado", null=True, blank=True, default=0)
    ue_porempleador = models.FloatField("porcentaje por empleador", null=True, blank=True, default=0)
    ue_trabajopesado = models.CharField("Trabajo pesado", choices=OPCIONES, max_length=1, default="N")
    # -----------------------------
    # CICLO DE VIDA
    ue_prestamo = models.DecimalField("Prestamo", max_digits=15, decimal_places=2, null=True, blank=True, default=0)
    ue_cuotas = models.IntegerField("Cuotas prestamo", null=True, blank=True, default=0)

    # CERTIFICADO
    ue_certificado = models.TextField("Descripción de certificado", null=True, blank=True, default="")

    # AMONESTACION
    ue_amonestacion = models.TextField("Descripción de amonestacion", null=True, blank=True, default="")

    # ANEXO CONTRATO
    ue_anexocontrato = models.TextField("Anexo contrato", null=True, blank=True, default="")

    # ENTREGA DE EQUIPOS SEGURIDAD Y OTROS
    ue_entregaequiposeguridad = models.TextField("Entrega equipos de seguridad y otros", null=True, blank=True,
                                                 default="")

    # -----------------------------
    # TERMINO RELACION LABORAL
    ue_fechanotificacioncartaaviso = models.DateField("Fecha de notificacion carta aviso", null=True, blank=True,
                                                      default=None)  #
    ue_fechatermino = models.DateField("Fecha de termino relacion laboral", null=True, blank=True, default=None)  #
    ue_cuasal = models.TextField("Causal", null=True, blank=True, default="")
    ue_fundamento = models.TextField("Fundamento", null=True, blank=True, default="")
    ue_tiponoticacion = models.CharField("Tipo de notificacion", choices=NOTIFICACION, max_length=1, null=True,
                                         blank=True, default="")
    # -----------------------------
    # OTROS
    ue_otros = models.TextField("Otro", null=True, blank=True, default="")
    # -----------------------------

    ue_totalhaberes = models.DecimalField("Total haberes", max_digits=15, decimal_places=2, null=True, blank=True,
                                          default=0)
    ue_totaldescuentos = models.DecimalField("Total descuentos", max_digits=15, decimal_places=2, null=True, blank=True,
                                             default=0)
    ue_totalfinalhaberesdescuentos = models.DecimalField("Total final haberes y descuentos", max_digits=15,
                                                         decimal_places=2, null=True, blank=True, default=0)

    banco = models.ForeignKey(Bancos, verbose_name="Banco", db_column="ue_banco", null=True, blank=True)
    ue_cuentabancaria = models.CharField("Cuenta bancaria", max_length=50, null=True, blank=True, default="")  #

    ue_jornadalaboral = models.CharField("Jornada de trabajo", max_length=70, null=True, blank=True, default="")

    def __int__(self):
        return self.ue_id

    def __str__(self):
        return "{n}".format(n=self.ue_id)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(UsuarioEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_usuario_empresa'
        ordering = ['ue_id']


class UsuarioEmpresaAdmin(admin.ModelAdmin):
    list_display = ('ue_id', 'user', 'ue_fechacontratacion', 'cargo', 'ue_tipocontrato', 'centrocosto')


# ------------
class Haberes(models.Model):
    TIPO = (
        ('', '--- Seleccione ---'),
        ('HI', 'Haberes imponible'),
        ('HNI', 'Haberes no imponibles'),
        ('F', 'Finiquito'),
    )

    FINIQUITO = (
        ('', '--- Seleccione ---'),
        ('H', 'Haberes'),
        ('D', 'Descuento'),
    )

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    hab_id = models.AutoField("Key", primary_key=True)
    hab_nombre = models.CharField("Nombre", max_length=70)
    hab_monto = models.DecimalField("Monto", max_digits=15, decimal_places=6)
    hab_tipo = models.CharField("Tipo haber", choices=TIPO, max_length=3, null=True, blank=True, default=None)
    hab_tipohaberdescuento = models.CharField("Tipo haberes y descuento", choices=FINIQUITO, max_length=1, null=True,
                                              blank=True, default=None)
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', db_column='suc_empresa', default=0,
                                on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Usuario", db_column="ue_usuario")
    hab_activo = models.CharField("Haber activo", choices=OPCIONES, max_length=1, default="S")


class HaberesAdmin(admin.ModelAdmin):
    list_display = ('hab_id', 'hab_nombre', 'hab_monto', 'empresa', 'user')


# ------------
class RelacionDeAfiliacion(models.Model):
    TIPO_AFILIACION = (
        ('', '--- Seleccione ---'),
        ('IPS', 'Solo IPS'),
        ('MUT', 'Solo mutual'),
        ('CCAF', 'Solo CCAF'),
    )

    MUTUALES = (
        ('IST', 'Instituto de Seguridad del Trabajo'),
        ('ACHS', 'Asociación Chilena de Seguridad '),
        ('CCHC', 'Mutual de Seguridad C.Ch.C'),
    )

    rda_id = models.AutoField("Key", primary_key=True)
    empresa = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="rda_empresa")
    cajascompensacion = models.ForeignKey(CajasCompensacion, verbose_name="Cajas Compensacion",
                                          db_column="rda_cajacompemsacion", null=True, blank=True)
    rda_inp = models.CharField("Nombre INP", max_length=150, null=True, blank=True)
    rda_tipoatipomutual = models.CharField("Tipo mutual", max_length=4, null=True, blank=True, choices=MUTUALES,
                                           default='')
    rda_porcentajemutual = models.DecimalField("Porcentaje mutual", max_digits=15, decimal_places=2, null=True,
                                               blank=True, default=0)
    rda_fechacreacion = models.DateTimeField("Fecha-Hora creación", null=True, blank=True, default=timezone.now)
    rda_tipoafiliacion = models.CharField("Tipo afiliacion", max_length=4, null=True, blank=True,
                                          choices=TIPO_AFILIACION, default='')

    def __int__(self):
        return self.rda_id

    def __str__(self):
        return "%s" % self.rda_id

    def save(self, *args, **kwargs):
        # print "save cto"
        super(RelacionDeAfiliacion, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_relacion_afiliacion'
        ordering = ['rda_id']


class RelacionDeAfiliacionAdmin(admin.ModelAdmin):
    list_display = ('rda_id', 'empresa', 'rda_tipoafiliacion', 'rda_tipoatipomutual', 'rda_inp', 'rda_fechacreacion')


# ------------
class MarcadorEntradaSalida(models.Model):
    TIPO_MARCADO = (
        ('E', 'Entrada'),
        ('SC', 'Salida a colación'),
        ('EC', 'Entrada de colación'),
        ('S', 'Salida'),
    )

    mes_id = models.AutoField("Key", primary_key=True)
    mes_hora = models.DateTimeField("Hora Entrada")
    mes_tipomarcado = models.CharField("Tipo afiliacion", max_length=2, choices=TIPO_MARCADO)
    user = models.ForeignKey(User, verbose_name="Colaborador", db_column="mes_user", on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="mes_empresa", on_delete=models.PROTECT)

    def __int__(self):
        return self.mes_id

    def __str__(self):
        return "{c}".format(c=self.user)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(CargoEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_marcador_entrada_salida'
        ordering = ['mes_id']


class MarcadorEntradaSalidaAdmin(admin.ModelAdmin):
    list_display = ('mes_id', 'mes_hora', 'mes_tipomarcado', 'user', 'empresa')


# ------------------------------------------------
class AsociacionUsuarioEmpresa(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    aue_id = models.AutoField("Key", primary_key=True)
    user = models.ForeignKey(User, verbose_name="Usuario", db_column="aue_usuario")
    empresa = models.ForeignKey(Empresa, verbose_name="Empresa", db_column="aue_empresa")
    sucursal = models.ForeignKey(Sucursal, verbose_name="Sucursal", db_column="aue_sucursal", null=True, blank=True)
    aue_activo = models.CharField("Personal activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.aue_id

    def __str__(self):
        return "{}".format(self.aue_id)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(AsociacionUsuarioEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'usu_asociacion_usuario_empresa'
        ordering = ['aue_id']


class AsociacionUsuarioEmpresaAdmin(admin.ModelAdmin):
    list_display = ('aue_id', 'user', 'empresa', 'sucursal')
