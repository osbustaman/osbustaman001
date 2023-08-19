# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import datetime

from clienteproveedor.models import ClienteProveedor
from configuracion.models import Moneda
from usuario.models import Empresa, Usuario


# --------------------------------------------------------------
class TipoDocumentos(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    FILTRO_DOCS = (
        ('DOC', 'Documentos laborales'),
        ('CLI', 'Documentos clientes'),
        ('PRO', 'Documentos proveedores'),
        ('DEF', 'Documentos por defecto'),
    )

    tdl_id = models.AutoField("Key", primary_key=True)
    tdl_codigo = models.CharField("Código", max_length=20)
    tdl_descripcion = models.CharField("Valor", max_length=50, null=True, blank=True, default='')
    tdl_activo = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")
    tdl_pordefecto = models.CharField("Doc. por defecto?", max_length=1, choices=OPCIONES, default="N")
    tdl_filtrodoc = models.CharField("Filtro documentos", max_length=3, choices=FILTRO_DOCS, null=True, blank=True,
                                     default='')

    def __int__(self):
        return self.tdl_id

    def __str__(self):
        return "{cc}".format(cc=self.tdl_descripcion)

    def save(self, *args, **kwargs):
        super(TipoDocumentos, self).save(*args, **kwargs)

    class Meta:
        db_table = "doc_tipo_documentos"
        ordering = ['tdl_id']


class TipoDocumentosAdmin(admin.ModelAdmin):
    list_display = ('tdl_id', 'tdl_descripcion', 'tdl_activo', 'tdl_filtrodoc')


class Documento(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    doc_id = models.AutoField("Key", primary_key=True)
    tipoDocumentos = models.ForeignKey(TipoDocumentos, verbose_name='Tipo documentos', db_column='doc_tipo_documentos', on_delete=models.CASCADE)
    doc_activo = models.CharField("Documento activo", max_length=1, choices=OPCIONES, default="S")
    doc_defecto = models.CharField("Documento por defecto", max_length=1, choices=OPCIONES, default="N")
    doc_nombre = models.CharField("Nombre documento", max_length=150, null=True, blank=True)
    doc_texto = models.TextField("Texto del documento", null=True, blank=True, default='')
    doc_template = models.CharField("Nombre template del doc", max_length=255, null=True, blank=True, default='')
    doc_fechacreacion = models.DateField(verbose_name="Fecha creación del documento", null=True, blank=True)

    def __int__(self):
        return self.doc_id

    def __str__(self):
        return self.doc_nombre

    def save(self, *args, **kwargs):
        # print "save cto"
        super(Documento, self).save(*args, **kwargs)

    class Meta:
        db_table = "doc_documento"


class DocumentoAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    list_display = ('doc_id', 'tipoDocumentos', 'doc_nombre', 'doc_fechacreacion')


class DocumentoEmpresa(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    docempr_id = models.AutoField("Key", primary_key=True)
    documento = models.ForeignKey(Documento, verbose_name='Documento', db_column='docempr_documento',
                                  on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', db_column='docempr_empresa', on_delete=models.PROTECT,
                                null=True, blank=True)
    docempr_activo = models.CharField("Documento activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.docempr_id

    def __str__(self):
        return "{} - {}".format(self.documento, self.empresa)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(DocumentoEmpresa, self).save(*args, **kwargs)

    class Meta:
        db_table = "doc_documento_empresa"


class DocumentoEmpresaAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    list_display = ('docempr_id', 'documento', 'empresa')


class DocumentoEmpleado(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    docemp_id = models.AutoField("Key", primary_key=True)
    # documento = models.ForeignKey(Documento, verbose_name='Documento', db_column='docemp_documento',
    #                               on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Usuario", db_column="docemp_usuario")
    docemp_estado = models.CharField("Documento activo", max_length=1, choices=OPCIONES, default="S")
    docemp_rutaarchivo = models.CharField("Ruta del archivo", max_length=220, null=True, blank=True, default='')
    docemp_nombrearchivo = models.CharField("Nombre del archivo", max_length=220, null=True, blank=True, default='')
    docemp_fechacreacion = models.DateField(verbose_name="Fecha creación", null=True, blank=True)

    def __int__(self):
        return self.docemp_id

    def __str__(self):
        return str(self.docemp_id) + ' ___ ' + str(self.user)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(DocumentoEmpleado, self).save(*args, **kwargs)

    class Meta:
        db_table = "doc_documento_empleado"


class DocumentoEmpleadoAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    list_display = ('docemp_id', 'user', 'docemp_estado', 'docemp_fechacreacion')


class DocumentoEncabezado(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    TIPO_DESCUENTO = (
        ('M', 'MONTO'),
        ('P', 'PORCENTAJE'),
    )

    docenc_id = models.AutoField("Key", primary_key=True)
    docenc_numerodoc = models.IntegerField("Número de documento", default=0)
    documento = models.ForeignKey(Documento, verbose_name='Documento', db_column='docenc_documento',
                                  on_delete=models.PROTECT)
    clienteProveedor = models.ForeignKey(ClienteProveedor, verbose_name='Cliente/Proveedor',
                                         db_column='docenc_cliente_proveedor', on_delete=models.PROTECT)
    empresa = models.ForeignKey(Empresa, verbose_name='Empresa', db_column='docenc_empresa', on_delete=models.PROTECT)
    user = models.ForeignKey(User, verbose_name="Usuario", db_column="docenc_usuario", on_delete=models.PROTECT)
    docenc_fechaemision = models.DateField(verbose_name='Fecha de emisión')
    docenc_fechavencimiento = models.DateField(verbose_name='Fecha de vencimiento', null=True, blank=True)
    docenc_estado = models.CharField("Documento activo", max_length=1, choices=OPCIONES, default="S")
    docenc_tipodescuento = models.CharField("Tipo de descuento", max_length=1, choices=TIPO_DESCUENTO, null=True,
                                            blank=True, default="")
    docenc_descripcionadicional = models.TextField("Descripcion adicional", null=True, blank=True, default="")
    docenc_descuento = models.DecimalField("Descuento", max_digits=15, decimal_places=6, null=True, blank=True,
                                           default=0)
    docenc_totalprecio = models.DecimalField("Precio total", max_digits=15, decimal_places=6, null=True, blank=True,
                                             default=0)
    docenc_totaliva = models.DecimalField("Valor total IVA", max_digits=15, decimal_places=6, null=True, blank=True,
                                          default=0)

    def __int__(self):
        return self.docenc_id

    def __str__(self):
        return str(self.documento) + ' ___ ' + str(self.clienteProveedor) + ' ___ ' + str(self.empresa) + ' ___ ' + str(
            self.user)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(DocumentoEncabezado, self).save(*args, **kwargs)

    class Meta:
        db_table = "doc_documento_encabezado"


class DocumentoEncabezadoAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    list_display = (
    'docenc_id', 'documento', 'clienteProveedor', 'empresa', 'user', 'docenc_fechaemision', 'docenc_estado')


class DocumentoEncabezadoDetalle(models.Model):
    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    TIPO_DESCUENTO = (
        ('', 'SELECCIONE'),
        ('M', 'MONTO'),
        ('P', 'PORCENTAJE'),
    )

    docdet_id = models.AutoField("Key", primary_key=True)
    docdet_numdetalle = models.IntegerField("Número de detalle", default=0)
    documentoEncabezado = models.ForeignKey(DocumentoEncabezado, verbose_name='Documento encabezado',
                                            db_column='docdet_documento_encabezado')
    moneda = models.ForeignKey(Moneda, verbose_name='Moneda', db_column='docdet_moneda')
    docdet_tasadecambio = models.DecimalField("Tasa de cambio", max_digits=15, decimal_places=6, null=True, blank=True,
                                              default=0)
    docdet_isiva = models.CharField("Tiene IVA?", max_length=1, choices=OPCIONES, default="N")
    docdet_cantidad = models.DecimalField("Cantidad", max_digits=15, decimal_places=6, null=True, blank=True, default=0)
    docdet_producto = models.CharField("Nombre del producto", max_length=220, null=True, blank=True, default='')
    docdet_preciounitario = models.DecimalField("Precio unitario", max_digits=15, decimal_places=6, null=True,
                                                blank=True, default=0)
    docdet_preciototal = models.DecimalField("Precio total del producto", max_digits=15, decimal_places=6, null=True,
                                             blank=True, default=0)
    docdet_tipodescuento = models.CharField("Tipo de descuento", max_length=1, choices=TIPO_DESCUENTO, null=True,
                                            blank=True, default="")
    docdet_descuento = models.DecimalField("Descuento", max_digits=15, decimal_places=6, null=True, blank=True,
                                           default=0)
    docdet_montoiva = models.DecimalField("Monto con IVA", max_digits=15, decimal_places=6, null=True, blank=True,
                                          default=0)
    docdet_valorcotizado = models.DecimalField("Valor cotizado", max_digits=15, decimal_places=6, null=True, blank=True,
                                               default=0)

    def __int__(self):
        return self.docdet_id

    def __str__(self):
        return ' DETALLE DOC: ' + str(self.docdet_id) + ' ___ ' + str(self.documentoEncabezado)

    def save(self, *args, **kwargs):
        # print "save cto"
        self.docdet_valorcotizado = float(self.docdet_preciounitario) * float(self.docdet_tasadecambio) * float(
            self.docdet_cantidad)
        super(DocumentoEncabezadoDetalle, self).save(*args, **kwargs)

    class Meta:
        db_table = "doc_documento_encabezado_detalle"


class DocumentoEncabezadoDetalleAdmin(admin.ModelAdmin):
    # actions = ['download_excel']
    list_display = ('docdet_id', 'docdet_numdetalle', 'documentoEncabezado', 'docdet_producto', 'docdet_cantidad',
                    'docdet_preciounitario', 'docdet_preciototal')
