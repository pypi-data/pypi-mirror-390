import io
import threading
import os
import uuid
from pathlib import Path
from .full_name_table import FullNameTable
from .font_resource import FontResource
from .font_information import FontInformation

class Font:
    '''
    Represents font
    '''
    
    _times_roman = None
    _times_bold = None
    _times_italic = None
    _times_bold_italic = None
    _helvetica = None
    _helvetica_bold = None
    _helvetica_oblique = None
    _helvetica_bold_oblique = None
    _courier = None
    _courier_bold = None
    _courier_oblique = None
    _courier_bold_oblique = None
    _symbol = None
    _zapf_dingbats = None
    _load_required = True
    _lock_object = threading.Lock()
    _font_details = []
    _path_to_fonts_resource_directory = ""

    def __init__(self, resource = None, resource_name = None):
        '''
        Initializes a new instance of the Font class 
        using the font name that is present in the cloud resource manager.

        Args:
            resource (string): The cloudResourceName
            resourceName (string): The resource name
        '''

        self._resource = None

        # Gets or sets a boolean indicating whether to embed the font.
        self.embed = None

        # Gets or sets a boolean indicating whether to subset embed the font.
        self.subset = None

        # Gets or sets a name for the font resource.
        self.resource_name = None

        if resource == None:
            pass
        elif type(resource) == str:
            self.resource_name = resource
            self._name = str(uuid.uuid4())
        else:
            self._resource = resource
            self.resource_name = resource_name
            self._name = str(uuid.uuid4())

    @staticmethod
    def times_roman():
        '''
        Gets the Times Roman core font with Latin 1 encoding.
        '''
        if Font._times_roman is None:
            Font._times_roman = Font()
            Font._times_roman._name = "timesRoman"
        return Font._times_roman

    @staticmethod
    def times_bold():
        '''
        Gets the Times Bold core font with Latin 1 encoding.
        '''
        if Font._times_bold is None:
            Font._times_bold = Font()
            Font._times_bold._name = "timesBold"
        return Font._times_bold

    @staticmethod
    def times_italic():
        '''
        Gets the Times Italic core font with Latin 1 encoding.
        '''
        if Font._times_italic is None:
            Font._times_italic = Font()
            Font._times_italic._name = "timesItalic"
        return Font._times_italic

    @staticmethod
    def times_bold_italic():
        '''
        Gets the Times Bold Italic core font with Latin 1 encoding.
        '''
        if Font._times_bold_italic is None:
            Font._times_bold_italic = Font()
            Font._times_bold_italic._name = "timesBoldItalic"
        return Font._times_bold_italic

    @staticmethod
    def helvetica():
        '''
        Gets the Helvetica core font with Latin 1 encoding.
        '''
        if Font._helvetica is None:
            Font._helvetica = Font()
            Font._helvetica._name = "helvetica"
        return Font._helvetica

    @staticmethod
    def helvetica_bold():
        '''
        Gets the Helvetica Bold core font with Latin 1 encoding.
        '''
        if Font._helvetica_bold is None:
            Font._helvetica_bold = Font()
            Font._helvetica_bold._name = "helveticaBold"
        return Font._helvetica_bold

    @staticmethod
    def helvetica_oblique():
        '''
        Gets the Helvetica Oblique core font with Latin 1 encoding.
        '''
        if Font._helvetica_oblique is None:
            Font._helvetica_oblique = Font()
            Font._helvetica_oblique._name = "helveticaOblique"
        return Font._helvetica_oblique

    @staticmethod
    def helvetica_bold_oblique():
        '''
        Gets the Helvetica Bold Oblique core font with Latin 1 encoding.
        '''
        if Font._helvetica_bold_oblique is None:
            Font._helvetica_bold_oblique = Font()
            Font._helvetica_bold_oblique._name = "helveticaBoldOblique"
        return Font._helvetica_bold_oblique

    @staticmethod
    def courier():
        '''
        Gets the Courier core font with Latin 1 encoding.
        '''
        if Font._courier is None:
            Font._courier = Font()
            Font._courier._name = "courier"
        return Font._courier

    @staticmethod
    def courier_bold():
        '''
        Gets the Courier Bold core font with Latin 1 encoding.
        '''
        if Font._courier_bold is None:
            Font._courier_bold = Font()
            Font._courier_bold._name = "courierBold"
        return Font._courier_bold

    @staticmethod
    def courier_oblique():
        '''
        Gets the Courier Oblique core font with Latin 1 encoding.
        '''
        if Font._courier_oblique is None:
            Font._courier_oblique = Font()
            Font._courier_oblique._name = "courierOblique"
        return Font._courier_oblique

    @staticmethod
    def courier_bold_oblique():
        '''
        Gets the Courier Bold Oblique core font with Latin 1 encoding.
        '''
        if Font._courier_bold_oblique is None:
            Font._courier_bold_oblique = Font()
            Font._courier_bold_oblique._name = "courierBoldOblique"
        return Font._courier_bold_oblique
    
    @staticmethod
    def symbol():
        '''
        Gets the Symbol core font.
        '''
        if Font._symbol is None:
            Font._symbol = Font()
            Font._symbol._name = "symbol"
        return Font._symbol

    @staticmethod
    def zapf_dingbats():
        '''
        Gets the Zapf Dingbats core font.
        '''
        if Font._zapf_dingbats is None:
            Font._zapf_dingbats = Font()
            Font._zapf_dingbats._name = "zapfDingbats"
        return Font._zapf_dingbats

    @staticmethod
    def from_file(file_path, resource_name=None):
        '''
        Initializes a new instance of the Font class 
        using the file path of the font and resource name.
        
        Args:
            filePath (string): The file path of the font file.
            resourceName (string): The resource name for the font.
        '''

        resource = FontResource(file_path, resource_name)
        font = Font(resource, resource.resource_name)
        return font
    
    @staticmethod
    def from_stream(stream, resource_name=None):
        '''
        Initializes a new instance of the Font class 
        using the stream of the font and resource name.
        
        Args:
            stream (stream): The stream of the font file.
            resource_name (string): The resource name for the font.
        '''
                
        resource = FontResource(stream, resource_name)
        font = Font(resource, resource.resource_name)
        return font
    
    @staticmethod
    def get_google_font_text(name, weight, italic):
        font_text = f"{name}:{weight}"
        if italic:
            font_text += "italic"
        return font_text
    
    @staticmethod
    def google(font_name, var=None, italic=False):
        '''
        Gets the font from the google.
        
        Args:
            font_name (string): The name of the google font.
            var (integer | boolean): The weight of the font | If true font weight will be taken as 700 otherwise 400. 
            italic (boolean): The italic property of the font.
        
        Returns:
            The font object.
        '''
        if var is False:
            var = 400
        font = Font()
        if var is True:
            font._name = Font.get_google_font_text(font_name, 700, italic)
        elif type(var) == int:
            font._name = Font.get_google_font_text(font_name, var, italic)
        else:
            font._name = font_name
        return font
    
    @staticmethod
    def global_font(font_name):
        '''
        Gets the font from the global.
        
        Args:
            font_name (string): The name of the font from the global storage.
        
        Returns:
            The font object.
        '''
        
        font = Font()
        font._name = font_name
        return font

    @staticmethod
    def from_system(font_name, resource_name=None):
        '''
        Initializes a new instance of the Font class 
        using the system of the font and resource name.
        
        Args:
            font_name (string): The name of the font in the system.
            resource_name (string): The resource name for the font.
        '''

        if font_name is None or font_name == '':
            return None
        font_name = font_name.replace("-", "").replace(" ", "")

        if Font._load_required:
            Font._load_fonts()

        for font_detail in Font._font_details:
            if font_detail._font_name.upper() == font_name.upper():
                font_resource = FontResource(font_detail._file_path, resource_name)
                return Font(font_resource, font_resource.resource_name)
        return None
    
    @staticmethod
    def _load_fonts():
        with Font._lock_object:
            if not Font._load_required:
                return
            Font._load_required = False
            if Font._path_to_fonts_resource_directory == "":
                try:
                    wind_dir = os.environ.get("WINDIR")
                    if wind_dir is not None and len(wind_dir) > 0:
                        Font._path_to_fonts_resource_directory = os.path.join(wind_dir, "Fonts")
                except Exception:
                    pass

            if Font._path_to_fonts_resource_directory and Font._path_to_fonts_resource_directory != "":
                di = Path(Font._path_to_fonts_resource_directory)
                all_files = di.rglob("*")

                for file in all_files:
                    if not file.suffix.lower() in [".ttf", ".otf"]:
                        continue
                    
                    with open(file, "rb") as reader:
                        name_table = Font._read_font_name_table(reader)
                    if name_table is not None:
                        Font._font_details.append(FontInformation(name_table.font_name, str(file)))

    @staticmethod
    def _read_font_name_table(reader):
        name_table = None
        try:
            reader.seek(4, io.SEEK_SET)
            int_table_count = (reader.read(1)[0] << 8) | reader.read(1)[0]
           
            if int_table_count > 0:
                reader.seek(12, io.SEEK_SET)
                byt_table_directory = bytearray(reader.read(int_table_count * 16))
            
                for i in range(0, len(byt_table_directory), 16):
                    tag_value = int.from_bytes(byt_table_directory[i: i+ 4], byteorder="big")
                    if tag_value == 0x6E616D65:  # "name"
                        name_table = FullNameTable(reader, byt_table_directory, i)
                        break
        except Exception as e:
            print("Error in _read_font_name_table:", e)
        return name_table
    
    def to_json(self):
        json= {
            "name": self._name
        }
        if self.resource_name is not None:
            json["resourceName"] = self.resource_name
        if self.embed is not None:
            json["embed"] = self.embed
        if self.subset is not None:
            json["subset"] = self.subset
        return json
