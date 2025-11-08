class MergeOptions:
    '''
    Represents different options for merging PDF documents
    '''

    def __init__(self):

        # Gets or sets a boolean indicating whether to import document information when merging
        self.document_info = None

        # Gets or sets a boolean indicating whether to import document level JavaScript when merging
        self.document_javascript = None

        # Gets or sets a boolean indicating whether to import document properties when merging
        self.document_properties = None

        # Gets or sets a boolean indicating whether to import embedded files when merging
        self.embedded_files = None

        # Gets or sets a boolean indicating whether to import form fields when merging
        self.form_fields = None

        # Gets or sets a boolean indicating whether to import XFA form data when merging
        self.forms_xfa_data = None

        # Gets or sets a boolean indicating whether to import logical structure (tagging information) when merging
        self.logical_structure = None

        # Gets or sets a boolean indicating whether to import document's opening action (initial page and zoom settings) when merging
        self.open_action = None

        # Gets or sets a boolean indicating whether to import optional content when merging
        self.optional_content_info = None

        # Gets or sets a boolean indicating whether to import outlines and bookmarks when merging
        self.outlines = False

        # Gets or sets a boolean indicating whether to import OutputIntent when merging
        self.output_intent = None

        # Gets or sets a boolean indicating whether to import PageAnnotations when merging
        self.page_annotations = None

        # Gets or sets a boolean indicating whether to import PageLabelsAndSections when merging
        self.page_labels_and_sections = None

        # Gets or sets the root form field for imported form fields.
        # Useful when merging a PDF repeatedly to have better control over the form field names.
        self.root_form_field = None

        # Gets or sets a boolean indicating whether to import XmpMetadata when merging
        self.xmp_metadata = None
    
    def to_json(self):
        json = {}
        if self.document_javascript is not None:
            json["documentJavaScript"] = self.document_javascript
        if self.document_info is not None:
            json["documentInfo"] = self.document_info
        if self.document_properties is not None:
            json["documentProperties"] = self.document_properties
        if self.embedded_files is not None:
            json["embeddedFiles"] = self.embedded_files
        if self.form_fields is not None:
            json["formFields"] = self.form_fields
        if self.forms_xfa_data is not None:
            json["formsXfaData"] = self.forms_xfa_data
        if self.logical_structure is not None:
            json["logicalStructure"] = self.logical_structure
        if self.open_action is not None:
            json["openAction"] = self.open_action
        if self.optional_content_info is not None:
            json["optionalContentInfo"] = self.optional_content_info
        if self.outlines is not None:
            json["outlines"] = self.outlines
        if self.output_intent is not None:
            json["outputIntent"] = self.output_intent
        if self.page_annotations is not None:
            json["pageAnnotations"] = self.page_annotations
        if self.page_labels_and_sections is not None:
            json["pageLabelsAndSections"] = self.page_labels_and_sections
        if self.root_form_field is not None:
            json["rootFormField"] = self.root_form_field
        if self.xmp_metadata is not None:
            json["xmpMetadata"] = self.xmp_metadata
        return json