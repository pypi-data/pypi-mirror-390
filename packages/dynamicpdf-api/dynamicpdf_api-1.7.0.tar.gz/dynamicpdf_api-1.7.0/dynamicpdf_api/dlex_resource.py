from .resource import Resource
from .resource_type import ResourceType


class DlexResource(Resource):
    '''
    Represents a Dlex resource object that is created using the DLEX file and a name.
    '''

    def __init__(self, dlex, resource = None):
        '''
        Initializes a new instance of the DlexResource class 
        with DLEX file path and resource name or
        byte data of the DLEX file and resource name as parameters.

        Args:
            dlex (string | Buffer[]): The dlex file path. | The Buffer array of the dlex file.
            resource(string): The name of the resource.
        '''

        super().__init__(dlex, resource)

        # Gets or sets name for layout data resource.
        self.layout_data_resource_name = None

        self._type = ResourceType.Dlex
        self._file_extension = ".dlex"
        self._mime_type = "application/xml"

    def to_json(self):
        return{
            "layoutDataResourceName": self.layout_data_resource_name,
            "resourceName": self.resource_name
        }