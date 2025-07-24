# baseTest.py
from playwright.sync_api import Page

# BaseTest class for handling common test operations in Playwright 
# This class provides methods for login and validation of login success.
# It can be extended for other common test functionalities.
class BaseTest:
    def __init__(self, page: Page):
        self.page = page

    def login(self, username, password):
        self.page.goto("https://parabank.parasoft.com")
        self.page.fill('input[name="username"]', username)
        self.page.fill('input[name="password"]', password)
        self.page.click('input[type="submit"]')

    def validate_login_success(self):
        assert self.page.inner_text("h2") == "Accounts Overview"