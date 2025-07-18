from base_api import BaseAPI

def test_get_account_by_id():
    api = BaseAPI()
    response = api.get("accounts/12345")
    data = response.json()
    assert data["id"] == 12345