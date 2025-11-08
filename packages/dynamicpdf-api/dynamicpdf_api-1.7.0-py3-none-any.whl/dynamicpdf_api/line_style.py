class LineStyle:
    '''
    Represents a style of line.
    '''

    _obj_formatter = "{0:.2f}"

    def __init__(self, dash_array, dash_phase = 0):
        '''
        Initializes a new instance of the LineStyle class.

        Args:
            dashArray (integer []): The array specifying the line style.
            dashPhase (integer []): The phase of the line style.
        '''

        if type(dash_array) == str:
            self.line_style_string = dash_array
        else:
            str_line_style = "["
            for i in range(len(dash_array)):
                val = dash_array[i]
                if i == len(dash_array) - 1:
                    str_line_style += self._obj_formatter.format(val)
                else:
                    str_line_style += self._obj_formatter.format(val) + ","
            str_line_style += "]"
            if dash_phase != 0:
                str_line_style += self._obj_formatter.format(dash_phase)
            self.line_style_string = str_line_style
            
    @property
    def _line_style_string(self):
        return self.line_style_string

    @_line_style_string.setter
    def _line_style_string(self, value):
        self.line_style_string = value

    @staticmethod
    def solid():
        '''
        Gets a solid line.
        '''
        return LineStyle("solid")
    
    @staticmethod
    def dots():
        '''
        Gets a dotted line.
        '''
        return LineStyle("dots")
    
    @staticmethod
    def dash_small():
        '''
        Gets a line with small dashes.
        '''
        return LineStyle("dashSmall")
    
    @staticmethod
    def dash():
        '''
        Gets a dashed line.
        '''
        return LineStyle("dash")
    
    @staticmethod
    def dash_large():
        '''
        Gets a line with large dashes. 
        '''
        return LineStyle("dashLarge")
     
    @staticmethod
    def none():
        '''
        Gets a invisible line.
        '''
        return LineStyle("none")
    
    def to_json(self):
        return{
            "lineStyle": self._line_style_string
        }