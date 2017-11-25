import java.util.Arrays;
import java.util.Vector;

class P55A0EmbeddedList extends PMCVariable {

    public P55A0EmbeddedList() {
        super("EMBED", "55 A0 embedded parameters", new Vector(), "", new int[]{1}, true, false, null);
    }

    P55AAEmbedded AA = new P55AAEmbedded();
}


