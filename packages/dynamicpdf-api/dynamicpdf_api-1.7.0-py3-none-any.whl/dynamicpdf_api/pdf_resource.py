from .resource import Resource
from .resource_type import ResourceType

class PdfResource(Resource):
    '''
    Represents a pdf resource
    '''

    def __init__(self, input, resource_name = None):
        '''
        Initializes a new instance of the PdfResource class.

        Args:
            input (string | Buffer[]): The pdf file path. | The byte array of the pdf file.
            resourceName (string): The name of the resource.
        '''
        
        super().__init__(input, resource_name)
        self._type = ResourceType.Pdf
        self._file_extension = ".pdf"
        self._mime_type = "application/pdf"

    def to_json(self):
        return {"type": self._type}