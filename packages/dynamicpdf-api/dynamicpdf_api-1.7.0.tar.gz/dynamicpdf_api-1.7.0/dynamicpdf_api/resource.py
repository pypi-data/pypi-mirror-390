import os
import uuid
import io
from .endpoint_exception import EndpointException

class Resource:
    '''
    Represents the base class resource
    '''
    
    def __init__(self, input = None, resource_name = None):
        self._type = ''
        self._file_extension = ''
        self._mime_type = ''
        self._resource_name = resource_name

        if input == None:
            pass
        else:
            if type(input) == str:
                file_path = input
                if os.path.exists(file_path): 
                    self._data = Resource._get_file_data(file_path)
                    self._file_path = file_path
                else:
                    raise EndpointException("File does not exist.")

            elif type(input) == list:
                value = input
                if len(value) > 0:
                    self._data = value
                else:
                    raise EndpointException("Byte array is empty.")
        
            elif type(input) == io.BytesIO:
                stream = input
                if stream is not None:
                    self._data = Resource._get_stream_data(stream)
                else:
                    raise EndpointException("Stream is null.")
    
    @property
    def resource_name(self):
        if self._resource_name is None:
            self._resource_name = str(uuid.uuid4()) + self._file_extension
        return self._resource_name
    
    @resource_name.setter
    def resource_name(self,value):
        self._resource_name=value

    @staticmethod
    def _get_stream_data(stream):
        data = None
        if stream is not None and stream.getvalue():
            data = stream.getvalue()
        return data

    @staticmethod
    def _get_utf8_file_data(file_path):
        with open(file_path, "r", encoding="utf-8") as file:
            data = file.read()
        return data.encode("utf-8")

    @staticmethod
    def _get_file_data(file_path):
        with open(file_path, "rb") as file:
            data = file.read()
        return data
