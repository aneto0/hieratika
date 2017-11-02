import java.util.Vector;

class PMCLibrary extends PMCVariable {

    public PMCLibrary(String name, String description) {
        super(name, description, new Vector(), "library", new int[]{1}, false, false, null, new Vector());
    }
}

