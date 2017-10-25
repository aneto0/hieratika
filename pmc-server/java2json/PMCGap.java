class PMCGap extends PMCComponent {

    public PMCGap(String name, String description, float x0, float x1, float y0, float y1) {
        super(name, description, "", "gap", new int[]{1});
        this.x0 = x0;
        this.y0 = y0;
        this.x1 = x1;
        this.y1 = y1;
    }

    public float x0;
    public float y0;
    public float x1;
    public float y1;
}

