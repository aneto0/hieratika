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


import { HtkComponent } from './htk-component.js'

const template = document.createElement('template');
template.innerHTML = `
<div id="dmatrix">
  <table border="0">
    <tr>
      <td>
        <table border="1" id="tmatrix">
          <tr></tr>
        </table>
      </td>
      <td>
        <button type="button" id="addRowButton">Add Row</button>
        <button type="button" id="addColButton">Add Col</button>
        <button type="button" id="removeRowButton">Remove Row</button>
        <button type="button" id="removeColButton">Remove Col</button>
      </td>
    </tr>
  </table>
</div>
`;

                /**
   * @brief Array editor component.
   */
  class HtkMatrixEditor extends HtkComponent {

    /**
     * @brief Constructor. NOOP.
     */
    constructor() {
      super();
    }

    checkValue() {
      //If the current value does not match the initial value set the font color blue
      var initialValue = this.getInitialValue();
      var refValue = this.getReferenceValue();
      var plantValue = this.getPlantValue();
      //this.value=new Array(this.tbl.rows.length);

      for (var i = 0;
        (i < this.tbl.rows.length); i++) {
        //this.value[i]=new Array(this.tbl.rows[0].cells.length);

        var row = this.tbl.rows[i];
        for (var j = 0;
          (j < this.tbl.rows[0].cells.length); j++) {
          var cell = row.cells[j];
          if (cell !== undefined) {
            var cellValue = cell.innerHTML;

            var cellInitValue = "";
            if (initialValue !== undefined) {
              if (initialValue[i] !== undefined) {
                if (initialValue[i][j] !== undefined) {
                  cellInitValue = initialValue[i][j];
                } else {
                  cellInitValue = "";
                }
              } else {
                cellInitValue = "";
              }
            }
            if (!this.compareValues(cellValue, cellInitValue)) {
              cell.style.color = Constants.DIFF_INIT_CHANGED_COLOR;
            } else {
              cell.style.color = Constants.STANDARD_FCOLOR;
            }

            var cellRefValue = "";
            if (refValue !== undefined) {
              if (refValue[i] !== undefined) {
                if (refValue[i][j] !== undefined) {
                  cellRefValue = refValue[i][j];
                } else {
                  cellRefValue = "";
                }
              } else {
                cellRefValue = "";
              }
            }
            var cellPlantValue;
            if (plantValue !== undefined) {
              if (plantValue[i] !== undefined) {
                if (plantValue[i][j] !== undefined) {
                  cellPlantValue = plantValue[i][j];
                } else {
                  cellPlantValue = "";
                }
              } else {
                cellPlantValue = "";
              }
            }

            var newBackgroundColor = Constants.STANDARD_BCOLOR;
            if ((!this.isUserAllowedToWrite()) || (this.isReadOnly())) {
              newBackgroundColor = Constants.DISABLED_COLOR;
            }
            if (!this.compareWithReference(cellValue, cellPlantValue, cellRefValue)) {
              newBackgroundColor = Constants.PLANT_OR_REF_CHANGED_COLOR;
            }
            cell.style.backgroundColor = newBackgroundColor;
          }
        }
      }
      var error = false;
      var errorIdx = 0;
      if (this.validations !== undefined) {
        for (errorIdx = 0;
          (errorIdx < this.validations.length) && (!error); errorIdx++) {
          error = !this.validations[errorIdx].test();
        }
      }
      if (error) {
        newBackgroundColor = Constants.ERROR_BCOLOR;
        for (var i = 0;
          (i < this.nRows); i++) {
          var row = this.tbl.rows[i];
          for (var j = 0;
            (j < this.nCols); j++) {
            var cell = row.cells[j];
            if (cell !== undefined) {
              cell.style.backgroundColor = Constants.ERROR_BCOLOR;
            }
          }
        }
        errorIdx--;
        this.title = "Failed @ " + this.validations[errorIdx].getValidationFunction();
      } else {
        this.title = this.toString();
      }

      for (var i = 0; i < this.addUpdateValueListeners.length; i++) {
        this.addUpdateValueListeners[i].updateValue(true);
      }
    }

    updateValue(userChanged) {
      //If the current value does not match the initial value set the font color blue
      this.value = new Array(this.tbl.rows.length);
      var typeValue = this.getTypeValue();

      for (var i = 0;
        (i < this.tbl.rows.length); i++) {
        this.value[i] = new Array(this.tbl.rows[0].cells.length);

        var row = this.tbl.rows[i];
        for (var j = 0;
          (j < this.tbl.rows[0].cells.length); j++) {
          var cell = row.cells[j];
          if (cell !== undefined) {
            var cellValue = cell.innerHTML;
            var numberValue = window.htkHelper.textToTypeValue(cellValue, typeValue);
            if (numberValue === undefined) {
              numberValue = cellValue;
            }
            this.value[i][j] = numberValue;
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





    /**
     * @brief See HtkComponent.refresh
     */
    refresh() {
      if ((this.getValue() !== undefined)) {
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
                col.style.width = this.width;
                col.style.height = this.height;
                col.style.textAlign = "right";
                col.setAttribute("contenteditable", "true");
                col.innerHTML = elementsToSet[i][j];
                col.addEventListener("input", function(e) {
                  this.updateValue(false);
                  this.checkValue();
                  if (this.addRefreshListeners !== undefined) {
                    for (var i = 0; i < this.addRefreshListeners.length; i++) {
                      this.addRefreshListeners[i].refresh();
                    }
                  }
                }.bind(this));
              }
            }
          } else {
            for (var i = 0; i < this.nRows; i++) {
              var row = this.tbl.rows[i];
              for (var j = 0; j < this.nCols; j++) {
                col = row.cells[j];
                col.innerHTML = elementsToSet[i][j];
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
    }

    /**
     * @brief See HtkComponent.setValue
     */
    setValue(elementsToSet, updateRemote = true) {
      super.setValue(elementsToSet.slice(0), updateRemote);
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


    addRowCallback() {
      var row = this.tbl.insertRow(this.nRows);
      this.nRows++;
      for (var i = 0; i < this.nCols; i++) {
        var col = row.insertCell(i);
        this.numberOfElements = this.nRows * this.nCols;
        col.setAttribute("contenteditable", "true");
        col.style.width = this.width;
        col.style.height = this.height;
        col.style.textAlign = "right";
        col.addEventListener("input", function(e) {
          this.updateValue(false);
          this.checkValue();
          if (this.addRefreshListeners !== undefined) {
            for (var i = 0; i < this.addRefreshListeners.length; i++) {
              this.addRefreshListeners[i].refresh();
            }
          }
        }.bind(this));
      }
      this.updateValue(true);
    }


    removeRowCallback() {
      //console.log("nRows=%d", this.nRows);
      if (this.nRows > 1) {
        this.tbl.deleteRow(this.nRows - 1);
        this.nRows--;
        this.numberOfElements = this.nRows * this.nCols;
        this.updateValue(true);
      }
    }

    addColCallback() {
      //console.log("nCols=%d", this.nCols);
      for (var i = 0; i < this.nRows; i++) {
        var row = this.tbl.rows[i];
        var col = row.insertCell(this.nCols);
        col.setAttribute("contenteditable", "true");
        col.style.width = this.width;
        col.style.height = this.height;

        col.style.textAlign = "right";
        col.addEventListener("input", function(e) {
          this.updateValue(false);
          this.checkValue();
          if (this.addRefreshListeners !== undefined) {
            for (var i = 0; i < this.addRefreshListeners.length; i++) {
              this.addRefreshListeners[i].refresh();
            }
          }
        }.bind(this));
      }
      this.nCols++;
      this.numberOfElements = this.nRows * this.nCols;
      this.updateValue(true);
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
        this.updateValue(true);

      }
    }


    showHideButtons(show) {
      this.addRowButton.hidden = !show;
      this.addColButton.hidden = !show;
      this.removeRowButton.hidden = !show;
      this.removeColButton.hidden = !show;
    }

    refreshAllCellsDimensions(width, height) {
      for (var i = 0; i < this.tbl.rows.length; i++) {
        for (var j = 0; j < this.tbl.rows[0].cells.length; j++) {

          var myCell = this.tbl.rows[i].cells[j];
          myCell.style.width = width;
          myCell.style.height = height;
        }
      }
      this.width = width;
      this.height = height;
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
      this.nRows = 1;
      this.nCols = 1;
      this.numberOfElements = 0;

      this.width = "20px";
      this.height = "20px";

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
  window.customElements.define('htk-matrix-editor', HtkMatrixEditor);