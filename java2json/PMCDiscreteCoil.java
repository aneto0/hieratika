import java.util.Arrays;
import java.util.Vector;

class PMCDiscreteCoil extends PMCVariable {

    public PMCDiscreteCoil(String name, String description, boolean isLiveVariable, double r, double z, double angle) {
        super(name, description, new Vector(), "coil", new int[]{1}, true, isLiveVariable, null);
        this.r = new PMCVariable("r", "r location of the coil", new Vector(Arrays.asList(new double[]{r})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.z = new PMCVariable("z", "z location of the coil", new Vector(Arrays.asList(new double[]{z})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.angle = new PMCVariable("angle", "Angle of the coil w.r.t. to its main axis", new Vector(Arrays.asList(new double[]{angle})), "float32", new int[]{1}, false, false, new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new double[]{180})), "Maximum allowed angle"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new double[]{-180})), "Minimum allowed angle"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
    }

    public PMCVariable r;
    public PMCVariable z;
    public PMCVariable angle;
}

