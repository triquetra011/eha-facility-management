__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django.test import TestCase
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.template.loader import render_to_string
from django.contrib.auth.models import User

from fm.views import home_view

from fm.views import areas_view
from fm.views import add_new_area_view
from fm.forms import AreaForm
from fm.models import Area

from fm.views import facilities_view
from fm.views import add_new_facility_view
from fm.forms import FacilityForm
from fm.models import Facility

from fm.views import contacts_view
from fm.views import add_new_contact_view
from fm.forms import ContactForm
from fm.models import Contact

from fm.views import roles_view
from fm.views import add_new_role_view
from fm.forms import RoleForm
from fm.models import Role


class FMPageBaseTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            'admin', 'admin@b.cc', 'adminpasswd')
        self.regular_user = User.objects.create_user(
            'user1', 'user@b.cc', 'userpasswd')

    def tearDown(self):
        self.superuser = None
        self.regular_user = None
        self.client.logout()

    def log_admin_in(self):
        self.client.login(username='admin', password='adminpasswd')

    def get_superuser_response(self, view):
        request = HttpRequest()
        request.user = self.superuser
        return view(request)

    def url_resolves_to_correct_view(self, url, view):
        found = resolve(url)
        self.assertIs(found.func, view)

    def view_returns_correct_html_for_superusers(
            self, view, template, data=None
    ):
        response = self.get_superuser_response(view)
        if data is None:
            data = {}
        if 'user' not in data:
            data['user'] = self.superuser
        expected_html = render_to_string(template, data)
        self.assertMultiLineEqual(response.content.decode(), expected_html)

    def page_redirects_and_asks_users_to_log_in(self, url, not_template,
                                                not_contains):
        response = self.client.get(url, follow=True)
        self.assertNotContains(response, not_contains)
        self.assertContains(response, 'Log in')
        self.assertTemplateNotUsed(response, not_template)


class HomePageTest(FMPageBaseTest):
    def test_fm_root_url_resolves_to_fm_home_page_view(self):
        self.url_resolves_to_correct_view('/fm/', home_view)

    def test_home_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(home_view, 'home.html')

    def test_home_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/')
        self.assertContains(response, 'Facility Management')
        self.assertNotContains(response, 'Log in')
        self.assertTemplateUsed(response, 'home.html')

    def test_home_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in('/fm/', 'home.html',
                                                     'Facility Management')

    def test_home_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in('/fm/', 'home.html',
                                                     'Facility Management')

    def test_home_page_contains_areas_link(self):
        # self.log_admin_in()
        response = self.get_superuser_response(home_view)
        self.assertRegexpMatches(
            response.content.decode(), r'<a [^>]*id="id_areas_link"',
            'Could not find link to the areas page')


class AreasPageTest(FMPageBaseTest):
    def test_areas_url_resolves_to_areas_view(self):
        self.url_resolves_to_correct_view('/fm/areas/', areas_view)

    def test_areas_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(areas_view, 'areas.html')

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/areas/')
        self.assertTemplateUsed(response, 'areas.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/areas/', 'areas', 'Areas')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/areas/', 'areas.html', 'Areas')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/areas/')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Areas',
                                 'Could not find Areas in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Areas',
                                 'Could not find the areas header')

    def test_page_contains_the_link_for_adding_new_areas(self):
        response = self.get_superuser_response(areas_view)
        self.assertRegexpMatches(
            response.content.decode(), r'<a [^>]*id="id_add_new_area_link"',
            'Could not find link to add a new area')

    def test_page_displays_areas(self):
        Area.objects.create(area_name='Area 1', area_type='State Zone')
        Area.objects.create(area_name='Area 2', area_type='Ward')
        self.assertEqual(Area.objects.count(), 2)
        response = self.get_superuser_response(areas_view)
        self.assertContains(response, 'Area 1')
        self.assertContains(response, 'State Zone')
        self.assertContains(response, 'Area 2')
        self.assertContains(response, 'Ward')


