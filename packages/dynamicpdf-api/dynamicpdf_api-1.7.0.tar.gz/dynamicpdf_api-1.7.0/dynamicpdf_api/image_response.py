import json
from .json_response import JsonResponse

class ImageResponse(JsonResponse):
    '''
    Represents an image response.
    '''

    def __init__(self, image_response = None):
        '''
        Initializes a new instance of the ImageResponse class.
        
        Args:
            imageResponse (string): The image content of the response.
        '''
        super().__init__(image_response)

        # Gets or sets a collection of ImageInformation
        self.content = json.loads(image_response)