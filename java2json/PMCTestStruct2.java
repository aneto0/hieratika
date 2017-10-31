import java.util.Arrays;
import java.util.Vector;

class PMCTestStruct2 extends PMCVariable {

    public PMCTestStruct2(String name, String description, boolean isLiveVariable, boolean isLibrary, PMCTestStruct1[] var2) {
        super(name, description, new Vector(), "Another test struct", new int[]{1}, true, isLiveVariable, isLibrary, null);
        this.var2 = var2;
        this.var3 = new PMCTestStruct1[3][2][4];
        for(int i=0; i<this.var3.length; i++) {
            for(int j=0; j<this.var3[i].length; j++) {
                for(int k=0; k<this.var3[i][j].length; k++) {
                    this.var3[i][j][k] = new PMCTestStruct1("var3_" + (i * this.var3[i].length * this.var3[i][j].length + j * this.var3[i][j].length + k), "Test gap", false, false, i, j, k, 0);
                }
            }
        }
        this.var1 = new PMCTestStruct1("var1", "Another struct", false, false, 1, 2, 3, 4);
        this.var4 = new PMCVariable("var4", "A variable", new Vector(Arrays.asList(new int[]{1})), "int32", new int[]{1}, false, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{10})), "Check the maximum value"),
                new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-1})), "Check the minimum value"),
                new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
            });

    }

    private PMCTestStruct1 var1;
    private PMCTestStruct1 []var2;
    private PMCTestStruct1 var3[][][];
    private PMCVariable var4;
}
 
