from .dim2_barcode_element import Dim2BarcodeElement
from .element_type import ElementType

class AztecBarcodeElement(Dim2BarcodeElement):
    '''
    Represents an Aztec barcode element.
    '''
    
    def __init__(self, value, placement, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the AztecBarcodeElement class.

        Args:
            value (string | bytes[]): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.</param>
        '''
        
        super().__init__(value, placement, x_offset, y_offset)
        self._type = ElementType.AztecBarcode
        self._text_font = None

        # Gets or Sets a boolean indicating whether to process tilde symbol in the input.
        # Setting True will check for ~ character and processes it for FNC1 or ECI characters.
        self.process_tilde = None

        # Gets or Sets the barcode size
        self.symbol_size = None

        # Gets or Sets the error correction value.
        # Error correction value may be between 5% to 95%.
        self.aztec_error_correction = None

        # Gets or Sets a boolean representing if the barcode is a reader initialization symbol.
        # Setting True will mark the symbol as reader initialization symbol
        self.reader_initialization_symbol = None

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
        if self._value_type is not None:
            json["valueType"] = self._value_type
        if self.process_tilde is not None:
            json["processTilde"] = self.process_tilde
        if self.symbol_size is not None:
            json["symbolSize"] = self.symbol_size
        if self.aztec_error_correction is not None:
            json["aztecErrorCorrection"] = self.aztec_error_correction
        if self.reader_initialization_symbol is not None:
            json["readerInitializationSymbol"] = self.reader_initialization_symbol
        return json
    
