import requests

class Endpoint:
    '''
    Represents the base class for endpoint and has settings for 
    base url, api key and creates a rest request object.
    '''
    
    endpoint_version = "v1.0"

    def __init__(self, base_url = "https://api.dynamicpdf.com", api_key = None):
        self._endpoint_name = None

        # Gets or sets base url for the api.
        self.base_url = base_url

        # Gets or sets api key.
        self.api_key = api_key 

    def create_rest_request(self):
        self.rest_client = requests.Session()
        self.rest_client.headers.update({"Authorization": "Bearer " + str(self.api_key)})
        self.url = f"{self.base_url}/{self.endpoint_version}/{self._endpoint_name}"
        return self.rest_client
