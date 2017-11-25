import java.util.Arrays;
import java.util.Vector;

class P55A0DiscreteCoils extends PMCVariable {

    public P55A0DiscreteCoils() {
        super("MLFS", "55 A0 discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    P55A3DiscreteCoils A3 = new P55A3DiscreteCoils();
    P55A4DiscreteCoils A4 = new P55A4DiscreteCoils();
    P55A5DiscreteCoils A5 = new P55A5DiscreteCoils();
    P55A6DiscreteCoils A6 = new P55A6DiscreteCoils();
    P55A9DiscreteCoils A9 = new P55A9DiscreteCoils();
    P55AADiscreteCoils AA = new P55AADiscreteCoils();
    P55ABDiscreteCoils AB = new P55ABDiscreteCoils();
    P55AGDiscreteCoils AG = new P55AGDiscreteCoils();
    P55AKDiscreteCoils AK = new P55AKDiscreteCoils();
    P55APDiscreteCoils AP = new P55APDiscreteCoils();
    P55ACDiscreteCoils AC = new P55ACDiscreteCoils();
    P55AJDiscreteCoils AJ = new P55AJDiscreteCoils();
    P55ALDiscreteCoils AL = new P55ALDiscreteCoils();

}


