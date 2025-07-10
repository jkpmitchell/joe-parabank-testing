# test_login.py
from baseTest import BaseTest

def test_valid_login(page):
    test = BaseTest(page)
    test.login("john", "demo")
    test.validate_login_success()