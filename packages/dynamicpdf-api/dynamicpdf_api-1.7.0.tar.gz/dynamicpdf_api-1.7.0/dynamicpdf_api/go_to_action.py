from .page_zoom import PageZoom
from .action import Action

class GoToAction(Action):
    '''
    Represents a goto action in a PDF document that navigates 
    to a specific page using page number and zoom options.
    '''

    def __init__(self, input, page_offset = 0, page_zoom = PageZoom.FitPage):
        '''
        Initializes a new instance of the  GoToAction class using an
        input to create the PDF, page number, and a zoom option.

        Args:
            input (Input): Any of the ImageInput, DlexInput or PdfInput objects to create PDF
            pageOffset (integer): Page number to navigate
            pageZoom (pageZoom): PageZoom to display the destination
        '''

        super().__init__()
        self._input = input
        self._input_id = input.id

        # Gets or sets page Offset.
        self.page_offset = page_offset

        # Gets or sets PageZoom to display the destination.
        self.page_zoom = page_zoom

    def to_json(self):
        return {
            "inputID": self._input_id,
            "pageOffset": self.page_offset,
            "pageZoom": self.page_zoom
        }