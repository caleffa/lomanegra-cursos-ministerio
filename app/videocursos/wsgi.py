"""
WSGI config for videocursos project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/2.1/howto/deployment/wsgi/
"""

import os


# import pydevd
# pydevd.settrace('host.docker.internal', port=9876, stdoutToServer=True, stderrToServer=True, suspend=False)

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'videocursos.settings')

application = get_wsgi_application()
