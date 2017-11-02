import java.util.Arrays;
import java.util.Vector;

class P55ALDiscreteCoils extends PMCVariable {

    public P55ALDiscreteCoils() {
        super("AL", "55 AL discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M1001 = new PMCDiscreteCoil("M1001", "55.AL.00-MLF-1001", false, 5.87282,-3.88933,135);
    PMCDiscreteCoil M1002 = new PMCDiscreteCoil("M1002", "55.AL.00-MLF-1002", false, 5.87282,-3.92313,-135);
    PMCDiscreteCoil M1003 = new PMCDiscreteCoil("M1003", "55.AL.00-MLF-1003", false, 5.87282,-4.11463,135);
    PMCDiscreteCoil M1004 = new PMCDiscreteCoil("M1004", "55.AL.00-MLF-1004", false, 5.87282,-4.14844,-135);
    PMCDiscreteCoil M1005 = new PMCDiscreteCoil("M1005", "55.AL.00-MLF-1005", false, 5.12547,-4.23675,-60);
    PMCDiscreteCoil M1006 = new PMCDiscreteCoil("M1006", "55.AL.00-MLF-1006", false, 5.09543,-4.18472,30);
    PMCDiscreteCoil M1007 = new PMCDiscreteCoil("M1007", "55.AL.00-MLF-1007", false, 4.8932,-3.97336,-22);
    PMCDiscreteCoil M1008 = new PMCDiscreteCoil("M1008", "55.AL.00-MLF-1008", false, 4.8373,-3.95134,69);
    PMCDiscreteCoil M1009 = new PMCDiscreteCoil("M1009", "55.AL.00-MLF-1009", false, 4.63185,-3.96449,30);
    PMCDiscreteCoil M1010 = new PMCDiscreteCoil("M1010", "55.AL.00-MLF-1010", false, 4.57982,-3.99453,120);
    PMCDiscreteCoil M1011 = new PMCDiscreteCoil("M1011", "55.AL.00-MLF-1011", false, 4.1091,-3.30179,-73);
    PMCDiscreteCoil M1012 = new PMCDiscreteCoil("M1012", "55.AL.00-MLF-1012", false, 4.12474,-3.2718,17);
}
