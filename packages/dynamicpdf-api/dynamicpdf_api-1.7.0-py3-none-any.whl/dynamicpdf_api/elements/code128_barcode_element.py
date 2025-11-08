from .text_barcode_element import TextBarcodeElement
from .element_type import ElementType

class Code128BarcodeElement(TextBarcodeElement):
    '''
    Represents a Code 128 barcode element.
    '''
    
    def __init__(self, value, placement, height, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the Code128BarcodeElement class.

        Args:
            value (string): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            height (integer): The height of the barcode.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        
        Remarks:
            Code sets can be specified along with data, in order to do this ProcessTilde property needs to be set to True.
            Example value: "~BHello ~AWORLD 1~C2345", where ~A, ~B and ~C representing code sets A, B and C respectively.
            However if any inline code set has invalid characters it will be shifted to an appropriate code set.
        '''
        
        super().__init__(value, placement, x_offset, y_offset)
        
        # Gets or sets the height of the barcode.
        self.height = height

        # Gets or sets a boolean representing if the barcode is a UCC / EAN Code 128 barcode.
        # If True an FNC1 code will be the first character in the barcode.
        self.ucc_ean128 = None

        # Gets or Sets a boolean indicating whether to process the tilde character.
        # If True checks for fnc1 (~1) character in the barcode Value and checks for the inline code sets if present in the data to process.
        # Example value: "~BHello ~AWORLD 1~C2345", where ~A, ~B and ~C representing code sets A, B and C respectively.
        # However if any inline code set has invalid characters it will be shifted to an appropriate code set.
        # "\" is used as an escape character to add ~.
        self.process_tilde = None
        
        self._type = ElementType.Code128Barcode

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
        if self.process_tilde is not None:
            json['processTilde'] = self.process_tilde
        if self.ucc_ean128 is not None:
            json['uccEan128'] = self.ucc_ean128
        return json
    
