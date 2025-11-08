from .png_color_format import PngColorFormat
from .color_format_type import ColorFormatType

class PngMonochromeColorFormat(PngColorFormat):
    def __init__(self, black_threshold=None, dithering_percent=None, dithering_algorithm=None):
        super().__init__(ColorFormatType.Monochrome)
        self.black_threshold = black_threshold
        self.dithering_percent = dithering_percent
        self.dithering_algorithm = dithering_algorithm