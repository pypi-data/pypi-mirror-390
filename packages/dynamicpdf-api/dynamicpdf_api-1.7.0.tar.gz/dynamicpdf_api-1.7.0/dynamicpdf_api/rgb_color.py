from .color import Color
from .endpoint_exception import EndpointException

class RgbColor(Color):
    '''
    Represents an RGB color.
    '''

    def __init__(self, red, green = 0, blue = 0):
        '''
        Initializes a new instance of the RgbColor class.

        Args:
            red (integer): The red intensity.
            green (integer): The green intensity.
            blue (integer): The blue intensity.
        '''

        super().__init__()
        if type(red) != str:
            if red < 0.0 or red > 1.0 or green < 0.0 or green > 1.0 or blue < 0.0 or blue > 1.0:
                raise EndpointException("RGB values must be from 0.0 to 1.0.")
            self._red = red
        else:
            self.color_string = red
        self._green = green
        self._blue = blue

    @property
    def _color_string(self):
        if self.color_string is not None:
            return self.color_string
        else:
            return f"rgb({self._red}, {self._green}, {self._blue})"

    @_color_string.setter
    def _color_string(self, value):
        self.color_string = value

    @staticmethod
    def red():
        """
        Gets the color red.
        """
        return RgbColor("Red")

    @staticmethod
    def blue():
        """
        Gets the color blue.
        """
        return RgbColor("Blue")

    @staticmethod
    def green():
        """
        Gets the color green.
        """
        return RgbColor("Green")

    @staticmethod
    def black():
        """
        Gets the color black.
        """
        return RgbColor("Black")

    @staticmethod
    def silver():
        """
        Gets the color silver.
        """
        return RgbColor("Silver")

    @staticmethod
    def dark_gray():
        """
        Gets the color dark grey.
        """
        return RgbColor("DarkGray")

    @staticmethod
    def gray():
        """
        Gets the color grey.
        """
        return RgbColor("Gray")

    @staticmethod
    def dim_gray():
        """
        Gets the color dim grey.
        """
        return RgbColor("DimGray")

    @staticmethod
    def white():
        """
        Gets the color white.
        """
        return RgbColor("White")

    @staticmethod
    def lime():
        """
        Gets the color lime.
        """
        return RgbColor("Lime")

    @staticmethod
    def aqua():
        """
        Gets the color aqua.
        """
        return RgbColor("Aqua")

    @staticmethod
    def purple():
        """
        Gets the color purple.
        """
        return RgbColor("Purple")

    @staticmethod
    def cyan():
        """
        Get the color cyan.
        """
        return RgbColor("Cyan")

    @staticmethod
    def magenta():
        """
        Get the color magenta.
        """
        return RgbColor("Magenta")

    @staticmethod
    def yellow():
        """
        Get the color yellow.
        """
        return RgbColor("Yellow")

    @staticmethod
    def alice_blue():
        """
        Get the color alice blue.
        """
        return RgbColor("AliceBlue")

    @staticmethod
    def antique_white():
        """
        Get the color antique white.
        """
        return RgbColor("AntiqueWhite")

    @staticmethod
    def aquamarine():
        """
        Get the color aquamarine.
        """
        return RgbColor("Aquamarine")

    @staticmethod
    def azure():
        """
        Get the color azure.
        """
        return RgbColor("Azure")

    @staticmethod
    def beige():
        """
        Get the color beige.
        """
        return RgbColor("Beige")

    @staticmethod
    def bisque():
        """
        Get the color bisque.
        """
        return RgbColor("Bisque")

    @staticmethod
    def blanched_almond():
        """
        Get the color blanched almond.
        """
        return RgbColor("BlanchedAlmond")

    @staticmethod
    def blue_violet():
        """
        Get the color blue violet.
        """
        return RgbColor("BlueViolet")

    @staticmethod
    def brown():
        """
        Get the color brown.
        """
        return RgbColor("Brown")

    @staticmethod
    def burly_wood():
        """
        Get the color burly wood.
        """
        return RgbColor("BurlyWood")

    @staticmethod
    def cadet_blue():
        """
        Get the color cadet blue.
        """
        return RgbColor("CadetBlue")

    @staticmethod
    def chartreuse():
        """
        Get the color chartreuse.
        """
        return RgbColor("Chartreuse")

    @staticmethod
    def chocolate():
        """
        Get the color chocolate.
        """
        return RgbColor("Chocolate")

    @staticmethod
    def coral():
        """
        Get the color coral.
        """
        return RgbColor("Coral")

    @staticmethod
    def cornflower_blue():
        """
        Get the color cornflower blue.
        """
        return RgbColor("CornflowerBlue")

    @staticmethod
    def cornsilk():
        """
        Get the color cornsilk.
        """
        return RgbColor("Cornsilk")

    @staticmethod
    def crimson():
        """
        Get the color crimson.
        """
        return RgbColor("Crimson")

    @staticmethod
    def dark_blue():
        """
        Get the color dark blue.
        """
        return RgbColor("DarkBlue")
    
    @staticmethod
    def dark_cyan():
        """
        Get the color dark cyan.
        """
        return RgbColor("DarkCyan")

    @staticmethod
    def dark_goldenrod():
        """
        Get the color dark goldenrod.
        """
        return RgbColor("DarkGoldenrod")

    @staticmethod
    def dark_green():
        """
        Get the color dark green.
        """
        return RgbColor("DarkGreen")

    @staticmethod
    def dark_khaki():
        """
        Get the color dark khaki.
        """
        return RgbColor("DarkKhaki")

    @staticmethod
    def dark_magenta():
        """
        Get the color dark magenta.
        """
        return RgbColor("DarkMagenta")

    @staticmethod
    def dark_olive_green():
        """
        Get the color dark olive green.
        """
        return RgbColor("DarkOliveGreen")

    @staticmethod
    def dark_orange():
        """
        Get the color dark orange.
        """
        return RgbColor("DarkOrange")

    @staticmethod
    def dark_orchid():
        """
        Get the color dark orchid.
        """
        return RgbColor("DarkOrchid")

    @staticmethod
    def dark_red():
        """
        Get the color dark red.
        """
        return RgbColor("DarkRed")

    @staticmethod
    def dark_salmon():
        """
        Get the color dark salmon.
        """
        return RgbColor("DarkSalmon")

    @staticmethod
    def dark_sea_green():
        """
        Get the color dark sea green.
        """
        return RgbColor("DarkSeaGreen")

    @staticmethod
    def dark_slate_blue():
        """
        Get the color dark slate blue.
        """
        return RgbColor("DarkSlateBlue")

    @staticmethod
    def dark_slate_gray():
        """
        Get the color dark slate gray.
        """
        return RgbColor("DarkSlateGray")

    @staticmethod
    def dark_turquoise():
        """
        Get the color dark turquoise.
        """
        return RgbColor("DarkTurquoise")

    @staticmethod
    def dark_violet():
        """
        Get the color dark violet.
        """
        return RgbColor("DarkViolet")

    @staticmethod
    def deep_pink():
        """
        Get the color deep pink.
        """
        return RgbColor("DeepPink")

    @staticmethod
    def deep_sky_blue():
        """
        Get the color deep sky blue.
        """
        return RgbColor("DeepSkyBlue")

    @staticmethod
    def dim_grey():
        """
        Get the color dim grey.
        """
        return RgbColor("DimGrey")

    @staticmethod
    def dodger_blue():
        """
        Get the color dodger blue.
        """
        return RgbColor("DodgerBlue")

    @staticmethod
    def firebrick():
        """
        Get the color firebrick.
        """
        return RgbColor("Firebrick")

    @staticmethod
    def floral_white():
        """
        Get the color floral white.
        """
        return RgbColor("FloralWhite")

    @staticmethod
    def forest_green():
        """
        Get the color forest green.
        """
        return RgbColor("ForestGreen")

    @staticmethod
    def fuchsia():
        """
        Get the color fuchsia.
        """
        return RgbColor("Fuchsia")

    @staticmethod
    def gainsboro():
        """
        Get the color gainsboro.
        """
        return RgbColor("Gainsboro")

    @staticmethod
    def ghost_white():
        """
        Get the color ghost white.
        """
        return RgbColor("GhostWhite")

    @staticmethod
    def gold():
        """
        Get the color gold.
        """
        return RgbColor("Gold")

    @staticmethod
    def goldenrod():
        """
        Get the color goldenrod.
        """
        return RgbColor("Goldenrod")

    @staticmethod
    def green_yellow():
        """
        Get the color green yellow.
        """
        return RgbColor("GreenYellow")

    @staticmethod
    def honeydew():
        """
        Get the color honeydew.
        """
        return RgbColor("Honeydew")


    @staticmethod
    def hot_pink():
        """
        Get the color hot pink.
        """
        return RgbColor("HotPink")

    @staticmethod
    def indian_red():
        """
        Get the color indian red.
        """
        return RgbColor("IndianRed")

    @staticmethod
    def indigo():
        """
        Get the color indigo.
        """
        return RgbColor("Indigo")

    @staticmethod
    def ivory():
        """
        Get the color ivory.
        """
        return RgbColor("Ivory")

    @staticmethod
    def khaki():
        """
        Get the color khaki.
        """
        return RgbColor("Khaki")

    @staticmethod
    def lavender():
        """
        Get the color lavender.
        """
        return RgbColor("Lavender")

    @staticmethod
    def lavender_blush():
        """
        Get the color lavender blush.
        """
        return RgbColor("LavenderBlush")

    @staticmethod
    def lawn_green():
        """
        Get the color lawn green.
        """
        return RgbColor("LawnGreen")

    @staticmethod
    def lemon_chiffon():
        """
        Get the color lemon chiffon.
        """
        return RgbColor("LemonChiffon")

    @staticmethod
    def light_blue():
        """
        Get the color light blue.
        """
        return RgbColor("LightBlue")

    @staticmethod
    def light_coral():
        """
        Get the color light coral.
        """
        return RgbColor("LightCoral")

    @staticmethod
    def light_cyan():
        """
        Get the color light cyan.
        """
        return RgbColor("LightCyan")

    @staticmethod
    def light_goldenrod_yellow():
        """
        Get the color light goldenrod yellow.
        """
        return RgbColor("LightGoldenrodYellow")

    @staticmethod
    def light_gray():
        """
        Get the color light gray.
        """
        return RgbColor("LightGray")

    @staticmethod
    def light_green():
        """
        Get the color light green.
        """
        return RgbColor("LightGreen")

    @staticmethod
    def light_pink():
        """
        Get the color light pink.
        """
        return RgbColor("LightPink")

    @staticmethod
    def light_salmon():
        """
        Get the color light salmon.
        """
        return RgbColor("LightSalmon")

    @staticmethod
    def light_sea_green():
        """
        Get the color light sea green.
        """
        return RgbColor("LightSeaGreen")

    @staticmethod
    def light_sky_blue():
        """
        Get the color light sky blue.
        """
        return RgbColor("LightSkyBlue")

    @staticmethod
    def light_slate_gray():
        """
        Get the color light slate gray.
        """
        return RgbColor("LightSlateGray")

    @staticmethod
    def light_steel_blue():
        """
        Get the color light steel blue.
        """
        return RgbColor("LightSteelBlue")

    @staticmethod
    def light_yellow():
        """
        Get the color light yellow.
        """
        return RgbColor("LightYellow")

    @staticmethod
    def lime_green():
        """
        Get the color lime green.
        """
        return RgbColor("LimeGreen")

    @staticmethod
    def linen():
        """
        Get the color linen.
        """
        return RgbColor("Linen")

    @staticmethod
    def maroon():
        """
        Get the color maroon.
        """
        return RgbColor("Maroon")

    @staticmethod
    def medium_aquamarine():
        """
        Get the color medium aquamarine.
        """
        return RgbColor("MediumAquamarine")

    @staticmethod
    def medium_blue():
        """
        Get the color medium blue.
        """
        return RgbColor("MediumBlue")

    @staticmethod
    def medium_orchid():
        """
        Get the color medium orchid.
        """
        return RgbColor("MediumOrchid")

    @staticmethod
    def medium_purple():
        """
        Get the color medium purple.
        """
        return RgbColor("MediumPurple")

    @staticmethod
    def medium_sea_green():
        """
        Get the color medium sea green.
        """
        return RgbColor("MediumSeaGreen")

    @staticmethod
    def medium_slate_blue():
        """
        Get the color medium slate blue.
        """
        return RgbColor("MediumSlateBlue")

    @staticmethod
    def medium_spring_green():
        """
        Get the color medium spring green.
        """
        return RgbColor("MediumSpringGreen")

    @staticmethod
    def medium_turquoise():
        """
        Get the color medium turquoise.
        """
        return RgbColor("MediumTurquoise")

    @staticmethod
    def medium_violet_red():
        """
        Get the color medium violet red.
        """
        return RgbColor("MediumVioletRed")

    @staticmethod
    def midnight_blue():
        """
        Get the color midnight blue.
        """
        return RgbColor("MidnightBlue")

    @staticmethod
    def mint_cream():
        """
        Get the color mint cream.
        """
        return RgbColor("MintCream")

    @staticmethod
    def misty_rose():
        """
        Get the color misty rose.
        """
        return RgbColor("MistyRose")

    @staticmethod
    def moccasin():
        """
        Get the color moccasin.
        """
        return RgbColor("Moccasin")

    @staticmethod
    def navajo_white():
        """
        Get the color navajo white.
        """
        return RgbColor("NavajoWhite")

    @staticmethod
    def navy():
        """
        Get the color navy.
        """
        return RgbColor("Navy")

    @staticmethod
    def old_lace():
        """
        Get the color old lace.
        """
        return RgbColor("OldLace")

    @staticmethod
    def olive():
        """
        Get the color olive.
        """
        return RgbColor("Olive")

    @staticmethod
    def olive_drab():
        """
        Get the color olive drab.
        """
        return RgbColor("OliveDrab")

    @staticmethod
    def orange():
        """
        Get the color orange.
        """
        return RgbColor("Orange")

    @staticmethod
    def orange_red():
        """
        Get the color orange red.
        """
        return RgbColor("OrangeRed")

    @staticmethod
    def orchid():
        """
        Get the color orchid.
        """
        return RgbColor("Orchid")

    @staticmethod
    def pale_goldenrod():
        """
        Get the color pale goldenrod.
        """
        return RgbColor("PaleGoldenrod")

    @staticmethod
    def pale_green():
        """
        Get the color pale green.
        """
        return RgbColor("PaleGreen")

    @staticmethod
    def pale_turquoise():
        """
        Get the color pale turquoise.
        """
        return RgbColor("PaleTurquoise")

    @staticmethod
    def pale_violet_red():
        """
        Get the color pale violet red.
        """
        return RgbColor("PaleVioletRed")

    @staticmethod
    def papaya_whip():
        """
        Get the color papaya whip.
        """
        return RgbColor("PapayaWhip")

    @staticmethod
    def peach_puff():
        """
        Get the color peach puff.
        """
        return RgbColor("PeachPuff")

    @staticmethod
    def peru():
        """
        Get the color peru.
        """
        return RgbColor("Peru")

    @staticmethod
    def pink():
        """
        Get the color pink.
        """
        return RgbColor("Pink")

    @staticmethod
    def plum():
        """
        Get the color plum.
        """
        return RgbColor("Plum")

    @staticmethod
    def powder_blue():
        """
        Get the color powder blue.
        """
        return RgbColor("PowderBlue")

    @staticmethod
    def rosy_brown():
        """
        Get the color rosy brown.
        """
        return RgbColor("RosyBrown")

    @staticmethod
    def royal_blue():
        """
        Get the color royal blue.
        """
        return RgbColor("RoyalBlue")

    @staticmethod
    def saddle_brown():
        """
        Get the color saddle brown.
        """
        return RgbColor("SaddleBrown")

    @staticmethod
    def salmon():
        """
        Get the color salmon.
        """
        return RgbColor("Salmon")

    @staticmethod
    def sandy_brown():
        """
        Get the color sandy brown.
        """
        return RgbColor("SandyBrown")

    @staticmethod
    def sea_green():
        """
        Get the color sea green.
        """
        return RgbColor("SeaGreen")

    @staticmethod
    def sea_shell():
        """
        Get the color sea shell.
        """
        return RgbColor("SeaShell")

    @staticmethod
    def sienna():
        """
        Get the color sienna.
        """
        return RgbColor("Sienna")

    @staticmethod
    def sky_blue():
        """
        Get the color sky blue.
        """
        return RgbColor("SkyBlue")

    @staticmethod
    def slate_blue():
        """
        Get the color slate blue.
        """
        return RgbColor("SlateBlue")

    @staticmethod
    def slate_gray():
        """
        Get the color slate gray.
        """
        return RgbColor("SlateGray")

    @staticmethod
    def snow():
        """
        Get the color snow.
        """
        return RgbColor("Snow")

    @staticmethod
    def spring_green():
        """
        Get the color spring green.
        """
        return RgbColor("SpringGreen")

    @staticmethod
    def steel_blue():
        """
        Get the color steel blue.
        """
        return RgbColor("SteelBlue")

    @staticmethod
    def tan():
        """
        Get the color tan.
        """
        return RgbColor("Tan")

    @staticmethod
    def teal():
        """
        Get the color teal.
        """
        return RgbColor("Teal")

    @staticmethod
    def thistle():
        """
        Get the color thistle.
        """
        return RgbColor("Thistle")

    @staticmethod
    def tomato():
        """
        Get the color tomato.
        """
        return RgbColor("Tomato")

    @staticmethod
    def turquoise():
        """
        Get the color turquoise.
        """
        return RgbColor("Turquoise")

    @staticmethod
    def violet():
        """
        Get the color violet.
        """
        return RgbColor("Violet")

    @staticmethod
    def wheat():
        """
        Get the color wheat.
        """
        return RgbColor("Wheat")

    @staticmethod
    def white_smoke():
        """
        Get the color white smoke.
        """
        return RgbColor("WhiteSmoke")

    @staticmethod
    def yellow_green():
        """
        Get the color yellow green.
        """
        return RgbColor("YellowGreen")
