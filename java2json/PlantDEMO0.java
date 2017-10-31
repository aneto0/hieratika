import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Vector;

class PlantDEMO0 {

    public PlantDEMO0(Vector variables) {
        try {
            Field[] fields = PlantDEMO0.class.getFields();
            for (int i=0; i<fields.length; i++) {
                variables.add(fields[i].get(this)); 
            }
        }
        catch(Exception e) {
            e.printStackTrace();
        }
    }

    public PMCVariable var1 = new PMCVariable("VAR1", "A variable", new Vector(Arrays.asList(new int[]{1})), "int32", new int[]{1}, false, false, false,
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{10})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-1})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
        });


    public PMCVariable var2 = new PMCVariable("VAR2", "An array", new Vector(Arrays.asList(new float[]{7, 8, 9, 0})), "float32", new int[]{4}, false, false, false,
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[][]{{10, 11, 12, 13}})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[][]{{-1, -2, -3, -4}})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
        });


    public PMCShape shape = new PMCShape("VAR4", "A shape", false, false, new PMCGap[]{
        new PMCGap("gap1", "A gap", false, false, 0, 0, 1, 1), 
        new PMCGap("gap2", "Another gap", false, false, 0, 0, 2, 3), 
        new PMCGap("gap3", "Another gap", false, false, 0, 0, 2, 4)});

    public PMCVariable multiDim = new PMCVariable("VAR5", "A multi dimensional variable", new Vector(), "gap", new int[]{2, 2}, true, false, false, new PMCValidation[]{}, new Vector(
        Arrays.asList(new PMCGap[][]{
            {
                new PMCGap("gap4", "A gap", false, false, 0, 0, 1, 1), 
                new PMCGap("gap5", "Another gap", false, false, 0, 0, 2, 3)
            },
            {
                new PMCGap("gap6", "A gap", false, false, 0, 0, 1, 1), 
                new PMCGap("gap7", "Another gap", false, false, 0, 0, 2, 3)

            }
        }
        )
    ));

}
