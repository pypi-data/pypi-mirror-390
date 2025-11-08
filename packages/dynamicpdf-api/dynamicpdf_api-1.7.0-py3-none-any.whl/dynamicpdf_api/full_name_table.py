import io

class FullNameTable:
    def __init__(self, reader, table_directory, position):
        self._full_font_name = ''
        self._data = None
        self._table_directory = table_directory
        
        if table_directory is not None:
            int_offset = self._read_u_long(table_directory, position + 8)
            int_length = self._read_u_long(table_directory, position + 12)

            self._data = bytearray(int_length)

            reader.seek(int_offset, io.SEEK_SET)
            reader.readinto(self._data)

        data_start = self._read_u_short(4)
        header_start = 6
        header_end = (self._read_u_short(2) * 12)

        for i in range(header_start, header_end, 12):
            if self._read_u_short(i + 6) == 4:  
                if (self._read_u_short(i) == 3 and self._read_u_short(i + 2) == 1 and self._read_u_short(i + 4) == 0x0409):  # 3 for Platform ID, 1 for Encoding ID and 0x0409 Language ID for English (United States)
                    full_font_name = self._data[data_start + self._read_u_short(i + 10) : data_start + self._read_u_short(i + 10) + self._read_u_short(i + 8)]
                    self._full_font_name = full_font_name.decode('utf-16-be').strip().replace(" ", "").replace("-", "")
                    break

        if len(self._full_font_name) == 0:
            for i in range(header_start, header_end, 12):
                if self._read_u_short(i + 6) == 4:
                    if (self._read_u_short(i) == 3 and self._read_u_short(i + 2) == 0 and self._read_u_short(i + 4) == 0x0409): 
                        full_font_name = self._data[data_start + self._read_u_short(i + 10) : data_start + self._read_u_short(i + 10) + self._read_u_short(i + 8)]
                        self._full_font_name = full_font_name.decode('utf-16-be').strip().replace(" ", "").replace("-", "")
                        break

        self._data = None

    @property
    def font_name(self):
        return self._full_font_name

    def _read_u_long(self, data, index):
        int_return = data[index]
        int_return *= 0x100
        int_return += data[index + 1]
        int_return *= 0x100
        int_return += data[index + 2]
        int_return *= 0x100
        int_return += data[index + 3]
        return int_return
    
    def _read_u_short(self, index):
        return (self._data[index] << 8) | self._data[index + 1]

    def _read_u_short1(self, index):
        return (self._data[index]) | (self._data[index + 1] << 8)

    def _read_byte(self, index):
        return self._data[index+1]
    
    def _read_fixed(self, index):
            int_integer = self._data[index+1]
            if (int_integer > 127):
                int_integer -= 256
            int_integer *= 0x100
            int_integer += self._data[index+1]
            int_integer *= 0x100
            int_integer += self._data[index+1]
            int_integer *= 0x100
            int_integer += self._data[index]
            return int_integer / 0x10000
    
    def _read_f_word(self, index):
        int_return = self._data[index+1]
        if (int_return > 127):
            int_return -= 256
        int_return *= 0x100
        int_return += self._data[index]
        return int_return
