"""
ASGI config for the Invoices project.

ASGI (Asynchronous Server Gateway Interface) supports async views,
WebSockets, and long-lived connections. Used with servers like Daphne or Uvicorn.
The 'application' variable is the entry point the server calls.
"""

import os

from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

application = get_asgi_application()
