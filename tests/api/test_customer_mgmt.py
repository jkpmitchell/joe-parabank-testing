from base_api import BaseAPI

# Test for the BaseAPI class to ensure it can make GET requests successfully.
def test_get_request():
    api = BaseAPI()
    response = api.get("accounts")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)  # Assuming the endpoint returns a list of accounts

def test_get_account_by_id():
    api = BaseAPI()
    response = api.get("accounts/12345")
    data = response.json()
    assert data["id"] == 12345