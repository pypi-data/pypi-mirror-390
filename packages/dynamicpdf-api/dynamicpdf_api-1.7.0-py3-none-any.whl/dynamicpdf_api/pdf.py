import asyncio
import os
import json
from concurrent.futures import ThreadPoolExecutor
from .endpoint import Endpoint
from .page_input import PageInput
from .pdf_instruction import PdfInstructions
from .additional_resource import AdditionalResource
from .additional_resource_type import AdditionalResourceType
from .resource_type import ResourceType
from .image_input import ImageInput
from .pdf_input import PdfInput
from .html_input import HtmlInput
from .word_input import WordInput
from .excel_input import ExcelInput
from .html_resource import HtmlResource
from .page_size import PageSize
from .dlex_input import DlexInput
from .page_orientation import PageOrientation
from .pdf_response import PdfResponse
from .input_type import InputType
from .endpoint_exception import EndpointException 

class Pdf(Endpoint):
    '''
    Represents a pdf endpoint
    '''

    def __init__(self):
        '''
        Initializes a new instance of the Pdf class.
        '''

        super().__init__()
        self._instructions = PdfInstructions()

        # Gets or sets the collection of resource.
        self.resources = set()
        self._endpoint_name = "pdf"

        # Gets or sets the inputs.
        self.inputs = self._instructions._inputs
        
        # Gets or sets the templates.
        self.templates = self._instructions._templates

        # Gets or sets the fonts.
        self.fonts = self._instructions._fonts
        
        # Gets or sets the formFields.
        self.form_fields = self._instructions._form_fields

        # Gets or sets the outlines.
        self.outlines = self._instructions._outlines

    @property
    def author(self):
        '''
        Gets the Author
        '''
        return self._instructions._author

    @author.setter
    def author(self, value):
        '''
        Sets the Author
        '''
        self._instructions._author = value

    @property
    def title(self):
        '''
        Gets the Title
        '''
        return self._instructions._title

    @title.setter
    def title(self, value):
        '''
        Sets the Title
        '''
        self._instructions._title = value

    @property
    def subject(self):
        '''
        Gets the Subject
        '''
        return self._instructions._subject

    @subject.setter
    def subject(self, value):
        '''
        Sets the Subject
        '''
        self._instructions._subject = value

    @property
    def creator(self):
        '''
        Gets the Creator
        '''
        return self._instructions._creator

    @creator.setter
    def creator(self, value):
        '''
        Sets the Creator
        '''
        self._instructions._creator = value

    @property
    def producer(self):
        '''
        Gets the PDF Producer
        '''
        return self._instructions._producer

    @producer.setter
    def producer(self, value):
        '''
        Sets the PDF Producer
        '''
        self._instructions._producer = value
        
    @property
    def tag(self):
        '''
        Gets the Tag property
        '''
        return self._instructions._tag

    @tag.setter
    def tag(self, value):
        '''
        Sets the Tag property
        '''
        self._instructions._tag = value

    @property
    def keywords(self):
        '''
        Gets the Keywords
        '''
        return self._instructions._keywords

    @keywords.setter
    def keywords(self, value):
        '''
        Sets the Keywords
        '''
        self._instructions._keywords = value

    @property
    def security(self):
        '''
        Gets the Security
        '''
        return self._instructions._security

    @security.setter
    def security(self, value):
        '''
        Sets the Security
        '''
        self._instructions._security = value

    @property
    def flatten_all_form_fields(self):
        '''
        Gets the boolean indicating whether to flatten all form fields
        '''
        return self._instructions._flatten_all_form_fields

    @flatten_all_form_fields.setter
    def flatten_all_form_fields(self, value):
        '''
        Sets the boolean indicating whether to flatten all form fields
        '''
        self._instructions._flatten_all_form_fields = value

    @property
    def retain_signature_form_fields(self):
        '''
        Gets the boolean indicating whether to retain signature form field
        '''
        return self._instructions._retain_signature_form_fields

    @retain_signature_form_fields.setter
    def retain_signature_form_fields(self, value):
        '''
        Sets the boolean indicating whether to retain signature form field
        '''
        self._instructions._retain_signature_form_fields = value
        
        
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
            self.resources.add(resource)
        else:
            resource_data = var1
            additional_resource_type = var2
            resource_name = var3
            type_mapping = {
                AdditionalResourceType.Font: ResourceType.Font,
                AdditionalResourceType.Image: ResourceType.Image,
                AdditionalResourceType.Pdf: ResourceType.Pdf,
                AdditionalResourceType.Html: ResourceType.Html
            }
            _type = type_mapping.get(additional_resource_type, ResourceType.Pdf)
            resource = AdditionalResource(resource_data, resource_name, _type)
            self.resources.add(resource)

    
    def add_pdf(self, value, options = None):
        '''
        Returns a PdfInput object containing the input pdf.
        
        Args:
            value (PdfResource | string): The resource of type PdfResource. | The resource path in cloud resource manager.
            options (MergeOptions): The merge options for the pdf.
        '''

        input = PdfInput(value, options)
        self.inputs.append(input)
        return input 

    def add_image(self, value):
        '''
        Returns a ImageInput object containing the input pdf.
        
        Args:
            value (PdfResource | string): The resource of type ImageResource. | The resource path in cloud resource manager.
        '''

        input = ImageInput(value)
        self.inputs.append(input)
        return input

    def add_html(self, resource, base_path = None, size = None, orientation = None, margins = None):
        '''
        Returns a HtmlInput object containing the input pdf.

        Args:
            resource (HtmlResource | string):  The resource of type HtmlResource. | The HTML input string.
            basepath (string): The root path for any relative path used in html.
            size (PageSize): the page size of the PDF pages
            orientation (PageOrientation): The page orientation for the PDF pages
            margins (integer): Margins for all four sides
        '''

        if type(resource) == str:
            html_resource = HtmlResource(resource)
        else:
            html_resource = resource
        input = HtmlInput(html_resource, base_path, size, orientation, margins)
        self.inputs.append(input)
        return input
    
    def add_word(self, resource, size = None, orientation = None, margins = None):
        '''
        Returns a WordInput object containing the input pdf.

        Args:
            resource (WordResource):  The resource of type WordResource.
            size (PageSize): the page size of the PDF pages
            orientation (PageOrientation): The page orientation for the PDF pages
            margins (integer): Margins for all four sides
        '''

        input = WordInput(resource, size, orientation, margins)
        self.inputs.append(input)
        return input
    
    def add_excel(self, resource, size = None, orientation = None, margins = None):
        '''
        Returns a ExcelInput object containing the input pdf.

        Args:
            resource (ExcelResource):  The resource of type ExcelResource.
            size (PageSize): the page size of the PDF pages
            orientation (PageOrientation): The page orientation for the PDF pages
            margins (integer): Margins for all four sides
        '''

        input = ExcelInput(resource, size, orientation, margins)
        self.inputs.append(input)
        return input

    def add_dlex(self, value, layout_data):
        '''
        Returns a DlexInput object containing the input pdf.

        Args:
            value (string | DlexResource): The resource path in cloud resource manager. | The resource of type DlexResource
            layoutData (LayoutDataResource | string): The layout data resource of type LayoutDataResource | The json data string used to create the PDF report.
        '''

        input = DlexInput(value, layout_data)
        self.inputs.append(input)
        return input
    
    def add_page(self, page_width = None, page_height = None):
        '''
        Returns a PageInput object containing the input pdf.
        
        Args:
            pageWidth (float): The width of the page.
            pageHeight (float): The height of the page.
        '''
        if page_width != None and page_height != None:
            input = PageInput(page_width, page_height)
            self.inputs.append(input)
            return input
        else:
            input = PageInput()
            self.inputs.append(input)
            return input
    
    def get_instructions_json(self, indented = False):
        for input in self._instructions._inputs:
            if input._type == InputType.Page:
                for element in input.elements:
                    if element._text_font and element._text_font.resource_name:
                        self._instructions._fonts.add(element._text_font)          
            if input.template:
                self._instructions._templates.add(input.template)
                if input.template.elements and len(input.template.elements) > 0:
                    for element in input.template.elements:
                        if element._text_font:
                            self._instructions._fonts.add(element._text_font)
        
        if indented:
            return json.dumps(self._instructions.to_json(), indent = 2)
        else:
            return json.dumps(self._instructions.to_json())

    def process(self):
        '''
        Process to create pdf.
        '''
        return asyncio.get_event_loop().run_until_complete(self.process_async())

    async def process_async(self):
        '''
        Process data asynchronously to create pdf.
        '''
        rest_client = self.create_rest_request()
        final_resources=[]

        for input in self._instructions._inputs:
            if input._type == InputType.Page:
                for element in input.elements:
                    if element._resource:
                        final_resources.append(element._resource)
                    if element._text_font and element._text_font.resource_name:
                        self._instructions._fonts.add(element._text_font)          
            for resource in input._resources:
                final_resources.append(resource)
            if input.template:
                self._instructions._templates.add(input.template)
                if input.template.elements and len(input.template.elements) > 0:
                    for element in input.template.elements:
                        if element._resource:
                            final_resources.append(element._resource)
                        if element._text_font:
                            self._instructions._fonts.add(element._text_font)
        
        for resource in self.resources:
            final_resources.append(resource)

        files = []
        
        instructions = json.dumps(self._instructions.to_json(), indent = 2)
        files.append(("Instructions", ("Instructions.json", instructions, "application/json")))

        for resource in final_resources:
            if resource._type == ResourceType.LayoutData:
                files.append(('Resource',(
                    resource.layout_data_resource_name,  
                    resource._data, 
                    resource._mime_type)
                ))
            else:
                files.append(('Resource',(
                    resource.resource_name, 
                    resource._data,
                    resource._mime_type )
                ))
        with ThreadPoolExecutor() as executor:
            rest_response = executor.submit(rest_client.post, self.url, files=files).result()

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
        

