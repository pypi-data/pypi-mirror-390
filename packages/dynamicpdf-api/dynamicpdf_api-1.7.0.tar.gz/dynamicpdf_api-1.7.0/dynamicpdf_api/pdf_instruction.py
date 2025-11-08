from .outline_list import OutlineList

class PdfInstructions:
    def __init__(self):
        self._form_fields = []
        self._templates = set()
        self._fonts = set()
        self._outlines = OutlineList()
        self._author = "CeteSoftware"
        self._title = None
        self._subject = None
        self._creator = "DynamicPDF API"
        self._producer = "DynamicPDF API"
        self._tag = None
        self._keywords = None
        self._security = None
        self._flatten_all_form_fields = None
        self._retain_signature_form_fields = None
        self._inputs = []

    def to_json(self):
        json = {}
        if self._author is not None:
            json["author"] = self._author
        if self._title is not None:
            json["title"] = self._title
        if self._subject is not None:
            json["subject"] = self._subject
        if self._creator is not None:
            json["creator"] = self._creator
        if self._producer is not None:
            json["producer"] = self._producer
        if self._tag is not None:
            json["tag"] = self._tag
        if self._keywords is not None:
            json["keywords"] = self._keywords
        if self._security is not None:
            json["security"] = self._security.to_json()
        if self._flatten_all_form_fields is not None:
            json["flattenAllFormFields"] = self._flatten_all_form_fields
        if self._retain_signature_form_fields is not None:
            json["retainSignatureFormFields"] = self._retain_signature_form_fields
        fonts = []
        for i in self._fonts:
            fonts.append(i.to_json())
        if len(fonts) > 0:
            json["fonts"] = fonts
        inputs = []
        for i in self._inputs:
            inputs.append(i.to_json())
        json["inputs"] = inputs
        form_field = []
        for i in self._form_fields:
            form_field.append(i.to_json())
        if len(form_field) > 0:
            json["formFields"] = form_field
        templates = []
        for i in self._templates:
            templates.append(i.to_json())
        if len(templates) > 0:
            json["templates"] = templates
        if len(self._outlines._outlines) > 0:
            json["outlines"] = self._outlines.to_json()
        return json