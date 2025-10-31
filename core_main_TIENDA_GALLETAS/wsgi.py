"""
WSGI config for core_main_TIENDA_GALLETAS project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core_main_TIENDA_GALLETAS.settings')

application = get_wsgi_application()
