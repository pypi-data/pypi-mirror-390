from .image_size import ImageSize
from .image_size_type import ImageSizeType

class DpiImageSize(ImageSize):
    def __init__(self, horizontal_dpi=None, vertical_dpi=None):
        super().__init__(ImageSizeType.Dpi)
        self.horizontal_dpi = horizontal_dpi
        self.vertical_dpi = vertical_dpi