class AddNewAreaPageTest(FMPageBaseTest):
    def test_page_url_resolves_to_correct_view(self):
        self.url_resolves_to_correct_view('/fm/areas/new', add_new_area_view)

    def test_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(
            add_new_area_view, 'add_new_area.html', {'form': AreaForm()})

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/areas/new')
        self.assertTemplateUsed(response, 'add_new_area.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/areas/new', 'area', 'Area')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/areas/new', 'add_new_area.html', 'Area')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/areas/new')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Area',
                                 'Could not find Area in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Area',
                                 'Could not find "Area" in the header')

    def test_page_displays_area_form(self):
        self.log_admin_in()
        response = self.client.get('/fm/areas/new')
        self.assertIsInstance(response.context['form'], AreaForm)
        self.assertContains(response, 'name="area_name"')
        self.assertContains(response, 'name="area_type"')
        self.assertContains(response, 'name="area_parent"')

    def test_page_saves_a_new_area_and_redirects_to_areas_after_post(self):
        self.log_admin_in()
        response = self.client.post(
            '/fm/areas/new',
            data={'area_name': 'Some new area', 'area_type': 'LGA'}
        )
        self.assertRedirects(response, '/fm/areas/')
        response = self.client.get('/fm/areas/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Some new area')


class FacilitiesPageTest(FMPageBaseTest):
    def test_facilities_url_resolves_to_facilities_view(self):
        self.url_resolves_to_correct_view('/fm/facilities/', facilities_view)

    def test_facilities_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(facilities_view,
                                                      'facilities.html')

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/facilities/')
        self.assertTemplateUsed(response, 'facilities.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/facilities/', 'facilities', 'Facilities')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/facilities/', 'facilities.html', 'Facilities')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/facilities/')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Facilities',
                                 'Could not find Facilities in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Facilities',
                                 'Could not find the facilities header')

    def test_page_contains_the_link_for_adding_new_facilities(self):
        response = self.get_superuser_response(facilities_view)
        self.assertRegexpMatches(
            response.content.decode(), r'<a [^>]*id="id_add_new_facility_link"',
            'Could not find link to add a new facility')

    def test_page_displays_facilities(self):
        area = Area.objects.create(area_name='Area 1', area_type='State Zone')

        Facility.objects.create(facility_name='Facility 1',
                                facility_type='Zonal Store',
                                facility_status='Status 11')
        Facility.objects.create(facility_name='Facility 2',
                                facility_type='Health Facility',
                                facility_status='status22',
                                facility_area=area)
        self.assertEqual(Facility.objects.count(), 2)
        response = self.get_superuser_response(facilities_view)
        self.assertContains(response, 'Facility 1')
        self.assertContains(response, 'Zonal Store')
        self.assertContains(response, 'Status 11')
        self.assertContains(response, 'Facility 2')
        self.assertContains(response, 'Health Facility')
        self.assertContains(response, 'status22')
        self.assertContains(response, 'Area 1')
        self.assertContains(response, 'State Zone')


class AddNewFacilityPageTest(FMPageBaseTest):
    def test_page_url_resolves_to_correct_view(self):
        self.url_resolves_to_correct_view('/fm/facilities/new',
                                          add_new_facility_view)

    def test_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(
            add_new_facility_view, 'add_new_facility.html',
            {'form': FacilityForm()})

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/facilities/new')
        self.assertTemplateUsed(response, 'add_new_facility.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/facilities/new', 'facility', 'Facilit')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/facilities/new', 'add_new_facility.html', 'Facilit')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/facilities/new')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Facility',
                                 'Could not find Facility in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Facility',
                                 'Could not find "Facility" in the header')

    def test_page_displays_facility_form(self):
        self.log_admin_in()
        response = self.client.get('/fm/facilities/new')
        self.assertIsInstance(response.context['form'], FacilityForm)
        self.assertContains(response, 'name="facility_name"')
        self.assertContains(response, 'name="facility_status"')
        self.assertContains(response, 'name="facility_area"')

    def test_saves_a_new_facility_and_redirects_to_facilities_after_post(self):
        self.log_admin_in()
        response = self.client.post(
            '/fm/facilities/new',
            data={
                'facility_name': 'Some new facility1',
                'facility_type': 'Zonal Store',
                'facility_status': 'some status2'
            }
        )
        self.assertRedirects(response, '/fm/facilities/')
        response = self.client.get('/fm/facilities/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Some new facility1')
        self.assertContains(response, 'some status2')


