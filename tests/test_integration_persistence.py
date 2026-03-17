from app.models import Property
from .base_test_class import BaseTestClass


class PropertyIntegrationTest(BaseTestClass):
    def setUp(self) -> None:
        super().setUp()
        self.loginTestUser()

    def test_property_workflow(self):
        """Integration test for property details persistence across sessions"""

        # Step 1: Add a property with valid data
        address = '12 Test St'
        property_type = 'Apartment'
        square_footage = 1234
        bedrooms = 2
        bathrooms = 1
        rent_price = 1500
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=square_footage,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability,
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertNotIn(b'error', response.data)  # Ensure no validation errors occurred

        # Step 2: Verify the added property appears in the list
        response = self.client.get('/properties', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'id="PropertiesContainer"', response.data)
        self.assertIn(b'class="propertyTab"', response.data)  # Verify a property tab is present

        # Step 3: View the property's details
        with self.app.app_context():  # Ensure database queries are within application context
            property_id = Property.query.filter_by(address=address).first().id

        response = self.client.get(f'/property_details/{property_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)  # Address should appear on details page
        self.assertIn(str.encode(property_type), response.data)  # Property type should appear
        self.assertIn(str.encode(str(square_footage)), response.data)
        self.assertIn(str.encode(str(bedrooms)), response.data)
        self.assertIn(str.encode(str(bathrooms)), response.data)
        self.assertIn(str.encode(str(rent_price)), response.data)

        # Step 4: Log out using BaseTestClass logout method
        self.logoutUser()  # Explicitly calling logout method from BaseTestClass

        # Attempting to access property details while logged out should redirect to login
        response = self.client.get(f'/property_details/{property_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please log in to access this page.', response.data)  # Verify login required

        # Step 5: Log back in using BaseTestClass login method
        self.loginTestUser()

        # Verify property details after logging in again
        response = self.client.get(f'/property_details/{property_id}', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(str(square_footage)), response.data)
        self.assertIn(str.encode(str(bedrooms)), response.data)
        self.assertIn(str.encode(str(bathrooms)), response.data)
        self.assertIn(str.encode(str(rent_price)), response.data)
