import java.util.Arrays;
import java.util.Vector;

class P55A0Embedded extends PMCVariable {

    public P55A0Embedded(String name, String description, boolean isLiveVariable, String libraryAlias) {
        super(name, description, new Vector(), "", new int[]{1}, true, isLiveVariable, null, libraryAlias);
        library = new PMCLibrary("LIBRARY", "Library to group all the embedded configuration parameters");
    }

    public PMCVariable wo = new PMCVariable("WO", "WO time in seconds", new Vector(Arrays.asList(new int[]{1})), "float32", new int[]{1}, false, false, 
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new double[]{3600})), "The maximum WO time (cannot be greater than the ITER pulse length)"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new double[]{0})), "The WO time must be greater than zero"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new double[]{})), "Check the type")
        });
 

    public PMCVariable eo = new PMCVariable("EO", "EO time in seconds", new Vector(Arrays.asList(new int[]{1})), "float32", new int[]{1}, false, false, 
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new double[]{3600})), "The maximum EO time (cannot be greater than the ITER pulse length)"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new double[]{0})), "The EO time must be greater than zero"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new double[]{})), "Check the type")
        });

    public PMCVariable chopperFrequency = new PMCVariable("CHOPPERF", "Chopper frequency", new Vector(Arrays.asList(new int[]{1})), "float32", new int[]{1}, false, false, 
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new double[]{500000})), "The maximum chopper frequency"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new double[]{0})), "The minimum chopper frequency"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new double[]{})), "Check the type")
        });


    public PMCVariable filter = new PMCVariable("FILTER", "The input filter", new Vector(Arrays.asList(new double[][]{{1}, {0.0001,1}})), "double", new int[]{1,2}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new double[]{})), "Check the type")
        });


    public PMCVariable chopperEqualiserIn = new PMCVariable("CHOPPEREQIN", "An array", new Vector(Arrays.asList(new double[]{0.8, 0.9, 1, 1})), "double", new int[]{4}, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new Vector(Arrays.asList(new double[][]{{1.001, 1.001, 1.001, 1.001}})), "Check the maximum value"),
                new PMCValidation("checkMin", new Vector(Arrays.asList(new double[][]{{-1.001, -1.001, -1.001, -1.001}})), "Check the minimum value"),
                new PMCValidation("checkType", new Vector(Arrays.asList(new double[]{})), "Check the type")
            });


    public PMCVariable chopperEqualiserOut = new PMCVariable("CHOPPEREQOUT", "An array", new Vector(Arrays.asList(new double[]{-1, -1, 1, 1})), "double", new int[]{4}, false, false,
            new PMCValidation[]{
                new PMCValidation("checkMax", new Vector(Arrays.asList(new double[][]{{1.001, 1.001, 1.001, 1.001}})), "Check the maximum value"),
                new PMCValidation("checkMin", new Vector(Arrays.asList(new double[][]{{-1.001, -1.001, -1.001, -1.001}})), "Check the minimum value"),
                new PMCValidation("checkType", new Vector(Arrays.asList(new double[]{})), "Check the type")
            });


    public PMCLibrary library;
}


