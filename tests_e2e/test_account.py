from playwright.sync_api import expect

from .base_test_class import BaseTestClass

class AccountTests(BaseTestClass):

    def test_register(self):
        """Test the registration process"""
        register_full_path = self.getFullWebPath('/register')
        self.page.goto(register_full_path)

        test_first_name = 'End To'
        test_last_name = 'End Test'
        test_email = 'e2e@test.com'
        test_password = 'E2eTest1'

        self.page.fill('[name="first_name"]', test_first_name)
        self.page.fill('[name="last_name"]', test_last_name)
        self.page.fill('[name="email"]', test_email)
        self.page.fill('[name="password"]', test_password)
        self.page.fill('[name="confirm_password"]', test_password)

        self.page.click("#register-submit")

        # Check that the user is redirected to the setup 2FA page
        self.page.wait_for_url(lambda url: not url.startswith(register_full_path), wait_until="load")

        self.assertIn('/setup_2fa', self.page.url)

        # Check that the user is logged in
        nav_fullname = self.page.inner_text("#nav-user-fullname")
        self.assertEqual(f'{test_first_name} {test_last_name}', nav_fullname)

        self.assertTrue(self.pageFlashesContain("Account created successfully!"))

    def test_login(self):
        """Test the login process"""
        login_full_path = self.getFullWebPath('/login')
        self.page.goto(login_full_path)

        self.page.fill('[name="email"]', self.user_email)
        self.page.fill('[name="password"]', self.user_password)
        self.page.click("#login-submit")

        # Check that the user is redirected to the home page
        self.page.wait_for_url(lambda url: not url.startswith(login_full_path), wait_until="load")

        home_path = self.getFullWebPath('/')
        self.assertEqual(home_path, self.page.url)

        # Check that the user is logged in
        nav_fullname = self.page.inner_text("#nav-user-fullname")
        self.assertEqual(f'{self.user_first_name} {self.user_last_name}', nav_fullname)

        welcome_msg = self.page.inner_text('.WelcomeMessage1')
        self.assertIn(self.user_logged_in_welcome_msg, welcome_msg)

        self.assertTrue(self.pageFlashesContain("Logged in successfully!"))

    def test_logout(self):
        """Test the logout process"""
        with self.logged_in_context():
            home_full_path = self.getFullWebPath('/')
            self.page.goto(home_full_path)

            self.page.click("#nav-logout")

            self.page.wait_for_load_state("load")
            
            self.assertEqual(home_full_path, self.page.url)

            expect(self.page.locator('#nav-user-fullname')).not_to_be_attached()

            welcome_msg = self.page.inner_text('.WelcomeMessage1')
            self.assertIn(self.user_logged_out_welcome_msg, welcome_msg)

            self.assertTrue(self.pageFlashesContain("Logged out successfully!"))
