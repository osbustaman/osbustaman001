# -*- encoding: utf-8 -*-
from django import template
from django.conf import settings
from django.core.urlresolvers import reverse
from django.template.loader import get_template


register = template.Library()

#--------------------- TAGS PARA LOS ESTILOS, JS ----------------------
@register.simple_tag
def statics_tag_gentella(file):
    return '%s%s%s' % (settings.STATIC_URL , 'static/perfiles/gentella/' , file)

@register.simple_tag
def statics_tag_confirm(file):
    return '%s%s%s' % (settings.STATIC_URL , 'static/perfiles/confirm/' , file)

@register.simple_tag
def statics_tag(file):
    return '%s%s%s' % (settings.STATIC_URL , 'static/perfiles/' , file)

#@register.simple_tag
#def vendors_tag(file):
    #return '%s%s%s' % (settings.STATIC_URL , 'integrado/vendors/' , file)
