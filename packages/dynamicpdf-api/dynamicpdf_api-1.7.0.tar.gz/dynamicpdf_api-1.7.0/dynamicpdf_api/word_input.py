from .input_type import InputType
from .page_size import PageSize
from .page_orientation import PageOrientation
from .converter_input import ConverterInput

class WordInput(ConverterInput):
    '''
    Represents a Word input.
    '''

    def __init__(self, resource, size = None, orientation = None, margins = None):
        '''
        Initializes a new instance of the WordInput class.

        Args:
            resource (WordResource): The resource of type WordResource.
            size (PageSize): The page size of the output PDF.
            orientation (PageOrientation): The page orientation of the output PDF.
            margins (float): The page margins of the output PDF.
        '''
        
        super().__init__(resource, size, orientation, margins)
       
        self._type = InputType.Word

        # Gets or sets the TextReplace object List
        self.text_replace = []

    @property
    def _get_text_replace(self):
        if self.text_replace and len(self.text_replace) > 0:
            return self.text_replace
        return None
     
    def to_json(self):
        json = {
            "id":self.id,
            "type": self._type
        }
        if self._template_id is not None:
            json["templateId"] = self._template_id
        if self.page_height is not None:
            json["pageHeight"] = self.page_height
        if self.page_width is not None:
            json["pageWidth"] = self.page_width   
        if self.resource_name is not None:
            json["resourceName"] = self.resource_name
        if self.top_margin is not None:
            json["topMargin"] = self.top_margin
        if self.left_margin is not None:
            json["leftMargin"] = self.left_margin
        if self.bottom_margin is not None:
            json["bottomMargin"] = self.bottom_margin
        if self.right_margin is not None:
            json["rightMargin"] = self.right_margin
        if self._get_text_replace:
            text_replace=[]
            for i in self._get_text_replace:
                text_replace.append(i.to_json())
        # if len(text_replace) > 0:
            json["textReplace"] = text_replace
        return json