# -*- encoding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib import admin
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
import datetime

from django.core.cache import cache
from jab import settings
from usuario.models import Empresa, Sucursal


class Perfil(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.CharField(max_length=255, blank=True)
    web = models.URLField(blank=True)

    # Python 3
    def __str__(self):
        return self.usuario.username

# --------------------------------------------------------------

class Menu(models.Model):

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    menu_id            = models.AutoField("Key", primary_key=True)
    usuario            = models.ForeignKey(User, verbose_name="Usuario", db_column="menu_usuario")
    #empresa            = models.ForeignKey(Empresa, verbose_name="Empresa", null=True, blank=True, db_column="menu_empresa")
    menu_nombre        = models.CharField("Nombre del menu", max_length=255, null=True, blank=True)
    menu_fechacreacion = models.DateTimeField("Fecha-Hora creación",default = timezone.now)
    menu_estado        = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.menu_id

    def __str__(self):
        return "{n}".format(n=self.menu_nombre)

    def __nombre_menu(self):
        a = self.usuario
        n = "menu_{a}".format(a=a)
        return n

    menu_nombremenu = property(__nombre_menu)

    def save(self, *args, **kwargs):
        self.menu_nombre = self.menu_nombremenu.upper()
        super(Menu, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_menu'
        ordering = ['menu_id']

class MenuAdmin(admin.ModelAdmin):
    list_display  = ('menu_id', 'usuario', 'menu_nombre', 'menu_fechacreacion', 'menu_estado')

# ------------
class Item(models.Model):

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    item_id            = models.AutoField("Key", primary_key=True)
    item_nombre        = models.CharField("Nombre del item", max_length=120)
    item_sesion_menu   = models.CharField("Nombre de la sesion", max_length=120, null=True, blank=True)
    item_seguridad     = models.CharField("Seguridad (SI = True, NO = False)", max_length=1, choices=OPCIONES, default="S")
    item_css_img       = models.CharField("Icono por css", max_length=255)
    item_orden         = models.IntegerField("Lugar")
    item_fechacreacion = models.DateTimeField("Fecha-Hora creación",default = timezone.now)
    item_estado        = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.item_id

    def __str__(self):
        return "{n}".format(n=self.item_nombre)

    def __sesion_para_menu(self):
        cadena = ((self.item_nombre).replace(' ', '_')).lower()
        cadena = cadena.replace('á', 'a')
        cadena = cadena.replace('é', 'e')
        cadena = cadena.replace('í', 'i')
        cadena = cadena.replace('ó', 'o')
        cadena = cadena.replace('ú', 'u')

        cadena = cadena.replace('Á', 'A')
        cadena = cadena.replace('É', 'E')
        cadena = cadena.replace('Í', 'I')
        cadena = cadena.replace('Ó', 'O')
        cadena = cadena.replace('Ú', 'U')

        cadena = cadena.replace('ñ', 'n')
        cadena = cadena.replace('Ñ', 'N')

        return cadena
    sesion_para_menu = property(__sesion_para_menu)

    def save(self, *args, **kwargs):
        self.item_sesion_menu = self.sesion_para_menu
        super(Item, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_item'
        ordering = ['item_id']

class ItemAdmin(admin.ModelAdmin):
    list_display  = ('item_id', 'item_nombre', 'item_fechacreacion', 'item_estado', 'item_orden', 'item_sesion_menu')

# ------------
class MenuItem(models.Model):

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    men_ite_id            = models.AutoField("Key", primary_key=True)
    menu                  = models.ForeignKey(Menu, verbose_name="Menu", db_column="men_ite_menu")
    item                  = models.ForeignKey(Item, verbose_name="Item", db_column="men_ite_item")
    men_ite_fechacreacion = models.DateTimeField("Fecha-Hora creación",default = timezone.now)
    men_ite_estado        = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.men_ite_id

    def __str__(self):
        return "{n}".format(n=self.men_ite_id)

    def save(self, *args, **kwargs):
        super(MenuItem, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_menu_item'
        ordering = ['men_ite_id']

class MenuItemAdmin(admin.ModelAdmin):
    list_display  = ('men_ite_id', 'menu', 'item', 'men_ite_fechacreacion', 'men_ite_estado')
    raw_id_fields = ('menu', 'item')

# ------------
class SubItem(models.Model):

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    subitem_id             = models.AutoField("Key", primary_key=True)
    item                   = models.ForeignKey(Item, verbose_name="Item", db_column="subitem_item")
    subitem_nombre         = models.CharField("Nombre del sub-item", max_length=120)
    item_sesion_subitem    = models.CharField("Nombre de la sesion", max_length=120, null=True, blank=True)
    subitem_orden          = models.IntegerField("Lugar")
    subitem_namespace_link = models.CharField("link", max_length=120 ,default = "#")
    subitem_fechacreacion  = models.DateTimeField("Fecha-Hora creación",default = timezone.now)
    subitem_estado         = models.CharField("Activo", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.subitem_id

    def __str__(self):
        return "{n}".format(n=self.subitem_nombre)

    def __sesion_para_sub_item(self):
        cadena = ((self.subitem_nombre).replace(' ', '_')).replace('/', '_').replace('\\', '_').lower()
        cadena = cadena.replace('á', 'a')
        cadena = cadena.replace('é', 'e')
        cadena = cadena.replace('í', 'i')
        cadena = cadena.replace('ó', 'o')
        cadena = cadena.replace('ú', 'u')

        cadena = cadena.replace('Á', 'A')
        cadena = cadena.replace('É', 'E')
        cadena = cadena.replace('Í', 'I')
        cadena = cadena.replace('Ó', 'O')
        cadena = cadena.replace('Ú', 'U')

        cadena = cadena.replace('ñ', 'n')
        cadena = cadena.replace('Ñ', 'N')

        return cadena
    sesion_para_sub_item = property(__sesion_para_sub_item)

    def save(self, *args, **kwargs):
        self.item_sesion_subitem = self.sesion_para_sub_item
        super(SubItem, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_sub_item'
        ordering = ['subitem_id', 'item']

class SubItemAdmin(admin.ModelAdmin):
    list_display  = ('subitem_id', 'subitem_nombre', 'subitem_namespace_link', 'subitem_fechacreacion', 'subitem_estado', 'item', 'subitem_orden', 'item_sesion_subitem')


# ------------
class Grupo(models.Model):

    gru_id            = models.AutoField("Key", primary_key=True)
    gru_nombre        = models.CharField("Nombre del grupo", max_length=120)
    gru_fechacreacion = models.DateTimeField("Fecha-Hora creación",default = timezone.now)

    def __int__(self):
        return self.gru_id

    def __str__(self):
        return "{n}".format(n=self.gru_nombre)


    def save(self, *args, **kwargs):
        # print "save cto"
        super(Grupo, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_grupo'
        ordering = ['gru_id']

class GrupoAdmin(admin.ModelAdmin):
    list_display = ('gru_id', 'gru_nombre', 'gru_fechacreacion')

# ------------
class GrupoUsuario(models.Model):

    OPCIONES = (
        ('S', 'SI'),
        ('N', 'NO'),
    )

    gu_id            = models.AutoField("Key", primary_key=True)
    usuario          = models.ForeignKey(User, verbose_name="Usuario", db_column="gu_usuario")
    grupo            = models.ForeignKey(Grupo, verbose_name="Grupo", db_column="gu_grupo")
    gu_fechacreacion = models.DateTimeField("Fecha-Hora creación",default = timezone.now)
    gu_permisoadd    = models.CharField("Agrega", max_length=1, choices=OPCIONES, default="S")
    gu_permisoedit   = models.CharField("Edita", max_length=1, choices=OPCIONES, default="S")
    gu_permisodel    = models.CharField("Borra", max_length=1, choices=OPCIONES, default="S")

    def __int__(self):
        return self.gu_id

    def __str__(self):
        return "{n}".format(n=self.gu_id)

    def __retornarPermiso(self):
        return "{a}:::{e}:::{d}".format(a=self.gu_permisoadd, e=self.gu_permisoedit, d=self.gu_permisodel)
    permiso = property(__retornarPermiso)


    def save(self, *args, **kwargs):
        # print "save cto"
        super(GrupoUsuario, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_grupo_usuario'
        ordering = ['gu_id']

class GrupoUsuarioAdmin(admin.ModelAdmin):
    list_display = ('gu_id', 'usuario', 'grupo', 'permiso')
    raw_id_fields = ('usuario', 'grupo')

# ------------
class UsuarioLogeado(models.Model):

    SISTEMA = (
        ('LB', 'logout_bases'),
        ('L', 'logout'),
    )

    usuario          = models.ForeignKey(User, verbose_name="Usuario", db_column="ul_usuario")
    ul_fechacreacion = models.DateTimeField("Fecha-Hora creación",default = timezone.now)
    ul_sessionid     = models.CharField('ID sesión', max_length=40, default="", blank=True, null=True)
    ul_sistema       = models.CharField("Sistema", max_length=2, choices=SISTEMA, default="", blank=True, null=True)

    def __int__(self):
        return self.ul_id

    def __str__(self):
        return "{n}".format(n=self.usuario)

    def save(self, *args, **kwargs):
        # print "save cto"
        super(UsuarioLogeado, self).save(*args, **kwargs)

    class Meta:
        db_table = 'per_usuario_logeado'
        ordering = ['ul_fechacreacion']

class UsuarioLogeadoAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'ul_fechacreacion', 'ul_sessionid', 'ul_sistema')