__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django import forms

from fm.models import Area, Facility, Contact, Role


class AreaForm(forms.ModelForm):
    class Meta:
        model = Area
        fields = ('area_name', 'area_type', 'area_parent',)
        widgets = {
            'area_name': forms.fields.TextInput(attrs={
                'placeholder': 'Enter a name', }),
        }


class FacilityForm(forms.ModelForm):
    class Meta:
        model = Facility
        fields = ('facility_name', 'facility_type', 'facility_status',
                  'facility_area',)
        widgets = {
            'facility_name': forms.fields.TextInput(
                attrs={'placeholder': 'Enter a name', }),
            'facility_status': forms.fields.TextInput(
                attrs={'placeholder': 'Enter a status', }),
        }


class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ('contact_name', 'contact_phone', 'contact_email',)
        widgets = {
            'contact_name': forms.fields.TextInput(
                attrs={'placeholder': 'Enter a name', }),
            'contact_phone': forms.fields.TextInput(
                attrs={'placeholder': 'Enter a phone number', }),
            'contact_email': forms.fields.EmailInput(
                attrs={'placeholder': 'Enter an e-mail', }),
        }


class RoleForm(forms.ModelForm):
    class Meta:
        model = Role
        fields = ('role_name', 'role_contact', 'role_facility')
