from .image_size import ImageSize
from .image_size_type import ImageSizeType

class MaxImageSize(ImageSize):
    def __init__(self, max_width=None, max_height=None, unit=None):
        super().__init__(ImageSizeType.Max)
        self.max_width = max_width
        self.max_height = max_height
        self.unit = unit