__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django.test import TestCase

from fm.models import Area
from fm.models import Facility
from fm.models import Contact
from fm.models import Role


class AreaModelTest(TestCase):
    def test_default_field_values(self):
        area = Area.objects.create()
        self.assertEqual(area.area_name, '')

    def test_parent_set_correctly_on_adding_a_child(self):
        area1 = Area.objects.create()
        area2 = Area.objects.create()
        area2.area_children.add(area1)
        area1 = Area.objects.get(id=area1.id)
        area2 = Area.objects.get(id=area2.id)
        self.assertEqual(area1.area_parent.id, area2.id)
        self.assertIn(area1, area2.area_children.all())

    def test_child_added_correctly_on_setting_a_parent(self):
        area1 = Area.objects.create()
        area2 = Area.objects.create()
        area1.area_parent = area2
        area1.save()
        area2 = Area.objects.get(id=area2.id)
        area1 = Area.objects.get(id=area1.id)
        self.assertEqual(area1.area_parent.id, area2.id)
        self.assertIn(area1, area2.area_children.all())

    def test_by_default_area_string_contains_its_name_zone_type_and_path(self):
        area0 = Area.objects.create(area_name='Area 0', area_type='State')
        area1 = Area.objects.create(area_name='Area 1', area_type='State Zone',
                                    area_parent=area0)
        area2 = Area.objects.create(area_name='Area 2', area_type='LGA',
                                    area_parent=area1)
        self.assertEqual(u'Area 2 (LGA in Area 1 in Area 0)',
                         area2.__unicode__())
        self.assertEqual('Area 2 (LGA in Area 1 in Area 0)', area2.__str__())

    def test_child_preserved_and_its_parent_set_to_null_on_parent_delete(self):
        area1 = Area.objects.create(area_name='1')
        area2 = Area.objects.create(area_name='2')
        area1.area_children.add(area2)
        area1 = Area.objects.get(id=area1.id)
        area2 = Area.objects.get(id=area2.id)
        area1.delete()
        area2 = Area.objects.get(id=area2.id)
        self.assertIsNone(area2.area_parent)
        self.assertNotIn(area1, Area.objects.all())
        self.assertIn(area2, Area.objects.all())

    def test_parent_preserved_and_the_deleted_child_not_in_children(self):
        area1 = Area.objects.create(area_name='1')
        area2 = Area.objects.create(area_name='2')
        area1.area_children.add(area2)
        area1 = Area.objects.get(id=area1.id)
        area2 = Area.objects.get(id=area2.id)
        area2.delete()
        area1 = Area.objects.get(id=area1.id)
        self.assertNotIn(area2, Area.objects.all())
        self.assertIn(area1, Area.objects.all())
        self.assertEqual(0, area1.area_children.count())


class FacilityModelTest(TestCase):
    def test_default_field_values(self):
        facility = Facility.objects.create()
        self.assertEqual(facility.facility_name, '')
        self.assertEqual(facility.facility_status, '')
        self.assertEqual(facility.facility_area, None)
        self.assertEqual(facility.json, None)

    def test_area_set_correctly_on_adding_a_facility_to_an_area(self):
        facility = Facility.objects.create()
        area = Area.objects.create()
        area.area_facilities.add(facility)
        facility = Facility.objects.get(id=facility.id)
        area = Area.objects.get(id=area.id)
        self.assertEqual(facility.facility_area.id, area.id)
        self.assertIn(facility, area.area_facilities.all())

    def test_child_added_correctly_on_setting_a_parent(self):
        facility = Facility.objects.create()
        area = Area.objects.create()
        facility.facility_area = area
        facility.save()
        area = Area.objects.get(id=area.id)
        facility = Facility.objects.get(id=facility.id)
        self.assertEqual(facility.facility_area.id, area.id)
        self.assertIn(facility, area.area_facilities.all())

    def test_by_default_facility_string_contains_its_name_status_and_area(self):
        area = Area.objects.create(
            area_name='Area 51', area_type='State Zone')
        facility = Facility.objects.create(facility_name='Facility 0',
                                           facility_status='some status',
                                           facility_area=area)
        self.assertEqual(u'Facility 0 [some status] in Area 51 (State Zone)',
                         facility.__unicode__())
        self.assertEqual('Facility 0 [some status] in Area 51 (State Zone)',
                         facility.__str__())

    def test_facility_preserved_and_its_area_set_to_null_on_area_delete(self):
        area = Area.objects.create()
        facility = Facility.objects.create()
        area.area_facilities.add(facility)
        area = Area.objects.get(id=area.id)
        facility = Facility.objects.get(id=facility.id)
        area.delete()
        facility = Facility.objects.get(id=facility.id)
        self.assertIsNone(facility.facility_area)
        self.assertNotIn(area, Area.objects.all())
        self.assertIn(facility, Facility.objects.all())

    def test_area_preserved_and_the_deleted_facility_not_in_facilities(self):
        area = Area.objects.create()
        facility = Facility.objects.create()
        area.area_facilities.add(facility)
        area = Facility.objects.get(id=area.id)
        facility = Facility.objects.get(id=facility.id)
        facility.delete()
        area = Area.objects.get(id=area.id)
        self.assertNotIn(facility, Facility.objects.all())
        self.assertIn(area, Area.objects.all())
        self.assertEqual(0, area.area_facilities.count())


