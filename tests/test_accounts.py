import re

from pyotp import TOTP

from app.database import db
from .base_test_class import BaseTestClass


class AccountTests(BaseTestClass):
    current_user_index = 0

    def test_register_visible(self):
        """Test the register page"""
        response = self.client.get('/register')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)

    def test_login_visible(self):
        """Test the login page visibility"""
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'LOGIN', response.data)

    def test_setup_2fa_visible(self):
        """Test the 2fa setup page visibility"""
        self.loginTestUser()
        response = self.client.get('/setup_2fa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Setup 2FA', response.data)
        self.assertIn(b'Skip', response.data)

    def test_verify_2fa_visible(self):
        """Test the 2fa verficiation page visibility"""
        self.loginTestUser()
        self.enableTestUser2fa()
        response = self.client.get('/verify_2fa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Verify 2FA', response.data)

    def test_login_not_visible_logged_in(self):
        """Test to ensure the login page is
        not visible when logged in"""
        self.loginTestUser()
        response = self.client.get('/login')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_register_success(self):
        """Test a successful registration"""
        AccountTests.current_user_index += 1
        test_email = f'testemail{AccountTests.current_user_index}@example.com'
        test_first_name = 'Test'
        test_last_name = 'Name'
        response = self.client.post('/register', data=dict(
            first_name=test_first_name,
            last_name=test_last_name,
            email=test_email,
            password='Testingpassword1',
            confirm_password='Testingpassword1'
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Setup 2FA', response.data)
        self.assertIn(str.encode(test_first_name), response.data)
        self.assertIn(str.encode(test_last_name), response.data)

    def test_register_missing_info(self):
        """Test registering a user without providing all info"""
        response = self.client.post('/register', data=dict())
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Register', response.data)
        self.assertIn(b'Please enter a valid email address.', response.data)
        self.assertIn(b'Please enter a first name.', response.data)
        self.assertIn(b'Please enter a last name.', response.data)
        self.assertIn(b'The password does not meet the requirements.', response.data)

    def test_setup_2fa(self):
        """Test setup 2FA authentication"""
        self.loginTestUser()

        # Get the setup 2fa page to retrieve 2FA secret token
        response = self.client.get('/setup_2fa')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Setup 2FA', response.data)
        self.assertIn(b'Skip', response.data)

        token_2fa_search = re.search(r'2FA Secret Token: ([\w\d]{32})', response.text, re.IGNORECASE)
        self.assertIsNotNone(token_2fa_search)
        token_2fa = token_2fa_search.group(1)
        totp = TOTP(token_2fa)

        response = self.client.post('/setup_2fa', data=dict(
            verification_code=totp.now()
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_logged_in_welcome_msg, response.data)
        self.assertIn(str.encode(self.user_first_name), response.data)
        self.assertIn(str.encode(self.user_last_name), response.data)

    def test_invalid_setup_2fa(self):
        """Test setup 2FA authentication with invalid code"""
        self.loginTestUser()

        response = self.client.post('/setup_2fa', data=dict(
            verification_code='123456'
        ))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/setup_2fa'))

    def test_setup_2fa_after_enabled(self):
        """Test accessing the setup_2fa page after
        it has already been enabled"""
        self.loginTestUser()
        self.enableTestUser2fa()
        response = self.client.get('/setup_2fa')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/')

    def test_verify_2fa(self):
        """Test verify 2FA authentication"""
        self.loginTestUser()

        token_2fa = self.enableTestUser2fa()
        totp = TOTP(token_2fa)

        response = self.client.post('/verify_2fa', data=dict(
            verification_code=totp.now()
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_logged_in_welcome_msg, response.data)
        self.assertIn(str.encode(self.user_first_name), response.data)
        self.assertIn(str.encode(self.user_last_name), response.data)

    def test_invalid_verify_2fa(self):
        """Test verify 2FA authentication with wrong code"""
        self.loginTestUser()
        self.enableTestUser2fa()
        response = self.client.post('/verify_2fa', data=dict(
            verification_code='123456'
        ))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.location.endswith('/verify_2fa'))

    def test_skip_2fa_verification(self):
        """Test login as 2FA user and accessing a page
        other than verify_2fa without verifying 2FA"""
        self.loginTestUser()
        self.enableTestUser2fa()
        self.logoutUser()
        self.loginTestUser()
        response = self.client.get('/properties')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/verify_2fa?next=/properties')

    def test_verify_2fa_without_enabled(self):
        """Test accessing the verify_2fa page without having 2FA enabled"""
        self.loginTestUser()
        response = self.client.get('/verify_2fa')
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.location, '/setup_2fa')

    def test_register_fail(self):
        """Test a unsuccessful registration"""
        response = self.client.post('/register', data=dict(
            first_name=self.user_first_name,
            last_name=self.user_last_name,
            email=self.user_email,
            password=self.user_password
        ), follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The email provided is already registered. Please log in.', response.data)
        self.assertIn(b'Register', response.data)

    def test_valid_login(self):
        """Test Valid login"""
        response = self.client.post('/login', data=dict(
            email=self.user_email,
            password=self.user_password
        ), follow_redirects=True)
        self.assertIn(self.user_logged_in_welcome_msg, response.data)
        self.assertNotIn(b'LOGIN', response.data)
        self.assertNotIn(b'LOGIN', response.data)
        self.assertIn(str.encode(self.user_first_name), response.data)
        self.assertIn(str.encode(self.user_last_name), response.data)

    def test_invalid_login(self):
        """Test Invalid login"""
        response = self.client.post('/login', data=dict(
            email='nonexistent@example.com',
            password='boguspassword'
        ), follow_redirects=True)
        self.assertIn(b'LOGIN', response.data)
        self.assertIn(b'The email or password provided is invalid!', response.data)

    def test_login_missing_info(self):
        """Test login without providing all info"""
        response = self.client.post('/login', data=dict())
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login', response.data)
        self.assertIn(b'Please enter a valid email address to login.', response.data)
        self.assertIn(b'Please enter a valid password to login.', response.data)

    def test_logout(self):
        """Test logout"""
        self.loginTestUser()
        response = self.client.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_logged_out_welcome_msg, response.data)
        self.assertIn(b'LOGIN', response.data)

    def test_role_required_redirects_when_not_authenticated(self):
        """Test that unauthenticated user is redirected to login."""
        self.logoutUser()
        response = self.client.get('/properties', follow_redirects=False)
        self.assertEqual(response.status_code, 302)
        self.assertIn('/login', response.location)

    def test_role_required_redirects_when_wrong_role(self):
        """Test that user with wrong role is redirected to home with flash message."""
        # Create a user with a different role
        with self.app.app_context():
            from app.models import User
            from app.enums.AccountType import AccountType

            other_user = User(
                first_name='Tenant',
                last_name='User',
                email='tenant@example.com',
                password='Tenantpass1',
                account_type=AccountType.TENANT  # Wrong role
            )
            db.session.add(other_user)
            db.session.commit()

        # Log in as the other user
        self.logoutUser()
        self.client.post('/login', data=dict(
            email='tenant@example.com',
            password='Tenantpass1'
        ), follow_redirects=True)

        # Attempt to access the protected route
        response = self.client.get('/properties', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'The requested page requires different permissions to be accessed.', response.data)
        self.assertIn(b'Welcome Tenant, to the Rental Management System', response.data)  # Updated assertion
