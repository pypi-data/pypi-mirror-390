class UrlAction:
    '''
    Represents an action linking to an external URL
    '''

    def __init__(self, url):
        '''
        Initializes a new instance of the UrlAction class.

        Args:
            url (string): URL the action launches.
        '''

        super().__init__()

        # Gets or sets the URL launched by the action.
        self.url = url

    def to_json(self):
        return {
            "url": self.url
        }
