from .image_format import ImageFormat
from .image_format_type import ImageFormatType

class GifImageFormat(ImageFormat):
    def __init__(self, dithering_percent=None, dithering_algorithm=None):
        super().__init__(ImageFormatType.GIF)
        self.dithering_percent = dithering_percent
        self.dithering_algorithm = dithering_algorithm