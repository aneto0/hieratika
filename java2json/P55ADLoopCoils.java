import java.util.Arrays;
import java.util.Vector;

class P55ADLoopCoils extends PMCVariable {

    public P55ADLoopCoils() {
        super("AD", "55 AD loop coils", new Vector(), "", new int[]{1}, true, false, null);
    }

    PMCLoopCoil M1001 = new PMCLoopCoil("M1001", "55.AD.00-MSA-1001", false, 3.567,-1.653,3.56701,-2.55,16.05,47.67);
    PMCLoopCoil M1002 = new PMCLoopCoil("M1002", "55.AD.00-MSA-1002", false, 3.567,-0.535,3.567,-1.647,27.59,47.67);
    PMCLoopCoil M1003 = new PMCLoopCoil("M1003", "55.AD.00-MSA-1003", false, 3.567,0.47,3.56701,-0.525,16.05,47.67);
    PMCLoopCoil M1004 = new PMCLoopCoil("M1004", "55.AD.00-MSA-1004", false, 3.567,1.395,3.56699,0.48,16.05,47.67);
    PMCLoopCoil M1005 = new PMCLoopCoil("M1005", "55.AD.00-MSA-1005", false, 3.567,2.408,3.56699,1.455,16.05,47.67);
    PMCLoopCoil M1006 = new PMCLoopCoil("M1006", "55.AD.00-MSA-1006", false, 3.567,3.53,3.567,2.414,27.59,47.67);
    PMCLoopCoil M1007 = new PMCLoopCoil("M1007", "55.AD.00-MSA-1007", false, 3.9136,4.555,3.567,3.56,25.44,45.48);
    PMCLoopCoil M1008 = new PMCLoopCoil("M1008", "55.AD.00-MSA-1008", false, 4.70632,5.09,3.92161,4.565,25.37,45.43);
    PMCLoopCoil M1009 = new PMCLoopCoil("M1009", "55.AD.00-MSA-1009", false, 5.82179,5.012,4.76025,5.105,21.34,38.66);
    PMCLoopCoil M1010 = new PMCLoopCoil("M1010", "55.AD.00-MSA-1010", false, 7.24879,4.025,5.85986,4.994,35.9,44.1);
    PMCLoopCoil M1011 = new PMCLoopCoil("M1011", "55.AD.00-MSA-1011", false, 7.83935,3.43,7.26048,4.015,35.15,44.63);
    PMCLoopCoil M1012 = new PMCLoopCoil("M1012", "55.AD.00-MSA-1012", false, 8.3492,2.7,7.85605,3.41,35.14,44.66);
    PMCLoopCoil M1013 = new PMCLoopCoil("M1013", "55.AD.00-MSA-1013", false, 8.74056,1.84,8.36062,2.68,35.13,44.67);
    PMCLoopCoil M1014 = new PMCLoopCoil("M1014", "55.AD.00-MSA-1014", false, 8.94254,0.56,8.75419,1.8,36.52,43.48);
    PMCLoopCoil M1015 = new PMCLoopCoil("M1015", "55.AD.00-MSA-1015", false, 8.79086,-0.58,8.94261,0.554,36.52,43.48);
    PMCLoopCoil M1016 = new PMCLoopCoil("M1016", "55.AD.00-MSA-1016", false, 7.93744,-2.455,8.77503,-0.62,35,45);
    PMCLoopCoil M1017 = new PMCLoopCoil("M1017", "55.AD.00-MSA-1017", false, 6.78135,-3.25361,7.83876,-2.62263,35.33,43.41);
    PMCLoopCoil M1018 = new PMCLoopCoil("M1018", "55.AD.00-MSA-1018", false, 6.51429,-4.68,7.6149,-3.16,35.19,49.17);
    PMCLoopCoil M1019 = new PMCLoopCoil("M1019", "55.AD.00-MSA-1019", false, 4.8502,-5.075,6.50532,-4.686,33.56,49.02);
    PMCLoopCoil M1020 = new PMCLoopCoil("M1020", "55.AD.00-MSA-1020", false, 3.90836,-4.505,4.83988,-5.073,21.56,38.44);
    PMCLoopCoil M1021 = new PMCLoopCoil("M1021", "55.AD.00-MSA-1021", false, 3.567,-3.52,3.90051,-4.495,17.84,42.16);
    PMCLoopCoil M1022 = new PMCLoopCoil("M1022", "55.AD.00-MSA-1022", false, 3.567,-2.62,3.567,-3.475,17.84,42.16);

