"""
WSGI config for the Invoices project.

WSGI (Web Server Gateway Interface) is the standard for deploying
Django with traditional sync servers like Gunicorn or uWSGI.
The 'application' variable is the entry point the server calls.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_wsgi_application()
