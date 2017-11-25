class UserGroup(object):
    """ Describes a psps user group.
       
        Users that belong to the same group share the same access rights. 
    """

    def __init__(self, name):
        """ Constructs a UserGroup object against a given group name.
        
        Args:
            name(string): the group name.
        """
        self.name = name

    def getName(self):
        """ Returns the group name
       
        Returns: 
            The group name.
        """
        return self.name

    def __eq__(self, another):
        """ Two groups are equal if they have the same group name
            
        Returns:
            True if self and another group names are equal.
        """
        if isinstance(self, another.__class__):
            areEqual = (self.getName() == another.getName())
        else:
            areEqual = (self.getName() == str(another))
        return areEqual

    def __hash__(self):
        """ The class is univocally identified by the group name.

        Returns:
            The group name.
        """
        return getName()

    def __str__(self):
        """ Gets the group name.
        
        Returns:
            The group name.
        """
        return self.getName()

