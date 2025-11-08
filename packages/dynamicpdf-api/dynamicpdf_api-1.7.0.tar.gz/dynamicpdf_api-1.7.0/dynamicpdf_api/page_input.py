from .input import Input 
from .input_type import InputType
from .unit_converter import UnitConverter
from .page_size import PageSize
from .page_orientation import PageOrientation

class PageInput(Input):
    '''
    Represents a page input.
    '''

    def __init__(self, size = None, orientation = None, margins = None):
        '''
        Initializes a new instance of the PageInput class.

        Args:
            size (PageSize | float): The size of the page. | The width of the page.
            oriientation (PageOrientation | float): The orientation of the page. | The height of the page.
            margins (float): The margins of the page.
        '''

        super().__init__()
        self._elements = []

        # Gets or sets the top margin.
        self.top_margin = margins

        # Gets or sets the bottom margin.
        self.bottom_margin = margins

        # Gets or sets the right margin.
        self.right_margin = margins

        # Gets or sets the left margin.
        self.left_margin = margins

        # Gets or sets the width of the page.
        self.page_width = None

        # Gets or sets the height of the page.
        self.page_height = None

        self._type=InputType.Page

        if type(size) == float or type(size) == int:
            self.page_width = size
            self.page_height = orientation
        else:
            self._page_size = size
            self._page_orientation = orientation
            if self.page_size != None:
                self.page_size = size
            if self.page_orientation != None:
                self.page_orientation = orientation

    @property
    def page_size(self):
        '''
        Gets the Page size.
        '''
        return self._page_size

    @page_size.setter
    def page_size(self, value):
        '''
        Sets the Page size.
        '''
        self._page_size = value
        smaller, larger = UnitConverter._get_paper_size(value)
        if self._page_orientation == PageOrientation.Landscape:
            self.page_height = smaller
            self.page_width = larger
        else:
            self.page_height = larger
            self.page_width = smaller

    @property
    def page_orientation(self):
        '''
        Gets page orientation.
        '''
        return self._page_orientation

    @page_orientation.setter
    def page_orientation(self, value):
        '''
        Sets page orientation.
        '''
        self._page_orientation = value
        if self.page_width != None and self.page_height != None:
            if self.page_width > self.page_height:
                smaller = self.page_height
                larger = self.page_width
            else:
                smaller = self.page_width
                larger = self.page_height

            if self.page_orientation == PageOrientation.Landscape:
                self.page_height = smaller
                self.page_width = larger
            else:
                self.page_height = larger
                self.page_width = smaller

    @property
    def elements(self):
        '''
        Gets the elements of the page.
        '''
        return self._elements

    def to_json(self): 
        json = {
            "type": self._type,
            "id": self.id
        } 
        if self.resource_name is not None:
            json["resourceName"] = self.resource_name   
        elements = []
        for i in self.elements:
            elements.append(i.to_json())
        if len(elements) > 0:
            json["elements"] = elements
        if self.page_height is not None:
            json["pageHeight"] = self.page_height
        if self.page_width is not None:
            json["pageWidth"] = self.page_width   
        if self._template_id is not None:
            json["templateId"] = self._template_id
        if self.top_margin is not None:
            json["topMargin"] = self.top_margin
        if self.left_margin is not None:
            json["leftMargin"] = self.left_margin
        if self.bottom_margin is not None:
            json["bottomMargin"] = self.bottom_margin
        if self.right_margin is not None:
            json["rightMargin"] = self.right_margin
        return json