class ContactModelTest(TestCase):
    def test_default_field_values(self):
        contact = Contact.objects.create()
        self.assertEqual(contact.contact_name, '')
        self.assertEqual(contact.contact_phone, '')
        self.assertEqual(contact.contact_email, '')
        self.assertEqual(contact.json, None)

    def test_by_default_contact_string_contains_its_name(self):
        contact = Contact.objects.create(contact_name='Contact 0',
                                         contact_phone='055555',
                                         contact_email='a@b.cc')
        self.assertEqual(u'Contact 0 <a@b.cc>', contact.__unicode__())
        self.assertEqual('Contact 0 <a@b.cc>', contact.__str__())


class RoleModelTest(TestCase):
    def test_default_field_values(self):
        role = Role.objects.create()
        self.assertEqual(role.role_name, '')
        self.assertEqual(role.role_contact, None)
        self.assertEqual(role.role_facility, None)

    def test_role_and_contact_association_bidirectional_from_contact(self):
        role = Role.objects.create()
        contact = Contact.objects.create()
        contact.contact_roles.add(role)
        role = Role.objects.get(id=role.id)
        contact = Contact.objects.get(id=contact.id)
        self.assertEqual(role.role_contact.id, contact.id)
        self.assertIn(role, contact.contact_roles.all())

    def test_role_and_contact_association_bidirectional_from_role(self):
        role = Role.objects.create()
        contact = Contact.objects.create()
        role.role_contact = contact
        role.save()
        contact = Contact.objects.get(id=contact.id)
        role = Role.objects.get(id=role.id)
        self.assertEqual(role.role_contact.id, contact.id)
        self.assertIn(role, contact.contact_roles.all())

    def test_by_default_role_string_contains_its_name_and_facility_name(self):
        contact = Contact.objects.create(contact_name='contact 1')
        facility = Facility.objects.create(
            facility_name='Hyperion', facility_type='Zonal Store',
            facility_status='status1')
        role = Role.objects.create(role_name='SCCO',
                                   role_contact=contact,
                                   role_facility=facility)
        self.assertEqual(u'SCCO @ Hyperion [status1]',
                         role.__unicode__())
        self.assertEqual('SCCO @ Hyperion [status1]',
                         role.__str__())

    def test_role_deleted_on_contact_delete(self):
        contact = Contact.objects.create()
        role = Role.objects.create()
        contact.contact_roles.add(role)
        contact = Contact.objects.get(id=contact.id)
        role = Role.objects.get(id=role.id)
        self.assertIn(role, contact.contact_roles.all())
        contact.delete()
        self.assertNotIn(contact, Contact.objects.all())
        self.assertNotIn(role, Role.objects.all())

    def test_role_deleted_on_facility_delete(self):
        facility = Facility.objects.create()
        role = Role.objects.create()
        facility.facility_roles.add(role)
        facility = Facility.objects.get(id=facility.id)
        role = Role.objects.get(id=role.id)
        self.assertIn(role, facility.facility_roles.all())
        facility.delete()
        self.assertNotIn(facility, Facility.objects.all())
        self.assertNotIn(role, Role.objects.all())

    def test_contacts_and_facilities_kept_clean_upon_role_deletion(self):
        contact = Contact.objects.create()
        facility = Facility.objects.create()
        role = Role.objects.create()
        contact.contact_roles.add(role)
        facility.facility_roles.add(role)
        role = Role.objects.get(id=role.id)
        self.assertIn(role, contact.contact_roles.all())
        self.assertIn(role, facility.facility_roles.all())
        role.delete()
        self.assertNotIn(role, Role.objects.all())
        self.assertIn(contact, Contact.objects.all())
        self.assertIn(facility, Facility.objects.all())
        contact = Contact.objects.get(id=contact.id)
        facility = Facility.objects.get(id=facility.id)
        self.assertNotIn(role, contact.contact_roles.all())
        self.assertNotIn(role, facility.facility_roles.all())
