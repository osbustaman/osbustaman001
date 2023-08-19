# -*- encoding: utf-8 -*-
from django.core.urlresolvers import reverse
from usuario.models import Usuario, UsuarioEmpresa, Empresa
from perfil.models import MenuItem, SubItem, Item, Menu
from django.contrib.auth.models import User
from jab.threadlocal import thread_local

from usuario.models import AsociacionUsuarioEmpresa

class menu_middleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_view(self, request, view_func, view_args, view_kwargs):

        # print("view_kwargs: ", view_kwargs)
        # print("view_args: ", view_args)
        # print("view_func: ", view_func)
        # print("request: ", request.GET)
        # print("self: ", self)
        # print("USUARIO: ", request.session["dicUsuario"])

        try:
            lst_item = []
            lstEmpresas = []
            usu_id = request.session["dicUsuario"]['id']
            is_staff = request.session["dicUsuario"]['is_staff']


            request.session['nombre_usuario'] = request.session["dicUsuario"]['first_name']+" "+request.session["dicUsuario"]['last_name']
            if is_staff:
                menu = Item.objects.all()
                emp = Empresa.objects.all()

                for e in emp:
                    lstEmpresas.append({
                        'key':e.emp_id,
                        'value':e.emp_razonsocial
                    })


            else:
                user = User.objects.get(id=usu_id)
                emp = AsociacionUsuarioEmpresa.objects.filter(user=user)
                menuUsuario = Menu.objects.get(usuario=user)
                menu = MenuItem.objects.filter(menu=menuUsuario).exclude(men_ite_estado='N').order_by('item__item_orden')
                for e in emp:
                    lstEmpresas.append({
                        'key':e.empresa.emp_id,
                        'value':e.empresa.emp_razonsocial
                    })

            request.session['listado_empresas'] = lstEmpresas


            for mn in menu:

                lst_subItem = []
                if is_staff:
                    sItem = SubItem.objects.filter(item=mn)
                    item_nombre = mn.item_nombre
                    item_css_img = mn.item_css_img
                else:
                    sItem = SubItem.objects.filter(item=mn.item)
                    item_nombre = mn.item.item_nombre
                    item_css_img = mn.item.item_css_img

                for st in sItem:
                    if not st.subitem_namespace_link == '#':
                        # aqui se captura la cadena
                        el_item = st.subitem_namespace_link
                        # aqui se obtiene el nombre del link
                        reverse_ruta = []

                        for i in el_item.split(":::"):
                            reverse_ruta.append(i)

                        el_link = "bases:{l}".format(l=reverse_ruta[0])

                        la_ruta = reverse(el_link, args=reverse_ruta[1:])
                        idlink = reverse_ruta[1:]

                    else:
                        la_ruta = '#'
                        idlink = ''

                    subitem_nombre = st.subitem_nombre.lower()

                    lst_subItem.append({
                        'skey': st.subitem_id,
                        'idlink': idlink,
                        'svalue': st.subitem_nombre,
                        'slink': la_ruta,
                        'seguridad': 0,
                        'subitem_nombre': subitem_nombre,
                        'item_sesion_subitem':st.item_sesion_subitem
                    })


                if not is_staff:
                    itemSesion = mn.item.item_sesion_menu
                else:
                    itemSesion = mn.item_sesion_menu

                lst_item.append({
                    'key': mn.item_id,
                    'value': item_nombre,
                    'icon': item_css_img,
                    'lst_subItem': lst_subItem,
                    'item_sesion_menu':itemSesion
                })

            menu = {
                'lst_item': lst_item,
            }
            request.session['menu_sistema'] = menu
        except:
            pass
