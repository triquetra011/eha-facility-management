__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django.test import TestCase

from fm.forms import AreaForm, FacilityForm, ContactForm, RoleForm

from fm.models import Area, AREA_TYPES
from fm.models import Facility
from fm.models import Contact
from fm.models import Role


class FMFormTest(TestCase):
    def create_save_and_return_area(self, area_name, area_type, area_parent,
                                    number_of_areas_before):
        # fill in the form and save it and see if the number of areas is correct
        # both before and after
        if area_parent is None:
            parent_id = None
        else:
            parent_id = area_parent.id
        self.assertEqual(Area.objects.count(), number_of_areas_before)
        form = AreaForm(data={'area_name': area_name,
                              'area_type': area_type,
                              'area_parent': parent_id})
        if area_parent is not None:
            area_parent.save()
        area = form.save()
        self.assertEqual(Area.objects.count(), number_of_areas_before + 1)
        # check if the area object in the database at the current index is the
        # same as the one just created
        self.assertEqual(area, Area.objects.all()[number_of_areas_before])
        aid = area.id
        area = Area.objects.get(id=aid)
        # check attributes of the saved area object
        self.assertEqual(area.area_name, area_name)
        self.assertEqual(area.area_type, area_type)
        self.assertEqual(area.area_parent, area_parent)
        return area

    def create_save_and_return_facility(self, name, facility_type, status, area,
                                        number_of_facilities_before):
        # fill in the form and save it and see if the number of facilities is
        # correct both before and after
        if area is None:
            area_id = None
        else:
            area_id = area.id
        self.assertEqual(Facility.objects.count(), number_of_facilities_before)
        form = FacilityForm(data={'facility_name': name,
                                  'facility_type': facility_type,
                                  'facility_status': status,
                                  'facility_area': area_id})
        if area is not None:
            area.save()
        facility = form.save()
        self.assertEqual(Facility.objects.count(),
                         number_of_facilities_before + 1)
        # check if the facility object in the database at the current index is
        # the same as the one just created
        self.assertEqual(facility,
                         Facility.objects.all()[number_of_facilities_before])
        fid = facility.id
        facility = Facility.objects.get(id=fid)
        # check attributes of the saved facility object
        self.assertEqual(facility.facility_name, name)
        self.assertEqual(facility.facility_type, facility_type)
        self.assertEqual(facility.facility_status, status)
        self.assertEqual(facility.facility_area, area)
        return facility

    def create_save_and_return_contact(self, name, phone, email,
                                       number_of_contacts_before):
        # fill in the form and save it and see if the number of contacts is
        # correct both before and after
        self.assertEqual(Contact.objects.count(), number_of_contacts_before)
        form = ContactForm(data={'contact_name': name,
                                 'contact_phone': phone,
                                 'contact_email': email,
        })
        contact = form.save()
        self.assertEqual(Contact.objects.count(),
                         number_of_contacts_before + 1)
        # check if the contact object in the database at the current index is
        # the same as the one just created
        self.assertEqual(contact,
                         Contact.objects.all()[number_of_contacts_before])
        cid = contact.id
        contact = Contact.objects.get(id=cid)
        # check attributes of the saved contact object
        self.assertEqual(contact.contact_name, name)
        self.assertEqual(contact.contact_phone, phone)
        self.assertEqual(contact.contact_email, email)
        return contact

    def create_save_and_return_role(self, name, contact, facility,
                                    number_of_roles_before):
        # fill in the form and save it and see if the number of roles is
        # correct both before and after
        if contact is None:
            contact_id = None
        else:
            contact_id = contact.id
        if facility is None:
            facility_id = None
        else:
            facility_id = facility.id
        self.assertEqual(Role.objects.count(), number_of_roles_before)
        form = RoleForm(data={'role_name': name,
                              'role_contact': contact_id,
                              'role_facility': facility_id, })
        if contact is not None:
            contact.save()
        if facility is not None:
            facility.save()
        role = form.save()
        self.assertEqual(Role.objects.count(), number_of_roles_before + 1)
        # check if the role object in the database at the current index is
        # the same as the one just created
        self.assertEqual(role, Role.objects.all()[number_of_roles_before])
        rid = role.id
        role = Role.objects.get(id=rid)
        # check attributes of the saved role object
        self.assertEqual(role.role_name, name)
        self.assertEqual(role.role_contact, contact)
        self.assertEqual(role.role_facility, facility)
        return role


