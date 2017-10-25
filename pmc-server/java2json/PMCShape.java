import java.util.Vector;
class PMCShape extends PMCComponent {

    public PMCShape(String name, String description, Vector<PMCGap> gaps) {
        super(name, description, "", "shape", new int[]{1});
        this.gaps = gaps;
        this.limiter = new PMCGap[3][2][4];

    }

    private Vector<PMCGap> gaps;
    private PMCGap limiter[][][];
}


