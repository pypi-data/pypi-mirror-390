from .input import Input
from .input_type import InputType

class PdfInput(Input):
    '''
    Represents a pdf input
    '''

    def __init__(self, resource, options = None):
        '''
        Initializes a new instance of the `PdfInput` class.
        Args:
            resource (PdfResource | string): The resource of type PdfResource. | The resource path in cloud resource manager.
            options (MergeOptions): The merge options for the pdf.
        '''

        super().__init__(resource)

        # Gets or sets the merge options MergeOptions.
        self.merge_options = options

        # *Gets or sets the start page.
        self.start_page = None

        # Gets or sets the page count.
        self.page_count = None
        self._type = InputType.Pdf
    
    def to_json(self):
        json={
            "id": self.id,
            "type": self._type
        }
        if self.resource_name is not None:
            json['resourceName'] = self.resource_name
        if self._template_id is not None:
            json["templateId"] = self._template_id
        if self.merge_options is not None:
            json["mergeOptions"] = self.merge_options.to_json()
        if self.start_page is not None:
            json['startPage'] = self.start_page
        if self.page_count is not None:
            json['pageCount'] = self.page_count
        return json