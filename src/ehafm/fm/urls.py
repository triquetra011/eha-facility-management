__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'


from django.conf.urls import patterns, include, url

urlpatterns = patterns('',
    url(r'^$', 'fm.views.home_view', name='fm_home'),
    url(r'^areas/$', 'fm.views.areas_view', name='fm_areas'),
    url(r'^areas/new$', 'fm.views.add_new_area_view', name='fm_add_new_area'),
    url(r'^facilities/$', 'fm.views.facilities_view', name='fm_facilities'),
    url(r'^facilities/new$', 'fm.views.add_new_facility_view',
        name='fm_add_new_facility'),
    url(r'^(facilities)/([0-9]+)/json$',
        'fm.views.json_view', name='fm_facility_json'),
    url(r'^contacts/$', 'fm.views.contacts_view', name='fm_contacts'),
    url(r'^contacts/new$', 'fm.views.add_new_contact_view',
        name='fm_add_new_contact'),
    url(r'^(contacts)/([0-9]+)/json$',
        'fm.views.json_view', name='fm_contact_json'),
    url(r'^roles/$', 'fm.views.roles_view', name='fm_roles'),
    url(r'^roles/new$', 'fm.views.add_new_role_view',
        name='fm_add_new_role'),
)
