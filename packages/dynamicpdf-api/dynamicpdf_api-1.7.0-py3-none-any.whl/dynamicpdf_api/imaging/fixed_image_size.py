from .image_size import ImageSize
from .image_size_type import ImageSizeType

class FixedImageSize(ImageSize):
    def __init__(self, width=None, height=None, unit=None):
        super().__init__(ImageSizeType.Fixed)
        self.width = width
        self.height = height
        self.unit = unit