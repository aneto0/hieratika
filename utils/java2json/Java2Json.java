import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import com.google.gson.GsonBuilder;
import java.lang.reflect.*;
import java.util.Vector;

class Java2JSon {

    Vector variables = new Vector();

    Java2JSon() {
        Gson gson = new GsonBuilder().setPrettyPrinting().create();

        //variables.add(new PMCVariable("PLANT1::VAR1", "A variable", "1", "int32", new int[]{1}));
        
        //variables.add(new PMCShape("PLANT1::VAR11", "A Shape", gaps));
       
        //variables.add(new Plant55A0()); 
        Plant55A0 plant = new Plant55A0(variables);
        /*try {
            P55A0LoopCoils instance = new P55A0LoopCoils();
            Field[] fields = P55A0LoopCoils.class.getFields();
            for (int i=0; i<fields.length; i++) {
                variables.add(fields[i].get(instance)); 
            }
        }
        catch(Exception e) {
            e.printStackTrace();
        }*/

        //PlantDEMO0 plant = new PlantDEMO0(variables);
        //PMCTest0 plant = new PMCTest0(variables);
        String json = gson.toJson(this);
        System.out.println(json);
    }

    public static void main (String args[]) {
        new Java2JSon(); 
    }

}

