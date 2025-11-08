from .endpoint_exception import EndpointException
from .endpoint import Endpoint
from .pdf_response import PdfResponse
from .resource import Resource
from .additional_resource import AdditionalResource
from .additional_resource_type import AdditionalResourceType
from .resource_type import ResourceType
import asyncio
import json
import os
from concurrent.futures import ThreadPoolExecutor

class DlexLayout(Endpoint):
    '''
    Represents a Dlex layout endpoint.
    '''

    def __init__(self,dlex, layout_data):
        '''
        Initializes a new instance of the <see cref="DlexLayout"/> class using the 
        DLEX file path present in the cloud environment and the JSON data for the PDF report.

        Args:
            dlexPath (string): The DLEX file created as per the desired PDF report layout design.
            layoutData (LayoutDataResource): The LayoutDataResource json data file used to create the PDF report.
        '''

        super().__init__()
        
        self._endpoint_name = "dlex-layout"
        self._resources = []
        self.dlex_path = None
         
        if type(dlex) == str and type(layout_data) != str:
            self.dlex_path = dlex
            self._resource = layout_data
        elif type(dlex) != str and type(layout_data) != str:
            self._resources.append(dlex)
            self._resource = layout_data
        
    def add_additional_resource(self, var1, var2 = None, var3 = None):
        '''
        Adds additional resource to the endpoint.
        
        Args:
            var1 (string | bytes[]): The resource file path. | The resource data.
            var2 (string | AdditionalResourceType): The name of the resource. | The type of the additional resource.
            var3 (string): The name of the resource.
        '''
        
        if type(var1) == str:
            resource_path = var1
            resource_name = var2
            if resource_name is None:
                resource_name = os.path.basename(resource_path)
            resource = AdditionalResource(resource_path, resource_name)
            self._resources.append(resource)
        else:
            resource_data = var1
            additional_resource_type = var2
            resource_name = var3
            type_mapping = {
                AdditionalResourceType.Font: ResourceType.Font,
                AdditionalResourceType.Image: ResourceType.Image,
                AdditionalResourceType.Pdf: ResourceType.Pdf
            }
            _type = type_mapping.get(additional_resource_type, ResourceType.Pdf)
            resource = AdditionalResource(resource_data, resource_name, _type)
            self._resources.append(resource)

        
    def process(self):
        '''
        Process the DLEX and layout data to create PDF report.
        '''
        return asyncio.get_event_loop().run_until_complete(self.process_async())

    async def process_async(self):
        '''
        Process  the DLEX and layout data asynchronously to create PDF report.
        '''
        rest_client = self.create_rest_request()
        files = []
        files.append(('LayoutData',(
                    self._resource.layout_data_resource_name,  
                    self._resource._data, 
                    self._resource._mime_type)
                ))
      
        data = {'DlexPath': self.dlex_path}
      
        if self._resources and len(self._resources) > 0:
            for resource in self._resources:            
                files.append(('Resource',(resource.resource_name, resource._data, resource._mime_type)))
        
        with ThreadPoolExecutor() as executor:
            rest_response = executor.submit(rest_client.post, self.url, files=files, data=data).result()
        
        if rest_response.status_code == 200:
            response = PdfResponse(rest_response.content)
            response.is_successful = True
            response.status_code = rest_response.status_code
        elif rest_response.status_code == 401:
            raise EndpointException("Invalid api key specified.")
        else:
            response = PdfResponse()
            error_json = json.loads(rest_response.content)
            response.error_json = error_json
            response.error_id = error_json['id']
            response.error_message = error_json['message']
            response.is_successful = False
            response.status_code = rest_response.status_code

        return response
        
        