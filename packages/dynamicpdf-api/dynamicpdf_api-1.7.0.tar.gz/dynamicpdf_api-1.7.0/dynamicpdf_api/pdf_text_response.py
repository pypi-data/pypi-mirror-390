import json
from .json_response import JsonResponse

class PdfTextResponse(JsonResponse):
    '''
    Represents the pdf text response
    '''

    def __init__(self, json_content = None):
        '''
        Initializes a new instance of the PdfResponse class.

        Args:
            json_content (string): The json content
        '''
        self.content = None
        super().__init__(json_content)
        
        # Gets the collection of PdfContent.
        if json_content:
            self.content = json.loads(self.json_content)
