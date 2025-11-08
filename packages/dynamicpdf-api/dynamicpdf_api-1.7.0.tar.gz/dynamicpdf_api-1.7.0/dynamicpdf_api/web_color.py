from .rgb_color import RgbColor

class WebColor(RgbColor):
    '''
    Represents an RGB color created using the web hexadecimal convention.
    '''

    def __init__(self, web_hex_string):
        '''
        Initializes a new instance of the WebColor class.

        Args:
            webHexString (string): The hexadecimal string representing the color.
        '''
        self._color_string = web_hex_string
