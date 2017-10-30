import java.util.Arrays;
import java.util.Vector;

class PMCGap extends PMCVariable {

    public PMCGap(String name, String description, boolean isLiveVariable, boolean isLibrary, float r0, float r1, float z0, float z1) {
        super(name, description, new Vector(), "gap", new int[]{1}, true, isLiveVariable, isLibrary, null);
        this.r0 = new PMCVariable("r0", "r location 0", new Vector(Arrays.asList(new float[]{r0})), "float32", new int[]{1}, false, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.r1 = new PMCVariable("r1", "r location 1", new Vector(Arrays.asList(new float[]{r1})), "float32", new int[]{1}, false, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.z0 = new PMCVariable("z0", "z location 0", new Vector(Arrays.asList(new float[]{z0})), "float32", new int[]{1}, false, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
        this.z1 = new PMCVariable("z1", "z location 1", new Vector(Arrays.asList(new float[]{z1})), "float32", new int[]{1}, false, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new String[]{})), "Check the type")});
    }

    public PMCVariable r0;
    public PMCVariable z0;
    public PMCVariable r1;
    public PMCVariable z1;
}

