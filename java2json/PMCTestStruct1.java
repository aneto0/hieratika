import java.util.Arrays;
import java.util.Vector;

class PMCTestStruct1 extends PMCVariable {

    public PMCTestStruct1(String name, String description, boolean isLiveVariable, float var1, float var2, int var3, int var4) {
        super(name, description, new Vector(), "Test struct", new int[]{1}, true, isLiveVariable, null);
        this.var1 = new PMCVariable("var1", "A coefficient", new Vector(Arrays.asList(new float[]{var1})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type"),
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{10})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-1})), "Check the minimum value")});
        this.var2 = new PMCVariable("var2", "Another coefficient", new Vector(Arrays.asList(new float[]{var2})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type"),
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{5})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-1.5f})), "Check the minimum value")});
        this.var3 = new PMCVariable("var3", "And another coefficient", new Vector(Arrays.asList(new int[]{var3})), "int32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new int[]{})), "Check the type"),
            new PMCValidation("checkMax", new Vector(Arrays.asList(new int[]{10})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new int[]{-10})), "Check the minimum value")});
        this.var4 = new PMCVariable("var4", "And another coefficient", new Vector(Arrays.asList(new int[]{var4})), "int32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new int[]{})), "Check the type"),
            new PMCValidation("checkMax", new Vector(Arrays.asList(new int[]{30})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new int[]{-100})), "Check the minimum value")});

        float delta = 50;
        this.var5 = new PMCVariable("var5", "An array", new Vector(Arrays.asList(new float[]{var1, var2, var3, var4})), "float32", new int[]{4}, false, false, 
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[][]{{delta * var1 + delta, delta * var2 + delta, delta * var3 + delta, delta * var4 + delta}})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[][]{{-delta * var1 - delta, -delta * var2 -delta, -delta * var3 - delta,  -delta * var4 - delta}})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")});


    }

    public PMCVariable var1;
    public PMCVariable var2;
    public PMCVariable var3;
    public PMCVariable var4;
    public PMCVariable var5;
}

