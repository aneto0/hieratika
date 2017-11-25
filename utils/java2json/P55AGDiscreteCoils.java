import java.util.Arrays;
import java.util.Vector;

class P55AGDiscreteCoils extends PMCVariable {

    public P55AGDiscreteCoils() {
        super("AG", "55 AG discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M1001 = new PMCDiscreteCoil("M1001", "55.AG.00-MLF-1001", false, 7.49151,-3.28649,0);
    PMCDiscreteCoil M1002 = new PMCDiscreteCoil("M1002", "55.AG.00-MLF-1002", false, 7.49151,-3.28649,0);
    PMCDiscreteCoil M4001 = new PMCDiscreteCoil("M4001", "55.AG.00-MLF-4001", false, 7.49151,-3.28649,0);
    PMCDiscreteCoil M4002 = new PMCDiscreteCoil("M4002", "55.AG.00-MLF-4002", false, 7.49151,-3.28649,0);
    PMCDiscreteCoil M7001 = new PMCDiscreteCoil("M7001", "55.AG.00-MLF-7001", false, 7.49151,-3.28649,0);
    PMCDiscreteCoil M7002 = new PMCDiscreteCoil("M7002", "55.AG.00-MLF-7002", false, 7.49151,-3.28649,0);
}
