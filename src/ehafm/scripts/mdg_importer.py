__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

# To use, just edit the ehafm_url (below) and run without arguments.  Enter the
# username and password when prompted.

import os
import urllib
import urlparse
import json
import re
import codecs

from pyvirtualdisplay import Display

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# URL to the main page of the Facilities Management system (i.e. the target
# system we want to import the data into)
ehafm_url = 'http://127.0.0.1:8000/fm/'  # EDIT THIS!

# URL to get the data from
mdg_url = 'http://54.204.39.128/static/lgas/'

mdg_download_dir = 'mdg_download'

# A list of names of all LGAs in Kano
kano_lga_names = [
    'Ajingi',
    'Albasu',
    'Bagwai',
    'Bebeji',
    'Bichi',
    'Bunkure',
    'Dala',
    'Dambatta',
    'Dawakin-Kudu',
    'Dawakin-Tofa',
    'Doguwa',
    'Fagge',
    'Gabasawa',
    'Garko',
    'Garun Mallam',
    'Gaya',
    'Gazewa',
    'Gwale',
    'Gwarzo',
    'Kabo',
    'Kano-Municipal',
    'Karaye',
    'Kibiya',
    'Kiru',
    'Kumbotso',
    'Kunchi',
    'Kura',
    'Madobi',
    'Makoda',
    'Minjibir',
    'Nassarawa',
    'Rano',
    'Rimin Gado',
    'Rogo',
    'Shanono',
    'Sumaila',
    'Takai',
    'Tarauni',
    'Tofa',
    'Tsanyawa',
    'Tudun-Wada',
    'Ungogo',
    'Warawa',
    'Wudil',
]


def reformat_name(name):
    reformatted = name.replace('.', ' ').strip().title()
    reformatted = re.sub(r' {2,}', r' ', reformatted)
    return reformatted


def load_mdg_data():
    # prepare a data structure to be returned
    imported_data = {
        'areas': {
            'states': dict(),
            'lgas': dict(),
            'wards': dict(),
        },
        'facilities': set(),
    }

    # make a directory for the downloaded JSON documents (if it does not exist)
    if not os.path.exists(mdg_download_dir):
        os.mkdir(mdg_download_dir)

    # add Kano area (type: State)
    kano = Area('Kano', 'State')
    imported_data['areas']['states'][unicode(kano)] = kano

    # for each of the LGA names
    for lga_name in kano_lga_names:
        # add a new area of type LGA as a subarea of Kano
        lga = Area(lga_name, 'LGA', kano)
        imported_data['areas']['lgas'][unicode(lga)] = lga
        # if the LGA JSON document not in the download directory: download
        # json document names on mdg replace all spaces and - with underscores
        json_doc_name = '%s_%s.json' % (
            kano.name.lower(), lga.name.lower().replace(' ', '_').replace('-',
                                                                          '_')
        )
        json_doc_path = os.path.join(mdg_download_dir, json_doc_name)
        if not os.path.exists(json_doc_path):
            json_url = urlparse.urljoin(mdg_url, json_doc_name)
            print json_url
            urllib.urlretrieve(json_url, json_doc_path)
        # load downloaded JSON
        json_doc = json.load(codecs.open(json_doc_path, encoding='utf-8'))
        # for each of the health facilities in the downloaded JSON document for
        # the LGA: if the ward does not exist add it
        json_facilities = json_doc['facilities']
        for jf in json_facilities:
            if jf['sector'] != 'health':
                continue
            ward_name = reformat_name(jf['ward'])
            if 'unicode' not in str(type(ward_name)):
                print type(ward_name)
                exit('Not unicode!')
            ward = Area(ward_name, 'Ward', lga)
            if unicode(ward) not in imported_data['areas']['wards']:
                imported_data['areas']['wards'][unicode(ward)] = ward
            else:
                ward = imported_data['areas']['wards'][unicode(ward)]
            # create a facility object
            # set its facility type to 'Health Facility'
            # store the whole JSON record for this LGA in the "mdg" attribute
            # of the JSON field

            # set the area attribute to the just created Ward area object (if
            # it has been created), otherwise set it to Kano

            # set the name attribute of the facility object to the value stored
            # in "facility_name" (raise exception if no filled in facility_name
            # present)
            facility_name = jf['facility_name']
            facility = Facility(facility_name, ward, json.dumps(jf),
                                facility_type='Health Facility')
            imported_data['facilities'].add(facility)
    return imported_data


