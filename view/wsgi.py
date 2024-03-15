"""
WSGI config for view project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/howto/deployment/wsgi/
"""

from dotenv import load_dotenv  # for python-dotenv method
load_dotenv()  # for python-dotenv method

import os
from django.core.wsgi import get_wsgi_application


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'view.settings')

application = get_wsgi_application()
