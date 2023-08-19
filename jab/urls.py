"""jab URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings

from django.contrib.auth.views import logout, password_reset, password_reset_done, password_reset_complete

from perfil.views import index_bases, panel_bases, index, panel_control, login_user, login_user_bases

from django.contrib.auth.models import User

urlpatterns = [
    url(r'^admin/', admin.site.urls),

    # https://djangobook.com/authentication-web-requests/

    # ********************* url bases *********************
    url(r'^bases/$', index_bases, name='index_bases'),
    # url(r'^$', index_bases, name='index_bases'),
    url(r'^panelcontrol/$', panel_bases, name='panel_bases'),
    url(r'^login/user/bases/$', login_user_bases, name='login_user_bases'),
    url(r'^logout/bases/$', logout, {'next_page': '/bases'}, name='logout_bases'),
    # ********************* url bases *********************

    # ********************* url plataforma *********************
    url(r'^login/$', index, name='index'),
    url(r'^login/user/$', login_user, name='login_user'),
    url(r'^panel/$', panel_control, name='panel'),
    #url(r'^panel/', include('recursos_humanos.urls', namespace='recursos_humanos_namespace'), name='bd'),
    url(r'^logout/$', logout, {'next_page': '/login'}, name='logout'),
    # ********************* url plataforma *********************

    #url(r'^panel/rem/', include('remuneraciones.urls', namespace='remuneraciones_namespace'), name='remuneraciones'),


    url(r'panecontrol/', include('bases.urls', namespace='bases'), name='bases'),
]

