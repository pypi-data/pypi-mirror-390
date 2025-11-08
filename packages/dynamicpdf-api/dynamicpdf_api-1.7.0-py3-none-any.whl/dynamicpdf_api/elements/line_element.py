from .element import Element
from .element_type import ElementType

class LineElement(Element):
    '''
    Represents a line page element.
    
    Remarks:
        This class can be used to place lines of different length, width, color and patterns on a page.
    '''

    def __init__(self, placement, x2_offset = 0, y2_offset = 0):
        '''
        Initializes a new instance of the LineElement class.

        Args:
            placement (ElementPlacement): The placement of the line on the page.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        '''

        super().__init__(None, placement, 0, 0)
        self.placement = placement
        self.x2_offset = x2_offset
        self.y2_offset = y2_offset
        self._type = ElementType.Line
        self._color = None
        self._color_name = None
        self._line_style_name = None
        self._line_style = None
        self._text_font = None

        # Gets or sets the width of the line.
        self.width = None   

    @property
    def line_style(self):
        '''
        Gets LineStyle object to use for the style of the line.
        '''
        return self._line_style
    
    @line_style.setter
    def line_style(self, value):
        '''
        Sets LineStyle object to use for the style of the line.
        '''
        self._line_style = value
        self._line_style_name = self._line_style._line_style_string

    @property
    def color(self):
        '''
        Gets the Color object to use for the line.
        '''
        return self._color
        
    @color.setter
    def color(self, value):
        '''
        Sets the Color object to use for the line.
        '''
        self._color = value
        self._color_name = self._color._color_string

    def to_json(self):
        json = {
            "type": self._type
        }
        if self.placement is not None:
            json["placement"] = self.placement
        if self.x_offset is not None:
            json["xOffset"] = self.x_offset
        if self.y_offset is not None:
            json["yOffset"] = self.y_offset
        if self.x2_offset is not None:
            json["x2Offset"] = self.x2_offset
        if self.y2_offset is not None:
            json["y2Offset"] = self.y2_offset
        if self._color_name is not None:
            json["color"] = self._color_name
        if self.even_pages is not None:
            json["evenPages"] = self.even_pages
        if self.odd_pages is not None:
            json["oddPages"] = self.odd_pages
        if self._line_style_name is not None: 
            json["lineStyle"] = self._line_style_name
        if self.width is not None:
            json["width"] = self.width
        return json
    
