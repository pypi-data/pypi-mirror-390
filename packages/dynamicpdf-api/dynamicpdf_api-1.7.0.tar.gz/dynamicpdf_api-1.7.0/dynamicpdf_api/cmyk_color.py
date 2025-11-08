from .color import Color
from .endpoint_exception import EndpointException

class CmykColor(Color):
    '''
    Represents a CMYK color.
    '''

    def __init__(self, cyan, magenta, yellow, black):
        '''
         Initializes a new instance of the CmykColor class.

        Args:
            cyan (float): The cyan intensity.
            magenta (float): The magenta intensity.
            yellow (float): The yellow intensity.
            black (float): The black intensity.

        Remarks:
            Values must be between 0.0 and 1.0.
        '''

        super().__init__()
        self._cyan = 0
        self._magenta = 0
        self._yellow = 0
        self._black = 0

        if isinstance(cyan, str):
            self.color_string = cyan
        else:
            if (cyan < 0.0 or cyan > 1.0 or magenta < 0.0 or magenta > 1.0 or 
                yellow < 0.0 or yellow > 1.0 or black < 0.0 or black > 1.0):
                raise EndpointException("CMYK values must be from 0.0 to 1.0.")
            self._cyan = cyan
            self._magenta = magenta
            self._yellow = yellow
            self._black = black

    @staticmethod
    def black():
        """
        Gets the color black.
        """
        return CmykColor(1, 1, 1, 1)

    @staticmethod
    def white():
        """
        Gets the color white.
        """
        return CmykColor(0, 0, 0, 0)

    @property
    def _color_string(self):
        if self.color_string is not None:
            return self.color_string
        else:
            return f"cmyk({self._cyan},{self._magenta},{self._yellow},{self._black})"

    @_color_string.setter
    def _color_string(self, value):
        self.color_string = value