/*
 date: 11/02/2021
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
       <link rel="import" href="/htk-matrix-dropmenu-editor.html">
       <link rel="import" href="/htk-array-editor.html">
*/

import * as Constants from './htk-constants.js'
import { HtkComponent } from './htk-component.js'

const template = document.createElement('template');
template.innerHTML = `
<div id="dmatrix">
    <table border="0" id="mainTable">
        <tr>
            <td>
                <button type="button" id="functionAssignmentDone">Inputs Assigned</button>
            </td>
        </tr>
        <tr>
            <td>
        <select id="tselect" name="tselect">
        </select>
            </td>
        <tr>
        <tr>
            <td>
        <table id="flyTable" border="1">
        </table>
            </td>
        <tr>
    </table>
    <table border="0" id="testTable">
    <tr>
            <td>
        <input type="text" id="testInput"></input>
            </td>
            <td>
                <button type="button" id="testButton">Test</button>
            </td>
            <td>
        <input type="text" id="testOutput"></input>
            </td>
        <tr>
    </table>
</div>
`;

        /**
         * @brief Array editor component.
         */
        class LsFunctionLogic extends HtkComponent {

          /**
           * @brief Constructor. NOOP.
           */
          constructor() {
            super();
          }

          domLoaded() {
            var assignmentId = this.getAttribute("data-assignmentId");
            var htkCompArray = document._frameComponents[assignmentId];
            this.assignment = htkCompArray[0];
          }


          checkValue() {
            if (this.fnames.selectedIndex >= 0) {
              for (var i = 0; i < this.value[this.fnames.selectedIndex].length; i++) {
                for (var j = 0; j < this.value[this.fnames.selectedIndex][0].length; j++) {
                  var myCell = this.flytable.rows[i].cells[j];
                  myCell.style.color = Constants.STANDARD_FCOLOR;

                  if (this.getInitialValue() !== undefined) {
                    if (this.getInitialValue()[this.fnames.selectedIndex][i] !== undefined) {
                      if (this.getInitialValue()[this.fnames.selectedIndex][i][j] !== undefined) {

                        if (this.value[this.fnames.selectedIndex][i][j] !== this.initValue[this.fnames.selectedIndex][i][j]) {
                          myCell.style.color = Constants.DIFF_INIT_CHANGED_COLOR;
                        }
                      }
                    }
                  }
                  if (this.getPlantValue() !== undefined && this.getReferenceValue() !== undefined) {
                    if (this.getPlantValue()[this.fnames.selectedIndex][i] !== undefined) {
                      if (this.getPlantValue()[this.fnames.selectedIndex][i][j] !== undefined) {
                        if (this.getReferenceValue()[this.fnames.selectedIndex][i] !== undefined) {
                          if (this.getReferenceValue()[this.fnames.selectedIndex][i][j] !== undefined) {
                            if (!this.compareWithReference(this.getValue()[this.fnames.selectedIndex][i][j], this.getPlantValue()[this.fnames.selectedIndex][i][j], this.getReferenceValue()[this.fnames.selectedIndex][i][j])) {
                              myCell.style.color = Constants.PLANT_OR_REF_CHANGED_COLOR;
                            }
                          }
                        }
                      }
                    }
                  }

                  if ((this.value[this.fnames.selectedIndex][i][j] !== "x") && (this.value[this.fnames.selectedIndex][i][j] !== "0") && (this.value[this.fnames.selectedIndex][i][j] !== "1")) {
                    myCell.style.color = Constants.ERROR_BCOLOR;
                  }
                }
              }
            }
          }

          /**
           * @brief Checks if the component style should be updated due to a value change and executes all the validation functions.
           * @details For each element array, performs the same actions described in HtkAbstractInput.updateMatrix.
           * @param[in] userChanged true if the value update was triggered by a user action.
           */

          updateValue(userChanged) {
            if ((this.fnames.selectedIndex >= 0) && (this.value !== undefined)) {
              for (var i = 0; i < this.flytable.rows.length; i++) {
                var row = this.flytable.rows[i];
                for (var j = 0; j < row.cells.length; j++) {
                  if (this.value !== undefined) {
                    if (this.value[this.fnames.selectedIndex][i] !== undefined) {
                      if (this.value[this.fnames.selectedIndex][i][j] !== undefined) {
                        this.value[this.fnames.selectedIndex][i][j] = row.cells[j].innerHTML;
                      }
                    }
                  }
                }
              }
              if (userChanged) {
                this.fireValueChanged("value");
                this.updateRemote(this.getValue());
              }
            }
          }


          scheduleChanged(x) {
            var nElements = this.assignment.value.length;
            var selIndex = this.fnames.selectedIndex;
            while (this.fnames.hasChildNodes()) {
              this.fnames.removeChild(this.fnames.childNodes[0]);
            }
            for (var k = 0; k < nElements; k++) {
              var option = document.createElement("option");
              option.text = this.assignment.value[k];
              option.value = option.text;
              this.fnames.appendChild(option);
            }
            this.fnames.selectedIndex = selIndex;
            var nrows = this.flytable.rows.length;
            for (var i = 0; i < nrows; i++) {
              this.flytable.deleteRow(0);
            }

            var nInputs = this.assignment.matrix.value.length;
            for (var i = 0; i < nInputs; i++) {
              var row = this.flytable.insertRow(i);
              for (var j = 0; j < nInputs; j++) {
                var cell = row.insertCell(j);
                //cell config
                cell.style.width = "20px";
                cell.style.height = "20px";
                cell.style.textAlign = "right";
                cell.setAttribute("contenteditable", "true");
                var set = false;
                if ((this.fnames.selectedIndex >= 0) && (this.value !== undefined)) {
                  if (this.value[this.fnames.selectedIndex][i] !== undefined) {
                    if (this.value[this.fnames.selectedIndex][i][j] !== undefined) {
                      cell.innerHTML = "" + this.value[this.fnames.selectedIndex][i][j];
                      set = true;
                    }
                  }
                }
                if (!set) {
                  cell.innerHTML = "x";
                }
                cell.title = this.assignment.matrix.value[j][this.fnames.selectedIndex];
                cell.addEventListener("input", function(e) {
                  this.updateValue(true);
                }.bind(this));
              }
            }
          }





          variablesInfoLoaded() {
            var nElements = this.assignment.value.length;
            var selIndex = this.fnames.selectedIndex;
            while (this.fnames.hasChildNodes()) {
              this.fnames.removeChild(this.fnames.childNodes[0]);
            }
            for (var k = 0; k < nElements; k++) {
              var option = document.createElement("option");
              option.text = this.assignment.value[k];
              option.value = option.text;
              this.fnames.appendChild(option);
            }
            this.fnames.selectedIndex = selIndex;
            var nrows = this.flytable.rows.length;
            for (var i = 0; i < nrows; i++) {
              this.flytable.deleteRow(0);
            }

            var nInputs = this.assignment.matrix.value.length;
            for (var i = 0; i < nInputs; i++) {
              var row = this.flytable.insertRow(i);
              for (var j = 0; j < nInputs; j++) {
                var cell = row.insertCell(j);
                //cell config
                cell.style.width = "20px";
                cell.style.height = "20px";
                cell.style.textAlign = "right";
                cell.setAttribute("contenteditable", "true");
                var set = false;
                if ((this.fnames.selectedIndex >= 0) && (this.value !== undefined)) {
                  if (this.value[this.fnames.selectedIndex][i] !== undefined) {
                    if (this.value[this.fnames.selectedIndex][i][j] !== undefined) {
                      cell.innerHTML = "" + this.value[this.fnames.selectedIndex][i][j];
                      set = true;
                    }
                  }
                }
                if (!set) {
                  cell.innerHTML = "x";
                }
                cell.title = this.assignment.matrix.value[j][this.fnames.selectedIndex];
                cell.addEventListener("input", function(e) {
                  this.updateValue(true);
                }.bind(this));
              }
            }
          }



          /**
           * @brief See HtkComponent.refresh
           */
          refresh() {
            if (this.initialised) {
              this.checkValue();
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
          }

          /**
           * @brief See HtkComponent.getTemplate
           */
           getTemplate() {
             var templateContent = template.content;
             return templateContent;
           }


          assignmentDoneRefresh() {
            var nrows = this.flytable.rows.length;
            for (var i = 0; i < nrows; i++) {
              this.flytable.deleteRow(0);
            }
            var nElements = this.assignment.fnames.rows[0].cells.length;
            var nInputs = this.assignment.matrix.value.length;
            this.value = new Array(nElements);
            while (this.fnames.hasChildNodes()) {
              this.fnames.removeChild(this.fnames.childNodes[0]);
            }

            for (var k = 0; k < nElements; k++) {
              this.value[k] = new Array(nInputs);
              var option = document.createElement("option");
              option.text = this.assignment.fnames.rows[0].cells[k].innerHTML;
              option.value = option.text;
              this.fnames.appendChild(option);

              for (var n = 0; n < nInputs; n++) {
                this.value[k][n] = new Array(nInputs);
                for (var m = 0; m < nInputs; m++) {
                  this.value[k][n][m] = "x";
                }
              }
            }

            for (var i = 0; i < nInputs; i++) {
              var row = this.flytable.insertRow(i);
              for (var j = 0; j < nInputs; j++) {
                var cell = row.insertCell(j);
                cell.innerHTML = "x";
                cell.style.width = "20px";
                cell.style.height = "20px";
                cell.style.textAlign = "right";
                cell.setAttribute("contenteditable", "true");
                cell.addEventListener("input", function(e) {
                  this.updateValue(true);
                }.bind(this));
              }
            }
          }


          testCallback(inputFun = -1, index = -1) {
            var res = false;
            var input = inputFun;
            if (input < 0) {
              input = parseInt(this.testInput.value, 2);
            }
            //go to function assignment to see its functions
            var functionIdx = index;
            if (functionIdx < 0) {
              functionIdx = this.fnames.selectedIndex;
            }
            if (functionIdx >= 0) {
              var nInputs = this.assignment.matrix.value.length;

              for (var i = 0; i < nInputs; i++) {
                var resRow = true;
                for (var j = 0; j < nInputs; j++) {
                  if (this.value[functionIdx][i][j] == "1") {
                    resRow &= ((input & (1 << j)) != 0);
                  }
                  if (this.value[functionIdx][i][j] == "0") {
                    resRow &= ((input & (1 << j)) == 0);
                  }
                }
                res |= resRow;
              }
              this.testOutput.innerHTML = "" + res;
              this.testOutput.value = res;

            }
            return res;
          }



          /**
           * @brief See HtkComponent.connectedCallback
           */
          connectedCallback() {
            super.connectedCallback();

            this.numberOfElements = 0;
            this.initialised = false;

            window.htkHelper.addVariablesInfoLoadedListener(this);
            window.htkHelper.addScheduleChangedListener(this);

            this.fnames = this.shadowRoot.querySelector("#tselect");

            this.testInput = this.shadowRoot.querySelector("#testInput");
            this.testInput.setAttribute("contenteditable", "true");
            this.testInput.style.textAlign = "right";

            this.testButton = this.shadowRoot.querySelector("#testButton");
            this.testOutput = this.shadowRoot.querySelector("#testOutput");
            this.testOutput.style.textAlign = "right";

            this.width = "200px";
            this.height = "25px";
            this.fnames.style.width = this.width;
            this.fnames.style.height = this.height
            this.fnames.style.cursor = "pointer";
            this.fnames.style.fontSize = "18px";
            //this.fnames.hidden=true;
            this.flytable = this.shadowRoot.querySelector("#flyTable");
            //this.flytable.hidden=true;
            this.assignmentButton = this.shadowRoot.querySelector("#functionAssignmentDone");
            this.assignmentButton.onclick = function() {
              this.assignmentDoneRefresh()
            }.bind(this);
            this.fnames.addEventListener("input", function(e) {
              //create a table on the fly
              if (this.fnames.selectedIndex >= 0) {
                var nInputs = this.assignment.matrix.value.length;
                for (var i = 0; i < nInputs; i++) {
                  var row = this.flytable.rows[i];
                  for (var j = 0; j < nInputs; j++) {
                    var cell = row.cells[j];
                    cell.innerHTML = "" + this.value[this.fnames.selectedIndex][i][j];
                    cell.title = this.assignment.matrix.value[j][this.fnames.selectedIndex];
                  }
                }
                this.checkValue();
              }
            }.bind(this));


            this.testButton.onclick = function() {
              this.testCallback();
            }.bind(this);
          }
        }

        /**
         * @brief Registers the element.
         */
        window.customElements.define('ls-function-logic', LsFunctionLogic);
