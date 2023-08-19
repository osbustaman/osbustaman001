# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import datetime

from usuario.models import Empresa, Usuario, Pais, Region, Comuna, Bancos


# Create your models here.
class ClienteProveedor(models.Model):

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    TIPO_ENTIDAD = (
        ('C', 'Cliente'),
        ('P', 'Proveedor'),
        ('A', 'Cliente y proveedor'),
    )

    cp_id = models.AutoField("Key", primary_key=True)
    cp_rut = models.CharField("Rut", max_length=25)
    cp_razonsocial = models.CharField("Razón social", max_length=200)
    cp_nombrefantasia = models.CharField("Nombre de fantasía", max_length=150)
    cp_giro = models.CharField("Giro", max_length=150)
    cp_direccion = models.TextField("Calle")
    cp_numero = models.IntegerField("N°")
    cp_piso = models.CharField("Piso", max_length=25, null=True, blank=True)
    cp_dptooficina = models.CharField("Departamento/oficina", max_length=25, null=True, blank=True)
    pais = models.ForeignKey(Pais, verbose_name="País", db_column="cp_pais")
    region = models.ForeignKey(Region, verbose_name="Región", db_column="cp_region")
    comuna = models.ForeignKey(Comuna, verbose_name="Comuna", db_column="cp_comuna")
    cp_email = models.CharField("Email", max_length=50, default='', null=True, blank=True)
    cp_fono = models.CharField("Télefono", max_length=25, default='', null=True, blank=True)
    cp_comentario = models.CharField("Comentario", max_length=200, default='', null=True, blank=True)
    cp_estado = models.CharField("Activo", max_length=1, choices=OPCIONES, null=True, blank=True, default="S")  #
    cp_tipoentidad = models.CharField("Tipo entidad", choices=TIPO_ENTIDAD, max_length=1)
    # cp_emailsii = models.CharField("Mail SII", max_length=50, blank=True, null=True, default='')

    # id_ext = models.CharField(db_column='id_ext', max_length=15, verbose_name='ID Extranjero', default='')
    # num_dir = models.IntegerField(db_column='num_dir', verbose_name='Direccion', blank=True, default=0)
    # num_dir = models.ForeignKey("clientes_proveedores.direcciones", db_column='num_dir', verbose_name='Direccion', blank=True, null=True, on_delete=models.PROTECT)
    # holding = models.IntegerField(db_column='holding', verbose_name='Holding', default=0)
    # area_prod = models.IntegerField(db_column='area_prod', verbose_name='Codigo de Area de Produccion', blank=True, default=0)
    # clasif = models.IntegerField(db_column='clasif', verbose_name='Codigo de Clasificacion', blank=True, default=0)

    # cp_user_cre = models.IntegerField(verbose_name='Usuario Creador', default=0)
    # cp_fecha_cre = models.DateTimeField(verbose_name='Fecha Creacion', default=timezone.now)
    # cp_user_mod = models.IntegerField(verbose_name='Usuario Modificador', default=0)
    # cp_fecha_mod = models.DateTimeField(verbose_name='Fecha Modificacion', default=timezone.now)

    def __int__(self):
        return self.cp_id

    def __str__(self):
        return self.cp_razonsocial

    def save(self, *args, **kwargs):
        super(ClienteProveedor, self).save(*args, **kwargs)

    class Meta:
        db_table = 'cliprov_cliente_proveedor'
        ordering = ['cp_id']

class ClienteProveedorAdmin(admin.ModelAdmin):
    list_display = ('cp_id', 'cp_rut', 'cp_razonsocial', 'cp_tipoentidad', 'cp_estado')



class ClienteProveedorEmpresa(models.Model):
    TIPO_CLI_CHOICES = (
        ('N', 'No'),
        ('C', 'Nacional'),
        ('P', 'Prospecto'),
        ('E', 'Extranjero'),
    )
    TIPO_PROV_CHOICES = (
        ('N', 'No'),
        ('P', 'Nacional'),
        ('H', 'Honorario'),
        ('E', 'Extranjero'),
        ('A', 'Agente de Aduana'),
    )
    TIPO_CTA_CHOICES = (
        ('1', 'Cuenta vista'),
        ('2', 'Cuenta de ahorro'),
        ('3', 'Cuenta corriente'),
        ('4', 'Vale vista'),
    )

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    cpe_id = models.AutoField("Key", primary_key=True)
    clienteProveedor = models.ForeignKey(ClienteProveedor, db_column='cpe_clienteproveedor', verbose_name='Cliente/Proveedor', on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, db_column='cpe_empresa', verbose_name='Empresa', on_delete=models.PROTECT)
    cpe_tipocliente = models.CharField("Tipo cliente", max_length=1, choices=TIPO_CLI_CHOICES, null=True, blank=True, default="N")
    cpe_tipoproveedor = models.CharField("Tipo proveedor", max_length=1, choices=TIPO_PROV_CHOICES, null=True, blank=True, default="N")
    cpe_plazopago = models.IntegerField("Plazo pago", default=0)
    cpe_vencimiento = models.IntegerField("Vencimiento", default=0)
    banco = models.ForeignKey(Bancos, verbose_name="Bancos", db_column="cpe_banco")
    cpe_tipocuenta = models.CharField("Tipo cuenta", max_length=1, choices=TIPO_CTA_CHOICES, null=True, blank=True)
    cpe_ctacorriente = models.CharField("Número de cuenta", max_length=40, null=True, blank=True)
    cpe_credautorizado = models.DecimalField("Crédito Autorizado", max_digits=18, decimal_places=6, default=0)
    cpe_estado = models.CharField("Estado", max_length=1, choices=OPCIONES, default='A')

    # vendedor = models.IntegerField(db_column='vendedor', verbose_name='Codigo de vendedor', default=0)
    # cod_comis = models.IntegerField(db_column='cod_comis', verbose_name='Codigo de Comisionistas', default=0)
    # cobrador = models.IntegerField(db_column='cobrador', verbose_name='Codigo de Cobrador', default=0)
    # comen_emp = models.CharField(max_length=200, db_column='comen_emp', verbose_name='Comentario', default=' ')
    # user_cre = models.IntegerField(verbose_name='Usuario Creador', default=0)
    # fecha_cre = models.DateTimeField(verbose_name='Fecha Creacion', default=timezone.now)
    # user_mod = models.IntegerField(verbose_name='Usuario Modificador', default=0)
    # fecha_mod = models.DateTimeField(verbose_name='Fecha Modificacion', default=timezone.now)
    # forma_pago = models.ForeignKey('tesoreria.FormaPago', verbose_name='Forma de Pago', db_column='forma_pago', on_delete=models.PROTECT)
    # num_lista = models.ForeignKey("prod_serv.lista_precio_enc", db_column='num_lista', null=True, blank=True, on_delete=models.PROTECT)
    # cta_banco = models.ForeignKey(tablagral, db_column='cta_banco', related_name='cta_banco', on_delete=models.PROTECT, null=True, blank=True)

    def __int__(self):
        return self.cpe_id

    def __str__(self):
        return "{}-{}-{}".format(self.cpe_id, self.clienteProveedor, self.empresa)

    def save(self, *args, **kwargs):
        super(ClienteProveedorEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = 'cliprov_cliente_proveedor_empresa'
        ordering = ['cpe_id']


class ClienteProveedorEmpresaAdmin(admin.ModelAdmin):
    list_display = ('cpe_id', 'clienteProveedor', 'empresa', 'cpe_estado')

