class Response:
    '''
    Represents the base class for response
    '''

    def __init__(self):

        # Gets the boolean, indicating the response's status.
        self.is_successful = None

        # Gets the error message.
        self.error_message = None

        # Gets the error id.
        self.error_id = None

        # Gets the status code.
        self.status_code = None

        # Gets the error json.
        self.error_json = None