import java.util.Arrays;
import java.util.Vector;

class P55A6DiscreteCoils extends PMCVariable {

    public P55A6DiscreteCoils() {
        super("A6", "55 A6 discrete coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCDiscreteCoil M2001 = new PMCDiscreteCoil("M2001", "55.A6.00-MSS-2001", false, 3.2324,-2.81374,-180);
    PMCDiscreteCoil M2002 = new PMCDiscreteCoil("M2002", "55.A6.00-MSS-2002", false, 3.2324,-1.34174,-180);
    PMCDiscreteCoil M2003 = new PMCDiscreteCoil("M2003", "55.A6.00-MSS-2003", false, 3.2324,0.13026,-180);
    PMCDiscreteCoil M2004 = new PMCDiscreteCoil("M2004", "55.A6.00-MSS-2004", false, 3.2324,1.60227,-180);
    PMCDiscreteCoil M2005 = new PMCDiscreteCoil("M2005", "55.A6.00-MSS-2005", false, 3.2324,3.07427,-180);
    PMCDiscreteCoil M2006 = new PMCDiscreteCoil("M2006", "55.A6.00-MSS-2006", false, 3.38561,4.52545,157);
    PMCDiscreteCoil M2007 = new PMCDiscreteCoil("M2007", "55.A6.00-MSS-2007", false, 4.40885,5.53135,112);
    PMCDiscreteCoil M2008 = new PMCDiscreteCoil("M2008", "55.A6.00-MSS-2008", false, 5.85509,5.62154,76);
    PMCDiscreteCoil M2009 = new PMCDiscreteCoil("M2009", "55.A6.00-MSS-2009", false, 7.17685,4.98893,56);
    PMCDiscreteCoil M2010 = new PMCDiscreteCoil("M2010", "55.A6.00-MSS-2010", false, 8.28484,4.02611,42);
    PMCDiscreteCoil M2011 = new PMCDiscreteCoil("M2011", "55.A6.00-MSS-2011", false, 9.11275,2.81391,27);
    PMCDiscreteCoil M2012 = new PMCDiscreteCoil("M2012", "55.A6.00-MSS-2012", false, 9.60652,1.43147,12);
    PMCDiscreteCoil M2013 = new PMCDiscreteCoil("M2013", "55.A6.00-MSS-2013", false, 9.67333,-0.03036,-8);
    PMCDiscreteCoil M2014 = new PMCDiscreteCoil("M2014", "55.A6.00-MSS-2014", false, 9.20677,-1.42026,-24);
    PMCDiscreteCoil M2015 = new PMCDiscreteCoil("M2015", "55.A6.00-MSS-2015", false, 8.61264,-2.76702,-24);
    PMCDiscreteCoil M2016 = new PMCDiscreteCoil("M2016", "55.A6.00-MSS-2016", false, 8.00968,-4.08002,-30);
    PMCDiscreteCoil M2017 = new PMCDiscreteCoil("M2017", "55.A6.00-MSS-2017", false, 7.00327,-5.13642,-57);
    PMCDiscreteCoil M2018 = new PMCDiscreteCoil("M2018", "55.A6.00-MSS-2018", false, 5.63329,-5.63799,-83);
    PMCDiscreteCoil M2019 = new PMCDiscreteCoil("M2019", "55.A6.00-MSS-2019", false, 4.2076,-5.40294,-120);
    PMCDiscreteCoil M2020 = new PMCDiscreteCoil("M2020", "55.A6.00-MSS-2020", false, 3.3143,-4.27775,-163);
    PMCDiscreteCoil M5001 = new PMCDiscreteCoil("M5001", "55.A6.00-MSS-5001", false, 3.23239,-2.32307,180);
    PMCDiscreteCoil M5002 = new PMCDiscreteCoil("M5002", "55.A6.00-MSS-5002", false, 3.23239,-0.85107,180);
    PMCDiscreteCoil M5003 = new PMCDiscreteCoil("M5003", "55.A6.00-MSS-5003", false, 3.23239,0.62093,180);
    PMCDiscreteCoil M5004 = new PMCDiscreteCoil("M5004", "55.A6.00-MSS-5004", false, 3.23239,2.09294,180);
    PMCDiscreteCoil M5005 = new PMCDiscreteCoil("M5005", "55.A6.00-MSS-5005", false, 3.23239,3.56494,180);
    PMCDiscreteCoil M5006 = new PMCDiscreteCoil("M5006", "55.A6.00-MSS-5006", false, 3.63493,4.94638,142);
    PMCDiscreteCoil M5007 = new PMCDiscreteCoil("M5007", "55.A6.00-MSS-5007", false, 4.88115,5.65969,99);
    PMCDiscreteCoil M5008 = new PMCDiscreteCoil("M5008", "55.A6.00-MSS-5008", false, 6.3177,5.46044,66);
    PMCDiscreteCoil M5009 = new PMCDiscreteCoil("M5009", "55.A6.00-MSS-5009", false, 7.57316,4.69996,51);
    PMCDiscreteCoil M5010 = new PMCDiscreteCoil("M5010", "55.A6.00-MSS-5010", false, 8.59503,3.64613,37);
    PMCDiscreteCoil M5011 = new PMCDiscreteCoil("M5011", "55.A6.00-MSS-5011", false, 9.31654,2.36773,22);
    PMCDiscreteCoil M5012 = new PMCDiscreteCoil("M5012", "55.A6.00-MSS-5012", false, 9.68937,0.94805,7);
    PMCDiscreteCoil M5013 = new PMCDiscreteCoil("M5013", "55.A6.00-MSS-5013", false, 9.56985,-0.50963,-16);
    PMCDiscreteCoil M5014 = new PMCDiscreteCoil("M5014", "55.A6.00-MSS-5014", false, 9.00873,-1.86918,-24);
    PMCDiscreteCoil M5015 = new PMCDiscreteCoil("M5015", "55.A6.00-MSS-5015", false, 8.41461,-3.21594,-24);
    PMCDiscreteCoil M5016 = new PMCDiscreteCoil("M5016", "55.A6.00-MSS-5016", false, 7.72957,-4.48227,-39);
    PMCDiscreteCoil M5017 = new PMCDiscreteCoil("M5017", "55.A6.00-MSS-5017", false, 6.57405,-5.37306,-66);
    PMCDiscreteCoil M5018 = new PMCDiscreteCoil("M5018", "55.A6.00-MSS-5018", false, 5.14371,-5.66011,-92);
    PMCDiscreteCoil M5019 = new PMCDiscreteCoil("M5019", "55.A6.00-MSS-5019", false, 3.81721,-5.10809,-134);
    PMCDiscreteCoil M5020 = new PMCDiscreteCoil("M5020", "55.A6.00-MSS-5020", false, 3.23385,-3.79506,-178);
    PMCDiscreteCoil M8001 = new PMCDiscreteCoil("M8001", "55.A6.00-MSS-8001", false, 3.2324,-3.30441,-180);
    PMCDiscreteCoil M8002 = new PMCDiscreteCoil("M8002", "55.A6.00-MSS-8002", false, 3.2324,-1.83241,-180);
    PMCDiscreteCoil M8003 = new PMCDiscreteCoil("M8003", "55.A6.00-MSS-8003", false, 3.2324,-0.3604,-180);
    PMCDiscreteCoil M8004 = new PMCDiscreteCoil("M8004", "55.A6.00-MSS-8004", false, 3.2324,1.1116,-180);
    PMCDiscreteCoil M8005 = new PMCDiscreteCoil("M8005", "55.A6.00-MSS-8005", false, 3.2324,2.5836,-180);
    PMCDiscreteCoil M8006 = new PMCDiscreteCoil("M8006", "55.A6.00-MSS-8006", false, 3.2525,4.05463,172);
    PMCDiscreteCoil M8007 = new PMCDiscreteCoil("M8007", "55.A6.00-MSS-8007", false, 3.98379,5.28931,127);
    PMCDiscreteCoil M8008 = new PMCDiscreteCoil("M8008", "55.A6.00-MSS-8008", false, 5.37001,5.68909,88);
    PMCDiscreteCoil M8009 = new PMCDiscreteCoil("M8009", "55.A6.00-MSS-8009", false, 6.75734,5.24304,61);
    PMCDiscreteCoil M8010 = new PMCDiscreteCoil("M8010", "55.A6.00-MSS-8010", false, 7.9434,4.37824,47);
    PMCDiscreteCoil M8011 = new PMCDiscreteCoil("M8011", "55.A6.00-MSS-8011", false, 8.87166,3.24108,32);
    PMCDiscreteCoil M8012 = new PMCDiscreteCoil("M8012", "55.A6.00-MSS-8012", false, 9.48153,1.90579,17);
    PMCDiscreteCoil M8013 = new PMCDiscreteCoil("M8013", "55.A6.00-MSS-8013", false, 9.7134,0.45832,-1);
    PMCDiscreteCoil M8014 = new PMCDiscreteCoil("M8014", "55.A6.00-MSS-8014", false, 9.40473,-0.97131,-23);
    PMCDiscreteCoil M8015 = new PMCDiscreteCoil("M8015", "55.A6.00-MSS-8015", false, 8.81069,-2.3181,-24);
    PMCDiscreteCoil M8016 = new PMCDiscreteCoil("M8016", "55.A6.00-MSS-8016", false, 8.21657,-3.66485,-24);
    PMCDiscreteCoil M8017 = new PMCDiscreteCoil("M8017", "55.A6.00-MSS-8017", false, 7.39147,-4.83717,-48);
    PMCDiscreteCoil M8018 = new PMCDiscreteCoil("M8018", "55.A6.00-MSS-8018", false, 6.11381,-5.54156,-74);
    PMCDiscreteCoil M8019 = new PMCDiscreteCoil("M8019", "55.A6.00-MSS-8019", false, 4.65935,-5.59073,-105);
    PMCDiscreteCoil M8020 = new PMCDiscreteCoil("M8020", "55.A6.00-MSS-8020", false, 3.51298,-4.72491,-149);
}
