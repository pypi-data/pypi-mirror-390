class FormField:
    '''
    Represents a form field in the PDF document
    '''

    def __init__(self, name, value = None):
        '''
        Initializes a new instance of the FormField class 
        using the name of the form field as a parameter.

        Args:
            name (string): The name of the form field.
            value (string): The value of the form field.
        '''

        # Gets or sets name of the form field.
        self.name = name

        # Gets or sets value of the form field.
        self.value = value

        # Gets or sets a boolean indicating whether to flatten the form field
        self.flatten = None

        # Gets or sets a boolean indicating whether to remove the form field
        self.remove = None

    def to_json(self):
        json={
            "name": self.name
        }
        if self.value is not None:
            json['value'] = self.value
        if self.flatten is not None:
            json['flatten'] = self.flatten
        if self.remove is not None:
            json['remove'] = self.remove
        return json