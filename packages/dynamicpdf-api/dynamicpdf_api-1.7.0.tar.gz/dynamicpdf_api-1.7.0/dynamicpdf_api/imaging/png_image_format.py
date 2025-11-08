from .image_format import ImageFormat
from .image_format_type import ImageFormatType

class PngImageFormat(ImageFormat):
    def __init__(self, color_format = None):
        super().__init__(ImageFormatType.PNG)
        self.color_format = color_format