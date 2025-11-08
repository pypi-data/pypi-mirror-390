class EndpointException(Exception):
    """
    Represents the exception that occurs in case of any issues with sending the request.
    """

    def __init__(self, message):
        ''' 
        Initializes a new instance of the EndpointException class.
        '''
        
        super().__init__(message)