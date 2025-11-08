from .resource import Resource
from .resource_type import ResourceType
from .endpoint_exception import EndpointException

class FontResource(Resource):
    def __init__(self, variable, resource_name = None):
        super().__init__(variable, resource_name)
        self._type = ResourceType.Font

    @property
    def _file_extention(self):
        if self._data[:4] == b"\x4f\x54\x54\x4f":
            self._mime_type = "font/otf"
            return ".otf"
        elif self._data[:4] == b"\x00\x01\x00\x00":
            self._mime_type = "font/ttf"
            return ".ttf"
        else:
            raise EndpointException("Unsupported font")