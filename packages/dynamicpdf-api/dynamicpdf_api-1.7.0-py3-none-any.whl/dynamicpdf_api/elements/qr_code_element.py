from .element_type import ElementType
from .text_barcode_element import TextBarcodeElement

class QrCodeElement(TextBarcodeElement):
    '''
    Represents a QR code barcode element.
    '''

    def __init__(self, value, placement, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the QrCodeElement class.

        Args:
            value (string): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        '''
        
        super().__init__(value, placement, x_offset, y_offset)
        self._type = ElementType.QRCode

        # Gets or sets the QR code version.
        self.version = None

        # Gets or sets FNC1 mode.
        self.fnc1 = None
        

    def to_json(self):
        json = {
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
        if self.version is not None:
            json['version'] = self.version
        if self.fnc1 is not None:
            json['fnc1'] = self.fnc1
        return json
