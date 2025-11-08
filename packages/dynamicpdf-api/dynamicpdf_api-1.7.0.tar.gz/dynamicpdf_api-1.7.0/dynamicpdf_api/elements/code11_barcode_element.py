from .text_barcode_element import TextBarcodeElement
from .element_type import ElementType

class Code11BarcodeElement(TextBarcodeElement):
    '''
    This class can be used to place a Code 11 barcode on a page.
    '''

    def __init__(self, value, placement, height, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the Code11BarcodeElement class.

        Args:
            value (string): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            height (integer): The height of the barcode.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
     '''
        super().__init__(value, placement, x_offset, y_offset)

        # Gets or sets the height of the barcode.
        self.height = height
        
        self._type = ElementType.Code11Barcode

    def to_json(self):
        json={
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
        if self._color_name is not None:
            json["color"] = self._color_name
        if self.even_pages is not None:
            json["evenPages"] = self.even_pages
        if self.odd_pages is not None:
            json["oddPages"] = self.odd_pages
        if self.x_dimension is not None:
            json["xDimension"] = self.x_dimension
        if self.font_size is not None:
            json["fontSize"] = self.font_size
        if self.show_text is not None:
            json["showText"] = self.show_text
        if self._font_name is not None:
            json["font"] = self._font_name
        if self._text_color_name is not None:
            json["textColor"] = self._text_color_name
        return json