import java.util.Arrays;
import java.util.Vector;

class P55ADLoopCoils extends PMCVariable {

    public P55ADLoopCoils() {
        super("AD", "55 AD loop coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCLoopCoil M1001 = new PMCLoopCoil("M1001", "55.AD.00-MSA-1001", false,  3.567, -1.653, 3.567, -2.55, 16.05, 47.67);
    PMCLoopCoil M1013 = new PMCLoopCoil("M1013", "55.AD.00-MSA-1013", false, 8.740, 1.84, 8.36, 2.68, 35.13, 44.67 );
}


