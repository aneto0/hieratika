class Page(object):
    """ Describes a scriptorium page.

        A page is a container for a list of Variables.
       
        Typically a page is also an html user-interface which contains widgets that are identified by a unique key (which in turn corresponds to a given variable).
    """

    def __init__(self, name, url, description):
        """ Constructs a Page object against a given name, url and description.
        
        Args:
            name (str): the page name.
            url (str): the page url. It shall not contain the .html suffix.
            description (str): the page description.
        """
        self.name = name
        self.url = url
        self.description = description

    def getName(self):
        """ Returns the page name. This must be unique in whole psps environment.
       
        Returns: 
            The page name.
        """
        return self.name

    def getUrl(self):
        """ Returns the page url.
       
        Returns: 
            The page url.
        """
        return self.url

    def getDescription(self):
        """ Returns the page description.
       
        Returns: 
            The page description.
        """
        return self.description


    def __eq__(self, another):
        """ Two pages are equal if they have the same name
            
        Returns:
            True if self and another page names are equal.
        """
        if isinstance(self, another.__class__):
            areEqual = (self.getName() == another.getName())
        else:
            areEqual = (self.getName() == str(another))
        return areEqual

    def __hash__(self):
        """ The class is univocally identified by the page name.

        Returns:
            The page name.
        """
        return getName()

    def __str__(self):
        """ Gets the page name.
        
        Returns:
            The page name.
        """
        return self.getName()

