import re
from flask import Flask
from pyotp import TOTP
from .base_test_class import BaseTestClass
from app.models import Property
from app.database import db
from app.app import create_app

class IntegrationTests(BaseTestClass):

    def test_register_and_2fa_setup(self):
        """Test the integration of the registration and 2FA setup process"""
        test_first_name = 'Integration'
        test_last_name = 'Test'
        # Register a new user
        response = self.client.post('/register', data=dict(
            first_name=test_first_name,
            last_name=test_last_name,
            email='integration@test.com',
            password='Integrationtest1',
            confirm_password='Integrationtest1',
        ), follow_redirects=True)
        
        # Ensure the registration was successful
        self.assertEqual(response.status_code, 200)
        self.assertIn(str.encode(test_first_name), response.data)
        self.assertIn(str.encode(test_last_name), response.data)

        # Ensure user redirected to 2FA setup page
        self.assertIn(b'Setup 2FA', response.data)

        # Extract the 2FA secret token from the response
        token_2fa_search = re.search(r'2FA Secret Token: ([\w\d]{32})', response.text, re.IGNORECASE)
        self.assertIsNotNone(token_2fa_search)
        token_2fa = token_2fa_search.group(1)
        totp = TOTP(token_2fa)
        # Enable 2FA for the user
        response = self.client.post('/setup_2fa', data=dict(
            verification_code=totp.now()
        ), follow_redirects=True)

        # Ensure the 2FA setup was successful
        self.assertEqual(response.status_code, 200)
        
        # Ensure user is redirected to the home page
        self.assertIn(f"Welcome {test_first_name}, to the Rental Management System", response.text)
        self.assertIn(str.encode(test_first_name), response.data)
        self.assertIn(str.encode(test_last_name), response.data)

    def test_login_with_2fa(self):
        """Test the integration of the login process with 2FA"""
        token_2fa = self.enableTestUser2fa()

        # Login
        response = self.client.post('/login', data=dict(
            email=self.user_email,
            password=self.user_password,
        ), follow_redirects=True)

        # Ensure user is asked for 2FA
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Verify 2FA', response.data)

        # Get 2FA secret token
        totp = TOTP(token_2fa)

        # Verify 2FA code
        response = self.client.post('/verify_2fa', data=dict(
            verification_code=totp.now()
        ), follow_redirects=True)

        # Ensure login is successful
        self.assertEqual(response.status_code, 200)
        self.assertIn(f"Welcome {self.user_first_name}, to the Rental Management System", response.text)
        self.assertIn(str.encode(self.user_first_name), response.data)
        self.assertIn(str.encode(self.user_last_name), response.data)

    def test_new_property(self):
        """Test the property addition process"""
        # Login to to begin a session
        response = self.client.post('/login', data=dict(
            email=self.user_email,
            password=self.user_password
        ), follow_redirects=True)

        # Ensure the login was successful
        self.assertIn(self.user_logged_in_welcome_msg, response.data)
        self.assertNotIn(b'LOGIN', response.data)
        self.assertIn(str.encode(self.user_first_name), response.data)
        self.assertIn(str.encode(self.user_last_name), response.data)

        # Test property details
        address = '3434 Integration Blvd'
        property_type = 'House'
        sqrFtg = '2100'
        bedrooms = '4'
        bathrooms = '2'
        rent_price = '1850'
        avail = 'available'

        prop = self.client.post('/add_property', data=dict(
            streetAddress=address,
            ptype=property_type,
            sqft=sqrFtg,
            bdr=bedrooms,
            btr=bathrooms,
            price=rent_price,
            availability=avail
        ), follow_redirects=True)

        # Verify the response
        self.assertEqual(prop.status_code, 200)
        self.assertIn(str.encode(address), prop.data)
        self.assertIn(str.encode(property_type), prop.data)
        self.assertIn(str.encode(sqrFtg), prop.data)
        self.assertIn(str.encode(bedrooms), prop.data)
        self.assertIn(str.encode(bathrooms), prop.data)
        self.assertIn(str.encode(rent_price), prop.data)
        self.assertIn(b'selected="selected"\n            \n            >Available', prop.data)
