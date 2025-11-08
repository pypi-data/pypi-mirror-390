from .tiff_color_format import TiffColorFormat
from .color_format_type import ColorFormatType

class TiffIndexedColorFormat(TiffColorFormat):
    def __init__(self, quantization_algorithm=None, dithering_percent=None, dithering_algorithm=None):
        super().__init__(ColorFormatType.Indexed)
        self.quantization_algorithm = quantization_algorithm
        self.dithering_percent = dithering_percent
        self.dithering_algorithm = dithering_algorithm