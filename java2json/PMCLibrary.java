import java.util.Vector;

class PMCLibrary extends PMCVariable {

    public PMCLibrary(String name, String description) {
        super(name, description, new Vector(), "string", new int[]{1}, false, false, true, null, new Vector());
    }
}

