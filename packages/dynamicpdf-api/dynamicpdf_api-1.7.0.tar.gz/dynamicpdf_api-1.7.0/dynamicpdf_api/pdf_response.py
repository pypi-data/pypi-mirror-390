from .response import Response

class PdfResponse(Response):
    '''
    Represents the pdf response.
    '''

    def __init__(self, content = None):
        '''
        Initializes a new instance of the PdfResponse class.
        
        Args:
            content (Buffer[]): The byte array of pdf content.
        '''
        
        super().__init__()

        # Gets the content of pdf.
        self.content = content