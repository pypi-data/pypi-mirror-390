import json
from .json_response import JsonResponse
from .pdf_security_info import PdfSecurityInfo

class PdfSecurityInfoResponse(JsonResponse):
    '''
    Represents the pdf security inforamtion response.
    '''

    def __init__(self, json_content = None):
        '''
        Initializes a new instance of the PdfSecurityInfoResponse class.
        
        Args:
            json_content (string): The json of pdf's security information.
        '''
        self.content = None
        super().__init__(json_content)
        if json_content:
            self.content = PdfSecurityInfo(json.loads(self.json_content))

            