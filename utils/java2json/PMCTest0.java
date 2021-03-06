import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Vector;

class PMCTest0 {

    public PMCTest0(Vector variables) {
        try {
            Field[] fields = PMCTest0.class.getFields();
            for (int i=0; i<fields.length; i++) {
                variables.add(fields[i].get(this)); 
            }
        }
        catch(Exception e) {
            e.printStackTrace();
        }
    }

    public PMCVariable var1 = new PMCVariable("VAR1", "A variable", new Vector(Arrays.asList(new int[]{1})), "int32", new int[]{1}, false, false, 
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{10})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-1})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
        });


    public PMCVariable var2 = new PMCVariable("VAR2", "An array", new Vector(Arrays.asList(new float[]{7, 8, 9, 0})), "float32", new int[]{4}, false, false,
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[][]{{10, 11, 12, 13}})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[][]{{-1, -2, -3, -4}})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
        });


    public PMCTestStruct3 var3 = new PMCTestStruct3("VAR3", "A complex structure", false);

    public PMCVariable multiDim = new PMCVariable("VAR4", "A multi dimensional variable", new Vector(), "PMCTestStruct1", new int[]{2, 2}, true, false, new PMCValidation[]{}, new Vector(
        Arrays.asList(new PMCTestStruct1[][]{
            {
                new PMCTestStruct1("gap4", "A gap", false, 0, 0, 1, 1), 
                new PMCTestStruct1("gap5", "Another gap", false, 0, 0, 2, 3)
            },
            {
                new PMCTestStruct1("gap6", "A gap", false, 0, 0, 1, 1), 
                new PMCTestStruct1("gap7", "Another gap", false, 0, 0, 2, 3)
            }
        }
        )
    ));

    public PMCLibrary var5 = new PMCLibrary("VAR5", "A library");

    public PMCVariable var6 = new PMCVariable("VAR6", "A variable", new Vector(Arrays.asList(new int[]{5})), "int32", new int[]{1}, false, false,
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[]{50})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[]{-50})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
        });


    public PMCVariable var7 = new PMCVariable("VAR7", "An array", new Vector(Arrays.asList(new float[]{5, 5, 5, 3})), "float32", new int[]{4}, false, false,
        new PMCValidation[]{
            new PMCValidation("checkMax", new Vector(Arrays.asList(new float[][]{{10, 11, 12, 13}})), "Check the maximum value"),
            new PMCValidation("checkMin", new Vector(Arrays.asList(new float[][]{{-1, -2, -3, -4}})), "Check the minimum value"),
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
        });

    public PMCVariable var8 = new PMCVariable("VAR8", "A filter", new Vector(Arrays.asList(new float[][]{{1}, {1,1}})), "float32", new int[]{1,2}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
    });

    public PMCVariable var9 = new PMCVariable("VAR9", "Another filter", new Vector(Arrays.asList(new float[][]{{2}, {1,1,1,1}})), "float32", new int[]{1,4}, false, false, new PMCValidation[]{
            new PMCValidation("checkType", new Vector(Arrays.asList(new float[]{})), "Check the type")
    });

    public PMCVariable var10 = new PMCVariable("VAR10", "A switch configuration", new Vector(Arrays.asList(new String[]{"interface FastEthernet0/1\n switchport access vlan 2\n switchport mode access\n spanning-tree portfast\n ip dhcp snooping trust\n!\n\ninterface FastEthernet0/2\n switchport access vlan 2\n switchport mode access\n spanning-tree portfast\n ip dhcp snooping trust\n!"})), "string", new int[]{1}, false, false, new PMCValidation[]{});

    public PMCVariable var11 = new PMCVariable("VAR11", "A cubicle", new Vector(Arrays.asList(new String[]{""})), "string", new int[]{1}, false, false, new PMCValidation[]{});
    
    public PMCLibrary var12 = new PMCLibrary("VAR12", "A switch library");
}