class ContactsPageTest(FMPageBaseTest):
    def test_contacts_url_resolves_to_contacts_view(self):
        self.url_resolves_to_correct_view('/fm/contacts/', contacts_view)

    def test_contacts_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(contacts_view,
                                                      'contacts.html')

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/contacts/')
        self.assertTemplateUsed(response, 'contacts.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/contacts/', 'contacts', 'Contacts')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/contacts/', 'contacts.html', 'Contacts')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/contacts/')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Contacts',
                                 'Could not find Contacts in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Contacts',
                                 'Could not find the contacts header')

    def test_page_contains_the_link_for_adding_new_contacts(self):
        response = self.get_superuser_response(contacts_view)
        self.assertRegexpMatches(
            response.content.decode(), r'<a [^>]*id="id_add_new_contact_link"',
            'Could not find link to add a new contact')

    def test_page_displays_contacts(self):
        Contact.objects.create(contact_name='Contact 1',
                               contact_phone='04444',
                               contact_email='a@b.cc')
        Contact.objects.create(contact_name='Contact 2',
                               contact_phone='055555',
                               contact_email='e@d.cc')
        self.assertEqual(Contact.objects.count(), 2)
        response = self.get_superuser_response(contacts_view)
        self.assertContains(response, 'Contact 1')
        self.assertContains(response, '04444')
        self.assertContains(response, 'a@b.cc')
        self.assertContains(response, 'Contact 2')
        self.assertContains(response, '055555')
        self.assertContains(response, 'e@d.cc')


class AddNewContactPageTest(FMPageBaseTest):
    def test_page_url_resolves_to_correct_view(self):
        self.url_resolves_to_correct_view('/fm/contacts/new',
                                          add_new_contact_view)

    def test_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(
            add_new_contact_view, 'add_new_contact.html',
            {'form': ContactForm()})

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/contacts/new')
        self.assertTemplateUsed(response, 'add_new_contact.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/contacts/new', 'contact', 'Contact')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/contacts/new', 'add_new_contact.html', 'Contact')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/contacts/new')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Contact',
                                 'Could not find Contact in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Contact',
                                 'Could not find "Contact" in the header')

    def test_page_displays_contact_form(self):
        self.log_admin_in()
        response = self.client.get('/fm/contacts/new')
        self.assertIsInstance(response.context['form'], ContactForm)
        self.assertContains(response, 'name="contact_name"')
        self.assertContains(response, 'name="contact_phone"')
        self.assertContains(response, 'name="contact_email"')

    def test_saves_a_new_contact_and_redirects_to_contacts_after_post(self):
        self.log_admin_in()
        response = self.client.post(
            '/fm/contacts/new',
            data={
                'contact_name': 'Some new contact1',
                'contact_phone': '04444',
                'contact_email': 'a@b.cc'
            }
        )
        self.assertRedirects(response, '/fm/contacts/')
        response = self.client.get('/fm/contacts/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Some new contact1')
        self.assertContains(response, '04444')
        self.assertContains(response, 'a@b.cc')


