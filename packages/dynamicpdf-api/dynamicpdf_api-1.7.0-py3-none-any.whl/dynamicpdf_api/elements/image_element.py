from .element import Element
from .element_type import ElementType

class ImageElement(Element):
    '''
    Represents an image element.
    
    Remarks:
        This class can be used to place images on a page.
    '''

    def __init__(self, resource, placement, x_offset = 0, y_offset = 0):
        '''
        Initializes a new instance of the ImageElement class.

        Args:
            resource (ImageResource | string): ImageResource object containing the image resource. | The name of the image resource. 
            placement (ElementPlacement): The placement of the image on the page.
            xOffset (integer): The X coordinate of the barcode.
            yOffset (integer): The Y coordinate of the barcode.
        '''
         
        super().__init__(resource, placement, x_offset, y_offset)
        if isinstance(resource, str):
            self._resource_name = resource
        else:
            self._resource = resource
            self._resource_name = self._resource.resource_name
        self.x_offset = x_offset
        self.y_offset = y_offset
        self._type = ElementType.Image
        self._text_font = None
        
        # Gets or sets the horizontal scale of the image.
        self.scale_x = None

        # Gets or sets the vertical scale of the image.
        self.scale_y = None

        # Gets or sets the maximum height of the image.
        self.max_height = None

        # Gets or sets the maximum width of the image.
        self.max_width = None

    def to_json(self):
        json= {
            "type": self._type
        }
        if self.placement is not None:
            json["placement"] = self.placement
        if self.x_offset is not None:
            json["xOffset"] = self.x_offset
        if self.y_offset is not None:
            json["yOffset"] = self.y_offset
        if self._resource_name is not None:
            json["resourceName"] = self._resource_name
        if self.even_pages is not None:
            json["evenPages"] = self.even_pages
        if self.odd_pages is not None:
            json["oddPages"] = self.odd_pages
        if self.scale_x:
            json["scaleX"]= self.scale_x
        if self.scale_y:
            json["scaleY"]= self.scale_y
        if self.max_height:
            json["maxHeight"]= self.max_height
        if self.max_width:
            json["maxWidth"]= self.max_width
        return json
