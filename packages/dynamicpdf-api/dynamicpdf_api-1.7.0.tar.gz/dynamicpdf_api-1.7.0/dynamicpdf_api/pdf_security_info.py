from .encryption_type import EncryptionType

class PdfSecurityInfo:
    """
    Represents the PDF security information endpoint.
    
    """

    def __init__(self, json_data=None):
        json_data = json_data or {}

        # Gets or sets the encryption type.
        self.encryption_type_string = json_data.get("encryptionType")

        # Gets or sets if the document can be edited by the user. 
        self.allow_edit = json_data.get("allowEdit")
        
        # Gets or sets if the document can be printed by the user.
        self.allow_print = json_data.get("allowPrint")
        
        # Gets or sets if annotations and form fields can be added, edited and modified by the user.
        self.allow_update_annots_and_fields = json_data.get("allowUpdateAnnotsAndFields")
        
        # Gets or sets if text and images can be copied to the clipboard by the user.
        self.allow_copy = json_data.get("allowCopy")
        
        # Gets or sets if the document can be printed at a high resolution by the user.
        self.allow_high_resolution_printing = json_data.get("allowHighResolutionPrinting")
        
        # Gets or sets if the document can be assembled and manipulated by the user.
        self.allow_document_assembly = json_data.get("allowDocumentAssembly")
        
        # Gets or sets if form filling should be allowed by the user.
        self.allow_form_filling = json_data.get("allowFormFilling")
        
        # Gets or sets if accessibility programs should be able to read the documents text and images for the user.
        self.allow_accessibility = json_data.get("allowAccessibility")

        # Gets or sets a value indicating whether all data should be encrypted except for metadata.
        self.encrypt_all_except_metadata = json_data.get("encryptAllExceptMetadata")
        
        # Gets or sets a value indicating whether only file attachments should be encrypted.
        self.encrypt_only_file_attachments = json_data.get("encryptOnlyFileAttachments")
        
        # Gets or sets a value indicating whether the PDF document has an owner password set.
        self.has_owner_password = json_data.get("hasOwnerPassword", False)
        
        # Gets or sets a value indicating whether the PDF document has an user password set.
        self.has_user_password = json_data.get("hasUserPassword", False)
    
    @property
    def encryption_type(self) -> EncryptionType:
        """
        Gets the resolved encryption type based on encryption_type_string.
        """
        value = (self.encryption_type_string)

        if value == "rc4-40":
            return EncryptionType.RC440
        elif value == "rc4-128":
            return EncryptionType.RC4128
        elif value == "aes-128-cbc":
            return EncryptionType.Aes128Cbc
        elif value == "aes-256-cbc":
            return EncryptionType.Aes256Cbc
        else:
            return EncryptionType.NONE
              