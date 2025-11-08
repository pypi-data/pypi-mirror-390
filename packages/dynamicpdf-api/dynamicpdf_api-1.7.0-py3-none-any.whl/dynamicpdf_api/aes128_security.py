from .security import Security
from .security_type import SecurityType

class Aes128Security(Security):
    '''
    Represents AES 128 bit PDF document security.

    AES 128 bit PDF security is compatible with PDF version 1.5 and higher and, 
    Adobe Acrobat Reader version 7 or higher is needed to open these documents.
    Older readers will not be able to read documents encrypted with this security.
    ''' 

    def __init__(self, user_password, owner_password):
        ''' 
        Initializes a new instance of the Aes128Security class by taking the owner and user passwords as parameters to create PDF.
        
        Args:
            user_password (str): The user password to open the document.
            owner_password (str): The owner password to open the document.
        '''
        super().__init__(user_password, owner_password)
        self._type = SecurityType.Aes128
        
        # Gets or sets the EncryptDocumentComponents, components of the document to be encrypted. 
        # We can encrypt all the PDF content or the content, excluding the metadata.
        self.document_components = None

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
        if self.document_components is not None:
            json['documentComponents'] = self.document_components
        return json