class EHAFMWebImporter(object):
    def __init__(self, url):
        self.url = url
        self.logged_in = False
        if os.environ.get('DISPLAY'):
            self.display = None
        else:
            self.display = Display(visible=0, size=(800, 600))
            self.display.start()
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.wait = WebDriverWait(self.browser, 30)

    def __del__(self):
        self.browser.quit()
        if self.display:
            self.display.stop()

    def log_user_in(self, username, password):
        self.browser.get(self.url)
        self.wait.until(EC.title_contains('Log in'))
        login_box = self.wait.until(
            EC.presence_of_element_located((By.ID, 'id_username')))
        login_box.send_keys(username)
        password_box = self.wait.until(
            EC.presence_of_element_located((By.ID, 'id_password')))
        password_box.send_keys(password)
        password_box.send_keys(Keys.ENTER)
        self.wait.until(EC.title_contains('Facility Management'))
        self.logged_in = True

    def go_to_a_sub_page_of_the_fm_home_page(self, link_id):
        self.browser.get(self.url)

        link = self.wait.until(EC.presence_of_element_located((By.ID, link_id)))
        link.click()

    def go_to_areas(self):
        self.go_to_a_sub_page_of_the_fm_home_page('id_areas_link')
        self.wait.until(EC.title_is('Areas'))

    def area_not_found_on_the_server(self, area):
        self.browser.get(self.url)
        self.go_to_areas()
        # escape the fully qualified area name as it contains parentheses
        matched = re.search(r'<td>' + re.escape(unicode(area)) + r'</td>',
                            self.browser.page_source, re.MULTILINE)
        return not bool(matched)

    def add_a_new_area(self, area):
        self.go_to_areas()
        self.wait.until(EC.title_is('Areas'))
        link = self.wait.until(EC.presence_of_element_located(
            (By.ID, 'id_add_new_area_link')))
        link.click()
        self.wait.until(EC.title_is('Add New Area'))
        inputbox = self.wait.until(
            EC.presence_of_element_located((By.ID, 'id_area_name')))
        inputbox.send_keys(area.name)
        self.browser.find_element_by_xpath(
            '//select[@id="id_area_type"]/option[text()="%s"]' % area.type
        ).click()
        # He selects the parent area
        if area.parent:
            select = Select(self.browser.find_element_by_id('id_area_parent'))
            select.select_by_visible_text(unicode(area.parent))
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        self.wait.until(EC.title_is('Areas'))

    def go_to_facilities(self):
        self.go_to_a_sub_page_of_the_fm_home_page('id_facilities_link')
        self.wait.until(EC.title_is('Facilities'))

    def facility_not_found_on_the_server(self, facility):
        self.browser.get(self.url)
        self.go_to_facilities()
        pattern = r'<td>%s</td>[\s]*' * 4
        # escape facility attribute names to make sure the pattern is valid
        pattern = pattern % (re.escape(facility.name),
                             re.escape(facility.type),
                             re.escape(facility.status),
                             re.escape(unicode(facility.area)))
        matched = re.search(pattern, self.browser.page_source, re.MULTILINE)
        return not bool(matched)

    def add_a_new_facility(self, facility):
        self.go_to_facilities()
        self.wait.until(EC.title_is('Facilities'))
        link = self.wait.until(EC.presence_of_element_located(
            (By.ID, 'id_add_new_facility_link')))
        link.click()
        self.wait.until(EC.title_is('Add New Facility'))
        inputbox = self.wait.until(
            EC.presence_of_element_located((By.ID, 'id_facility_name')))
        inputbox.send_keys(facility.name)
        self.browser.find_element_by_xpath(
            '//select[@id="id_facility_type"]/option[text()="%s"]' %
            facility.type).click()
        inputbox = self.wait.until(
            EC.presence_of_element_located((By.ID, 'id_facility_status')))
        inputbox.send_keys(facility.status)
        if facility.area:
            select = Select(self.browser.find_element_by_id('id_facility_area'))
            select.select_by_visible_text(unicode(facility.area))
        if facility.json:
            inputbox = self.wait.until(
                EC.presence_of_element_located((By.ID, 'id_json')))
            inputbox.send_keys(facility.json)

        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        self.wait.until(EC.title_is('Facilities'))


