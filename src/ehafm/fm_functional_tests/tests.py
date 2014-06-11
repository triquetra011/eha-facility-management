__author__ = 'Tomasz J. Kotarba <tomasz@kotarba.net>'
__copyright__ = 'Copyright (c) 2014, Tomasz J. Kotarba. All rights reserved.'

import time

from django.test import LiveServerTestCase

from pyvirtualdisplay import Display
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.select import Select


class AdminAndNonAdminVisitorTest(LiveServerTestCase):
    fixtures = ['users.json', 'contact.json', 'facility.json']

    @classmethod
    def setUpClass(cls):
        cls.display = Display(visible=0, size=(800, 600))
        cls.display.start()
        super(AdminAndNonAdminVisitorTest, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        cls.display.stop()
        super(AdminAndNonAdminVisitorTest, cls).tearDownClass()

    def setUp(self):
        self.browser = webdriver.Firefox()
        self.browser.implicitly_wait(3)
        self.fm_url = self.live_server_url + '/fm/'
        self.logout_url = self.live_server_url + '/logout'

    def tearDown(self):
        self.browser.quit()

    def log_user_in(self, username, password):
        self.browser.get(self.fm_url)
        inputbox = self.browser.find_element_by_id('id_username')
        inputbox.send_keys(username)
        # inputbox.send_keys(Keys.ENTER)
        inputbox = self.browser.find_element_by_id('id_password')
        inputbox.send_keys(password)
        inputbox.send_keys(Keys.ENTER)
        time.sleep(1)  # # wait a second for the page to reload

    def log_current_user_out(self):
        self.browser.get(self.logout_url)
        self.assertIn('Logged out', self.browser.title)

    def log_admin_in(self):
        self.log_user_in('admin', 'adminpassword')

    def follow_link(self, link):
        page_source = self.browser.page_source
        page_url = self.browser.current_url
        link.click()
        self.assertNotEqual(
            page_source, self.browser.page_source,
            'Page source does not change after clicking the link')
        self.assertNotEqual(
            page_url, self.browser.current_url,
            'Clicking the link has not changed the current URL')

    def check_for_row_in_a_table(self, strings_in_one_row, table_id):
        table = self.browser.find_element_by_id(table_id)
        rows = table.find_elements_by_tag_name('tr')
        matched = False
        number_of_strings = len(strings_in_one_row)
        for row in rows:
            for i in xrange(number_of_strings):
                if strings_in_one_row[i] not in row.text:
                    break
                elif i == number_of_strings - 1:
                    matched = True
            if matched:
                break
        self.assertTrue(
            matched,
            'No row containing all the required text found in table %s' %
            table_id)

    def current_user_goes_to_a_sub_page_of_the_fm_home_page(
            self, link_id, text_in_title_and_header):
        self.browser.get(self.fm_url)
        link = self.browser.find_element_by_id(link_id)
        self.follow_link(link)

        # The link takes the admin to a page with title and header mentioning
        # text_in_title_and_header
        self.assertIn(text_in_title_and_header, self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn(text_in_title_and_header, header.text)

    def current_user_goes_to_areas(self):
        self.current_user_goes_to_a_sub_page_of_the_fm_home_page(
            'id_areas_link', 'Areas')

    def current_user_goes_to_facilities(self):
        self.current_user_goes_to_a_sub_page_of_the_fm_home_page(
            'id_facilities_link', 'Facilities')

    def current_user_goes_to_contacts(self):
        self.current_user_goes_to_a_sub_page_of_the_fm_home_page(
            'id_contacts_link', 'Contacts')

    def current_user_goes_to_roles(self):
        self.current_user_goes_to_a_sub_page_of_the_fm_home_page(
            'id_roles_link', 'Roles')

    def current_user_adds_new_area(
            self, area_name, area_type, area_parent=None
    ):
        self.current_user_goes_to_areas()
        link = self.browser.find_element_by_id('id_add_new_area_link')
        self.follow_link(link)
        inputbox = self.browser.find_element_by_id('id_area_name')
        inputbox.send_keys(area_name)
        self.browser.find_element_by_xpath(
            '//select[@id="id_area_type"]/option[text()="%s"]' % area_type
        ).click()
        # He selects the parent area
        if area_parent:
            select = Select(self.browser.find_element_by_id('id_area_parent'))
            select.select_by_visible_text(str(area_parent))
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        ## wait a second for the browser to reload
        time.sleep(1)
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Areas', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Areas', header.text)
        self.check_for_row_in_a_table([area_name, area_type], 'id_areas_table')

    def test_only_admin_can_access_the_new_facility_management_home_page(self):
        # Jane heard about the new facility management app and goes to check out
        # its home page anonymously.  She quickly learns that anonymous users
        # apparently do not have permission to access the new app home page as
        # she is asked to log in.
        self.browser.get(self.fm_url)
        self.assertNotIn('Facility Management', self.browser.title)
        self.assertIn('Log in', self.browser.title)
        # Jane logs in but sees that she does not have permission to access the
        # page with her regular account.
        self.log_user_in('jane', 'janepassword')
        self.assertNotIn('Facility Management', self.browser.title)
        self.assertIn('Log in', self.browser.title)
        # She knows her friend Zygmunt has a superuser account so she asks him
        # to check out the new app and logs out.
        self.browser.get(self.logout_url)
        self.assertIn('Logged out', self.browser.title)
        # Zygmunt goes to the website, logs in with his superuser account and
        # notices that the page title and header mention facility management.
        self.log_admin_in()
        self.browser.get(self.fm_url)
        self.assertNotIn('Log in', self.browser.title)
        self.assertIn('Facility Management', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Facility Management', header.text)

    def test_admin_can_add_and_delete_areas(self):
        # Zygmunt the Admin visits the app home page and follows the link for
        # managing areas
        self.log_admin_in()
        self.browser.get(self.fm_url)
        link = self.browser.find_element_by_id('id_areas_link')
        self.follow_link(link)

        # The link takes him to a page with title and header mentioning areas
        self.assertIn('Areas', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Areas', header.text)

        # He clicks on a link allowing him to add new areas and it takes him
        # to a page for adding new areas
        link = self.browser.find_element_by_id('id_add_new_area_link')
        self.follow_link(link)
        # He sees a page with a form. He decides to fill in all the input boxes.
        # He starts with the area name
        inputbox = self.browser.find_element_by_id('id_area_name')
        inputbox.send_keys('Krakow')
        # He presses enter and is being told that he must fill in all the
        # required fields before saving.
        inputbox.send_keys(Keys.ENTER)
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Areas', self.browser.title)
        # He tries to submit the form as is by pressing the save button but he
        # is again asked to fill in all the required fields
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        time.sleep(1)
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Areas', self.browser.title)

        # He fills in the area type field
        self.browser.find_element_by_xpath(
            '//select[@id="id_area_type"]/option[text()="State Zone"]').click()
        # select = Select(self.browser.find_element_by_id('id_area_type'))
        # select.select_by_visible_text('State Zone')
        # Upon pressing submit he is redirected to Areas and can see his new
        # area on the list.
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        # # wait a second for the browser to reload
        time.sleep(1)
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Areas', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Areas', header.text)
        self.check_for_row_in_a_table(['Krakow', 'State Zone'],
                                      'id_areas_table')
        # He goes to add another area this time of type LGA and contained in the
        # previously added area.
        link = self.browser.find_element_by_id('id_add_new_area_link')
        self.follow_link(link)
        inputbox = self.browser.find_element_by_id('id_area_name')
        inputbox.send_keys('Barcelona')
        self.browser.find_element_by_xpath(
            '//select[@id="id_area_type"]/option[text()="LGA"]').click()
        # He selects the parent area
        # self.browser.find_element_by_xpath(
        #     '//select[@id="id_parent_area"]/option[text()="Krakow"]').click()
        select = Select(self.browser.find_element_by_id('id_area_parent'))
        select.select_by_visible_text('Krakow (State Zone)')
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        ## wait a second for the browser to reload
        time.sleep(1)
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Areas', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Areas', header.text)
        self.check_for_row_in_a_table(['Barcelona', 'LGA'], 'id_areas_table')

        # He decides to see if the area appeared on the children list of the
        # parent object todo:

        # He goes to the admin site and deletes Krakow
        ## todo: refactor if native delete added
        self.browser.get(self.live_server_url + '/admin/fm/area/1/delete/')
        input_widget = self.browser.find_element_by_tag_name('form')
        input_widget.submit()

        # He returns to the list of areas
        self.browser.get(self.fm_url + 'areas/')

        # Barcelona, which was the subarea of Krakow, is still on the list
        self.check_for_row_in_a_table(['Barcelona', 'LGA'], 'id_areas_table')

        # Krakow is no longer shown and Barcelona does not display Krakow as
        # its parent
        self.assertNotIn('Krakow', self.browser.page_source)

    def test_admin_can_add_and_delete_facilities(self):
        # Zygmunt the Admin visits the app home page and follows the link for
        # managing facilities
        self.log_admin_in()
        self.browser.get(self.fm_url)
        link = self.browser.find_element_by_id('id_facilities_link')
        self.follow_link(link)

        # The link takes him to a page with title and header mentioning
        # facilities
        self.assertIn('Facilities', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Facilities', header.text)

        # He clicks on a link allowing him to add new facilities and it takes
        # him to a page for adding new facilities
        link = self.browser.find_element_by_id('id_add_new_facility_link')
        self.follow_link(link)
        # He sees a page with a form. He decides to fill in all the input boxes.
        # He starts with the facility name
        inputbox = self.browser.find_element_by_id('id_facility_name')
        inputbox.send_keys('My Favourite Facility')
        # He presses enter and is being told that he must fill in all the
        # required fields before saving.
        inputbox.send_keys(Keys.ENTER)
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Facilities', self.browser.title)
        # He selects the correct facility type
        select = Select(self.browser.find_element_by_id('id_facility_type'))
        select.select_by_visible_text('Zonal Store')
        # He tries to submit the form as is by pressing the save button but he
        # is again asked to fill in all the required fields
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Facilities', self.browser.title)

        # He fills in the last required field - facility status
        time.sleep(1)  # # wait a second for the browser to reload
        inputbox = self.browser.find_element_by_id('id_facility_status')
        inputbox.send_keys('Beautiful')
        # Upon pressing submit he is redirected to Facilities and can see his
        # new facility on the list.
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        time.sleep(1)  # # wait a second for the browser to reload
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Facilities', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Facilities', header.text)
        self.check_for_row_in_a_table(
            ['My Favourite Facility', 'Beautiful', 'Zonal Store'],
            'id_facilities_table')

        # He goes to add another facility this time with a different status and
        # an area where the facility is located...
        # But first he must add the area as there are no areas defined
        self.current_user_adds_new_area('Helsinki', 'Ward')
        # He gets back to Facilities and clicks the link to add a new one
        self.current_user_goes_to_facilities()
        link = self.browser.find_element_by_id('id_add_new_facility_link')
        self.follow_link(link)
        inputbox = self.browser.find_element_by_id('id_facility_name')
        inputbox.send_keys('Not Bad Either')
        select = Select(self.browser.find_element_by_id('id_facility_type'))
        select.select_by_visible_text('Health Facility')
        inputbox = self.browser.find_element_by_id('id_facility_status')
        inputbox.send_keys('Pretty')
        # This time he selects the area where the facility is based
        select = Select(self.browser.find_element_by_id('id_facility_area'))
        select.select_by_visible_text('Helsinki (Ward)')
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        ## wait a second for the browser to reload
        time.sleep(1)
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Facilities', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Facilities', header.text)
        self.check_for_row_in_a_table(
            [
                'Not Bad Either',
                'Health Facility',
                'Pretty',
                'Helsinki'
            ],
            'id_facilities_table')

        # He decides to see if the facility appeared on the facilities list of
        # the parent area todo:

        # He goes to the admin site and deletes the parent area
        ## todo: refactor if native delete added
        self.browser.get(self.live_server_url + '/admin/fm/area/1/delete/')
        input_widget = self.browser.find_element_by_tag_name('form')
        input_widget.submit()

        # He returns to the list of facilities
        self.current_user_goes_to_facilities()

        # The facility added to the now deleted area is still on the list
        self.check_for_row_in_a_table(['Not Bad Either', 'Pretty'],
                                      'id_facilities_table')

        # Helsinki is not shown anywhere on the page
        self.assertNotIn('Helsinki', self.browser.page_source)

    def test_admin_can_add_and_delete_contacts(self):
        # Zygmunt the Admin visits the app home page and follows the link for
        # managing contacts
        self.log_admin_in()
        self.browser.get(self.fm_url)
        link = self.browser.find_element_by_id('id_contacts_link')
        self.follow_link(link)

        # The link takes him to a page with title and header mentioning
        # contacts
        self.assertIn('Contacts', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Contacts', header.text)

        # He clicks on a link allowing him to add new contacts and it takes
        # him to a page for adding new contacts
        link = self.browser.find_element_by_id('id_add_new_contact_link')
        self.follow_link(link)
        # He sees a page with a form. He decides to fill in all the input boxes.
        # He starts with the contact name
        inputbox = self.browser.find_element_by_id('id_contact_name')
        inputbox.send_keys('Zygmunt the Admin')
        # He presses enter and is being told that he must fill in all the
        # required fields before saving.
        inputbox.send_keys(Keys.ENTER)
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Contacts', self.browser.title)
        # He tries to submit the form as is by pressing the save button but he
        # is again asked to fill in all the required fields
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        time.sleep(1)
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Contacts', self.browser.title)

        # He fills in the last two required fields
        time.sleep(1)  # # wait a second for the browser to reload
        inputbox = self.browser.find_element_by_id('id_contact_phone')
        inputbox.send_keys('+44 7890 123 432')
        inputbox = self.browser.find_element_by_id('id_contact_email')
        inputbox.send_keys('zygmunt@fm.zyg')
        # Upon pressing submit he is redirected to Contacts and can see his
        # new contact on the list.
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        time.sleep(1)  # # wait a second for the browser to reload
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Contacts', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Contacts', header.text)
        self.check_for_row_in_a_table(
            ['Zygmunt the Admin', '+44 7890 123 432', 'zygmunt@fm.zyg'],
            'id_contacts_table')

        # He goes to add another contact this time with a different status
        link = self.browser.find_element_by_id('id_add_new_contact_link')
        self.follow_link(link)
        inputbox = self.browser.find_element_by_id('id_contact_name')
        inputbox.send_keys('Jane the User')
        inputbox = self.browser.find_element_by_id('id_contact_phone')
        inputbox.send_keys('+7 777 777 7777')
        inputbox = self.browser.find_element_by_id('id_contact_email')
        inputbox.send_keys('jane@users.org')
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        ## wait a second for the browser to reload
        time.sleep(1)
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Contacts', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Contacts', header.text)
        self.check_for_row_in_a_table(
            [
                'Jane the User',
                '+7 777 777 7777',
                'jane@users.org',
            ],
            'id_contacts_table')

    def test_admin_can_add_and_delete_roles(self):
        # Zygmunt the Admin visits the app home page and follows the link for
        # managing roles
        self.log_admin_in()
        self.browser.get(self.fm_url)
        link = self.browser.find_element_by_id('id_roles_link')
        self.follow_link(link)

        # The link takes him to a page with title and header mentioning
        # roles
        self.assertIn('Roles', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Roles', header.text)

        # He clicks on a link allowing him to add new roles and it takes
        # him to a page for adding new roles
        link = self.browser.find_element_by_id('id_add_new_role_link')
        self.follow_link(link)
        # He sees a page with a form. He decides to fill in all the input boxes.
        # He starts by selecting the correct role name
        select = Select(self.browser.find_element_by_id('id_role_name'))
        select.select_by_visible_text('SCCO')
        # He tries to submit the form as is by pressing the save button but he
        # is asked to fill in all the required fields
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        time.sleep(1)
        self.assertIn('field is required', self.browser.page_source)
        self.assertNotIn('Roles', self.browser.title)

        # He fills in the last two required fields
        time.sleep(1)  # # wait a second for the browser to reload
        select = Select(self.browser.find_element_by_id('id_role_contact'))
        select.select_by_visible_text('Zygmunt the Admin <zygmunt@fm.zyg>')
        select = Select(self.browser.find_element_by_id('id_role_facility'))
        select.select_by_visible_text('Hyperion Lab [operational]')
        ss = self.browser.get_screenshot_as_png()
        with open('/home/vagrant/shared/ss.png', mode='w') as f:
            f.write(ss)
        # Upon pressing submit he is redirected to Roles and can see his
        # new role on the list.
        submit = self.browser.find_element_by_id('id_submit_button')
        submit.click()
        time.sleep(1)  # # wait a second for the browser to reload
        ## all required fields have been entered
        self.assertNotIn('field is required', self.browser.page_source)
        ## all fields in drop down lists filled in with correct values
        self.assertNotIn('not one of the available choices',
                         self.browser.page_source)
        self.assertIn('Roles', self.browser.title)
        header = self.browser.find_element_by_tag_name('h1')
        self.assertIn('Roles', header.text)
        self.check_for_row_in_a_table(
            ['SCCO', 'Hyperion Lab', 'Zygmunt the Admin <zygmunt@fm.zyg'],
            'id_roles_table')

        # He goes to delete the facility associated with the role
        ## todo: refactor if native delete added
        self.browser.get(self.live_server_url + '/admin/fm/facility/1/delete/')
        form = self.browser.find_element_by_tag_name('form')
        form.submit()
        time.sleep(1)

        # He returns to the list of roles and the role is no longer there
        self.current_user_goes_to_roles()
        self.assertNotIn('SCCO', self.browser.page_source)
        self.assertNotIn('Hyperion', self.browser.page_source)
        self.assertNotIn('Zygmunt', self.browser.page_source)

        # He goes to see the list of contacts and sees that the contact
        # associated with the deleted role remains
        self.current_user_goes_to_contacts()
        self.check_for_row_in_a_table(
            ['Zygmunt the Admin', 'zygmunt@fm.zyg', '+44 4444 444 444'],
            'id_contacts_table')

        # Relieved that everything is working perfectly Zygmunt goes to sleep.
