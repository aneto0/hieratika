<html>
    <head>
        <link rel="import" href="/libraries.html">
        <link rel="import" href="/htk-helper.html">
    </head>
    <body>
        <template id="tloopcoils3d">
            <div id="dloopcoils3d" width="300px" height="300px">
            </div>
        </template>

        <script>
            //This is enclosure is required to protect the importDoc
            (function () {
                var importDoc = document.currentScript.ownerDocument; // importee
                //Constructor
                class HtkLoopCoils3D extends HTMLElement {
                    constructor() {
                        super();
                    }

                    createdCallback () {
                        var template = importDoc.querySelector("#tloopcoils3d");
                        var clone = document.importNode(template.content, true);
                        const root = this.attachShadow({mode: 'open'});
                        root.appendChild(clone);

                        parent.htkHelper.addVariablesInfoLoadedListener(this);
                    }
        
                    attachedCallback() {
                        this.div3d = this.shadowRoot.querySelector("#dloopcoils3d");
                        var minPhi = parseFloat(this.getAttribute("data-tokamak-min-phi"));
                        var maxPhi = parseFloat(this.getAttribute("data-tokamak-max-phi"));
                        this.drawVessel(minPhi, maxPhi);
                    }

                    variablesInfoLoaded() {
                        this.controls = new THREE.TrackballControls( this.camera, this.div3d );
                        this.controls.minDistance = 0;
                        this.controls.maxDistance = 50;

                        var coilVariables = this.getAttribute("data-coil-variables");
                        this.coils = {}; 
                        if (coilVariables !== undefined) {
                            coilVariables = JSON.parse(coilVariables);
                            coilVariables = coilVariables["ids"];
                            var props = ["r1", "z1", "r2", "z2", "phi1", "phi2"];
                            $.each(coilVariables, function (i, coilVariable) {
                                var coil = {color:STANDARD_FCOLOR};
                                $.each(props, function(p, prop) {
                                    var coilVariableId = coilVariable + "@" + prop;
                                    var htkCompArray = document._frameComponents[coilVariableId];
                                    if (htkCompArray !== undefined) {
                                        coil[prop] = parseFloat(htkCompArray[0].getValue());
                                        $.each(htkCompArray, function (j, htkComp) {
                                            htkComp.addValueChangedListener(this);
                                            htkComp.addEventListener("mouseover", function (evt) {
                                                this.setCoilHighlighted(coilVariable, true);
                                            }.bind(this));
                                            htkComp.addEventListener("mouseout", function (evt) {
                                                this.setCoilHighlighted(coilVariable, false);
                                            }.bind(this));
                                        }.bind(this));
                                    }
                                }.bind(this));
                                coil.name = coilVariable;
                                this.drawCoil(coil, 1);
                                this.coils[coilVariable] = coil;
                            }.bind(this));
                        }

                        this.animate();
                    }

                    valueChanged(source, typeOfChange) {
                    }

                    drawCoil(coil) {
                        var pts = [];
                        if (coil.z1 > coil.z2) {
                            pts.push(new THREE.Vector2(coil.r2, coil.z2));
                            pts.push(new THREE.Vector2(coil.r1, coil.z1));
                        }
                        else {
                            pts.push(new THREE.Vector2(coil.r1, coil.z1));
                            pts.push(new THREE.Vector2(coil.r2, coil.z2));
                        }
                        var coilGeometry = new THREE.LatheBufferGeometry( pts, 12, coil.phi1 * Math.PI / 180, coil.phi2 * Math.PI / 180);
                        coil.wireFrameMat = new THREE.MeshBasicMaterial({ color: 0xff0000} );
                        coil.wireFrameMat.wireframe = true;
                        var canvas = document.createElement("canvas");
                        var context = canvas.getContext("2d");
                        canvas.width = 256;
                        canvas.height = 128;
                        context.font = "16pt Arial";
                        context.textAlign = "center";
                        context.fillStyle = "yellow";
                        context.fillText(coil.name, canvas.width / 2, canvas.height / 2);
                        var fontTexture = new THREE.Texture(canvas);
                        fontTexture.needsUpdate = true;
                        var fontMaterial = new THREE.MeshBasicMaterial({
                            map : fontTexture,
                        });
                        fontMaterial.side = THREE.DoubleSide;
                        var coilLathe = THREE.SceneUtils.createMultiMaterialObject(coilGeometry, [coil.wireFrameMat, fontMaterial]);
                        this.scene.add(coilLathe);
                    }

                    setCoilHighlighted(coilVariable, highlight) {
                        if(highlight) {
                            this.coils[coilVariable].wireFrameMat.color = new THREE.Color(0xff00ff);
                        }
                        else {
                            this.coils[coilVariable].wireFrameMat.color = new THREE.Color(0xff0000);
                        }
                    } 

                    drawVessel(minPhi, maxPhi) {
                        this.renderer = new THREE.WebGLRenderer();
                        this.renderer.setSize(window.innerWidth, window.innerHeight);
                        this.div3d.appendChild(this.renderer.domElement);

                        this.camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 1, 500);
                        this.camera.position.set(-5, 0, 20);
                        this.camera.lookAt(new THREE.Vector3(0, 0, 0));

                        this.scene = new THREE.Scene();
                        var rcoords = [3.54,3.54,3.54,3.54,3.54,3.54,3.54,3.645,3.949,4.411,4.971,5.556,6.091,6.56,7.031,7.482,7.886,8.237,8.53,8.762,8.917,8.977,8.983,8.936,8.782,8.543,8.305,8.066,7.828,7.59,7.346,7.019,6.599,6.105,5.562,4.99,4.424,3.956,3.647,3.54,3.54,3.54,3.54,3.54,3.54];
                        var zcoords = [0.031,0.622,1.214,1.805,2.396,2.988,3.579,4.156,4.658,5.02,5.194,5.159,4.918,4.595,4.264,3.883,3.452,2.977,2.465,1.922,1.368,0.833,0.31,-0.209,-0.701,-1.222,-1.743,-2.264,-2.785,-3.306,-3.822,-4.283,-4.661,-4.935,-5.093,-5.122,-4.956,-4.599,-4.097,-3.518,-2.926,-2.335,-1.744,-1.152,-0.561];
                        var pts = [];
                        for (var i=1; i<(rcoords.length); i++) {
                            pts.push(new THREE.Vector2(rcoords[i], zcoords[i]));
                        }
                        pts.push(new THREE.Vector2(rcoords[1], zcoords[1]));
                        var geometry = new THREE.LatheBufferGeometry( pts, 12, minPhi * Math.PI / 180, maxPhi * Math.PI / 180);
                        var meshMaterial = new THREE.MeshBasicMaterial( { color: 0x2194ce} );
                        //meshMaterial.side = THREE.DoubleSide;
                        var wireFrameMat = new THREE.MeshBasicMaterial();
                        wireFrameMat.wireframe = true;
                        var lathe = THREE.SceneUtils.createMultiMaterialObject(geometry, [meshMaterial, wireFrameMat]);
                        this.scene.add(lathe);

                        this.renderer.render(this.scene, this.camera);
                    }

                    animate() {
                        requestAnimationFrame(this.animate.bind(this) );
                        this.controls.update();
                        this.renderer.render( this.scene, this.camera );
                    }
                }
       
                document.registerElement("htk-loop-coils-3d", {
                    prototype: HtkLoopCoils3D.prototype,
                });
            })(); 
        </script>
    </body>
</html>
