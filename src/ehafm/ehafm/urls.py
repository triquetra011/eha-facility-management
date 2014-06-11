__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'


from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'ehafm.views.home', name='home'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^login$', 'django.contrib.auth.views.login'),
    url(r'^logout$', 'django.contrib.auth.views.logout'),
    url(r'^fm/', include('fm.urls')),
)
