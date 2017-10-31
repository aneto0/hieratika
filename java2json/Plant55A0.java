import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Vector;

class Plant55A0 {

    public Plant55A0(Vector variables) {
        try {
            Field[] fields = Plant55A0.class.getFields();
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
            new PMCValidation("checkMax", new Vector(Arrays.asList(new String[]{"10"})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new String[]{"-1"})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")
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
