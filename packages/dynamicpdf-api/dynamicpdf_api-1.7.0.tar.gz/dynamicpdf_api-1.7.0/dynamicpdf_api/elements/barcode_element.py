from .element import Element

class BarcodeElement(Element):
    '''
    Base class from which barcode page elements are derived.
    '''
    
    def __init__(self, value, placement, x_offset, y_offset):
        super().__init__(value, placement, x_offset, y_offset)
        self._color_name = None
        self._color = None
        self.x_dimension = None

    @property
    def value(self):
        '''
        Gets the value of the barcode.
        '''
        return self._input_value
    
    @value.setter
    def value(self, input):
        '''
        Sets the value of the barcode.
        '''
        self._input_value = input

    @property
    def color(self):
        '''
        Gets the Color of the barcode.
        '''
        return self._color
    
    @color.setter
    def color(self, value):
        '''
        Sets the Color of the barcode.
        '''
        self._color = value
        self._color_name = self._color._color_string
