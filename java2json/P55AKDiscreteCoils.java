import java.util.Arrays;
import java.util.Vector;

class P55AKDiscreteCoils extends PMCVariable {

    public P55AKDiscreteCoils() {
        super("AK", "55 AK discrete sensors", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M1001 = new PMCDiscreteCoil("M1001", "55.AK.00-MLF-1001", false, 8.92771,0.55954,-89);
    PMCDiscreteCoil M3001 = new PMCDiscreteCoil("M3001", "55.AK.00-MLF-3001", false, 8.9277,0.55954,-89);
    PMCDiscreteCoil M4001 = new PMCDiscreteCoil("M4001", "55.AK.00-MLF-4001", false, 8.92771,0.55954,-89);
    PMCDiscreteCoil M6001 = new PMCDiscreteCoil("M6001", "55.AK.00-MLF-6001", false, 8.92771,0.55954,-89);
    PMCDiscreteCoil M7001 = new PMCDiscreteCoil("M7001", "55.AK.00-MLF-7001", false, 8.9277,0.55954,-89);
    PMCDiscreteCoil M9001 = new PMCDiscreteCoil("M9001", "55.AK.00-MLF-9001", false, 8.9277,0.55954,-89);
}
