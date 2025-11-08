class TextReplace:
    '''
    Represents the find and replace values and its options.
    '''

    def __init__(self, text, replace_text, match_case = False):
        '''
        Creates new instance of text replace.
        
        Args:
        text (string): Text to find.
        replaceText (string): Text to replace.
        matchCase (boolean): True value will make the search operation case sensitive.
        '''

        # Gets or sets the find text value. This string will be replaced with ReplaceText during conversion.
        self.text = text
        
        # Gets or sets the replace text value. This string will replace the Text during conversion.
        self.replace_text = replace_text

        # If true, the search operation will be case sensitive.
        self.match_case = match_case

    def to_json(self):
        return {
            "text":self.text,
            "replaceText": self.replace_text,
            "matchCase": self.match_case
        }