class AreaFormTest(FMFormTest):
    def test_form_has_all_required_inputs_and_text(self):
        form = AreaForm()
        form_html = form.as_p()
        fields = form.Meta.fields
        widgets = form.Meta.widgets

        self.assertIn('area_name', fields)
        self.assertEqual(widgets['area_name'].attrs['placeholder'],
                         'Enter a name')
        self.assertIn('placeholder="Enter a name"', form_html)
        self.assertIn('id="id_area_name"', form_html)

        self.assertIn('area_type', fields)
        self.assertIn('id="id_area_type"', form_html)

        for area_type in AREA_TYPES:
            self.assertIn(area_type[0], form_html)
            self.assertIn(area_type[1], form_html)

        self.assertIn('id="id_area_parent"', form_html)

    def test_form_validation_for_blank_items(self):
        form = AreaForm(data={'area_name': '', 'area_type': ''})
        self.assertFalse(form.is_valid())
        # todo: only test those which should not accept blanks

    def test_form_saves_area_objects_correctly(self):
        self.create_save_and_return_area('state area1', 'State', None, 0)
        self.create_save_and_return_area('state zone area2', 'State Zone', None,
                                         1)
        self.create_save_and_return_area('lga area3', 'LGA', None, 2)
        self.create_save_and_return_area('ward area4', 'Ward', None, 3)

    def test_child_added_correctly_on_setting_a_parent(self):
        area1 = self.create_save_and_return_area('area1', 'State', None, 0)
        area2 = self.create_save_and_return_area('area2', 'State', area1, 1)
        self.assertIn(area2, area1.area_children.all())


