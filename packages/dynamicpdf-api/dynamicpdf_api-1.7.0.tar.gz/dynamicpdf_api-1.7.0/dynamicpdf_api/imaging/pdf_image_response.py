from ..response import Response


class PdfImageResponse(Response):
    def __init__(self):
        super().__init__()
        self.image_format = ""
        self.images = []
        self.content_type = ""
        self.horizontal_dpi = 0
        self.vertical_dpi = 0
        
    @property
    def image_format(self):
        return self._image_format

    @image_format.setter
    def image_format(self, value):
        self._image_format = value

    @property
    def images(self):
        return self._images

    @images.setter
    def images(self, value):
        self._images = value

    @property
    def content_type(self):
        return self._content_type

    @content_type.setter
    def content_type(self, value):
        self._content_type = value

    @property
    def horizontal_dpi(self):
        return self._horizontal_dpi

    @horizontal_dpi.setter
    def horizontal_dpi(self, value):
        self._horizontal_dpi = value

    @property
    def vertical_dpi(self):
        return self._vertical_dpi

    @vertical_dpi.setter
    def vertical_dpi(self, value):
        self._vertical_dpi = value

class Image:
    def __init__(self):
        self._page_number = 0
        self._data = ""
        self._billed_pages = 0
        self._width = 0
        self._height = 0

    @property
    def page_number(self):
        return self._page_number

    @page_number.setter
    def page_number(self, value):
        self._page_number = value

    @property
    def data(self):
        return self._data

    @data.setter
    def data(self, value):
        self._data = value

    @property
    def billed_pages(self):
        return self._billed_pages

    @billed_pages.setter
    def billed_pages(self, value):
        self._billed_pages = value

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value

  
   