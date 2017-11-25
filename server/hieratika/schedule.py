class Schedule(object):
    """ Describes a hieratika parameter schedule.
    """

    def __init__(self, uid, name, pageName, owner, description = ""):
        """ Constructs a Schedule object against a uid, name and description.
        
        Args:
            uid (str): a unique system identifier for the schedule.
            name (str): the name of the schedule.
            pageName (str): the name of the Page associated to this schedule.
            description (str): a description of the schedule.
            owner (str): the username of the User which owns the schedule.
        """
        self.uid = uid
        self.name = name
        self.pageName = pageName 
        self.description = description
        self.owner = owner 

    def getUID(self):
        """ 
        Returns: 
            A unique system identifier for the schedule.
        """
        return self.uid

    def getName(self):
        """ 
        Returns:
            The schedule name (may not be unique).
        """
        return self.name

    def getDescription(self):
        """ 
        Returns:
            The schedule description.
        """
        return self.description

    def getOwner(self):
        """ 
        Returns:
            The username of the User which owns the schedule.
        """
        return self.owner

    def getPage(self):
        """ 
        Returns:
            The name of the page to which this schedule belongs to.
        """
        return self.page


    def __eq__(self, another):
        """ Two schedules are equal if they have the same uid.
           
        Args:
            self (Schedule): this Schedule instance.
            another (Schedule or str): another Schedule or a string. 
        Returns:
            True if self and another uid are equal or if another is a string whose value is the self.getUID().
        """
        if isinstance(self, another.__class__):
            areEqual = (self.getUID() == another.getUID())
        else:
            areEqual = (self.getUID() == str(another))
        return areEqual

    def __cmp__(self, another):
        """ See __eq__
        """
        return (self == another) 

    def __hash__(self):
        """ The class is univocally identified by the uid.

        Returns:
            The username.
        """
        return getUID()

    def __str__(self):
        """ Returns a string representation of a schedule.
            
        Returns:
            A string representation of a schedule which consists of the uid followed by the name,
        description and owner username.
        """
        return "{0} {1} {2} (owner:{3})".format(self.uid, self.name, self.description, self.owner) 

