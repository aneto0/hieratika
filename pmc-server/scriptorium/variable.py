class Variable(dict):
    """ Describes a scriptorium variable.
        Variables may contain other variables (i.e. they can represent a member of a structure), where their name is the key of a __dict__ representation of the Variable object.
    """

    def __init__(self, name, alias, vtype, numberOfElements, description, parent = None, permissions = [], value = "", *args, **kwargs):
        """ Constructs a new Variable object.
        
        Args:
            name (str): the variable name. This name can either encode a @ separated path of a name which univocally identifies the variable in the system; or it can be the relative name of the variable when it represents a member of another variable.
            alias (str): free format text which provides a meaningful name to the variable.
            vtype (str): the variable type as one of: uint8, int8, uint16, int16, uint32, int32, uint64, int64, string;
            numberOfElements ([str]): as an array where each entry contains the number of elements on any given direction; 
            description (str): one-line description of the variable;
            permissions (str): user groups that are allowed to change this variable;
            value (str): string encoded variable value.
            parent (Variable): the Variable which holds this Variable instance (only used when representing structured types).
        """
        self.name = name
        self.alias = alias 
        self.vtype = vtype 
        self.numberOfElements = numberOfElements
        self.description = description
        self.parent = parent
        self.permissions = permissions
        self.value = value
        self.update(*args, **kwargs)

    def getName(self):
        """ 
        Returns: 
            The variable name (see __init__).
        """
        return self.name

    def getAlias(self):
        """ 
        Returns: 
            The variable alias (see __init__).
        """
        return self.alias

    def getType(self):
        """
        Returns:
            The variable type (see __init__)
        """
        return self.vtype 

    def getNumberOfElements(self):
        """
        Returns:
            The variable numberOfElements(see __init__)
        """
        return self.numberOfElements

    def getDescription(self):
        """
        Returns:
            The variable description(see __init__)
        """
        return self.description

    def getParent(self):
        """
        Returns:
            The variable parent(see __init__)
        """
        return self.parent

    def getPermissions(self):
        """
        Returns:
            The variable permissions(see __init__)
        """
        return self.permissions

    def getValue(self):
        """
        Returns:
            The variable value(see __init__)
        """
        return self.value

    def getAbsoluteName(self):
        """
        Returns:
            The a @ separated name which univocally identifies the variable in the system. Each @ separates a substructure variable.
        """
        varName = self.name
        p = self.parent
        while (p is not None):
            varName = p.getName() + "@" + varName
            p = p.getParent()
        return varName

    def __eq__(self, another):
        """ Two Variables are equal if they have the same absolute name.
           
        Args:
            self (User): this variable instance.
            another (User or str): another Variable or a string. 
        Returns:
            True if self and another Variable are equal or if another is a string whose value is the self.getAbsoluteName().
        """
        if isinstance(self, another.__class__):
            areEqual = (self.getAbsoluteName() == another.getAbsoluteName())
        else:
            areEqual = (self.getUsername() == str(another))
        return areEqual

    def __cmp__(self, another):
        """ See __eq__
        """
        return (self == another) 

    def __hash__(self):
        """ The class is univocally identified by the absolute name.

        Returns:
            The absolute name of the variable.
        """
        return getAbsoluteName()

    def __str__(self):
        """ Returns a string representation of a Variable.
            
            Returns:
                A string representation of a Variable which consists of the absolute name followed by the value.
        """
        return "{0} : {1}".format(self.getAbsoluteName(), self.getValue()) 
