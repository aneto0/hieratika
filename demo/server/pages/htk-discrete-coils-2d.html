<html>
    <head>
        <link rel="import" href="/libraries.html">
        <link rel="import" href="/htk-helper.html">
    </head>
    <body>
        <template id="tdiscretecoils2d">
            <svg style="background-color:transparent" id="tcanvas" xmlns="http://www.w3.org/2000/svg" width="600" height="600"></svg>
        </template>

        <script>
            //This is enclosure is required to protect the importDoc
            (function () {
                var importDoc = document.currentScript.ownerDocument; // importee
                //Constructor
                class HtkDiscreteCoils2D extends HTMLElement {
                    constructor() {
                        super();
                    }

                    createdCallback () {
                        var template = importDoc.querySelector("#tdiscretecoils2d");
                        var clone = document.importNode(template.content, true);
                        const root = this.attachShadow({mode: 'open'});
                        root.appendChild(clone);

                        this.canvas = this.shadowRoot.querySelector("#tcanvas");
                        parent.htkHelper.addVariablesInfoLoadedListener(this);
                    }

                    variablesInfoLoaded() {
                        var coilVariables = this.getAttribute("data-coil-variables");
                        this.coils = {}; 
                        this.canvasHeight = this.canvas.getAttribute("height");
                        this.scale = 50;
                        this.roffset = -3;
                        this.zoffset = 6;
                        this.drawVessel(1, "red");
                        if (coilVariables !== undefined) {
                            coilVariables = JSON.parse(coilVariables);
                            coilVariables = coilVariables["ids"];
                            var props = ["r", "z", "angle"];
                            $.each(coilVariables, function (i, coilVariable) {
                                var coil = {color:STANDARD_FCOLOR};
                                var coilRef = {color:REFERENCE_COLOR};
                                var coilPlant = {color:PLANT_COLOR};
                                $.each(props, function(p, prop) {
                                    var coilVariableId = coilVariable + "@" + prop;
                                    var htkCompArray = document._frameComponents[coilVariableId];
                                    if (htkCompArray !== undefined) {
                                        coil[prop] = parseFloat(htkCompArray[0].getValue());
                                        coilRef[prop] = parseFloat(htkCompArray[0].getValue());
                                        coilPlant[prop] = parseFloat(htkCompArray[0].getValue());
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
                                this.drawCoil(coilRef, 1, true);
                                this.drawCoil(coilPlant, 1, true);
                                this.drawCoil(coil, 1, true);
                                this.coils[coilVariable + "Ref"] = coilRef;
                                this.coils[coilVariable + "Plant"] = coilPlant;
                                this.coils[coilVariable] = coil;
                            }.bind(this));
                        }
                    }

                    valueChanged(src, typeOfChange) {
                        //Find if the coil is already registered
                        var coilId = src.id.substring(0, src.id.lastIndexOf("@"));
                        var propChange = src.id.substring(src.id.lastIndexOf("@") + 1);
                        var coil;
                        var value;
                        if (typeOfChange === HtkComponent.VALUE_CHANGED) {
                            coil = this.coils[coilId];
                            value = parseFloat(src.getValue());
                        }
                        else if (typeOfChange === HtkComponent.VALUE_CHANGED_PLANT) {
                            coil = this.coils[coilId + "Plant"];
                            value = parseFloat(src.getPlantValue());
                        }
                        else if (typeOfChange === HtkComponent.VALUE_CHANGED_REFERENCE) {
                            coil = this.coils[coilId + "Ref"];
                            value = parseFloat(src.getReferenceValue());
                        }
                        if (value !== NaN) {
                            if(coil !== undefined) {
                                if (propChange === "r") {
                                    coil["r"] = value;
                                }
                                else if (propChange === "z") {
                                    coil["z"] = value;
                                }
                                else if (propChange === "angle") {
                                    coil["angle"] = value;
                                }
                                this.drawCoil(coil, 1);
                            }
                        }
                    }
                    
                    createText(x1, y1, t, color) {
                        var text = document.createElementNS("http://www.w3.org/2000/svg", "text");
                        text.setAttribute("x", x1);
                        text.setAttribute("y", y1);
                        text.setAttribute("fill", color);
                        text.setAttribute("font-size", 8);
                        text.textContent = t; 
                        text.addEventListener("mouseover", function(evt) {
                            text.setAttribute("font-size", 16);
                        }.bind(this));
                        text.addEventListener("mouseout", function (evt) {
                            text.setAttribute("font-size", 8);
                        }.bind(this));

                        return text;
                    }

                    createLine(x1, y1, x2, y2, w, color) {
                        var line = document.createElementNS("http://www.w3.org/2000/svg", "line");
                        line.setAttribute("x1", x1);
                        line.setAttribute("y1", y1);
                        line.setAttribute("x2", x2);
                        line.setAttribute("y2", y2);
                        line.setAttribute("stroke", color);
                        line.setAttribute("stroke-width", w);
                        return line;
                    }

                    getX(r) {
                        return (r + this.roffset) * this.scale;
                    }

                    getY(z) {
                        return (this.canvasHeight - ((z + this.zoffset) * this.scale));
                    }

                    setCoilHighlighted(coilId, highlight) {
                        var coil = this.coils[coilId];
                        if (coil !== undefined) {
                            if (highlight) {
                                var color = "#00FF00";
                                coil.line.setAttribute("stroke", color);
                                coil.text.setAttribute("fill", color);
                                coil.text.setAttribute("font-size", 16);
                            }
                            else {
                                var color = STANDARD_FCOLOR;
                                coil.line.setAttribute("stroke", color);
                                coil.text.setAttribute("fill", color);
                                coil.text.setAttribute("font-size", 8);

                            }
                        }
                    }

                    drawCoil(coil, w, create = false, coilPseudoSize = 0.1) {
                        var angleRads = coil.angle * Math.PI / 180.;
                        var r1 = coil.r - (coilPseudoSize * Math.cos(angleRads)); 
                        var r2 = coil.r + coilPseudoSize * Math.cos(angleRads); 
                        var z1 = coil.z - coilPseudoSize * Math.sin(angleRads); 
                        var z2 = coil.z + coilPseudoSize * Math.sin(angleRads); 
                        var x1 = this.getX(r1);
                        var y1 = this.getY(z1);
                        var x2 = this.getX(r2);
                        var y2 = this.getY(z2);

                        if (create) {
                            coil["line"] = this.createLine(x1, y1, x2, y2, w, coil.color);
                            this.canvas.appendChild(coil.line);
                            if (coil.name !== undefined) {
                                coil["text"] = this.createText(x1, y1, coil.name, coil.color);
                                this.canvas.appendChild(coil.text);
                            }
                        }
                        else {
                            coil.line.setAttribute("x1", x1);
                            coil.line.setAttribute("y1", y1);
                            coil.line.setAttribute("x2", x2);
                            coil.line.setAttribute("y2", y2);
                            coil.line.setAttribute("stroke", coil.color);
                            if (coil.name !== undefined) {
                                coil.text.setAttribute("x", x1);
                                coil.text.setAttribute("y", y1);
                                coil.text.setAttribute("fill", coil.color);
                            }
                        }
                    }

                    drawVessel(w, color) {
                        var rcoords = [3.54,3.54,3.54,3.54,3.54,3.54,3.54,3.645,3.949,4.411,4.971,5.556,6.091,6.56,7.031,7.482,7.886,8.237,8.53,8.762,8.917,8.977,8.983,8.936,8.782,8.543,8.305,8.066,7.828,7.59,7.346,7.019,6.599,6.105,5.562,4.99,4.424,3.956,3.647,3.54,3.54,3.54,3.54,3.54,3.54];
                        var zcoords = [0.031,0.622,1.214,1.805,2.396,2.988,3.579,4.156,4.658,5.02,5.194,5.159,4.918,4.595,4.264,3.883,3.452,2.977,2.465,1.922,1.368,0.833,0.31,-0.209,-0.701,-1.222,-1.743,-2.264,-2.785,-3.306,-3.822,-4.283,-4.661,-4.935,-5.093,-5.122,-4.956,-4.599,-4.097,-3.518,-2.926,-2.335,-1.744,-1.152,-0.561];
                        for (var i=0; i<(rcoords.length - 1); i++) {
                            this.canvas.appendChild(this.createLine(this.getX(rcoords[i]), this.getY(zcoords[i]), this.getX(rcoords[i+1]), this.getY(zcoords[i+1]), w, color));
                        }
                        this.canvas.appendChild(this.createLine(this.getX(rcoords[i]), this.getY(zcoords[i]), this.getX(rcoords[0]), this.getY(zcoords[0]), w, color));
                    }
                }
                
                document.registerElement("htk-discrete-coils-2d", {
                    prototype: HtkDiscreteCoils2D.prototype,
                });
            })(); 
        </script>
    </body>
</html>
