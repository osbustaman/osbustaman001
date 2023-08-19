# -*- encoding: utf-8 -*-
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.db.models import Case, CharField, Value, When, BooleanField, IntegerField, Subquery, Sum, Q

from usuario.models import Empresa, CargoEmpresa, CentroCosto

def existe_empresa(func):
    def valida(request, *args, **kwargs):
        cantidadEmpresas = Empresa.objects.count()
        if cantidadEmpresas < 1:
            valor = redirect('bases:errorcuatrocientostres')
        else:
            valor = func(request, *args, **kwargs)
        return valor

    return valida


def cargo_empresa(func):

    def valida_cargo(request, *args, **kwargs):
        emp=Empresa.objects.get(emp_id=request.session['la_empresa'])
        cantCargoEmpresa = CargoEmpresa.objects.filter(empresa=emp).count()
        if cantCargoEmpresa < 1:
            valor = redirect('bases:decoradorCargoError403')
        else:
            valor = func(request, *args, **kwargs)
        return valor

    return valida_cargo


def centro_costo_empresa(func):

    def valida_cargo(request, *args, **kwargs):
        emp=Empresa.objects.get(emp_id=request.session['la_empresa'])
        cantCentroCosto = CentroCosto.objects.filter(grupocentrocosto__empresa=emp).count()
        if cantCentroCosto < 1:
            valor = redirect('bases:decoradorCentroCostoError403')
        else:
            valor = func(request, *args, **kwargs)
        return valor

    return valida_cargo



def verificar_cantidad_ususario(func):

    def valida_cargo(request, *args, **kwargs):
        emp=Empresa.objects.get(emp_id=request.session['la_empresa'])
        cantCentroCosto = CentroCosto.objects.filter(grupocentrocosto__empresa=emp).count()
        if cantCentroCosto < 1:
            valor = redirect('bases:decoradorCentroCostoError403')
        else:
            valor = func(request, *args, **kwargs)
        return valor

    return valida_cargo

