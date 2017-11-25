import java.util.Vector;


class PMCVariable {

    public PMCVariable(String name, String description, Vector value, String type, int[] numberOfElements, boolean isStruct, boolean isLiveVariable, PMCValidation[] validation) {
        this.name = name;
        this.description = description;
        this.value = value;
        this.type = type;
        this.numberOfElements = numberOfElements;
        this.isStruct = isStruct;
        this.isLiveVariable = isLiveVariable;
        this.validation = validation;
    }

    /**
     * @brief 
     * @param[in] _private_vec_ allows to register variables that are (multi-dimensional) arrays of structs.
     */ 
    public PMCVariable(String name, String description, Vector value, String type, int[] numberOfElements, boolean isStruct, boolean isLiveVariable, PMCValidation[] validation, Vector _private_vec_) {
        this(name, description, value, type, numberOfElements, isStruct, isLiveVariable, validation);
        this._private_vec_ = _private_vec_;
    }

    public String name;
    public String description;
    public Vector value;
    public String type;
    public boolean isStruct;
    public boolean isLiveVariable;
    public int[] numberOfElements;
    public PMCValidation[] validation;            
    public Vector _private_vec_;
}

