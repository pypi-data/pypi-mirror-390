import uuid

class Template:
    '''
    Represents a document template
    '''

    def __init__(self, id = None):
        '''
        Initializes a new instance of the Template class.

        Args:
            id (string): The id string representing id for the template.
        '''

        if id is None:
            self.id = str(uuid.uuid4())
        else:
            self.id = id

        # Gets or sets the elements for the template.
        self.elements = []

    def to_json(self):
        elements = []
        for i in self.elements:
            elements.append(i.to_json())
        return {
            "id": self.id,
            "elements": elements
        }
