from .element import Element
from .element_type import ElementType

class RectangleElement(Element):
    '''
    Represents a rectangle page element.
    
    Remarks:
        This class can be used to place rectangles of any size or color on a page.
    '''
    
    def __init__(self, placement, width, height):
        '''
        Initializes a new instance of the RectangleElement class.

        Args:
            placement (ElementPlacement): The placement of the barcode on the page.
            width (integer): Width of the rectangle.
            height (integer): Height of the rectangle.
        '''

        super().__init__(None, placement, width, height)
        self._type = ElementType.Rectangle
        self._fill_color = None
        self._border_color = None
        self._border_style = None
        self._fill_color_name = None
        self._border_color_name = None
        self._border_style_name = None
        self._text_font = None
        
        # Gets or sets the width of the rectangle.
        self.width = width

        # Gets or sets the height of the rectangle.
        self.height = height

        # Gets or sets the border width of the rectangle.
		# To force the borders not to appear set the border width to any value 0 or less.
        self.border_width = None

        # Gets or sets the corner radius of the rectangle.
        self.corner_radius = None
    
    @property
    def fill_color(self):
        '''
        Gets the Color object to use for the fill of the rectangle.
        '''
        return self._fill_color
    
    @fill_color.setter
    def fill_color(self, value):
        '''
        Sets the Color object to use for the fill of the rectangle.
        '''
        self._fill_color = value
        self._fill_color_name = self._fill_color._color_string

    @property
    def border_color(self):
        '''
        Gets the Color object to use for the border of the rectangle.
        '''
        return self._border_color
    
    @border_color.setter
    def border_color(self, value):
        '''
        Sets the Color object to use for the border of the rectangle.
        '''
        self._border_color = value
        self._border_color_name = self._border_color._color_string

    @property
    def border_style(self):
        '''
        Gets the LineStyle object used to specify the border style of the rectangle.
        '''
        return self._border_style
    
    @border_style.setter
    def border_style(self, value):
        '''
        Sets the LineStyle object used to specify the border style of the rectangle.
        '''
        self._border_style = value
        self._border_style_name = self._border_style._line_style_string

    def to_json(self):
        json= {
            "type": self._type
        }
       
        if self.placement is not None:
            json["placement"] = self.placement
        if self.x_offset is not None:
            json["xOffset"] = self.x_offset
        if self.y_offset is not None:
            json["yOffset"] = self.y_offset
        if self.width is not None:
            json["width"] = self.width
        if self.height:
            json["height"] = self.height
        if self.even_pages is not None:
            json["evenPages"] = self.even_pages
        if self.odd_pages is not None:
            json["oddPages"] = self.odd_pages
        if self._fill_color_name:
            json["fillColor"]= self._fill_color_name
        if self._border_color_name:
            json["borderColor"]= self._border_color_name
        if self._border_style_name:
            json["borderStyle"]= self._border_style_name
        if self.corner_radius:
            json["cornerRadius"]= self.corner_radius
        if self.border_width:
            json["borderWidth"]= self.border_width
        return json
