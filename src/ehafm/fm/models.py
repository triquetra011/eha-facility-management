__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

from django.db import models

from jsonfield import JSONField


AREA_TYPES = (
    ('State', 'State'),
    ('State Zone', 'State Zone'),
    ('LGA', 'LGA'),
    ('Ward', 'Ward'),
)


class Area(models.Model):
    area_name = models.TextField()
    area_type = models.CharField(max_length=32, choices=AREA_TYPES)
    area_parent = models.ForeignKey('self', related_name='area_children',
                                    default=None, null=True, blank=True,
                                    on_delete=models.SET_NULL)

    def __unicode__(self):
        return u'%s (%s%s)' % (self.area_name, self.area_type,
                               self._path(self._ancestry_chain()))

    def _ancestry_chain(self, chain=None):
        if chain is None:
            chain = []

        if len(chain) > len(AREA_TYPES) or self.area_parent is None:
            return chain
        else:
            chain.insert(0, self.area_parent)
            chain = self.area_parent._ancestry_chain(chain)
            return chain

    @staticmethod
    def _path(chain):
        if len(chain):
            chain.reverse()
            chain = [a.area_name for a in chain]
            return u' in ' + u' in '.join(chain)
        else:
            return u''


class Facility(models.Model):
    FACILITY_TYPES = (
        ('State Store',) * 2,
        ('Zonal Store',) * 2,
        ('LGA Store',) * 2,
        ('Health Facility',) * 2,
    )

    facility_name = models.TextField()
    facility_type = models.CharField(max_length=32, choices=FACILITY_TYPES)
    facility_status = models.TextField()
    facility_area = models.ForeignKey(Area, related_name='area_facilities',
                                      default=None, null=True, blank=True,
                                      on_delete=models.SET_NULL)
    # Set help_text to something else than empty but still invisible so that
    # the JSONField does not set it to its custom default (we want nothing
    # displayed).
    json = JSONField(null=True, blank=True, help_text=' ')

    def __unicode__(self):
        name = str(self.facility_name)
        if self.facility_status:
            status = u' [%s]' % self.facility_status
        else:
            status = u''
        if self.facility_area is None:
            area = u''
        else:
            area = u' in %s' % unicode(self.facility_area)
        return u'%s%s%s' % (name, status, area)


class Contact(models.Model):
    contact_name = models.TextField()
    contact_phone = models.CharField(max_length=32)
    contact_email = models.EmailField()
    # Set help_text to something else than empty but still invisible so that
    # the JSONField does not set it to its custom default (we want nothing
    # displayed).
    json = JSONField(null=True, blank=True, help_text=' ')

    def __unicode__(self):
        if self.contact_email:
            email = u' <%s>' % self.contact_email
        else:
            email = u''
        return unicode(self.contact_name + email)


class Role(models.Model):
    ROLE_NAMES = (
        ('SCCO',) * 2,
        ('ZCCO',) * 2,
        ('LGA CCO',) * 2,
        ('LIO',) * 2,
        ('WTO',) * 2,
        ('HFIC',) * 2,
    )

    role_name = models.CharField(max_length=64, choices=ROLE_NAMES)
    role_contact = models.ForeignKey(Contact, related_name='contact_roles',
                                     default=None, null=True, blank=False)
    role_facility = models.ForeignKey(Facility, related_name='facility_roles',
                                     default=None, null=True, blank=False)

    def __unicode__(self):
        if self.role_facility is None:
            facility = u''
        else:
            facility = u' @ %s' % unicode(self.role_facility)
        return u'%s%s' % (self.role_name, facility)
