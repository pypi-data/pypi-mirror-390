from .input import Input
from .input_type import InputType
from .page_size import PageSize
from .page_orientation import PageOrientation
from .unit_converter import UnitConverter
from .converter_input import ConverterInput

class HtmlInput(ConverterInput):
    ''' 
    Represents a html input
    '''
    
    def __init__(self, resource, base_path = None, size = None, orientation = None, margins = None):
        '''
        Initializes a new instance of the HtmlInput class.
        
        Args:
            resource (HtmlResource): The resource of type HtmlResource.
            basepath (string): The basepath options for the url.
            size (PageSize): The page size of the output PDF.
            orientation (PageOrientation): The page orientation of the output PDF.
            margins (integer): The page margins of the output PDF.
        '''

        super().__init__(resource, size, orientation, margins)

        # Gets or sets the base path option.
        self.base_path = base_path

        self.html_string = ''
        self._type = InputType.Html
        
    def to_json(self):
        json = {
            "type": self._type,
            "id": self.id
        }
        if self.page_height is not None:
            json["pageHeight"] = self.page_height
        if self.page_width is not None:
            json["pageWidth"] = self.page_width   
        if self.resource_name is not None:
            json["resourceName"] = self.resource_name
        if self._template_id is not None:
            json["templateId"] = self._template_id
        if self.base_path is not None:
            json["basePath"] = self.base_path
        if self.top_margin is not None:
            json["topMargin"] = self.top_margin
        if self.left_margin is not None:
            json["leftMargin"] = self.left_margin
        if self.bottom_margin is not None:
            json["bottomMargin"] = self.bottom_margin
        if self.right_margin is not None:
            json["rightMargin"] = self.right_margin
        return json