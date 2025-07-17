# test_login.py
from baseTest import BaseTest

def test_valid_login(page):
    test = BaseTest(page)
    test.login("john", "demo")
    test.validate_login_success()

    # tests/test_login.py
from framework.base_test import BaseTest
from pages.LoginPage import LoginPage

def test_valid_login(page):
    login_page = LoginPage(page)
    login_page.navigate()
    login_page.login("john", "demo")

    test = BaseTest(page)
    test.validate_login_success()