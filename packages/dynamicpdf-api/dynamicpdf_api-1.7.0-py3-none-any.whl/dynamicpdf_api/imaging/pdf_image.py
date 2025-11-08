from ..endpoint_exception import EndpointException
from ..endpoint import Endpoint
from .pdf_image_response import PdfImageResponse, Image
from .dpi_image_size import DpiImageSize
from .fixed_image_size import FixedImageSize
from .max_image_size import MaxImageSize
from .percentage_image_size import PercentageImageSize
from .gif_image_format import GifImageFormat
from .jpeg_image_format import JpegImageFormat
from .png_image_format import PngImageFormat
from .png_indexed_color_format import PngIndexedColorFormat
from .png_monochrome_color_format import PngMonochromeColorFormat
from .tiff_image_format import TiffImageFormat
from .tiff_indexed_color_format import TiffIndexedColorFormat
from .tiff_monochrome_color_format import TiffMonochromeColorFormat
from .bmp_image_format import BmpImageFormat
from .bmp_monochrome_color_format import BmpMonochromeColorFormat
from ..pdf_resource import PdfResource
import asyncio
import json
from concurrent.futures import ThreadPoolExecutor

class PdfImage(Endpoint):
    '''
    Represents a PDF Rasterizing endpoint that converts PDF to image.
    '''

    def __init__(self, resource):
        super().__init__()

        self.resource = resource
        self.start_page_number = None
        self.page_count = None
        self.image_format = None
        self.image_size = None
        self._endpoint_name = "pdf-image"

    def process(self):
        '''
        Process the PDF to create Images.
        '''
        return asyncio.get_event_loop().run_until_complete(self.process_async())
    
    async def process_async(self):
        '''
        Process PDF asynchronously to create Images.
        '''
        rest_client = self.create_rest_request()
        files = []
        files.append(('pdf',(
                    self.resource.resource_name,  
                    self.resource._data, 
                    self.resource._mime_type)
                ))
      
        data = {}

        if self.start_page_number is not None:
            data["sp"] = self.start_page_number
        if self.page_count is not None:
            data["pc"] = self.page_count

        if self.image_size is not None:
            self._add_image_size_params(data)

        if self.image_format is not None:
            self._add_image_format_params(data)
        
        with ThreadPoolExecutor() as executor:
            rest_response = executor.submit(rest_client.post, self.url, files=files, data=data).result()
        
        response = PdfImageResponse()
        response.images = []
        response.status_code = rest_response.status_code

        if rest_response.status_code == 200:
            pdf_image = json.loads(rest_response.content)
                
            image_type = pdf_image['contentType']
            response.content_type = image_type
            response.horizontal_dpi = pdf_image['horizontalDpi']
            response.vertical_dpi = pdf_image['verticalDpi']
            response.image_format = image_type.split('/')[-1]
            
            for img in pdf_image['images']:
                    image = Image()
                    image.page_number = img.get('pageNumber', 0)
                    image.data = img.get('data', '')
                    image.billed_pages = img.get('billedPages', 0)
                    image.width = img.get('width', 0)
                    image.height = img.get('height', 0)
                    response.images.append(image)
                    
            response.is_successful = True
        elif rest_response.status_code == 401:
            raise EndpointException("Invalid api key specified.")
        else:
            error_json = json.loads(rest_response.content)
            response.error_json = error_json
            response.error_id = error_json['id']
            response.error_message = error_json['message']
            response.is_successful = False

        return response
    
    def _add_image_size_params(self, data):
        if isinstance(self.image_size, DpiImageSize):
            data["is"] = self.image_size.type.value
            if self.image_size.horizontal_dpi:
                data["hd"] = self.image_size.horizontal_dpi
            if self.image_size.vertical_dpi:
                data["vd"] = self.image_size.vertical_dpi
        elif isinstance(self.image_size, FixedImageSize):
            data["is"] = self.image_size.type.value
            if self.image_size.height:
                data["ht"] = self.image_size.height
            if self.image_size.width:
                data["wd"] = self.image_size.width
            if self.image_size.unit:
                data["ut"] = self.image_size.unit.value
        elif isinstance(self.image_size, MaxImageSize):
            data["is"] = self.image_size.type.value
            if self.image_size.max_height:
                data["mh"] = self.image_size.max_height
            if self.image_size.max_width:
                data["mw"] = self.image_size.max_width
            if self.image_size.unit:
                data["ut"] = self.image_size.unit.value
        elif isinstance(self.image_size, PercentageImageSize):
            data["is"] = self.image_size.type.value
            if self.image_size.horizontal_percentage:
                data["hp"] = self.image_size.horizontal_percentage
            if self.image_size.vertical_percentage:
                data["vp"] = self.image_size.vertical_percentage

    def _add_image_format_params(self, data):
        if isinstance(self.image_format, GifImageFormat):
            data["if"] = self.image_format.type.value
            if self.image_format.dithering_percent:
                data["dp"] = self.image_format.dithering_percent
            if self.image_format.dithering_algorithm:
                data["da"] = self.image_format.dithering_algorithm.value
        elif isinstance(self.image_format, JpegImageFormat):
            data["if"] = self.image_format.type.value
            if self.image_format.quality:
                data["qt"] = self.image_format.quality
        elif isinstance(self.image_format, PngImageFormat):
            data["if"] = self.image_format.type.value
            if self.image_format.color_format:
                data["cf"] = self.image_format.color_format.type.value
                if isinstance(self.image_format.color_format, PngIndexedColorFormat):
                    if self.image_format.color_format.dithering_algorithm:
                        data["da"] = self.image_format.color_format.dithering_algorithm.value
                    if self.image_format.color_format.dithering_percent:
                        data["dp"] = self.image_format.color_format.dithering_percent
                    if self.image_format.color_format.quantization_algorithm:
                        data["qa"] = self.image_format.color_format.quantization_algorithm.value
                elif isinstance(self.image_format.color_format, PngMonochromeColorFormat):
                    if self.image_format.color_format.black_threshold:
                        data["bt"] = self.image_format.color_format.black_threshold
                    if self.image_format.color_format.dithering_algorithm:
                        data["da"] = self.image_format.color_format.dithering_algorithm.value
                    if self.image_format.color_format.dithering_percent:
                        data["dp"] = self.image_format.color_format.dithering_percent
        elif isinstance(self.image_format, TiffImageFormat):
            data["if"] = self.image_format.type.value
            if self.image_format.multi_page:
                data["mp"] = "true"
            if self.image_format.color_format:
                data["cf"] = self.image_format.color_format.type.value
                if isinstance(self.image_format.color_format, TiffIndexedColorFormat):
                    if self.image_format.color_format.dithering_algorithm:
                        data["da"] = self.image_format.color_format.dithering_algorithm.value
                    if self.image_format.color_format.dithering_percent:
                        data["dp"] = self.image_format.color_format.dithering_percent
                    if self.image_format.color_format.quantization_algorithm:
                        data["qa"] = self.image_format.color_format.quantization_algorithm.value
                elif isinstance(self.image_format.color_format, TiffMonochromeColorFormat):
                    if self.image_format.color_format.compression_type:
                        data["ct"] = self.image_format.color_format.compression_type.value
                    if self.image_format.color_format.black_threshold:
                        data["bt"] = self.image_format.color_format.black_threshold
                    if self.image_format.color_format.dithering_algorithm:
                        data["da"] = self.image_format.color_format.dithering_algorithm.value
                    if self.image_format.color_format.dithering_percent:
                        data["dp"] = self.image_format.color_format.dithering_percent
        elif isinstance(self.image_format, BmpImageFormat):
            data["if"] = self.image_format.type.value
            if self.image_format.color_format:
                data["cf"] = self.image_format.color_format.type.value
                if isinstance(self.image_format.color_format, BmpMonochromeColorFormat):
                    if self.image_format.color_format.black_threshold:
                        data["bt"] = self.image_format.color_format.black_threshold
                    if self.image_format.color_format.dithering_percent:
                        data["dp"] = self.image_format.color_format.dithering_percent
                    if self.image_format.color_format.dithering_algorithm:
                        data["da"] = self.image_format.color_format.dithering_algorithm.value
