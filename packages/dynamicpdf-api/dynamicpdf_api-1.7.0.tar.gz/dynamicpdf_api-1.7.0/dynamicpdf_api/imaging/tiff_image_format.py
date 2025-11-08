from .image_format import ImageFormat
from .image_format_type import ImageFormatType

class TiffImageFormat(ImageFormat):
    def __init__(self, multi_page=False, color_format=None):
        super().__init__(ImageFormatType.TIFF)
        self.multi_page = multi_page
        self.color_format = color_format