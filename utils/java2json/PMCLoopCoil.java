import java.util.Arrays;
import java.util.Vector;

class PMCLoopCoil extends PMCVariable {

    public PMCLoopCoil(String name, String description, boolean isLiveVariable, double r1, double z1, double r2, double z2, double phi1, double phi2) {
        super(name, description, new Vector(), "coil", new int[]{1}, true, isLiveVariable, null);
        this.r1 = new PMCVariable("r1", "r1 location of the coil", new Vector(Arrays.asList(new double[]{r1})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.z1 = new PMCVariable("z1", "z1 location of the coil", new Vector(Arrays.asList(new double[]{z1})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.r2 = new PMCVariable("r2", "r2 location of the coil", new Vector(Arrays.asList(new double[]{r2})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.z2 = new PMCVariable("z2", "z2 location of the coil", new Vector(Arrays.asList(new double[]{z2})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.phi1 = new PMCVariable("phi1", "Starting angle of the loop", new Vector(Arrays.asList(new double[]{phi1})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new double[]{180})), "Maximum allowed angle"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new double[]{-180})), "Minimum allowed angle"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.phi2 = new PMCVariable("phi2", "Ending angle of the loop", new Vector(Arrays.asList(new double[]{phi2})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new double[]{180})), "Maximum allowed angle"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new double[]{-180})), "Minimum allowed angle"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});

    }

    public PMCVariable r1;
    public PMCVariable z1;
    public PMCVariable r2;
    public PMCVariable z2;
    public PMCVariable phi1;
    public PMCVariable phi2;
}

