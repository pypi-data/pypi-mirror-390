from .color_format import ColorFormat
from .color_format_type import ColorFormatType

class BmpColorFormat(ColorFormat):
    def __init__(self, type):
        super().__init__(type if type == ColorFormatType.Monochrome else ColorFormatType.Rgb)