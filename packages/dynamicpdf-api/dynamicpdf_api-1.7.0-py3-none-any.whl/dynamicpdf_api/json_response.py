from .response import Response

class JsonResponse(Response):
    '''
    Represents the base class for JSON response.
    '''

    def __init__(self, json_content = None):
        super().__init__()

        # Gets the json content.
        self.json_content = json_content
