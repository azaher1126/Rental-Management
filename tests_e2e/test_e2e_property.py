from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait

from .base_test_class import BaseTestClass

class AddPropertyTests(BaseTestClass):

    def test_add_property(self):
        """Test process for adding a property"""

        self.loginTestUser()

        # Navigate to 'add_property' page
        ap_path = self.getFullWebPath('/add_property')
        self.driver.get(ap_path)

        # Verify navigation to the correct page
        self.assertEqual(ap_path, self.driver.current_url)

        # Test data
        test_address = '123 Test St'
        test_property_type = 'House'
        test_sqft = '4800'
        test_bdr = '4'
        test_btr = '2'
        test_rent = '2700'

        # Fill form fields
        property_address_input = self.driver.find_element(By.NAME, 'streetAddress')
        property_address_input.send_keys(test_address)

        property_ptype_input = self.driver.find_element(By.NAME, 'ptype')
        property_ptype_input.send_keys(test_property_type)

        property_sqft_input = self.driver.find_element(By.NAME, 'sqft')
        property_sqft_input.send_keys(test_sqft)

        property_bdr_input = self.driver.find_element(By.NAME, 'bdr')
        property_bdr_input.send_keys(test_bdr)

        property_btr_input = self.driver.find_element(By.NAME, 'btr')
        property_btr_input.send_keys(test_btr)

        property_rent_input = self.driver.find_element(By.NAME, 'price')
        property_rent_input.send_keys(test_rent)

        # Select availability from the availability dropdown
        availability_dropdown = self.driver.find_element(By.NAME, 'availability')
        for option in availability_dropdown.find_elements(By.TAG_NAME, 'option'):
            if option.text == 'Available':
                option.click()
                break

        # Save property form
        save = self.driver.find_element(By.CLASS_NAME, 'OptionsButton')
        save.click()

        # Verify flash message for successful addition
        self.assertTrue(self.pageFlashesContain("Successfully added the new property."))

        # Extract property ID from url
        property_id = self.driver.current_url.split('/')[-1]

        # Navigate to the properties page
        properties_path = self.getFullWebPath('/properties')
        self.driver.get(properties_path)

        # Verify navigation to the correct page
        WebDriverWait(self.driver, 10).until(ec.url_matches(properties_path))

        # Allow time to render to reduce potential issues from delays
        property_list = WebDriverWait(self.driver, 10).until(ec.presence_of_all_elements_located((By.CLASS_NAME, 'propertyTab')))

        # Check if the new property is listed
        property_ids = [property.get_dom_attribute('id') for property in property_list]

        # Assert that the test address is present in the list of property addresses
        self.assertIn(property_id, property_ids, "Property not found on properties page.")