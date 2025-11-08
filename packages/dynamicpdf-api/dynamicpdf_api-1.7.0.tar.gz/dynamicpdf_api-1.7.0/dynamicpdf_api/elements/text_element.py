from .element_type import ElementType
from .element import Element

class TextElement(Element):
    '''
    Represents a text element.
    
    Remarks:
        This class can be used to place text on a page.
    '''

    def __init__(self, value, placement, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the StackedGs1DataBarBarcodeElement class.

        Args:
            value (string): >Text to display in the text element.
            placement (ElementPlacement): The placement of the barcode on the page.
            xOffset (integer): The X coordinate of the text element.
            yOffset (integer): The Y coordinate of the text element.
        '''
        
        super().__init__(value, placement, x_offset, y_offset)
        self._color = None
        self._font = None
        self._font_name = None
        self._color_name = None
        self.font_size = None
        self._type = ElementType.Text

    @property
    def text(self):
        '''
        Gets the text to display in the text element.
        '''
        return self._input_value

    @text.setter
    def text(self, value):
        '''
        Sets the text to display in the text element.
        '''
        self._input_value = value
    
    @property
    def font(self):
        '''
        Gets the Font object to use for the text of the label.
        '''
        return self._font
    
    @font.setter
    def font(self, value):
        '''
        Sets the Font object to use for the text of the label.
        '''
        self._font = value
        self._font_name = self._font._name
        self._resource = self._font._resource
    
    @property
    def color(self):
        '''
        Gets the Color object to use for the text of the label.
        '''
        return self._color

    @color.setter
    def color(self, value):
        '''
        Sets the Color object to use for the text of the label.
        '''
        self._color = value
        self._color_name = self._color._color_string
    
    @property
    def _text_font(self):
        '''
        Gets the Font object to use for the text of the label.
        '''
        return self._font
    
    def to_json(self):
        json= {
            "type": self._type,
            "text": self.text
        }
        if self.placement:
            json["placement"] = self.placement
        if self.x_offset is not None:
            json["xOffset"] = self.x_offset
        if self.y_offset is not None:
            json["yOffset"] = self.y_offset
        if self._color_name:
            json["color"] = self._color_name
        if self.even_pages is not None:
            json["evenPages"] = self.even_pages
        if self.odd_pages is not None:
            json["oddPages"] = self.odd_pages
        if self._font_name: 
            json["font"] = self._font_name
        if self.font_size:
            json["fontSize"] = self.font_size
        return json