    PMCLoopCoil M2001 = new PMCLoopCoil("M2001", "55.AD.00-MSA-2001", false, 3.567,-1.653,3.567,-2.55,56.05,87.67);
    PMCLoopCoil M2002 = new PMCLoopCoil("M2002", "55.AD.00-MSA-2002", false, 3.567,-0.535,3.567,-1.647,67.59,87.67);
    PMCLoopCoil M2003 = new PMCLoopCoil("M2003", "55.AD.00-MSA-2003", false, 3.567,0.47,3.567,-0.525,56.05,87.67);
    PMCLoopCoil M2004 = new PMCLoopCoil("M2004", "55.AD.00-MSA-2004", false, 3.56701,1.395,3.567,0.48,56.05,87.67);
    PMCLoopCoil M2005 = new PMCLoopCoil("M2005", "55.AD.00-MSA-2005", false, 3.567,2.408,3.567,1.455,56.05,87.67);
    PMCLoopCoil M2006 = new PMCLoopCoil("M2006", "55.AD.00-MSA-2006", false, 3.567,3.53,3.567,2.414,67.59,87.67);
    PMCLoopCoil M2007 = new PMCLoopCoil("M2007", "55.AD.00-MSA-2007", false, 3.9136,4.555,3.567,3.56,65.44,85.48);
    PMCLoopCoil M2008 = new PMCLoopCoil("M2008", "55.AD.00-MSA-2008", false, 4.70632,5.09,3.92161,4.565,65.37,85.43);
    PMCLoopCoil M2009 = new PMCLoopCoil("M2009", "55.AD.00-MSA-2009", false, 5.82179,5.012,4.76026,5.105,61.34,78.66);
    PMCLoopCoil M2010 = new PMCLoopCoil("M2010", "55.AD.00-MSA-2010", false, 7.24879,4.025,5.85985,4.994,75.9,84.1);
    PMCLoopCoil M2011 = new PMCLoopCoil("M2011", "55.AD.00-MSA-2011", false, 7.83935,3.43,7.26048,4.015,75.15,84.63);
    PMCLoopCoil M2012 = new PMCLoopCoil("M2012", "55.AD.00-MSA-2012", false, 8.3492,2.7,7.85604,3.41,75.14,84.66);
    PMCLoopCoil M2013 = new PMCLoopCoil("M2013", "55.AD.00-MSA-2013", false, 8.74056,1.84,8.36062,2.68,75.13,84.67);
    PMCLoopCoil M2016 = new PMCLoopCoil("M2016", "55.AD.00-MSA-2016", false, 7.93744,-2.455,8.77503,-0.62,75,85);
    PMCLoopCoil M2017 = new PMCLoopCoil("M2017", "55.AD.00-MSA-2017", false, 6.78135,-3.25361,7.83876,-2.62263,75.33,83.41);
    PMCLoopCoil M2018 = new PMCLoopCoil("M2018", "55.AD.00-MSA-2018", false, 6.51429,-4.68,7.6149,-3.16,75.19,89.17);
    PMCLoopCoil M2019 = new PMCLoopCoil("M2019", "55.AD.00-MSA-2019", false, 4.8502,-5.075,6.50532,-4.686,73.56,89.02);
    PMCLoopCoil M2020 = new PMCLoopCoil("M2020", "55.AD.00-MSA-2020", false, 3.90837,-4.505,4.83988,-5.073,61.56,78.44);
    PMCLoopCoil M2021 = new PMCLoopCoil("M2021", "55.AD.00-MSA-2021", false, 3.567,-3.52,3.90051,-4.495,57.84,82.16);
    PMCLoopCoil M2022 = new PMCLoopCoil("M2022", "55.AD.00-MSA-2022", false, 3.567,-2.62,3.567,-3.475,57.84,82.16);
    PMCLoopCoil M2023 = new PMCLoopCoil("M2023", "55.AD.00-MSA-2023", false, 8.79086,-0.58,8.7542,1.8,76.52,86.93);

}


