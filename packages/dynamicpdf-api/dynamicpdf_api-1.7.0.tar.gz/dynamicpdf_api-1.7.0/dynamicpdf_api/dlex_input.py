from .input_type import InputType
from .input import Input
from .layout_data_resource import LayoutDataResource

class DlexInput(Input):
    '''
    Represents a Dlex input
    '''

    def __init__(self, resource, layout_data):
        '''
        Initializes a new instance of the DlexInput class by posting the 
        DLEX file and the JSON data file or
        DLEX file path that is present in the cloud environment and the JSON data file or
        DLEX file path and DLEX data file path that is present in the cloud environment
        from the client to the API to create the PDF report.    
        Args:
            DlexResource (string): Resource dlex file created as per the desired PDF report layout design. | The DLEX file path present in the resource manager.
            LayoutDataResource (string): LayoutData json data file used to create the PDF report. | The JSON data file path present in the resource manager used to create the PDF report.
        '''
        super().__init__()

        if type(resource) != str:
            self.resource_name = resource.resource_name
            self._resources.append(resource)
        else:
            self.resource_name = resource

        if type(layout_data) != str:
            self.layout_data_resource_name = layout_data.layout_data_resource_name
            self._resources.append(layout_data)
        else:
            layout_data_resource = LayoutDataResource(layout_data)
            self.layout_data_resource_name = layout_data_resource.layout_data_resource_name
            self._resources.append(layout_data_resource)
        self._Type = InputType.Dlex
    
    def to_json(self):
        json = {
            "id": self.id,
            "type": InputType.Dlex,
            "layoutDataResourceName": self.layout_data_resource_name
            }
        if self.resource_name is not None:
            json["resourceName"] = self.resource_name
        if self._template_id is not None:
            json["templateId"] = self._template_id
        return json
