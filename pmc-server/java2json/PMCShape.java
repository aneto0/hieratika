import java.util.Vector;
class PMCShape extends PMCVariable {

    public PMCShape(String name, String description, boolean isLiveVariable, boolean isLibrary, PMCGap[] gaps) {
        super(name, description, "", "shape", new int[]{1}, true, false, false, null);
        this.gaps = gaps;
        this.testCube = new PMCGap[3][2][4];
        for(int i=0; i<this.testCube.length; i++) {
            for(int j=0; j<this.testCube[i].length; j++) {
                for(int k=0; k<this.testCube[i][j].length; k++) {
                    this.testCube[i][j][k] = new PMCGap("cube" + (i * this.testCube[i].length * this.testCube[i][j].length + j * this.testCube[i][j].length + k), "Test gap", false, false, i, j, k, 0);
                    System.out.println(this.testCube[i][j][k].name);
                }
            }
        }
    }

    private PMCGap []gaps;
    private PMCGap testCube[][][];
}


