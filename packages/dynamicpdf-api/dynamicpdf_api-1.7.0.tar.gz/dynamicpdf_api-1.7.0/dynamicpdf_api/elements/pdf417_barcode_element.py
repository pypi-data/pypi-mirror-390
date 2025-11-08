from .element_type import ElementType
from .text_barcode_element import TextBarcodeElement

class Pdf417BarcodeElement(TextBarcodeElement):
    '''
    Represents Pdf417 barcode element.

    Remarks:
        This class can be used to generate Pdf417 barcode symbol.
    '''

    def __init__(self, value, placement, columns, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the Pdf417BarcodeElement class.

        Args:
            value (string): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            columns (integer): Columns of the PDF417 barcode.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        '''

        super().__init__(value, placement, x_offset, y_offset)
        self._type = ElementType.PDF417Barcode
        
        # Gets or sets the columns of the barcode.
        self.columns = columns

        # Gets or sets the YDimension of the barcode.
        self.y_dimension = None

        # Gets or Sets a boolean indicating whether to process the tilde character.
        self.process_tilde = None
        
        # Gets or sets the Compact Pdf417.
        self.compact_pdf417 = None

        # Gets or sets the error correction level for the PDF417 barcode.
        self.error_correction = None

        # Gets or sets the type of compaction.
        self.compaction = None

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
        if self.columns is not None:
            json["columns"] = self.columns
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
        if self.y_dimension:
            json["yDimension"] = self.y_dimension
        if self.process_tilde:
            json["processTilde"] = self.process_tilde
        if self.compact_pdf417:
            json["compactPdf417"] = self.compact_pdf417
        if self.error_correction:
            json["errorCorrection"] = self.error_correction
        if self.compaction:
            json["compaction"] = self.compaction
        return json
