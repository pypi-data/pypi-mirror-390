from .response import Response

class XmlResponse(Response):
    '''
    Represents the xml response.
    '''

    def __init__(self, xml_content = None):
        '''
        Initializes a new instance of the <see cref="XmlResponse"/> class.
        
        Args:
            xmlContent (string): The xml content of the response.
        '''

        super().__init__()

        # Gets the xml content.
        self.content = xml_content