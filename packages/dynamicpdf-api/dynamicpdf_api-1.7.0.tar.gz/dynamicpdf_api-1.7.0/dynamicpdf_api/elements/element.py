from .element_placement import ElementPlacement

class Element:
    '''
    Base class from which all page elements are derived.
    '''

    def __init__(self, value, placement, x_offset, y_offset):
        if placement is None:
            self.placement = ElementPlacement.TopLeft
        self._input_value = value
        self._resource = None
        self._type = None

        # Gets and sets placement of the page element on the page.
        self.placement = placement

        # Gets or sets the X coordinate of the page element.
        self.x_offset = x_offset

        # Gets or sets the Y coordinate of the page element.
        self.y_offset = y_offset

        # Gets or sets the boolean value specifying whether the element should be added to even pages or not.
        self.even_pages = None

        # Gets or sets the boolean value specifying whether the element should be added to odd pages or not.
        self.odd_pages = None
