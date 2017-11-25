import java.lang.reflect.*;
import java.util.Arrays;
import java.util.Vector;

class Plant55A0 {

    public Plant55A0(Vector variables) {
        try {
            Field[] fields = Plant55A0.class.getFields();
            for (int i=0; i<fields.length; i++) {
                variables.add(fields[i].get(this)); 
            }
        }
        catch(Exception e) {
            e.printStackTrace();
        }
    }

    public P55A0DiscreteCoils discreteCoils = new P55A0DiscreteCoils();
    public P55A0LoopCoils loopCoils = new P55A0LoopCoils();
    public P55A0EmbeddedList embedded = new P55A0EmbeddedList();
}
