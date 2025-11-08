import os
from .resource import Resource 
from .resource_type import ResourceType
from .image_resource import ImageResource 
from .endpoint_exception import EndpointException 

class AdditionalResource(Resource):
    def __init__(self, variable, resource_name, type = None):
        super().__init__(variable, resource_name) 
        if type:
            self._type = type
        else:
            self._type = self._get_resource_type(variable)
        self._file_extension = self._get_file_extension()

    def _get_resource_type(self, resource_path):
        file_extension = os.path.splitext(resource_path)[1].lower()
        if file_extension == ".pdf":
            return ResourceType.Pdf
        elif file_extension == ".dlex":
            return ResourceType.Dlex
        elif file_extension == ".json":
            return ResourceType.LayoutData
        elif file_extension in [".ttf", ".otf"]:
            return ResourceType.Font
        elif file_extension in [".tiff", ".tif", ".png", ".gif", ".jpeg", ".jpg", ".bmp"]:
            return ResourceType.Image
        elif file_extension == ".html":
            return ResourceType.Html
        else:
            return ResourceType.LayoutData

    def _get_file_extension(self):
        file_header = self._data[:16]
        if self._type == ResourceType.Image:
            if ImageResource._is_png_image(file_header):
                self._mime_type = "image/png"
                return ".png"
            elif ImageResource._is_jpeg_image(file_header):
                self._mime_type = "image/jpeg"
                return ".jpeg"
            elif ImageResource._is_gif_image(file_header):
                self._mime_type = "image/gif"
                return ".gif"
            elif ImageResource._is_tiff_image(file_header):
                self._mime_type = "image/tiff"
                return ".tiff"
            elif ImageResource._is_jpeg2000_image(file_header):
                self._mime_type = "image/jpeg"
                return ".jpeg"
            elif ImageResource._is_valid_bitmap_image(file_header):
                self._mime_type = "image/bmp"
                return ".bmp"
            else:
                EndpointException("Not supported image type or invalid image.")
        elif self._type == ResourceType.Pdf:
            self._mime_type = "application/pdf"
            return ".pdf"
        elif self._type == ResourceType.LayoutData:
            self._mime_type = "application/json"
            return ".json"
        elif self._type == ResourceType.Dlex:
            self._mime_type = "application/xml"
            return ".dlex"
        elif self._type == ResourceType.Font:
            if self._data[0] == 0x4f and self._data[1] == 0x54 and self._data[2] == 0x54 and self._data[3] == 0x4f:
                self._mime_type = "font/otf"
                return ".otf"
            elif self._data[0] == 0x00 and self._data[1] == 0x01 and self._data[2] == 0x00 and self._data[3] == 0x00:
                self._mime_type = "font/ttf"
                return ".ttf"
            else:
                EndpointException("Unsupported font")
        elif self._type == ResourceType.Html:
            self._mime_type = "text/html"
            return ".html"
        return None
