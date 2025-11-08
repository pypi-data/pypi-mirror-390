from .element_type import ElementType
from .element import Element

class PageNumberingElement(Element):
    """
    Represents a page numbering label page element.

    This class can be used to add page numbering to a PDF document. The following tokens can be used within the
    text of a PageNumberingLabel. They will be replaced with the appropriate value when the PDF is output.

    Token    Description
    ------   -----------
    CP       Current page. The default numbering style is numeric.
    TP       Total pages. The default numbering style is numeric.
    SP       Section page.
    ST       Section Total.
    PR       Prefix.

    All tokens except the /%/%PR/%/% token can also contain a numbering style specifier. The numbering style specifier
    is placed in parenthesis after the token.

    Numbering Style    Description
    ----------------   -----------
    1                  Numeric. Arabic numbers are used: 1, 2, 3, etc.
    i                  Lower Case Roman Numerals. Lower case roman numerals are used: i, ii, iii, etc.
    I                  Upper Case Roman Numerals. Upper case roman numerals are used: I, II, III, etc.
    a                  Lower Latin Letters. Lower case Latin letters are used: a, b, c, etc. After z, aa is used followed by bb, cc, etc.
    A                  Upper Latin Letters. Upper case Latin letters are used: A, B, C, etc. After Z, AA is used followed by BB, CC, etc.
    b                  Lower Latin Letters. Lower case Latin letters are used: a, b, c, etc. After z, aa is used followed by ab, ac, etc.
    B                  Lower Latin Letters. Lower case Latin letters are used: A, B, C, etc. After Z, AA is used followed by AB, AC, etc.

    There should be no spaces within a token, only the token and optional numbering style specifier.
    """
        
    def __init__(self, text, placement, x_offset = 0, y_offset = 0):
        """
        Initializes a new instance of the PageNumberingElement class.

        Args:
            text (str): Text to display in the label.
            placement (ElementPlacement): The placement of the page numbering element on the page.
            xOffset (float): X coordinate of the label.
            yOffset (float): Y coordinate of the label.
        """

        super().__init__(text, placement, x_offset, y_offset)
        self._type = ElementType.PageNumbering
        self._resource = None
        self._font = None
        self._color = None
        self._font_name = None
        self._color_name = None
        self.font_size = None

    @property
    def font(self):
        '''
        Gets the Font object to use for the text of the label.
        '''
        return self._font
    
    @font.setter
    def font(self, value):
        '''
        Sets the Font object to use for the text of the label.
        '''
        self._font = value
        self._font_name = self._font._name
        self._resource = self._font._resource

    
    @property
    def text(self):
        '''
        Gets the text to display in the label.
        '''
        return self._input_value

    @text.setter
    def text(self, value):
        '''
        Sets the text to display in the label.
        '''
        self._input_value = value

    @property
    def _text_font(self):
        '''
        Gets the font object.
        '''
        return self._font

    @property
    def color(self):
        '''
        Gets the Color object to use for the text of the label.
        '''
        return self._color

    @color.setter
    def color(self, value):
        '''
        Sets the Font Color to use for the text of the label.
        '''
        self._color = value
        self._color_name = self._color._color_string

    def to_json(self):
        json = {
            "type": self._type,
            "text": self.text
        }
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
        if self.font_size is not None:
            json["fontSize"] = self.font_size
        if self._font_name is not None:
            json["font"] = self._font_name
        return json
