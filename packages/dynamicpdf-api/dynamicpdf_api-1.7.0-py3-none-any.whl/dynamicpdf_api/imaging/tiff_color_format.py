from .color_format import ColorFormat

class TiffColorFormat(ColorFormat):
    def __init__(self, type):
        super().__init__(type)