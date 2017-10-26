
class PMCVariable {

    public PMCVariable(String name, String description, String value, String type, int[] numberOfElements, boolean isStruct, boolean isLiveVariable, boolean isLibrary, PMCValidation[] validation) {
        this.name = name;
        this.description = description;
        this.value = value;
        this.type = type;
        this.numberOfElements = numberOfElements;
        this.isStruct = isStruct;
        this.isLiveVariable = isLiveVariable;
        this.isLibrary = isLibrary;
        this.validation = validation;
    }

    public String name;
    public String description;
    public String value;
    public String type;
    public boolean isStruct;
    public boolean isLiveVariable;
    public boolean isLibrary;
    public int[] numberOfElements;
    public PMCValidation[] validation;            
}