class FacilityFormTest(FMFormTest):
    def test_form_has_all_required_inputs_and_text(self):
        form = FacilityForm()
        form_html = form.as_p()
        fields = form.Meta.fields
        widgets = form.Meta.widgets

        self.assertIn('facility_name', fields)
        self.assertEqual(widgets['facility_name'].attrs['placeholder'],
                         'Enter a name')
        self.assertIn('placeholder="Enter a name"', form_html)
        self.assertIn('id="id_facility_name"', form_html)

        self.assertIn('facility_type', fields)
        self.assertIn('id="id_facility_type"', form_html)
        for facility_type in Facility.FACILITY_TYPES:
            self.assertIn(facility_type[0], form_html)
            self.assertIn(facility_type[1], form_html)

        self.assertIn('facility_status', fields)
        self.assertEqual(widgets['facility_status'].attrs['placeholder'],
                         'Enter a status')
        self.assertIn('placeholder="Enter a status"', form_html)
        self.assertIn('id="id_facility_status"', form_html)

        self.assertIn('facility_area', fields)
        self.assertIn('id="id_facility_area"', form_html)

    def test_form_validation_for_blank_items(self):
        form = FacilityForm(
            data={
                'facility_name': '',
                'facility_type': '',
                'facility_status': '',
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_saves_facilities_correctly(self):
        self.create_save_and_return_facility(
            'facility 1', 'State Store', 'status 1', None, 0)
        self.create_save_and_return_facility(
            'facility 2', 'Zonal Store', 'status 2', None, 1)
        self.create_save_and_return_facility(
            'facility 3', 'LGA Store', 'status 3', None, 2)
        self.create_save_and_return_facility(
            'facility 4', 'Health Facility', 'status 4', None, 3)

    def test_on_setting_an_area_the_facility_is_added_to_area_facilities(self):
        area = self.create_save_and_return_area('area1', 'State', None, 0)
        facility = self.create_save_and_return_facility(
            'facility 1', 'State Store', 'status 1', area, 0)
        self.assertIn(facility, area.area_facilities.all())


class ContactFormTest(FMFormTest):
    def test_form_has_all_required_inputs_and_text(self):
        form = ContactForm()
        form_html = form.as_p()
        fields = form.Meta.fields
        widgets = form.Meta.widgets

        self.assertIn('contact_name', fields)
        self.assertEqual(widgets['contact_name'].attrs['placeholder'],
                         'Enter a name')
        self.assertIn('placeholder="Enter a name"', form_html)
        self.assertIn('id="id_contact_name"', form_html)

        self.assertIn('contact_phone', fields)
        self.assertEqual(widgets['contact_phone'].attrs['placeholder'],
                         'Enter a phone number')
        self.assertIn('placeholder="Enter a phone number"', form_html)
        self.assertIn('id="id_contact_phone"', form_html)

        self.assertIn('contact_email', fields)
        self.assertEqual(widgets['contact_email'].attrs['placeholder'],
                         'Enter an e-mail')
        self.assertIn('placeholder="Enter an e-mail"', form_html)
        self.assertIn('id="id_contact_email"', form_html)

    def test_form_validation_for_blank_items(self):
        form = ContactForm(
            data={
                'contact_name': '',
                'contact_phone': '',
                'contact_email': '',
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_saves_contacts_correctly(self):
        self.create_save_and_return_contact('contact 1', '+1231', 'a1@b.cc', 0)
        self.create_save_and_return_contact('contact 2', '+1232', 'a2@b.cc', 1)
        self.create_save_and_return_contact('contact 3', '+1233', 'a3@b.cc', 2)
        self.create_save_and_return_contact('contact 4', '+1234', 'a4@b.cc', 3)


class RoleFormTest(FMFormTest):
    def test_form_has_all_required_inputs_and_text(self):
        form = RoleForm()
        form_html = form.as_p()
        fields = form.Meta.fields

        self.assertIn('role_name', fields)
        self.assertIn('id="id_role_name"', form_html)
        for role_name in Role.ROLE_NAMES:
            self.assertIn(role_name[0], form_html)
            self.assertIn(role_name[1], form_html)

        self.assertIn('role_contact', fields)
        self.assertIn('id="id_role_contact"', form_html)

        self.assertIn('role_facility', fields)
        self.assertIn('id="id_role_facility"', form_html)

    def test_form_validation_for_blank_items(self):
        form = RoleForm(
            data={
                'role_name': '',
                'role_contact': None,
                'role_facility': None,
            }
        )
        self.assertFalse(form.is_valid())

    def test_form_saves_roles_correctly(self):
        contact1 = self.create_save_and_return_contact(
            'contact1', '0333', 'a@b.cc', 0)
        facility1 = Facility.objects.create(facility_name='facility1')
        self.create_save_and_return_role(
            'SCCO', contact1, facility1, 0)
        self.create_save_and_return_role(
            'ZCCO', contact1, facility1, 1)
        self.create_save_and_return_role(
            'LGA CCO', contact1, facility1, 2)
        self.create_save_and_return_role(
            'LIO', contact1, facility1, 3)

    def test_on_setting_a_contact_the_role_is_added_to_contact_roles(self):
        contact = Contact.objects.create()
        facility = Facility.objects.create()
        role = self.create_save_and_return_role('WTO', contact, facility, 0)
        self.assertIn(role, contact.contact_roles.all())

    def test_on_setting_a_facility_the_role_is_added_to_facility_roles(self):
        contact = Contact.objects.create()
        facility = Facility.objects.create()
        role = self.create_save_and_return_role(
            'HFIC', contact, facility, 0)
        self.assertIn(role, facility.facility_roles.all())
