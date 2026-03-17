from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from .base_test_class import BaseTestClass

class AccountTests(BaseTestClass):

    def test_register(self):
        """Test the registration process"""
        register_full_path = self.getFullWebPath('/register')
        self.driver.get(register_full_path)

        register_button = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'register-submit'))
        )
        # Rest of elements will be loaded on page, no need to wait for them

        test_first_name = 'End To'
        test_last_name = 'End Test'
        test_email = 'e2e@test.com'
        test_password = 'E2eTest1'

        # Fill out the registration form
        first_name_input = self.driver.find_element(By.NAME, 'first_name')
        first_name_input.send_keys(test_first_name)

        last_name_input = self.driver.find_element(By.NAME, 'last_name')
        last_name_input.send_keys(test_last_name)

        email_input = self.driver.find_element(By.NAME, 'email')
        email_input.send_keys(test_email)

        password_input = self.driver.find_element(By.NAME, 'password')
        password_input.send_keys(test_password)

        confirm_password_input = self.driver.find_element(By.NAME, 'confirm_password')
        confirm_password_input.send_keys(test_password)

        # Scroll to the register button and click it
        register_button.location_once_scrolled_into_view
        register_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'register-submit'))
        )
        register_button.click()

        # Check that the user is redirected to the setup 2FA page
        wait = WebDriverWait(self.driver, 10).until(
            EC.url_changes(register_full_path)
        )
        self.assertIn('/setup_2fa', self.driver.current_url)

        # Check that the user is logged in
        nav_fullname = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'nav-user-fullname'))
        )
        self.assertEqual(f'{test_first_name} {test_last_name}', nav_fullname.text)

        self.assertTrue(self.pageFlashesContain("Account created successfully!"))

    def test_login(self):
        """Test the login process"""
        login_full_path = self.getFullWebPath('/login')
        self.driver.get(login_full_path)

        login_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'login-submit'))
        )
        # Rest of elements will be loaded on page, no need to wait for them

        email_input = self.driver.find_element(By.NAME, 'email')
        email_input.send_keys(self.user_email)

        password_input = self.driver.find_element(By.NAME, 'password')
        password_input.send_keys(self.user_password)

        login_button.click()

        # Check that the user is redirected to the home page
        wait = WebDriverWait(self.driver, 10).until(
            EC.url_changes(login_full_path)
        )
        home_path = self.getFullWebPath('/')
        self.assertIn(home_path, self.driver.current_url)

        # Check that the user is logged in
        nav_fullname = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, 'nav-user-fullname'))
        )
        self.assertEqual(f'{self.user_first_name} {self.user_last_name}', nav_fullname.text)

        welcome_msg = self.driver.find_element(By.CSS_SELECTOR, '.WelcomeMessage1')
        self.assertIn(self.user_logged_in_welcome_msg, welcome_msg.text)

        self.assertTrue(self.pageFlashesContain("Logged in successfully!"))

    def test_logout(self):
        """Test the logout process"""
        self.loginTestUser()
        logout_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'nav-logout'))
        )
        logout_button.click()

        # Check that the user is redirected to the home page
        welcome_msg = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, '.WelcomeMessage1'))
        )
        home_full_path = self.getFullWebPath('/')
        self.assertIn(home_full_path, self.driver.current_url)

        # Check that the user is logged out
        nav_fullname = self.driver.find_elements(By.ID, 'nav-user-fullname')
        self.assertEqual(0, len(nav_fullname))

        self.assertIn(self.user_logged_out_welcome_msg, welcome_msg.text)
        self.assertTrue(self.pageFlashesContain("Logged out successfully!"))
