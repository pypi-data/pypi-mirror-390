import json
import asyncio
from concurrent.futures import ThreadPoolExecutor

from .endpoint_exception import EndpointException
from .endpoint import Endpoint
from .pdf_text_response import PdfTextResponse
from .text_order import TextOrder

class PdfText(Endpoint):
    '''
    Represents the pdf text endpoint.
    '''
    
    def __init__(self, resource, start_page = 1, page_count = 0, text_order = TextOrder.Stream):
        '''
        Initializes a new instance of the PdfText class.
        
        Args:
            resource (PdfResource): The image resource of type `PdfResource`.`
            start_page (integer): The start page.
            page_count (interger): The page count.
            text_order (TextOrder) : The text extraction order.
        '''

        super().__init__()
        self._resource = resource
        self.start_page = start_page
        self.page_count = page_count
        self.text_order = text_order
        self._endpoint_name = "pdf-text"

    def process(self):
        '''
        Process the pdf resource to get pdf's text.
        '''
        return asyncio.get_event_loop().run_until_complete(self.process_async())

    async def process_async(self):
        '''
        Process the pdf resource asynchronously to get pdf's text.
        '''
        rest_client = self.create_rest_request()
        headers = {"Content-Type": "application/pdf"}
        data = self._resource._data
        params = {
            "StartPage": str(self.start_page),
            "PageCount": str(self.page_count),
            "TextOrder": str(self.text_order)
        }
        with ThreadPoolExecutor() as executor:
            rest_response = executor.submit(rest_client.post, self.url, headers = headers, data=data, params=params).result()
        if rest_response.status_code == 200:
            response = PdfTextResponse(rest_response.content)
            response.is_successful = True
            response.status_code = rest_response.status_code
        elif rest_response.status_code == 401:
            raise EndpointException("Invalid api key specified.")
        else:
            response = PdfTextResponse()
            error_json = json.loads(rest_response.content)
            response.error_json = error_json
            response.error_id = error_json['id']
            response.error_message = error_json['message']
            response.is_successful = False
            response.status_code = rest_response.status_code
        return response

    