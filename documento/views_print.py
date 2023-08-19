from usuario.models import Usuario


def reimprimir_doc_pdf(request, id_usuario):

    usu=Usuario.objects.get(user_id = id_usuario)


    dict_usuario = {
        'username':usu.user.username,
        'first_name':usu.user.first_name,
        'last_name':usu.user.last_name,
        'usu_tiporut':usu.usu_tiporut,
        'usu_rut':usu.usu_rut,
        'usu_sexo':usu.usu_sexo,
        'usu_fono':usu.usu_fono,
        'usu_fechanacimiento':usu.usu_fechanacimiento,
        'pais':usu.pais.pa_nombre,
        'region':usu.region.re_nombre,
        'comuna':usu.comuna.com_nombre,
        'usu_direccion':usu.usu_direccion,
        'usu_estadocivil':usu.usu_estadocivil,
        'usu_tipousuario':usu.usu_tipousuario,
        'usu_profesion':usu.usu_profesion,
        'usu_extranjero':usu.usu_extranjero,
        'usu_usuarioactivo':usu.usu_usuarioactivo,
        'usu_licenciaconducir':usu.usu_licenciaconducir,
        'usu_nombreusuario':usu.usu_nombreusuario,
        'usu_passwordusuario':usu.usu_passwordusuario,
        'usu_fechacreacion':usu.usu_fechacreacion,
        'usu_tipocreacionusuario':usu.usu_tipocreacionusuario,
        'usu_rutafoto':usu.usu_rutafoto,
        'usu_nombrefoto':usu.usu_nombrefoto,
    }


    return {
        'dict_usuario': dict_usuario,
    }
