from .image_size import ImageSize
from .image_size_type import ImageSizeType

class PercentageImageSize(ImageSize):
    def __init__(self, horizontal_percentage=None, vertical_percentage=None):
        super().__init__(ImageSizeType.Percentage)
        self.horizontal_percentage = horizontal_percentage
        self.vertical_percentage = vertical_percentage