# -*- encoding: utf-8 -*-
from django.conf.urls import url, include
import bases.views as views
import bases.ut_views as b_ut_views
import empresa.views as views_emp
import usuario.ut_views as ut_views
import usuario.views as usu_views
import documento.views as doc_views
import documento.views_cliprov as doc_views_cp
import configuracion.views as config_views
import configuracion.views_mantenedores as config_views_m
import clienteproveedor.views as cliprov_views

urlpatterns = [
    # BASES
    #
    url(r'bases/', views.listado_bases, name='listado_bases'),
    url(r'agregar/base/', views.agregarBase, name='agregarBase'),
    url(r'editar/base/(?P<idbase>[\w\-]+)/', views.editarBaseDeDato, name='editarBaseDeDato'),
    url(r'create/database/', views.create_database, name='create_database'),

    url(r'create/documentos/(?P<baseId>[\w\-]+)/(?P<is_ajax>[\w\-]+)/', views.ajaxCrearDocumentos, name='ajaxCrearDocumentos'),
    url(r'datos/database/', views.datos_base, name='datos_base'),
    url(r'add/usuario/admin/(?P<emp_id>[\w\-]+)/', views.add_usuario_admin, name='add_usuario_admin'),
    url(r'activar/base/(?P<baseId>[\w\-]+)/(?P<accion>[\w\-]+)/', views.activarBase, name='activarBase'),
    url(r'borrar/usuario/(?P<baseId>[\w\-]+)/(?P<usuario>[\w\-]+)/', views.borrarUsuario, name='borrarUsuario'),
    url(r'armar/parametros/generales/del/sistema/', views.armarParametrosGeneralesDelSistema,
        name='armarParametrosGeneralesDelSistema'),
    url(r'obtener/datos/usuario/(?P<user_id>[\w\-]+)/(?P<bd_id>[\w\-]+)/', views.obtenerDatosUsuario, name='obtenerDatosUsuario'),
    url(r'edit/usuario/admin/(?P<emp_id>[\w\-]+)/(?P<usu_id>[\w\-]+)/', views.editUsuarioAdmin, name='editUsuarioAdmin'),


    url(r'doc/default/', views.documentoPorDefecto, name='documentoPorDefecto'),
    url(r'add/nuevo/tipo/documento/', views.addNuevoTipoDocumento, name='addNuevoTipoDocumento'),
    url(r'edit/nuevo/tipo/documento/(?P<tdl_id>[\w\-]+)/', views.editNuevoTipoDocumento, name='editNuevoTipoDocumento'),
    url(r'borrar/nuevo/tipo/documento/(?P<tdl_id>[\w\-]+)/', views.borrarTipoDocumento, name='borrarTipoDocumento'),
    url(r'agregar/documento/standart/(?P<tdl_id>[\w\-]+)/', views.agregarDocumentoStandart, name='agregarDocumentoStandart'),
    url(r'editar/documento/standart/(?P<tdl_id>[\w\-]+)/(?P<doc_id>[\w\-]+)/', views.editarDocumentoStandart, name='editarDocumentoStandart'),
    url(r'borrar/documento/standart/(?P<doc_id>[\w\-]+)/', views.borrarDocumentoStandart, name='borrarDocumentoStandart'),



    url(r'create/migrate/(?P<baseId>[\w\-]+)/(?P<is_ajax>[\w\-]+)/', b_ut_views.crearMigrate, name='crear_migrate'),
    url(r'armar/estructura/carpeta/empresa/(?P<baseId>[\w\-]+)/(?P<is_ajax>[\w\-]+)/', b_ut_views.armarEstructuraCarpetaEmpresa, name='ajaxArmarEstructuraCarpetaEmpresa'),
    url(r'ajax/armar/menu/(?P<baseId>[\w\-]+)/(?P<is_ajax>[\w\-]+)/', b_ut_views.ajaxArmarMenu, name='ajaxArmarMenu'),
    url(r'ajax/crear/documentos/(?P<baseId>[\w\-]+)/(?P<is_ajax>[\w\-]+)/', b_ut_views.ajaxCrearDocumentos, name='ajaxCrearDocumentos'),
    url(r'ajax/llenado/tabla/general/(?P<baseId>[\w\-]+)/(?P<is_ajax>[\w\-]+)/', b_ut_views.ajaxLlenadoTablaGeneral, name='ajaxLlenadoTablaGeneral'),

    # -----------------------------
    url(r'views/empresa/', views_emp.views_empresa, name='views_empresa'),
    url(r'add/empresa/', views_emp.add_empresa, name='add_empresa'),
    url(r'cambiar/empresa/(?P<id_emp>[\w\-]+)/', views_emp.cambiarEmpresa, name='cambiarEmpresa'),
    url(r'edit/empresa/(?P<id_emp>[\w\-]+)/', views_emp.edit_empresa, name='edit_empresa'),
    url(r'subir/logo/por/empresa/(?P<emp_id>[\w\-]+)/', views_emp.subirLogoPorEmpresa, name='subirLogoPorEmpresa'),
    url(r'remove/empresa', views_emp.remove_empresa, name='remove_empresa'),
    url(r'bajar/excel/emp/', views_emp.bajarExcelEmpresas, name='bajarExcelEmpresas'),

    url(r'add/relacion/(?P<id_emp>[\w\-]+)/', views_emp.add_relacion, name='add_relacion'),
    url(r'edit/relacion/(?P<id_emp>[\w\-]+)/(?P<id_relacion>[\w\-]+)/', views_emp.edit_relacion, name='edit_relacion'),
    url(r'remove/relacion/(?P<id_emp>[\w\-]+)/(?P<id_relacion>[\w\-]+)/', views_emp.remove_relacion,
        name='remove_relacion'),

    url(r'add/sucursal/(?P<id_emp>[\w\-]+)/', views_emp.add_sucursal, name='add_sucursal'),
    url(r'edit/sucursal/(?P<id_emp>[\w\-]+)/(?P<suc_id>[\w\-]+)/', views_emp.edit_sucursal, name='edit_sucursal'),
    url(r'delete/sucursal/(?P<id_emp>[\w\-]+)/(?P<id_suc>[\w\-]+)/', views_emp.delete_sucursal, name='delete_sucursal'),

    url(r'add/personal/(?P<id_emp>[\w\-]+)/', views_emp.add_personal, name='add_personal'),
    url(r'edit/personal/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', views_emp.edit_personal,
        name='edit_personal'),
    url(r'remove/personal/(?P<id_usuario>[\w\-]+)/(?P<id_emp>[\w\-]+)/', views_emp.remove_personal,
        name='remove_personal'),
    url(r'ajax/add/haberes/(?P<usu_id>[\w\-]+)/', views_emp.ajax_add_haberes, name='ajax_add_haberes'),
    url(r'ajax/edit/haberes/(?P<hab_id>[\w\-]+)/', views_emp.ajax_edit_haberes, name='ajax_edit_haberes'),
    url(r'ajax/delete/haberes/(?P<hab_id>[\w\-]+)/', views_emp.ajax_delete_haberes, name='ajax_delete_haberes'),

    url(r'add/cargo/(?P<id_emp>[\w\-]+)/', views_emp.add_cargo, name='add_cargo'),
    url(r'edit/cargo/(?P<car_id>[\w\-]+)/(?P<id_emp>[\w\-]+)/', views_emp.edit_cargo, name='edit_cargo'),
    url(r'delete/cargo/(?P<car_id>[\w\-]+)/(?P<id_emp>[\w\-]+)/', views_emp.delete_cargo, name='delete_cargo'),

    url(r'ajax/obtener/asignacio/familiar/(?P<is_ajax>[\w\-]+)/', ut_views.ajaxObtenerAsignacioFamiliar,
        name='ajaxObtenerAsignacioFamiliar'),
    url(r'ajax/verificar/empleado/', ut_views.ajaxVerificarEmpleado, name='ajaxVerificarEmpleado'),
    url(r'ajax/carga/datos/usuario/', ut_views.ajaxCargaDatosUsuario, name='ajaxCargaDatosUsuario'),
    url(r'ajax/data/afp/', ut_views.ajax_data_afp, name='ajax_data_afp'),
    url(r'ajax/salud/', ut_views.ajax_salud, name='ajax_salud'),
    url(r'ajax/seguro/desempleo/', ut_views.ajax_seguro_desempleo, name='ajax_seguro_desempleo'),
    url(r'ajax/ciclo/(?P<id_usuario>[\w\-]+)/', ut_views.ajax_ciclo, name='ajax_ciclo'),
    url(r'ajax/termino/laboral/(?P<id_usuario>[\w\-]+)/', ut_views.ajax_termino_laboral, name='ajax_termino_laboral'),
    url(r'ajax/otro/(?P<id_usuario>[\w\-]+)/', ut_views.ajax_otro, name='ajax_otro'),
    url(r'ajax/add/haber/descuento/(?P<user_id>[\w\-]+)/(?P<emp_id>[\w\-]+)/', ut_views.ajax_add_haber_descuento, name='ajax_add_haber_descuento'),
    url(r'ajax/delete/haber/descuento/(?P<hab_id>[\w\-]+)/', ut_views.ajax_delete_haber_descuento, name='ajax_delete_haber_descuento'),
    url(r'ajax/asociar/usuario/empresa', ut_views.ajaxAsociarUsuarioEmpresa, name='ajaxAsociarUsuarioEmpresa'),
    url(r'ajax/editar/usuario/empresa/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/',
        ut_views.ajaxEditarUsuarioEmpresa, name='ajaxEditarUsuarioEmpresa'),
    url(r'ajax/add/datos/personales/(?P<usu_id>[\w\-]+)/', ut_views.ajaxAddDatosPersonales,
        name='ajaxAddDatosPersonales'),
    url(r'ajax/add/datos/laborales/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', ut_views.ajaxAddDatosLaborales,
        name='ajaxAddDatosLaborales'),
    url(r'ajax/datos/leyes/sociales/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', ut_views.ajaxDatosLeyesSociales,
        name='ajaxDatosLeyesSociales'),
    url(r'ajax/add/remuneracion/empleado/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/',
        ut_views.ajaxAddRemuneracionEmpleado, name='ajaxAddRemuneracionEmpleado'),
    url(r'ajax/add/menu/empleado/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', ut_views.ajaxAddMenuEmpleado,
        name='ajaxAddMenuEmpleado'),
    url(r'remove/items/(?P<id_usuario>[\w\-]+)/(?P<empresa_id>[\w\-]+)/(?P<men_ite_id>[\w\-]+)/',
        ut_views.removeItems, name='removeItems'),
    url(r'ajax/crear/usuario/empresa/', ut_views.ajaxCrearUsuarioEmpresa, name='ajaxCrearUsuarioEmpresa'),
    url(r'ajax/add/imagen/perfil/usuario/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', ut_views.ajaxAddImagenPerfilUSuario, name='ajaxAddImagenPerfilUSuario'),

    url(r'views/grupo/ccostos/', views_emp.views_grupos_centro_costo, name='views_grupos_centro_costo'),
    url(r'add/grupo/centro/costos/(?P<id_emp>[\w\-]+)/', views_emp.add_grupo_centro_costo, name='add_grupo_centro_costo'),
    url(r'edit/grupo/centro/costos/(?P<gcencost_id>[\w\-]+)/(?P<id_emp>[\w\-]+)/', views_emp.edit_grupo_centro_costo, name='edit_grupo_centro_costo'),
    url(r'delete/grupo/centro/costos/(?P<gcencost_id>[\w\-]+)/(?P<id_emp>[\w\-]+)/', views_emp.delete_grupo_centro_costo, name='delete_grupo_centro_costo'),

    url(r'add/centro/costos/(?P<gcencost_id>[\w\-]+)/', views_emp.add_centro_costo, name='add_centro_costo'),
    url(r'edit/centro/costos/(?P<gcencost_id>[\w\-]+)/(?P<cencost_id>[\w\-]+)/', views_emp.edit_centro_costo, name='edit_centro_costo'),
    url(r'delete/centro/costos/(?P<gcencost_id>[\w\-]+)/(?P<cencost_id>[\w\-]+)/', views_emp.delete_centro_costo, name='delete_centro_costo'),

    url(r'views/cargos/', views_emp.views_cargos, name='views_cargos'),

    url(r'views/personal/', usu_views.views_empleados, name='views_empleados'),
    url(r'views/ficha/empleado/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/(?P<accion>[\w\-]+)/', usu_views.viewsFichaEmpleado, name='viewsFichaEmpleado'),
    url(r'pdf/datos/empleado/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', usu_views.pdfFichaEmpleado, name='pdfFichaEmpleado'),
    url(r'edit/data/empleado/(?P<id_usuario>[\w\-]+)/(?P<id_empresa>[\w\-]+)/', usu_views.editDataEmpleado, name='editDataEmpleado'),

    # ---------------------------------------------------------
    # config_view
    url(r'views/parametros/', config_views.views_parametros, name='views_parametros'),
    url(r'add/parametros/', config_views.addParametros, name='addParametros'),
    url(r'editar/parametros/(?P<parametro_id>[\w\-]+)/', config_views.editarParametros, name='editarParametros'),
    url(r'borrar/parametros/(?P<parametro_id>[\w\-]+)/(?P<estado>[\w\-]+)/', config_views.borrarParametros, name='borrarParametros'),
    url(r'views/config/empresa/', config_views.views_config_empresa, name='views_config_empresa'),
    url(r'views/add/moneda/', config_views.views_add_moneda, name='views_add_moneda'),
    url(r'views/edit/moneda/(?P<mon_id>[\w\-]+)/(?P<flag>[\w\-]+)/', config_views.views_edit_moneda, name='views_edit_moneda'),

    # DOCUMENTOS
    # configuracion documentos
    url(r'listado/documentos/(?P<filtro>[\w\-]+)/', doc_views.listadoDocumentos, name='listadoDocumentos'),
    url(r'listado/documentos/', doc_views.listadoDocumentos, name='listadoDocumentos'),
    url(r'add/grupo/documento/', doc_views.addGrupoDocumento, name='addGrupoDocumento'),
    url(r'edit/grupo/documento/(?P<tdl_id>[\w\-]+)/', doc_views.editGrupoDocumento, name='editGrupoDocumento'),
    url(r'borrar/tipo/documento/', doc_views.borrarTipoDocumento, name='borrarTipoDocumento'),
    url(r'add/nuevo/documento/(?P<tdl_id>[\w\-]+)/', doc_views.addNuevoDocumento, name='addNuevoDocumento'),
    url(r'editar/nuevo/documentos/(?P<tdl_id>[\w\-]+)/', doc_views.editDocumento,name='editDocumento'),
    url(r'consultar/borrar/documento/', doc_views.consultarBorrarDocumento, name='consultarBorrarDocumento'),
    url(r'borrar/documento/(?P<doc_id>[\w\-]+)/(?P<estado>[\w\-]+)/', doc_views.borrarDocumento, name='borrarDocumento'),
    url(r'ajax/add/file/usuario/(?P<id_usuario>[\w\-]+)/', doc_views.ajaxAddFileUsuario, name='ajaxAddFileUsuario'),
    url(r'add/doc/empresa/(?P<tdl_id>[\w\-]+)/', doc_views.documentoEmpresa,name='documentoEmpresa'),
    url(r'editar/documento/empresa/(?P<docempr_id>[\w\-]+)/', doc_views.editDocumentoEmpresa,name='editDocumentoEmpresa'),
    url(r'borra/doc/emp/(?P<docemp_id>[\w\-]+)/(?P<accion>[\w\-]+)/', doc_views.borrarDocumentoEmpleado,name='borrarDocumentoEmpleado'),
    url(r'pdf/documento/(?P<doc_id>[\w\-]+)/(?P<id_usuario>[\w\-]+)/', doc_views.pdfDocumento,name='pdfDocumento'),

    url(r'ajax/filtro/empresa/', config_views.ajaxFiltroPorEmpresa, name='ajaxFiltroPorEmpresa'),
    url(r'ajax/buscar/documento/', doc_views.ajaxBuscarDocumento, name='ajaxBuscarDocumento'),

    # MANTENEDORES
    # cliente/proveedor
    url(r'views/cliente/proveedor/(?P<entidad>[\w\-]+)/', cliprov_views.viewsClientesProveedores,name='viewsClientesProveedores'),
    url(r'views/cliente/proveedor/', cliprov_views.viewsClientesProveedores,name='viewsClientesProveedores'),
    url(r'add/cliente/proveedor/', cliprov_views.addClienteProveedor,name='addClienteProveedor'),
    url(r'edit/cliente/proveedor/(?P<cp_id>[\w\-]+)/', cliprov_views.editClienteProveedor,name='editClienteProveedor'),
    url(r'cliente/proveedor/empresa/(?P<cp_id>[\w\-]+)/', cliprov_views.addClienteProveedorEmpresa,name='addClienteProveedorEmpresa'),
    url(r'edit/cli/prov/empresa/(?P<cp_id>[\w\-]+)/(?P<cpe_id>[\w\-]+)/', cliprov_views.editClienteProveedorEmpresa,name='editClienteProveedorEmpresa'),
    url(r'borrar/cliente/proveedor/', cliprov_views.borrarClienteProveedor,name='borrarClienteProveedor'),
    url(r'borrar/cli/prov/emp/(?P<cpe_id>[\w\-]+)/(?P<estado>[\w\-]+)/', cliprov_views.borrarClienteProveedorEmpresa,name='borrarClienteProveedorEmpresa'),

    url(r'exportador/(?P<accion>[\w\-]+)/', config_views_m.viewsExportador,name='viewsExportador'),
    url(r'exportador/', config_views_m.viewsExportador,name='viewsExportador'),
    url(r'campos/cliente/proveedor/(?P<accion>[\w\-]+)/', config_views_m.camposClienteProveedor,name='camposClienteProveedor'),
    url(r'campos/personal/', config_views_m.camposPersonal,name='camposPersonal'),
    url(r'modal/ids/', config_views_m.modal_ids,name='modal_ids'),

    url(r'error/403/', config_views.errorcuatrocientostres, name='errorcuatrocientostres'),
    url(r'errorcargoempresa/403/', config_views.decoradorCargoError403, name='decoradorCargoError403'),
    url(r'errorcentrocostoempresa/403/', config_views.decoradorCentroCostoError403, name='decoradorCentroCostoError403'),

    # ******* DOCUMENTO CLIENTE PROVEEDOR ********
    url(r'doc/cliente/', doc_views_cp.listadoDocumentosCliente, name='listadoDocumentosCliente'),
    url(r'doc/proveedor/', doc_views_cp.listadoDocumentosProveedor, name='listadoDocumentosProveedor'),
    url(r'cant/documentos/(?P<doc_id>[\w\-]+)/(?P<tipoDoc>[\w\-]+)/', doc_views_cp.cantidad_documentos, name='cantidad_documentos'),
    url(r'add/doc/c/p/(?P<doc_id>[\w\-]+)/(?P<tipoDoc>[\w\-]+)/', doc_views_cp.addNuevoDocumentosCP, name='addNuevoDocumentosCP'),
    url(r'edit/doc/c/p/(?P<doc_id>[\w\-]+)/(?P<docenc_id>[\w\-]+)/(?P<tipoDoc>[\w\-]+)/', doc_views_cp.editNuevoDocumentosCP, name='editNuevoDocumentosCP'),
    url(r'ajax/add/detalle/(?P<docenc_id>[\w\-]+)/', doc_views_cp.ajaxAddDetalle, name='ajaxAddDetalle'),
    url(r'ajax/delete/detalle/(?P<docdet_id>[\w\-]+)/(?P<docenc_id>[\w\-]+)/', doc_views_cp.ajaxDelDetalle, name='ajaxDelDetalle'),
    url(r'ajax/edit/detalle/(?P<docenc_id>[\w\-]+)/(?P<docdet_id>[\w\-]+)/', doc_views_cp.ajaxEditDetalle, name='ajaxEditDetalle'),
    url(r'pdf/doc/C/P/(?P<doc_id>[\w\-]+)/(?P<docenc_id>[\w\-]+)/(?P<tipoDoc>[\w\-]+)/', doc_views_cp.pdfDocumentoClienteProveedor, name='pdfDocumentoClienteProveedor'),
    url(r'ajax/delete/documento/', doc_views_cp.ajaxDeleteDocumento, name='ajaxDeleteDocumento'),

]

