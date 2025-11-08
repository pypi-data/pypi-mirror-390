from .resource import Resource
from .resource_type import ResourceType
from .endpoint_exception import EndpointException

class ImageResource(Resource):
    '''
    Represents an image resource used to create an ImageInput 
    object to create PDF from images
    '''

    def __init__(self, image, resource_name = None):
        '''
        Initializes a new instance of the ImageResource class.

        Args:
            image (string | Buffer[]): The image file path. | The byte array of the image file.
            resource_name (string): The name of the resource.
        '''
        
        super().__init__(image, resource_name)
        self._type = ResourceType.Image
        header = self._data[:16]
        if self._is_png_image(header):
            self._mime_type = "image/png"
            self._file_extension = ".png"
        elif self._is_jpeg_image(header) or self._is_jpeg2000_image(header):
            self._mime_type = "image/jpeg"
            self._file_extension = ".jpeg"
        elif self._is_gif_image(header):
            self._mime_type = "image/gif"
            self._file_extension = ".gif"
        elif self._is_tiff_image(header):
            self._mime_type = "image/tiff"
            self._file_extension = ".tiff"
        elif self._is_valid_bitmap_image(header):
            self._mime_type = "image/bmp"
            self._file_extension = ".bmp"
        else:
            raise EndpointException("Not supported image type or invalid image.")

    @staticmethod
    def _is_jpeg2000_image(header):
        return (
            (header[0] == 0x00 and header[1] == 0x00 and header[2] == 0x00 and header[3] == 0x0C and
             header[4] == 0x6A and header[5] == 0x50 and (header[6] == 0x1A or header[6] == 0x20) and 
             (header[7] == 0x1A or header[7] == 0x20) and header[8] == 0x0D and header[9] == 0x0A and 
             header[10] == 0x87 and header[11] == 0x0A) or (header[0] == 0xFF and header[1] == 0x4F and 
             header[2] == 0xFF and header[3] == 0x51 and header[6] == 0x00 and header[7] == 0x00)
        )

    @staticmethod
    def _is_png_image(header):
        return (
            header[0] == 0x89 and header[1] == 0x50 and header[2] == 0x4E and header[3] == 0x47 and 
            header[4] == 0x0D and header[5] == 0x0A and header[6] == 0x1A and header[7] == 0x0A
        )

    @staticmethod    
    def _is_tiff_image(header):
        return (
            (header[0] == 0x49 and header[1] == 0x49 and header[2] == 0x2A and header[3] == 0x00) or 
            (header[0] == 0x4D and header[1] == 0x4D and header[2] == 0x00 and header[3] == 0x2A)
        )

    @staticmethod
    def _is_gif_image(header):
        return (
            header[0] == 0x47 and header[1] == 0x49 and header[2] == 0x46 and header[3] == 0x38
            and (header[4] == 0x37 or header[4] == 0x39) and header[5] == 0x61
        )

    @staticmethod
    def _is_jpeg_image(header):
        return header[0] == 0xFF and header[1] == 0xD8 and header[2] == 0xFF

    @staticmethod
    def _is_valid_bitmap_image(header):
        return header[0] == 0x42 and header[1] == 0x4D
