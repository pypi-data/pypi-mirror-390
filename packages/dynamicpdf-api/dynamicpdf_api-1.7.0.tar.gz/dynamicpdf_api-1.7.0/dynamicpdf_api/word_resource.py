from .endpoint_exception import EndpointException
from .resource import Resource
from .resource_type import ResourceType

class WordResource(Resource):
    '''
    Represents a word resource.
    '''

    def __init__(self, variable, resource_name = None):
        '''
        Initializes a new instance of the WordResource class.

        Args:
            filePath (string | byte[]): The word file path. | The byte array of the word file.
            resource_name (ResourceName): The resource name with file extension.
        '''

        super().__init__(variable, resource_name)
        self._resource_name = resource_name
        if resource_name and resource_name.strip() == "":
            raise EndpointException("Unsupported file type or invalid file extension.")
        self._type = ResourceType.Word
        self._file_extension = self.file_extension
    
    @property
    def file_extension(self):
        file_extension = ''
        if self._resource_name is not None and self._resource_name.strip() != "":
            file_extension = '.' + self._resource_name.split('.')[-1]
        elif self._file_path is not None and self._file_path.strip() != "":
            file_extension = '.' + self._file_path.split('.')[-1]
        else:
            raise EndpointException("Invalid file path or resource name.")

        if file_extension == ".doc":
            self._mime_type = "application/msword"
            return ".doc"
        
        elif file_extension == ".docx":
            if self._data[0] == 0x50 and self._data[1] == 0x4b:
                self._mime_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                return ".docx"
            
        elif file_extension == ".odt":
            if self._data[0] == 0x50 and self._data[1] == 0x4b:
                self._mime_type = "application/vnd.oasis.opendocument.text"
                return ".odt"
        raise EndpointException("Unsupported file type or invalid file extension.")

