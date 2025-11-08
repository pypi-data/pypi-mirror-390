from .text_barcode_element import TextBarcodeElement
from .element_type import ElementType

class StackedGs1DataBarBarcodeElement(TextBarcodeElement):
    '''
    Represents a StackedGS1DataBar barcode element.
    
    Remarks:
        This class can be used to place StackedGS1DataBar barcode on a page.
    '''

    def __init__(self, value, placement, stacked_gs1_data_bar_type, row_height, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the StackedGs1DataBarBarcodeElement class.

        Args:
            value (string): The value of the barcode.
            placement (ElementPlacement): The placement of the barcode on the page.
            stackedGs1DataBarType (StackedGs1DataBarType): The StackedGs1DataBarType of the barcode.
            rowHeight (integer): The row height of the barcode.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        '''

        super().__init__(value, placement, x_offset, y_offset)
        self._stacked_gs1_data_bar_type = stacked_gs1_data_bar_type
        self._type = ElementType.StackedGS1DataBarBarcode
        
        # Gets or sets the row height of the barcode.
        self.row_height = row_height

        # Gets or Sets the segment count of the Expanded Stacked barcode.
        # This is used only for the ExpandedStacked Gs1DataBar type.
        self.expanded_stacked_segment_count = None

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
        if self._stacked_gs1_data_bar_type is not None:
            json["stackedGs1DataBarType"] = self._stacked_gs1_data_bar_type
        if self.row_height is not None:
            json["rowHeight"] = self.row_height
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
        if self.expanded_stacked_segment_count is not None:
            json["expandedStackedSegmentCount"] = self.expanded_stacked_segment_count,
        return json
