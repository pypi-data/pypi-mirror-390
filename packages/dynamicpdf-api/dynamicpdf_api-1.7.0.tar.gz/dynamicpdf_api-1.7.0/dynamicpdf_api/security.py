class Security:
    ''' 
    Base class from which all security classes are derived
    '''

    def __init__(self, user_pwd = '', owner_pwd = ''):
        self.type = None

        # Gets or sets the owner password.
        self.owner_password = owner_pwd
        
        # Gets or sets the user password.
        self.user_password = user_pwd

        # Gets or sets if text and images can be copied to the clipboard by the user.
        self.allow_copy = None

        # Gets or sets if the document can be edited by the user. 
        self.allow_edit = None

        # Gets or sets if the document can be printed by the user.
        self.allow_print = None

        # Gets or sets if annotations and form fields can be added, edited and modified by the user.
        self.allow_update_annots_and_fields = None
        
        # Gets or sets if accessibility programs should be able to read the documents text and images for the user.
        self.allow_accessibility = None

        # Gets or sets if form filling should be allowed by the user.
        self.allow_form_filling = None

        # Gets or sets if the document can be printed at a high resolution by the user.
        self.allow_high_resolution_printing = None

        # Gets or sets if the document can be assembled and manipulated by the user. 
        self.allow_document_assembly = None
        