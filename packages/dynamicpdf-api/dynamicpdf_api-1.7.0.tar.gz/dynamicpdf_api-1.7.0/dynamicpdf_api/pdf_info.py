import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

from .endpoint_exception import EndpointException
from .endpoint import Endpoint
from .pdf_info_response import PdfInfoResponse

class PdfInfo(Endpoint):
    '''
    Represents the pdf info endpoint.
    '''

    def __init__(self, resource):
        '''
        Initializes a new instance of the PdfInfo class.

        Args:
            resource (PdfResource): The resource of type PdfResource
        '''

        super().__init__()
        self._resource = resource
        self._endpoint_name = "pdf-info"

    def process(self):
        '''
        Process the pdf resource to get pdf's information.
        '''
        return asyncio.get_event_loop().run_until_complete(self.process_async())

    async def process_async(self):
        '''
        Process the pdf resource asynchronously to get pdf's information.
        '''
        rest_client = self.create_rest_request()
        headers = {"Content-Type": "application/pdf"}
        data = self._resource._data
        with ThreadPoolExecutor() as executor:
            rest_response = executor.submit(rest_client.post, self.url, headers = headers, data=data).result()
        if rest_response.status_code == 200:
            response = PdfInfoResponse(rest_response.content)
            response.is_successful = True
            response.status_code = rest_response.status_code
        elif rest_response.status_code == 401:
            raise EndpointException("Invalid api key specified.")
        else:
            response = PdfInfoResponse()
            error_json = json.loads(rest_response.content)
            response.error_json = error_json
            response.error_id = error_json['id']
            response.error_message = error_json['message']
            response.is_successful = False
            response.status_code = rest_response.status_code

        return response
        