/*
 date: 01/02/2021
 author: Luca Porzio

 copyright: Copyright 2017 F4E | European Joint Undertaking for ITER and
 the Development of Fusion Energy ('Fusion for Energy').
 Licensed under the EUPL, Version 1.1 or - as soon they will be approved
 by the European Commission - subsequent versions of the EUPL (the "Licence")
 You may not use this work except in compliance with the Licence.
 You may obtain a copy of the Licence at: http://ec.europa.eu/idabc/eupl

 warning: Unless required by applicable law or agreed to in writing,
 software distributed under the Licence is distributed on an "AS IS"
 basis, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express
 or implied. See the Licence permissions and limitations under the Licence.
*/

/*

<link rel="import" href="/libraries.html">
<link rel="import" href="/htk-component.html">

*/

import * as Constants. from './htk-constants.js'

const template = document.createElement('template');
template.innerHTML = `
<div id="dmatrix">
  <table border="0">
    <tr>
      <td>
        <button type="button" id="addRowButton">Add Row</button>
      </td>
      <td>
        <button type="button" id="removeRowButton">Remove Row</button>
      </td>
    </tr>
    <tr>
      <td>
        <button type="button" id="addColButton">Add Col</button>
      </td>
      <td>
        <button type="button" id="removeColButton">Remove Col</button>
      </td>
    </tr>
  </table>
  <table border="0">
    <tr>
      <td>
        <table border="1" id="tmatrix">
          <tr></tr>
        </table>
      </td>
    </tr>
  </table>
</div>
`;

  /**
   * @brief Array editor component.
   */
  class HtkMatrixDropMenuEditor extends HtkComponent {

    /**
     * @brief Constructor. NOOP.
     */
    constructor() {
      super();
    }


    domLoaded() {
      var enumId = this.getAttribute("data-initEnumId");
      var htkCompArray = document._frameComponents[enumId];
      this.enum = htkCompArray[0];
      if (this.enum !== null) {
        this.enum.hidden = true;
      }
    }

    //updates the matrix dimension? Do it in the refresh?
    updateMatrix(userChanged) {
      //If the current value does not match the initial value set the font color blue
      var initialValue = this.getInitialValue();
      var refValue = this.getReferenceValue();
      var plantValue = this.getPlantValue();
      var typeValue = this.getTypeValue();

      var temp = this.value.slice(0);
      var nRowsTemp = temp.length;
      var nColsTemp = temp[0].length;
      //resize the matrix
      this.value = new Array(this.nRows);


      for (var i = 0; i < this.nRows; i++) {
        this.value[i] = new Array(this.nCols);
        for (var j = 0; j < this.nCols; j++) {
          if ((j < nColsTemp) && (i < nRowsTemp)) {
            this.value[i][j] = temp[i][j];
          }
        }
      }

      if (userChanged) {
        this.fireValueChanged("value");
        this.updateRemote(this.getValue());
      }
      for (var i = 0; i < this.addUpdateValueListeners.length; i++) {
        this.addUpdateValueListeners[i].updateValue(userChanged);
      }
    }


    updateValue(userChanged) {
      for (var i = 0; i < this.nRows; i++) {
        this.value[i] = new Array(this.nCols);
        for (var j = 0; j < this.nCols; j++) {
          var id = "#menu_" + i.toString() + j.toString();
          var myCell = this.tbl.querySelector(id);
          if (myCell.selectedIndex >= 0) {
            this.value[i][j] = myCell[myCell.selectedIndex].value;
          }
        }
      }

      if (userChanged) {
        this.fireValueChanged("value");
        this.updateRemote(this.getValue());
      }

      for (var i = 0; i < this.addUpdateValueListeners.length; i++) {
        this.addUpdateValueListeners[i].updateValue(userChanged);
      }
    }



    refreshAllCellsDimensions(width, height) {
      for (var i = 0; i < this.nRows; i++) {
        for (var j = 0; j < this.nCols; j++) {
          var id = "#menu_" + i.toString() + j.toString();
          var myCell = this.tbl.querySelector(id);
          myCell.style.width = width;
          myCell.style.height = height;
        }
      }
      this.width = width;
      this.height = height;
    }


    refreshEnum(options) {
      if (this.value !== undefined) {
        this.refresh();
        this.enum.reset();
        this.enum.setChoices(options);
        for (var i = 0; i < this.value.length; i++) {
          for (var j = 0; j < this.value[0].length; j++) {
            var id = "#menu_" + i.toString() + j.toString();
            var myCell = this.tbl.querySelector(id);
            var cellIdx = myCell.selectedIndex;
            while (myCell.hasChildNodes()) {
              myCell.removeChild(myCell.childNodes[0]);
            }
            for (var n = 0; n < options.length; n++) {
              var option = document.createElement("option");
              option.text = options[n];
              option.value = options[n];
              myCell.appendChild(option);


              if (cellIdx >= 0) {
                myCell.selectedIndex = cellIdx;
              }
            }
          }
        }
        for (var h = 0; h < this.value.length; h++) {
          for (var k = 0; k < this.value[0].length; k++) {
            var id = "#menu_" + h.toString() + k.toString();
            var myCell = this.tbl.querySelector(id);
            for (var m = 0; m < options.length; m++) {
              var comp = myCell[m].value;
              if (comp === this.value[h][k]) {
                myCell.selectedIndex = m;
              }
            }
          }
        }
      }
    }


    checkValue() {
      for (var h = 0; h < this.value.length; h++) {
        for (var k = 0; k < this.value[0].length; k++) {
          var id = "#menu_" + h.toString() + k.toString();
          var myCell = this.tbl.querySelector(id);
          myCell.style.color = Constants.STANDARD_FCOLOR;
          if (this.getInitialValue() !== undefined) {
            if (this.getInitialValue()[h] !== undefined) {
              if (this.getInitialValue()[h][k] !== undefined) {

                if (this.value[h][k] != this.initValue[h][k]) {
                  myCell.style.color = Constants.DIFF_INIT_CHANGED_COLOR;
                }
              }
            }
          }
          if (this.getPlantValue() !== undefined && this.getReferenceValue() !== undefined) {
            if (this.getPlantValue()[h] !== undefined) {
              if (this.getPlantValue()[h][k] !== undefined) {
                if (this.getReferenceValue()[h] !== undefined) {
                  if (this.getReferenceValue()[h][k] !== undefined) {
                    if (!this.compareWithReference(this.getValue()[h][k], this.getPlantValue()[h][k], this.getReferenceValue()[h][k])) {
                      myCell.style.color = Constants.PLANT_OR_REF_CHANGED_COLOR;
                    }
                  }
                }
              }
            }
          }
        }
      }
    }


    /**
     * @brief See HtkComponent.refresh
     */
    refresh() {
      if (this.initialised) {
        var elementsToSet = this.getValue();

        if ((!isNaN(elementsToSet.length)) && (!isNaN(elementsToSet[0].length))) {
          var needRefresh = false;
          if ((this.nRows !== elementsToSet.length)) {
            needRefresh = true;
          }
          if ((this.nCols !== elementsToSet[0].length)) {
            needRefresh = true;
          }

          if (needRefresh) {

            for (var i = 0; i < this.nRows; i++) {
              this.tbl.deleteRow(0);
            }

            this.nRows = elementsToSet.length;
            this.nCols = elementsToSet[0].length;

            for (var i = 0; i < this.nRows; i++) {
              var row = this.tbl.insertRow(i);
              for (var j = 0; j < this.nCols; j++) {
                var col = row.insertCell(j);
                var createSel = document.createElement("select");
                createSel.id = "menu_" + i.toString() + j.toString();
                createSel.style.width = this.width;
                createSel.style.height = this.height
                createSel.style.cursor = "pointer";
                createSel.style.fontSize = "18px";
                col.appendChild(createSel);

                if (this.enum !== null) {
                  for (var k = 0; k < this.enum.getChoices().length; k++) {
                    var option = document.createElement("option");
                    option.text = this.enum.getChoices()[k];
                    option.value = this.enum.getChoices()[k];
                    createSel.appendChild(option);
                  }
                }

                createSel.addEventListener("input", function(e) {
                  this.updateValue(true);
                }.bind(this));
              }
            }

            for (var h = 0; h < this.value.length; h++) {
              for (var k = 0; k < this.value[0].length; k++) {
                var id = "#menu_" + h.toString() + k.toString();
                var myCell = this.tbl.querySelector(id);
                for (var m = 0; m < myCell.childElementCount; m++) {
                  var comp = myCell[m].value;
                  if (comp === this.value[h][k]) {
                    myCell.selectedIndex = m;
                  }
                }
              }
            }
          } else {
            for (var h = 0; h < this.value.length; h++) {
              for (var k = 0; k < this.value[0].length; k++) {
                var id = "#menu_" + h.toString() + k.toString();
                var myCell = this.tbl.querySelector(id);
                for (var m = 0; m < myCell.childElementCount; m++) {
                  var comp = myCell[m].value;
                  if (comp === this.value[h][k]) {
                    myCell.selectedIndex = m;
                  }
                }
              }
            }
          }
        }
        this.checkValue();
        if (this.addRefreshListeners !== undefined) {
          for (var i = 0; i < this.addRefreshListeners.length; i++) {
            this.addRefreshListeners[i].refresh();
          }
        }
      }
    }

    /**
     * @brief See HtkComponent.setValue
     */
    setValue(elementsToSet, updateRemote = true) {
      if (elementsToSet.length > 0) {
        super.setValue(elementsToSet.slice(0), updateRemote);
        this.initialised = true;
      }
    }

    /**
     * @brief See HtkComponent.setInitialValue
     */
    setInitialValue(initialValueToSet) {
      if (initialValueToSet.length > 0) {
        super.setInitialValue(initialValueToSet.slice(0));
      }
    }

    /**
     * @brief See HtkComponent.setPlantValue
     */
    setPlantValue(plantValueToSet) {
      if (plantValueToSet.length > 0) {
        super.setPlantValue(plantValueToSet.slice(0));
      }
    }

    /**
     * @brief See HtkComponent.setReferenceValue
     */
    setReferenceValue(referenceValueToSet) {
      if (referenceValueToSet.length > 0) {
        super.setReferenceValue(referenceValueToSet.slice(0));
      }
    }

    /**
     * @brief See HtkComponent.setReadOnly
     */
    setReadOnly(isReadOnly) {
      super.setReadOnly(isReadOnly);
      this.addRowButton.disabled = isReadOnly;
      this.removeRowButton.disabled = isReadOnly;
      this.addColButton.disabled = isReadOnly;
      this.removeColButton.disabled = isReadOnly;
    }

    /**
     * @brief See HtkComponent.getTemplate
     */
    getTemplate() {
      var templateContent = template.content;
      return templateContent;
    }

    getCell(i, j) {
      var id = "#menu_" + i.toString() + j.toString();
      return this.tbl.querySelector(id);
    }


    addRowCallback() {
      //console.log("nRows=%d", this.nRows);
      var row = this.tbl.insertRow(this.nRows);
      for (var i = 0; i < this.nCols; i++) {
        var col = row.insertCell(i);
        var createSel = document.createElement("select");
        createSel.id = "menu_" + (this.nRows).toString() + i.toString();
        createSel.style.width = this.width;
        createSel.style.height = this.height;
        createSel.style.cursor = "pointer";
        createSel.style.fontSize = "18px";
        col.appendChild(createSel);


        if (this.enum !== null) {
          for (var k = 0; k < this.enum.getChoices().length; k++) {
            var option = document.createElement("option");
            option.text = this.enum.getChoices()[k];
            option.value = this.enum.getChoices()[k];
            createSel.appendChild(option);
            if (k == 0) {
              col.value = option.value;
            }
          }
        }

        createSel.addEventListener("input", function(e) {
          this.updateValue(true);
        }.bind(this));

      }
      this.nRows++;
      this.updateMatrix(true);
      if (this.addAddRowListeners !== undefined) {
        for (var i = 0; i < this.addAddRowListeners.length; i++) {
          this.addAddRowListeners[i].addRowCallback();
        }
      }
    }

    removeRowCallback() {
      if (this.nRows > 1) {
        this.tbl.deleteRow(this.nRows - 1);
        this.nRows--;
        this.numberOfElements = this.nRows * this.nCols;
        this.updateMatrix(true);
      }

      if (this.removeRowListeners !== undefined) {
        for (var i = 0; i < this.addRemoveRowListeners.length; i++) {
          this.addRemoveRowListeners[i].removeRowCallback();
        }
      }
    }


    addColCallback() {
      for (var i = 0; i < this.nRows; i++) {
        var row = this.tbl.rows[i];
        var col = row.insertCell(this.nCols);

        var createSel = document.createElement("select");
        createSel.id = "menu_" + i.toString() + (this.nCols).toString();
        createSel.style.width = this.width;
        createSel.style.height = this.height;
        createSel.style.cursor = "pointer";
        createSel.style.fontSize = "18px";
        col.appendChild(createSel);

        if (this.enum !== null) {
          for (var k = 0; k < this.enum.choices.length; k++) {
            var option = document.createElement("option");
            option.text = this.enum.getChoices()[k];
            option.value = this.enum.getChoices()[k];
            createSel.appendChild(option);
            if (k == 0) {
              createSel.value = option.value;
            }
          }
        }

        createSel.addEventListener("input", function(e) {
          this.updateValue(true);
        }.bind(this));


      }
      this.nCols++;
      this.numberOfElements = this.nRows * this.nCols;
      this.updateMatrix(true);

      if (this.addAddColListeners !== undefined) {
        for (var i = 0; i < this.addAddColListeners.length; i++) {
          this.addAddColListeners[i].addColCallback();
        }
      }

    }

    removeColCallback() {
      //console.log("nCols=%d", this.nCols);
      if (this.nCols > 1) {
        for (i = 0; i < this.nRows; i++) {
          var row = this.tbl.rows[i];
          row.deleteCell(this.nCols - 1);
        }
        this.nCols--;
        this.numberOfElements = this.nRows * this.nCols;
        this.updateMatrix(true);

      }
      if (this.addRemoveColListeners !== undefined) {
        for (var i = 0; i < this.addRemoveColListeners.length; i++) {
          this.addRemoveColListeners[i].removeColCallback();
        }
      }
    }

    showHideButtons(show) {
      this.addRowButton.hidden = !show;
      this.addColButton.hidden = !show;
      this.removeRowButton.hidden = !show;
      this.removeColButton.hidden = !show;
    }


    addAddRowCallback(comp) {
      this.addAddRowListeners.push(comp);
    }

    addAddColCallback(comp) {
      this.addAddColListeners.push(comp);
    }

    addRemoveRowCallback(comp) {
      this.addRemoveRowListeners.push(comp);
    }

    addRemoveColCallback(comp) {
      this.addRemoveColListeners.push(comp);
    }


    addRefreshCallback(comp) {
      this.addRefreshListeners.push(comp);
    }

    addUpdateValueCallback(comp) {
      this.addUpdateValueListeners.push(comp);
    }


    /**
     * @brief See HtkComponent.createdCallback
     */
    connectedCallback() {
      super.connectedCallback();
      this.nRows = 0;
      this.nCols = 0;
      this.width = "200px";
      this.height = "25px";
      this.numberOfElements = 0;
      this.initialised = false;

      this.addAddRowListeners = new Array();
      this.addRemoveRowListeners = new Array();
      this.addAddColListeners = new Array();
      this.addRemoveColListeners = new Array();
      this.addRefreshListeners = new Array();
      this.addUpdateValueListeners = new Array();

      this.addRowButton = this.shadowRoot.querySelector("#addRowButton");


      this.tbl = this.shadowRoot.querySelector("#tmatrix");

      this.addRowButton.onclick = function() {
        this.addRowCallback();
      }.bind(this);

      this.removeRowButton = this.shadowRoot.querySelector("#removeRowButton");
      this.removeRowButton.onclick = function() {
        this.removeRowCallback();
      }.bind(this);

      this.addColButton = this.shadowRoot.querySelector("#addColButton");
      this.addColButton.onclick = function() {
        this.addColCallback();
      }.bind(this);

      this.removeColButton = this.shadowRoot.querySelector("#removeColButton");
      this.removeColButton.onclick = function() {
        this.removeColCallback();
      }.bind(this);
    }

  }

  /**
   * @brief Registers the element.
   */
  customElements.define('htk-matrix-dropmenu-editor', HtkMatrixDropMenuEditor);
