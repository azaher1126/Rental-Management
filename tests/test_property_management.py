from app.database import db
from app.models import Property
from .base_test_class import BaseTestClass


class PropertyTests(BaseTestClass):
    def setUp(self) -> None:
        super().setUp()
        self.loginTestUser()

    def test_add_property(self):
        """Test Adding a property"""
        address = '12 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', response.data)

    def test_add_property_empty_fields(self):
        """Test adding a property with empty fields"""
        response = self.client.post('/add_property', data=dict(
            streetAddress='',
            ptype='',
            sqft='',
            bdr='',
            btr='',
            price='',
            availability=''
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter an address.', response.data)
        self.assertIn(b'Please specify the property type.', response.data)
        self.assertIn(b'Please enter a valid square footage.', response.data)
        self.assertIn(b'Please enter a valid number of bedrooms.', response.data)
        self.assertIn(b'Please enter a valid number of bathrooms.', response.data)
        self.assertIn(b'Please enter a valid rent price.', response.data)
        self.assertIn(b'Please select availability status.', response.data)

    def test_add_property_invalid_data(self):
        """Test adding a property with invalid data"""
        address = '12 Test St'
        property_type = 'Virtual'
        sqrFtg = 'abc'  # Invalid square footage
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter a valid square footage.', response.data)

    def test_view_property_details(self):
        """Test viewing a property"""
        address = '123 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', response.data)

        property_id = response.request.path.split('/')[-1]

        response = self.client.get(f'/property_details/{property_id}')
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', response.data)

    def test_view_property_missing_details(self):
        """ Test viewing a non existent property"""
        non_existent_pid = 999999

        response = self.client.get(f'/property_details/{non_existent_pid}')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b'Oops! We couldn\'t find the page you were looking for.', response.data)
        # self.assertIn(b'back to homepage', response.data)

    def test_edit_property(self):
        """Test editing a property"""
        address = '1234 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', response.data)

        property_id = response.request.path.split('/')[-1]

        address = '9876 Changed Ave'
        property_type = 'House'
        sqrFtg = '321'
        rent_price = '2500'
        bedrooms = '7'
        bathrooms = '4'
        availability = 'unavailable'

        response = self.client.post(f'/property_details/{property_id}', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Not Available', response.data)

    def test_view_properties(self):
        """Test the properties page visibility and
            user properties are visible"""
        response = self.client.get('/properties')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'REMOVE', response.data)
        self.assertIn(b'ADD', response.data)

    def test_delete_properties(self):
        """Test deleting two properties at once"""
        address = '12345 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', response.data)

        property_id_1 = response.request.path.split('/')[-1]

        address = '6443 Test St'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(address), response.data)
        self.assertIn(str.encode(property_type), response.data)
        self.assertIn(str.encode(sqrFtg), response.data)
        self.assertIn(str.encode(bedrooms), response.data)
        self.assertIn(str.encode(bathrooms), response.data)
        self.assertIn(str.encode(rent_price), response.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', response.data)

        property_id_2 = response.request.path.split('/')[-1]

        response = self.client.post('/properties', data=dict(
            property_ids=f'{property_id_1},{property_id_2}'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        property_detail_url = '/property_details/'
        self.assertNotIn(str.encode(property_detail_url + property_id_1), response.data)
        self.assertNotIn(str.encode(property_detail_url + property_id_2), response.data)

    def test_delete_properties_no_ids(self):
        """Test deleting properties without providing property_ids"""
        response = self.client.post('/properties', data=dict(
            # No property_ids provided
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'No property IDs provided for deletion.', response.data)

    def test_delete_properties_invalid_ids(self):
        """Test deleting properties with invalid property_ids"""
        response = self.client.post('/properties', data=dict(
            property_ids='abc,def'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Invalid property IDs provided.', response.data)

    def test_view_property_other_user(self):
        """Test viewing a property that belongs to another user"""
        # Add a property
        address = '123 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        property_id = response.request.path.split('/')[-1]

        # Change owner_id to simulate another user
        with self.app.app_context():
            property = db.session.get(Property, int(property_id))
            property.owner_id = 99999  # Simulate another user
            db.session.commit()

        # Attempt to access the property details
        response = self.client.get(f'/property_details/{property_id}')
        self.assertEqual(response.status_code, 403)
        self.assertIn(b'Forbidden', response.data)

    def test_edit_property_invalid_data(self):
        """Test editing a property with invalid data"""
        # Add a property
        address = '1234 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'available'

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        property_id = response.request.path.split('/')[-1]

        # Attempt to edit with invalid data
        response = self.client.post(f'/property_details/{property_id}', data=dict(
            streetAddress='',  # Missing address
            ptype='',  # Missing property type
            sqft='abc',  # Invalid square footage
            bdr='',  # Missing bedrooms
            btr='-1',  # Invalid bathrooms
            price='abc',  # Invalid rent price
            availability='unknown'  # Invalid availability
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please enter an address.', response.data)
        self.assertIn(b'Please select a property type.', response.data)
        self.assertIn(b'Please enter a valid square footage.', response.data)
        self.assertIn(b'Please enter a valid number of bedrooms.', response.data)
        self.assertIn(b'Please enter a valid number of bathrooms.', response.data)
        self.assertIn(b'Please enter a valid rent price.', response.data)
        self.assertIn(b'Please select availability status.', response.data)

    def test_add_property_invalid_availability(self):
        """Test adding a property with invalid availability status"""
        address = '12 Test St'
        property_type = 'Virtual'
        sqrFtg = '12345'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1500'
        availability = 'unknown'  # Invalid availability

        response = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=availability
        ), follow_redirects=True)

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Please select availability status.', response.data)

    def test_add_property_get(self):
        """Test accessing add_property page via GET"""
        response = self.client.get('/add_property')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Add Property', response.data)
