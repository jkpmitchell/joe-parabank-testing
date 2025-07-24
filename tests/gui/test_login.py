
from framework.base_test import BaseTest
from pages.LoginPage import LoginPage

# Test for valid login functionality in the Parabank application.

def test_valid_login(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("john", "demo")

    test = BaseTest(page)
    test.validate_login_success()