import requests
# The following code will allow for shared/generic API calls to the Parabank application.
# This is useful for both local and public API testing.

# BaseAPI class for handling HTTP requests to the Parabank API in a local environment.
# This class provides methods only for GET and POST requests which are supported by the Parabank application.

class BaseAPI:
    def __init__(self, base_url="http://localhost:8080/parabank/services/bank"):
        self.base_url = base_url
        self.session = requests.Session()

    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def post(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response

       

# The following class will allow for testing the public API endpoints of the Parabank application.

class PublicAPI(BaseAPI):
    def __init__(self, base_url="http://parabank.parasoft.com:8080/parabank/services/bank"):
        super().__init__(base_url)
    
    def get(self, endpoint, params=None, headers=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.get(url, params=params, headers=headers)
        response.raise_for_status()
        return response

    def post(self, endpoint, data=None, json=None, headers=None):
        url = f"{self.base_url}/{endpoint}"
        response = self.session.post(url, data=data, json=json, headers=headers)
        response.raise_for_status()
        return response
    
