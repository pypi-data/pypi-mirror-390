from .element_type import ElementType
from .text_barcode_element import TextBarcodeElement

class MsiBarcodeElement(TextBarcodeElement):
    '''
    Represents a MSI Barcode element (also known as Modified Plessey).
    '''

    def __init__(self, value, placement, height, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the MsiBarcodeElement class.

        Args:
            value (string): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            height (integer): The height of the barcode.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        '''

        super().__init__(value, placement, x_offset, y_offset)
        self._type = ElementType.MSIBarcode
        
        # Gets or sets the height of the barcode.
        self.height = height
        
        # Gets or sets a value specifying if the check digit should calculated.
        self.append_check_digit = None

    def to_json(self):
        json= {
            "type": self._type
        }
        if self.value is not None:
            json["value"] = self.value
        if self.placement is not None:
            json["placement"] = self.placement
        if self.x_offset is not None:
            json["xOffset"] = self.x_offset
        if self.y_offset is not None:
            json["yOffset"] = self.y_offset
        if self.height is not None:
            json["height"] = self.height
        if self._color_name:
            json["color"] = self._color_name
        if self.even_pages is not None:
            json["evenPages"] = self.even_pages
        if self.odd_pages is not None:
            json["oddPages"] = self.odd_pages
        if self.x_dimension:
            json["xDimension"] = self.x_dimension
        if self.font_size:
            json["fontSize"] = self.font_size
        if self.show_text is not None:
            json["showText"] = self.show_text
        if self._font_name:
            json["font"] = self._font_name
        if self._text_color_name:
            json["textColor"] = self._text_color_name
        if self.append_check_digit:
            json["appendCheckDigit"] = self.append_check_digit
        return json
