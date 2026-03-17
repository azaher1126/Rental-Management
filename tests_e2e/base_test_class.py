import os
import threading
import unittest
from typing import Any
from uuid import uuid4
from contextlib import contextmanager
from flask_login import login_user
from flask import Response

from playwright.sync_api import sync_playwright

from app.app import create_app
from app.database import db
from app.enums.AccountType import AccountType
from app.models import User


class BaseTestClass(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        db_name_prefix = f'{uuid4()}_account_tests_'
        cls.app = create_app(db_name_prefix)
        cls.app.config['TESTING'] = True

        cls.user_first_name = 'Property'
        cls.user_last_name = 'Owner'
        cls.user_email = 'propertyowner@example.com'
        cls.user_password = 'Propertyowner1'

        cls.user_logged_out_welcome_msg = "Welcome to the Rental Management System"
        cls.user_logged_in_welcome_msg = f"Welcome {cls.user_first_name}, to the Rental Management System"

        with cls.app.app_context():
            cls.test_user = User(first_name=cls.user_first_name, last_name=cls.user_last_name, email=cls.user_email,
                                 password=cls.user_password, account_type=AccountType.PROPERTY_OWNER)
            db.session.add(cls.test_user)
            db.session.commit()
            db.session.refresh(cls.test_user)

        # Start the web app in a separate thread
        from werkzeug.serving import make_server
        cls.server = make_server('localhost', 0, cls.app)
        cls.server_thread = threading.Thread(target=cls.server.serve_forever)
        cls.server_thread.start()

        # Setting up playwright
        cls.playwright = sync_playwright().start()
        cls.browser = cls.playwright.chromium.launch(headless=True)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.browser.close()
        cls.playwright.stop()

        # Stop the web app
        cls.server.shutdown()

        with cls.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
            os.remove(db.db_path)

    def setUp(self) -> None:
        self.context = self.browser.new_context(viewport={"width": 1920, "height": 1080})
        self.context.set_default_timeout(10000)
        self.page = self.context.new_page()

        self.page.goto(f"http://localhost:{self.server.port}/")
        
        return super().setUp()
    
    def tearDown(self) -> None:
        with self.app.app_context():
            # Disable any 2FA that may have been setup in a test case
            self.test_user = db.session.get(User, self.test_user.id)
            self.test_user.is_2fa_auth_enabled = False
            db.session.commit()

        self.client = self.app.test_client()
        self.test_user_2fa_token = None

        self.page.close()
        self.context.close()

    def enableTestUser2fa(self) -> Any | None:
        if self.test_user_2fa_token:
            return
        with self.app.app_context():
            # Enable 2FA and return the 2FA secret token
            test_user = db.session.query(User).filter_by(email=self.user_email).scalar()
            test_user.is_2fa_auth_enabled = True
            db.session.commit()
            self.test_user_2fa_token = test_user.token_2fa
            return test_user.token_2fa

    def getFullWebPath(self, path: str) -> str:
        return f'http://localhost:{self.server.port}{path}'
    
    def pageFlashesContain(self, expectedStr: str) -> bool:
        flashesContainer = self.page.locator("#flashes")
        if not flashesContainer:
            return False
        flashes = flashesContainer.locator("li")
        for flash in flashes.all():
            if expectedStr in flash.inner_text():
                return True
        return False
    
    @contextmanager
    def logged_in_context(self):
        with self.app.test_request_context() as requestContext:
            login_user(self.test_user)

            if not requestContext.session:
                raise RuntimeError("The session attached to this request context is None. This should not happen.")

            response = Response()
            self.app.session_interface.save_session(self.app, requestContext.session, response)

            for header in response.headers.get_all('Set-Cookie'):
                if 'session' in header:  # Flask session cookie is named 'session'
                    cookie_parts = header.split(';')[0].split('=')
                    if len(cookie_parts) == 2:
                        self.context.add_cookies(
                            [
                                {
                                    "name": cookie_parts[0],
                                    "value": cookie_parts[1],
                                    "url": f"http://localhost:{self.server.port}/"
                                }
                            ]
                        )
            yield

        self.context.clear_cookies()
