__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django.contrib import admin

from fm.models import Area, Contact, Facility, Role

# Register your models here.
admin.site.register((Area, Contact, Facility, Role))