class Area(object):
    AREA_TYPES = (
        ('State',) * 2,
        ('State Zone',) * 2,
        ('LGA',) * 2,
        ('Ward',) * 2,
    )

    def __init__(self, name, area_type, parent=None):
        self.name = reformat_name(name)
        self.type = area_type
        self.parent = parent

    def add_to_ehafm(self, web_importer):
        web_importer.add_a_new_area(self)

    def __unicode__(self):
        return u'%s (%s%s)' % (self.name, self.type,
                               self._path(self._ancestry_chain()))

    def _ancestry_chain(self, chain=None):
        if chain is None:
            chain = []

        if len(chain) > len(self.AREA_TYPES) or self.parent is None:
            return chain
        else:
            chain.insert(0, self.parent)
            chain = self.parent._ancestry_chain(chain)
            return chain

    @staticmethod
    def _path(chain):
        if len(chain):
            chain.reverse()
            chain = [a.name for a in chain]
            return u' in ' + u' in '.join(chain)
        else:
            return u''


class Facility(object):
    def __init__(self, name, area, json,
                 status='unknown status; data imported from MDG',
                 facility_type='Health Facility'):
        self.name = reformat_name(name)
        self.area = area
        self.json = json
        self.status = status
        self.type = facility_type

    def add_to_ehafm(self, web_importer):
        web_importer.add_a_new_facility(self)

    def __unicode__(self):
        name = self.name
        if self.status:
            status = u' [%s]' % self.status
        else:
            status = u''
        if self.area is None:
            area = u''
        else:
            area = u' in %s' % unicode(self.area)
        return u'%s%s%s' % (name, status, area)


def add_areas_to_ehafm(imported_data, web_importer):
    i = 0
    already_present = []
    for area_type in ['states', 'lgas', 'wards']:
        for area in imported_data['areas'][area_type].values():
            print 'adding area: %s (%s)' % (area.name, area_type)
            if web_importer.area_not_found_on_the_server(area):
                area.add_to_ehafm(web_importer)
                i += 1
            else:
                print '\tarea %s already present on the server' % area.name
                already_present.append(area)
    print '%d imported (%d not added but detected on the server)' % (
        i, len(already_present))
    print 'Already present:'
    for area in already_present:
        print unicode(area)
    print 'Finished with areas.\n\n'


def add_facilities_to_ehafm(imported_data, web_importer):
    i = 0
    already_present = []
    for facility in imported_data['facilities']:
        print 'adding facility: %s' % (unicode(facility))
        if web_importer.facility_not_found_on_the_server(facility):
            facility.add_to_ehafm(web_importer)
            i += 1
        else:
            print '\tfacility already present on the server'
            already_present.append(facility)
    print '%d imported (%d not added but detected on the server)' % (
        i, len(already_present))
    print 'Already present:'
    for facility in already_present:
        print unicode(facility)
    print 'Finished with facilities.\n\n'


def save_facilities_to_a_file(imported_data,
                              file_name='facilities.txt', encoding='utf-8'):
    printout = []
    for f in imported_data['facilities']:
        printout.append(unicode(f))
    with codecs.open(file_name, encoding=encoding, mode='w') as f:
        f.writelines(u'\n'.join(printout))


def main():
    print '(Down)loading MDG data...'
    imported_data = load_mdg_data()
    print 'Please enter credentials for your EHAFM site below.'
    username = raw_input('Username: ')
    password = raw_input('Password: ')
    web_importer = EHAFMWebImporter(ehafm_url)
    web_importer.log_user_in(username, password)
    # for each area object in imported_data:  add it to ehafm
    add_areas_to_ehafm(imported_data, web_importer)
    # for each facility object in imported_data: add it to ehafm
    add_facilities_to_ehafm(imported_data, web_importer)


if __name__ == '__main__':
    main()
