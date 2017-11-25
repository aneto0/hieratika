import java.util.Arrays;
import java.util.Vector;

class P55A9DiscreteCoils extends PMCVariable {

    public P55A9DiscreteCoils() {
        super("A9", "55 A9 discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M1101 = new PMCDiscreteCoil("M1101", "55.A9.00-MLF-1101", false, 8.5504,-2.92489,0);
    PMCDiscreteCoil M1102 = new PMCDiscreteCoil("M1102", "55.A9.00-MLF-1102", false, 8.55036,-2.92489,0);
    PMCDiscreteCoil M1103 = new PMCDiscreteCoil("M1103", "55.A9.00-MLF-1103", false, 8.55038,-2.92489,0);
    PMCDiscreteCoil M1104 = new PMCDiscreteCoil("M1104", "55.A9.00-MLF-1104", false, 8.54862,-2.92489,0);
    PMCDiscreteCoil M1105 = new PMCDiscreteCoil("M1105", "55.A9.00-MLF-1105", false, 8.54862,-2.92489,0);
    PMCDiscreteCoil M1106 = new PMCDiscreteCoil("M1106", "55.A9.00-MLF-1106", false, 8.55039,-2.92489,0);
    PMCDiscreteCoil M1107 = new PMCDiscreteCoil("M1107", "55.A9.00-MLF-1107", false, 8.55036,-2.92489,0);
    PMCDiscreteCoil M1108 = new PMCDiscreteCoil("M1108", "55.A9.00-MLF-1108", false, 8.5504,-2.92489,0);
    PMCDiscreteCoil M1109 = new PMCDiscreteCoil("M1109", "55.A9.00-MLF-1109", false, 8.23798,-3.62585,0);
    PMCDiscreteCoil M1110 = new PMCDiscreteCoil("M1110", "55.A9.00-MLF-1110", false, 8.23653,-3.62585,0);
    PMCDiscreteCoil M1111 = new PMCDiscreteCoil("M1111", "55.A9.00-MLF-1111", false, 8.23653,-3.62585,0);
    PMCDiscreteCoil M1112 = new PMCDiscreteCoil("M1112", "55.A9.00-MLF-1112", false, 8.23798,-3.62585,0);
    PMCDiscreteCoil M4101 = new PMCDiscreteCoil("M4101", "55.A9.00-MLF-4101", false, 8.5504,-2.92489,0);
    PMCDiscreteCoil M4102 = new PMCDiscreteCoil("M4102", "55.A9.00-MLF-4102", false, 8.55036,-2.92489,0);
    PMCDiscreteCoil M4103 = new PMCDiscreteCoil("M4103", "55.A9.00-MLF-4103", false, 8.55039,-2.92489,0);
    PMCDiscreteCoil M4104 = new PMCDiscreteCoil("M4104", "55.A9.00-MLF-4104", false, 8.54862,-2.92489,0);
    PMCDiscreteCoil M4105 = new PMCDiscreteCoil("M4105", "55.A9.00-MLF-4105", false, 8.54862,-2.92489,0);
    PMCDiscreteCoil M4106 = new PMCDiscreteCoil("M4106", "55.A9.00-MLF-4106", false, 8.55038,-2.92489,0);
    PMCDiscreteCoil M4107 = new PMCDiscreteCoil("M4107", "55.A9.00-MLF-4107", false, 8.55036,-2.92489,0);
    PMCDiscreteCoil M4108 = new PMCDiscreteCoil("M4108", "55.A9.00-MLF-4108", false, 8.5504,-2.92489,0);
    PMCDiscreteCoil M4109 = new PMCDiscreteCoil("M4109", "55.A9.00-MLF-4109", false, 8.23798,-3.62585,0);
    PMCDiscreteCoil M4110 = new PMCDiscreteCoil("M4110", "55.A9.00-MLF-4110", false, 8.23653,-3.62585,0);
    PMCDiscreteCoil M4111 = new PMCDiscreteCoil("M4111", "55.A9.00-MLF-4111", false, 8.23653,-3.62585,0);
    PMCDiscreteCoil M4112 = new PMCDiscreteCoil("M4112", "55.A9.00-MLF-4112", false, 8.23798,-3.62585,0);
    PMCDiscreteCoil M7101 = new PMCDiscreteCoil("M7101", "55.A9.00-MLF-7101", false, 8.55039,-2.92489,0);
    PMCDiscreteCoil M7102 = new PMCDiscreteCoil("M7102", "55.A9.00-MLF-7102", false, 8.55036,-2.92489,0);
    PMCDiscreteCoil M7103 = new PMCDiscreteCoil("M7103", "55.A9.00-MLF-7103", false, 8.55039,-2.92489,0);
    PMCDiscreteCoil M7104 = new PMCDiscreteCoil("M7104", "55.A9.00-MLF-7104", false, 8.54861,-2.92489,0);
    PMCDiscreteCoil M7105 = new PMCDiscreteCoil("M7105", "55.A9.00-MLF-7105", false, 8.54861,-2.92489,0);
    PMCDiscreteCoil M7106 = new PMCDiscreteCoil("M7106", "55.A9.00-MLF-7106", false, 8.55039,-2.92489,0);
    PMCDiscreteCoil M7107 = new PMCDiscreteCoil("M7107", "55.A9.00-MLF-7107", false, 8.55036,-2.92489,0);
    PMCDiscreteCoil M7108 = new PMCDiscreteCoil("M7108", "55.A9.00-MLF-7108", false, 8.55039,-2.92489,0);
    PMCDiscreteCoil M7109 = new PMCDiscreteCoil("M7109", "55.A9.00-MLF-7109", false, 8.23797,-3.62585,0);
    PMCDiscreteCoil M7110 = new PMCDiscreteCoil("M7110", "55.A9.00-MLF-7110", false, 8.23653,-3.62585,0);
    PMCDiscreteCoil M7111 = new PMCDiscreteCoil("M7111", "55.A9.00-MLF-7111", false, 8.23653,-3.62585,0);
    PMCDiscreteCoil M7112 = new PMCDiscreteCoil("M7112", "55.A9.00-MLF-7112", false, 8.23797,-3.62585,0);
}
