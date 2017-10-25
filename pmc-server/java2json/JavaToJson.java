import com.google.gson.Gson;
import com.google.gson.JsonArray;
import com.google.gson.JsonParser;
import java.util.Vector;

class Java2JSon {

    Vector<PMCComponent> variables = new Vector<PMCComponent>();

    Java2JSon() {
        Gson gson = new Gson();

        variables.add(new PMCComponent("PLANT1::VAR1", "A variable", "1", "int32", new int[]{1}));
        
        Vector<PMCGap> gaps = new Vector<PMCGap>();
        gaps.add(new PMCGap("gap1", "A gap", 0, 0, 1, 1));
        gaps.add(new PMCGap("gap2", "Another gap", 0, 0, 2, 3));
        gaps.add(new PMCGap("gap3", "Another gap", 0, 0, 2, 4));
        variables.add(new PMCShape("PLANT1::VAR11", "A Shape", gaps));
        
        String json = gson.toJson(this);
        System.out.println(json);
    }

    public static void main (String args[]) {
        new Java2JSon(); 
    }

}