class RolesPageTest(FMPageBaseTest):
    def test_roles_url_resolves_to_roles_view(self):
        self.url_resolves_to_correct_view('/fm/roles/', roles_view)

    def test_roles_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(roles_view,
                                                      'roles.html')

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/roles/')
        self.assertTemplateUsed(response, 'roles.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/roles/', 'roles', 'Roles')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/roles/', 'roles.html', 'Roles')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/roles/')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Roles',
                                 'Could not find Roles in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Roles',
                                 'Could not find the roles header')

    def test_page_contains_the_link_for_adding_new_roles(self):
        response = self.get_superuser_response(roles_view)
        self.assertRegexpMatches(
            response.content.decode(), r'<a [^>]*id="id_add_new_role_link"',
            'Could not find link to add a new role')

    def test_page_displays_roles(self):
        contact1 = Contact.objects.create(contact_name='contact1')
        contact2 = Contact.objects.create(contact_name='contact2')
        facility1 = Facility.objects.create(facility_name='facility1')
        facility2 = Facility.objects.create(facility_name='facility2')

        Role.objects.create(role_name='Role 1',
                            role_contact=contact1,
                            role_facility=facility1)
        Role.objects.create(role_name='Role 2',
                            role_contact=contact2,
                            role_facility=facility2)

        self.assertEqual(Role.objects.count(), 2)
        response = self.get_superuser_response(roles_view)
        self.assertContains(response, 'Role 1')
        self.assertContains(response, 'contact1')
        self.assertContains(response, 'facility1')
        self.assertContains(response, 'Role 2')
        self.assertContains(response, 'facility2')
        self.assertContains(response, 'contact2')


class AddNewRolePageTest(FMPageBaseTest):
    def test_page_url_resolves_to_correct_view(self):
        self.url_resolves_to_correct_view('/fm/roles/new',
                                          add_new_role_view)

    def test_page_returns_correct_html_for_superusers(self):
        self.view_returns_correct_html_for_superusers(
            add_new_role_view, 'add_new_role.html',
            {'form': RoleForm()})

    def test_page_accessed_by_superusers_uses_correct_template(self):
        # superuser logged in
        self.log_admin_in()
        response = self.client.get('/fm/roles/new')
        self.assertTemplateUsed(response, 'add_new_role.html')

    def test_page_redirects_and_asks_anonymous_users_to_log_in(self):
        # not logged in
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/roles/new', 'role', 'Role')

    def test_page_redirects_and_asks_non_staff_users_to_log_in(self):
        # regular user logged in
        self.client.login(username='user1', password='userpasswd')
        self.page_redirects_and_asks_users_to_log_in(
            '/fm/roles/new', 'add_new_role.html', 'Role')

    def test_page_has_correct_title_and_header(self):
        self.log_admin_in()
        response = self.client.get('/fm/roles/new')
        content = response.content.decode()
        self.assertRegexpMatches(content, r'<title[^>]*>[^<]*Role',
                                 'Could not find Role in title')
        self.assertRegexpMatches(content, r'<h1[^>]*>[^<]*Role',
                                 'Could not find "Role" in the header')

    def test_page_displays_role_form(self):
        self.log_admin_in()
        response = self.client.get('/fm/roles/new')
        self.assertIsInstance(response.context['form'], RoleForm)
        self.assertContains(response, 'name="role_name"')
        self.assertContains(response, 'name="role_contact"')
        self.assertContains(response, 'name="role_facility"')

    def test_saves_a_new_role_and_redirects_to_roles_after_post(self):
        contact = Contact.objects.create(contact_name='contact22')
        facility = Facility.objects.create(facility_name='facility11')

        self.log_admin_in()
        response = self.client.post(
            '/fm/roles/new',
            data={
                'role_name': 'SCCO',
                'role_contact': contact.id,
                'role_facility': facility.id
            }
        )
        self.assertRedirects(response, '/fm/roles/')
        response = self.client.get('/fm/roles/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SCCO')
        self.assertContains(response, 'contact22')
        self.assertContains(response, 'facility11')

