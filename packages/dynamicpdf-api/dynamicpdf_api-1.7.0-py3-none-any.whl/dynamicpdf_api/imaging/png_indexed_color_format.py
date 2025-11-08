from .png_color_format import PngColorFormat
from .color_format_type import ColorFormatType

class PngIndexedColorFormat(PngColorFormat):
    def __init__(self, quantization_algorithm=None, dithering_percent=None, dithering_algorithm=None):
        super().__init__(ColorFormatType.Indexed)
        self.quantization_algorithm = quantization_algorithm
        self.dithering_percent = dithering_percent
        self.dithering_algorithm = dithering_algorithm