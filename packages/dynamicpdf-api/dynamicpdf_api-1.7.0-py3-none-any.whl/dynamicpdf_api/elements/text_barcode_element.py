from .barcode_element import BarcodeElement

class TextBarcodeElement(BarcodeElement):
    '''
    Base class from which barcode page elements that display text are derived.
    '''
    
    def __init__(self, value, placement, x_offset = 0, y_offset = 0):
        super().__init__(value, placement, x_offset, y_offset)
        self._font_name = None
        self._resource = None
        self._text_color_name = None
        self._text_color = None
        self._font = None

        # Gets or sets the font size to use when displaying the text.
        self.font_size = None

        # Gets or sets a value indicating if the value should be placed as text below the barcode.
        self.show_text = None
    
    @property
    def _text_font(self):
        '''
        Gets the font of the text.
        '''
        return self.font
    
    @property
    def text_color(self):
        '''
        Gets the color of the text.
        '''
        return self._text_color
    
    @text_color.setter
    def text_color(self, value):
        '''
        Sets the color of the text.
        '''
        self._text_color = value
        self._text_color_name = self._text_color._color_string
    
    @property
    def font(self):
        '''
        Gets the font to use when displaying the text.
        '''
        return self._font
    
    @font.setter
    def font(self, value):
        '''
        Sets the font to use when displaying the text.
        '''
        self._font = value
        self._font_name = self._font._name
        self._resource = self._font._resource
