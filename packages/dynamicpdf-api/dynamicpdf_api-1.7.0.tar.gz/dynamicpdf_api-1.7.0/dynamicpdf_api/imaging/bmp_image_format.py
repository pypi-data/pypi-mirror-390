from .image_format import ImageFormat
from .image_format_type import ImageFormatType

class BmpImageFormat(ImageFormat):
    def __init__(self, color_format = None):
        super().__init__(ImageFormatType.BMP)
        self.color_format = color_format