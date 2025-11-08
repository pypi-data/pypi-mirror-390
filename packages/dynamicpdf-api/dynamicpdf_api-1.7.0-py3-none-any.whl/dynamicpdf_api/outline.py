from .merge_options import MergeOptions

class Outline:
    '''
    Represents an outline.
    '''
    
    def __init__(self, pdf_input, action = None):
        '''
        Initializes a new instance of the Outline class.

        Args:
            pdfInput (PdfInpout | string): The input of type PdfInput. | text for the outline.
            action (Action): Action of the outline.
        '''

        self._color_name = None

        # Gets or sets the text of the outline.
        self.text = None

        # Gets or sets the style of the outline.
        self.style = None

        # Gets or sets a value specifying if the outline is expanded.
        self.expanded = False

        self._children = None

        # Gets or sets the Action of the outline.
        self.action = action
        self._from_input_id = None
        self._color = None

        if type(pdf_input) != str:
            self._from_input_id = pdf_input.id
        else:
            self.text = pdf_input
            self.action = action
    
    @property
    def color(self):
        '''
        Gets the color of the outline.
        '''
        return self._color
    
    @color.setter
    def color(self, value):
        '''
        Sets the color of the outline.
        '''
        self._color = value
        self._color_name = value._color_string
    
    @property
    def children(self):
        '''
        Gets a collection of child outlines.
        '''
        if self._children is None:     
            from .outline_list import OutlineList
            self._children = OutlineList()
        return self._children
    
    @property
    def _get_children(self):
        '''
        Gets a collection of child outlines.
        '''
        if self._children is not None:
            return self._children._outlines
        return None
    
    def to_json(self):
        json= {}
        if self._color_name:
            json['color'] = self._color_name
        if self.expanded is not None:
            json['expanded'] = self.expanded
        if self.text:
            json['text'] = self.text
        if self._from_input_id:
            json['fromInputID'] = self._from_input_id
        if self.style:
            json["style"] = self.style
        if self.action:
            json["linkTo"] = self.action.to_json()
        if self._children:
            json['children'] = self.children.to_json()
        return json