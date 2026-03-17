from playwright.sync_api import expect

from .base_test_class import BaseTestClass

class AddPropertyTests(BaseTestClass):

    def test_add_property(self):
        """Test process for adding a property"""

        # Test data
        test_address = '123 Test St'
        test_property_type = 'House'
        test_sqft = '4800'
        test_bdr = '4'
        test_btr = '2'
        test_rent = '2700'

        with self.logged_in_context():
            ap_path = self.getFullWebPath('/add_property')
            self.page.goto(ap_path)

            self.page.fill('[name="streetAddress"]', test_address)
            self.page.fill('[name="ptype"]', test_property_type)
            self.page.fill('[name="sqft"]', test_sqft)
            self.page.fill('[name="bdr"]', test_bdr)
            self.page.fill('[name="btr"]', test_btr)
            self.page.fill('[name="price"]', test_rent)

            self.page.select_option('[name="availability"]', 'Available')

            self.page.click('.OptionsButton')

            # Verify flash message for successful addition
            self.assertTrue(self.pageFlashesContain("Successfully added the new property."))

            # Extract property ID from url
            property_id = self.page.url.split('/')[-1]

            # Navigate to the properties page
            properties_path = self.getFullWebPath('/properties')
            self.page.goto(properties_path)

            self.page.wait_for_url(properties_path, wait_until="load")

            expect(self.page.locator(f'[id="{property_id}"].propertyTab')).to_be_attached()
