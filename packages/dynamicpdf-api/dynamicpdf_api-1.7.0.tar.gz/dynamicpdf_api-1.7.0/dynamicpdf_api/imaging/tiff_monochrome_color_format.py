from .tiff_color_format import TiffColorFormat
from .color_format_type import ColorFormatType

class TiffMonochromeColorFormat(TiffColorFormat):
    def __init__(self, black_threshold=None, compression_type=None, dithering_percent=None, dithering_algorithm=None):
        super().__init__(ColorFormatType.Monochrome)
        self.black_threshold = black_threshold
        self.compression_type = compression_type
        self.dithering_percent = dithering_percent
        self.dithering_algorithm = dithering_algorithm