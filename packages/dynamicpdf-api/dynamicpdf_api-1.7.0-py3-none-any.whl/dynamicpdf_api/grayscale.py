from .color import Color

class Grayscale(Color):
    '''
    Represents a grayscale color.
    '''

    def __init__(self, gray_level):
        '''
        Initializes a new instance of the Grayscale class.

        Args:
            grayLevel (integer): The gray level for the color.
        '''

        super().__init__()
        self._grayLevel = 0
        if isinstance(gray_level, str):
            self.color_string = gray_level
        else:
            self._gray_level = gray_level

    @staticmethod
    def black():
        '''
        Gets the color black.
        '''
        return Grayscale(0)

    @staticmethod
    def white():
        '''
        Gets the color white.
        '''
        return Grayscale(1)

    @property
    def _color_string(self):
        if self.color_string is not None:
            return self.color_string
        else:
            return f"gray({self._gray_level})"

    @_color_string.setter
    def _color_string(self, value):
        self.color_string = value