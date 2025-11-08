from .security import Security
from .security_type import SecurityType

class RC4128Security(Security):
    '''
    Represents RC4 128 bit PDF document security.
    RC4 128 bit PDF security, with UseCryptFilter property set to false is compatible with PDF version 1.4 or higher and can be read
    with Adobe Acrobat Reader version 5 or higher. By default UseCryptFilter property is false. RC4 128 bit PDF security with crypt filter 
    is compatible with PDF version 1.5 or higher and can be read with Adobe Acrobat Reader version 6 and higher. 
    Older readers will not be able to read document encrypted with this security.
    '''

    def __init__(self, user_password, owner_password):
        '''
        Initializes a new instance of the RC4128Security class.

        Args:
            userPassword (string): The owner password to open the document.
            ownerPassword (string): The user password to open the document.

        '''

        super().__init__(user_password, owner_password)
        self._type = SecurityType.RC4128

        # Gets or sets the documents components to be encrypted.
        self.encrypt_metadata = None

    def to_json(self):
        json = {
            'type': self._type
        }
        if self.user_password is not None:
            json["userPassword"] = self.user_password
        if self.owner_password is not None:
            json["ownerPassword"] = self.owner_password
        if self.allow_copy is not None:
            json["allowCopy"] = self.allow_copy
        if self.allow_edit is not None:
            json["allowEdit"] = self.allow_edit
        if self.allow_print is not None:
            json["allowPrint"] = self.allow_print
        if self.allow_update_annots_and_fields is not None:
            json["allowUpdateAnnotsAndFields"] = self.allow_update_annots_and_fields 
        if self.allow_accessibility is not None:
            json["allowAccessibility"] = self.allow_accessibility
        if self.allow_form_filling is not None:
            json["allowFormFilling"] = self.allow_form_filling
        if self.allow_high_resolution_printing is not None:
            json["allowHighResolutionPrinting"] = self.allow_high_resolution_printing
        if self.allow_document_assembly is not None:
            json["allowDocumentAssembly"] = self.allow_document_assembly
        if self.encrypt_metadata is not None:
            json['encryptMetadata'] = self.encrypt_metadata
        return json