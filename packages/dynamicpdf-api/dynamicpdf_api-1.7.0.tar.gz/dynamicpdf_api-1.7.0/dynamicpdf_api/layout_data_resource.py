import json
import uuid
from .resource import Resource
from .resource_type import ResourceType

class LayoutDataResource(Resource):
    '''
    Represents the Layout data resource used to create PDF reports
    '''

    def __init__(self, layout_data, layout_data_resource_name = None):
        '''
        Initializes a new instance of the LayoutDataResource class 
        using the layout data object and a resource name.

        Args:
            layoutData (LayoutData | string):  Serializable object data to create PDF report. | The layout data JSON file path.
            layoutDataResourceName (string):  The name for layout data resource.
        '''

        super().__init__()
        self._type = ResourceType.LayoutData
        self._file_extension = ".json"
        self._mime_type = "application/json"
        if type(layout_data) != str:
            json_text = json.dumps(layout_data)
            self._data = json_text.encode('utf-8')
        else:
            if layout_data.endswith(".json"):
                self._data = self._get_utf8_file_data(layout_data)
            else:
                self._data = layout_data.encode('utf-8')
        if layout_data_resource_name == None:
            self.layout_data_resource_name = f"{uuid.uuid4()}.json"
        else:
            self.layout_data_resource_name = layout_data_resource_name

    def to_json(self):
        return{
            "layoutDataResourceName": self.layout_data_resource_name,
            "resourceName": self.resource_name
        }