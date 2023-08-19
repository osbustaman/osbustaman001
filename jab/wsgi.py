#! /usr/bin/env python3.6
"""
WSGI config for jab project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "jab.settings")

application = get_wsgi_application()

from jab.views import load_data_base

load_data_base()
