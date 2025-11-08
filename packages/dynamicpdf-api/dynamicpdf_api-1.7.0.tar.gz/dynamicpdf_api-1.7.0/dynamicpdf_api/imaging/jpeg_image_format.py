from .image_format import ImageFormat
from .image_format_type import ImageFormatType

class JpegImageFormat(ImageFormat):
    def __init__(self, quality=None):
        super().__init__(ImageFormatType.JPEG)
        self.quality = quality