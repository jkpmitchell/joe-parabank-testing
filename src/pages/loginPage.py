from playwright.sync_api import Page, expect
from src.core.baseTest import BaseTest
from src.pages.base_page import BasePage

class LoginPage(BasePage):    
    def login(self, username: str, password: str):
        self.page.fill(self.username_field, username)
        self.page.fill(self.password_field, password)
        self.page.click(self.login_button)
    
    def verify_login_error(self, expected_error: str):
        expect(self.page.locator(self.error_message)).to_contain_text(expected_error)