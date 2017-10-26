import java.lang.reflect.*;
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

    public PMCVariable var1 = new PMCVariable("PLANT1::VAR1", "A variable", "1", "int32", new int[]{1}, false, false, false,
        new PMCValidation[]{
            new PMCValidation("checkMax", new String[]{"10"}, "Check the maximum value"),
            new PMCValidation("checkMin", new String[]{"-1"}, "Check the minimum value"),
            new PMCValidation("checkType", new String[]{}, "Check the type")
        });

    public PMCVariable[] PLANT1ARRVARS = new PMCVariable[]{
        new PMCVariable("VAR3", "A variable", "2", "int32", new int[]{1}, false, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new String[]{"10"}, "Check the maximum value"),
                new PMCValidation("checkMin", new String[]{"-1"}, "Check the minimum value"),
                new PMCValidation("checkType", new String[]{}, "Check the type")
            }
        ),
        new PMCVariable("VAR4", "A variable", "3", "int32", new int[]{1}, false, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new String[]{"10"}, "Check the maximum value"),
                new PMCValidation("checkMin", new String[]{"-1"}, "Check the minimum value"),
                new PMCValidation("checkType", new String[]{}, "Check the type")
            }
        )
    };

    public PMCVariable[] PLANT2ARRVARS = new PMCVariable[]{
        new PMCVariable("VAR5", "A variable", "2", "int32", new int[]{1}, false, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new String[]{"10"}, "Check the maximum value"),
                new PMCValidation("checkMin", new String[]{"-1"}, "Check the minimum value"),
                new PMCValidation("checkType", new String[]{}, "Check the type")
            }
        ),
        new PMCVariable("VAR6", "A variable", "3", "int32", new int[]{1}, false, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new String[]{"10"}, "Check the maximum value"),
                new PMCValidation("checkMin", new String[]{"-1"}, "Check the minimum value"),
                new PMCValidation("checkType", new String[]{}, "Check the type")
            }
        )
    };

    public PMCShape shape = new PMCShape("PLANT1::VAR11", "A shape", false, false, new PMCGap[]{
        new PMCGap("gap1", "A gap", false, false, 0, 0, 1, 1), 
        new PMCGap("gap2", "Another gap", false, false, 0, 0, 2, 3), 
        new PMCGap("gap3", "Another gap", false, false, 0, 0, 2, 4)});
}
