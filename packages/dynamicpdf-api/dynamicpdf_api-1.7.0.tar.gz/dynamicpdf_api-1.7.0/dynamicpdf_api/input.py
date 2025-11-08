import uuid
class Input:
    '''
    Represents the base class for inputs
    '''

    def __init__(self, resource = None):

        self._template = None
        self._id = None
        self._template_id = None
        self._resources = []
        self._type = None

        # Gets or sets the resource name.
        self.resource_name = None

        if type(resource) == str: 
            self.resource_name = resource
        elif resource is not None:
            self._resources.append(resource)
            self.resource_name = resource.resource_name

    @property
    def id(self):
        if self._id is None:
            self._id = str(uuid.uuid4())
        return self._id

    @id.setter
    def id(self, value):
        self._id = value

    @property
    def template(self):
        '''
        Gets the template.
        '''
        return self._template

    @template.setter
    def template(self, template):
        '''
        Sets the template.
        '''
        self._template = template
        self._template_id = template.id