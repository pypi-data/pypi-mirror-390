from .outline import Outline
from .go_to_action import GoToAction
from .url_action import UrlAction
from .page_zoom import PageZoom

class OutlineList:
    def __init__(self):
        self._outlines = []

    def add(self, text, input = None, page_offset = 0, page_zoom = PageZoom.FitPage):
        '''
        Adds an Outline object to the outline list.

        Args:
            text (strings): Text of the outline.
            input (string |Input): URL the action launches.| Any of the `ImageInput`, `DlexInput`, `PdfInput`,  
            pgOffset (integer): Page number to navigate.
            pgZoom (PageZoom): Page Zoom to display the destination.
        
        Returns:
            The Outline object that is created.
        '''

        if input is None:
            outline = Outline(text)
        elif type(input) == str:
            outline = Outline(text, UrlAction(input))
        else:
            link_to = GoToAction(input)
            link_to.page_offset = page_offset
            link_to.page_zoom = page_zoom
            outline = Outline(text, link_to)
        self._outlines.append(outline)
        return outline

    def add_pdf_outlines(self, pdf_input):
        '''
        Adds an Outline object to the outline list.

        Args:
            pdfInput (PdfInput): PdfInput of type PdfInput object to import outlines to the PDF.
        '''

        self._outlines.append(Outline(pdf_input))

    def to_json(self):
        outlines = []
        for i in self._outlines:
            outlines.append(i.to_json())
        return outlines
