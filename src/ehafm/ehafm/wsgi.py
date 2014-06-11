"""
WSGI config for ehafm project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'


import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ehafm.settings")

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
