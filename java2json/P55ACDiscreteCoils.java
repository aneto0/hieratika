import java.util.Arrays;
import java.util.Vector;

class P55ACDiscreteCoils extends PMCVariable {

    public P55ACDiscreteCoils() {
        super("AC", "55 AC discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M1001 = new PMCDiscreteCoil("M1001", "55.AC.00-MLF-1001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M2001 = new PMCDiscreteCoil("M2001", "55.AC.00-MLF-2001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M3001 = new PMCDiscreteCoil("M3001", "55.AC.00-MLF-3001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M4001 = new PMCDiscreteCoil("M4001", "55.AC.00-MLF-4001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M5001 = new PMCDiscreteCoil("M5001", "55.AC.00-MLF-5001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M6001 = new PMCDiscreteCoil("M6001", "55.AC.00-MLF-6001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M7001 = new PMCDiscreteCoil("M7001", "55.AC.00-MLF-7001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M8001 = new PMCDiscreteCoil("M8001", "55.AC.00-MLF-8001", false, 5.09972,5.14352,0);
    PMCDiscreteCoil M9001 = new PMCDiscreteCoil("M9001", "55.AC.00-MLF-9001", false, 5.09972,5.14352,0);
}
