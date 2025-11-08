import json
from .json_response import JsonResponse

class PdfInfoResponse(JsonResponse):
    '''
    Represents the pdf inforamtion response.
    '''

    def __init__(self, json_content = None):
        '''
        Initializes a new instance of the PdfInfoResponse class.
        
        Args:
            json_content (string): The json of pdf information.
        '''
        self.content = None
        super().__init__(json_content)
        if json_content:
            self.content = json.loads(self.json_content)