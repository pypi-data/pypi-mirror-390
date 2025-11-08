import uuid
from .resource import Resource
from .resource_type import ResourceType

class HtmlResource(Resource):
    '''
    Represents a pdf resource
    '''

    def __init__(self, html_string, resource_name = None):
        '''
        Initializes a new instance of the HtmlResource class 
        with html string and resource name.

        Args:
            html (string): The Html string.
            resource (string): The name of the resource.
        '''
        
        super().__init__(None, resource_name)
        self._data = html_string
        self._type = ResourceType.Html
        self._file_extension = ".html"
        self._mime_type = "text/html"
