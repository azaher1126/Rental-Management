from .base_test_class import BaseTestClass


class PublicTests(BaseTestClass):
    def test_home(self):
        """Test the home page"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(self.user_logged_out_welcome_msg, response.data)

    def test_custom_not_found_1(self):
        """Test the custom not found page is used"""
        response = self.client.get('/not-found')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Oops! We couldn't find the page you were looking for", response.data)

        response = self.client.get('/other-not-found')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Oops! We couldn't find the page you were looking for", response.data)

    def test_custom_not_found_2(self):
        """Test the custom not found page is used"""
        response = self.client.get('/nonexistent-page')
        self.assertEqual(response.status_code, 404)
        self.assertIn(b"Oops! We couldn't find the page you were looking for", response.data)
        self.assertIn(b'404 - Page Not Found', response.data)

    def test_user_loader_with_invalid_id(self):
        """Test that user_loader returns None for a non-numeric user ID"""
        with self.app.app_context():
            # Call user_loader with a non-numeric ID
            user = self.app.login_manager._user_callback("invalid_id")
            self.assertIsNone(user, "user_loader should return None for non-numeric user IDs")
