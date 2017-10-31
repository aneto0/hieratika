import java.util.Arrays;
import java.util.Vector;

class PMCTestStruct3 extends PMCVariable {
   public PMCTestStruct3(String name, String description, boolean isLiveVariable, boolean isLibrary) {
        super(name, description, new Vector(), "Another test struct", new int[]{1}, true, isLiveVariable, isLibrary, null);
        this.var1 = new PMCTestStruct1("var1", "Another struct", false, false, 1, 2, 3, 4);
        this.var2 = new PMCTestStruct2("var2", "Another struct", false, false, new PMCTestStruct1[]{
            new PMCTestStruct1("var1", "A var", false, false, 0, 1, 2, 3), 
            new PMCTestStruct1("var2", "Another var", false, false, 1, 2, 3, 4), 
            new PMCTestStruct1("var3", "Another var", false, false, 2, 3, 4, 5)});

        this.var3 = new PMCVariable("var3", "A variable", new Vector(Arrays.asList(new int[]{1})), "int32", new int[]{1}, false, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{10})), "Check the maximum value"),
                new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-1})), "Check the minimum value"),
                new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
            });

    }

    private PMCTestStruct1 var1;
    private PMCTestStruct2 var2;
    private PMCVariable var3;

}

