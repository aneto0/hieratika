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
       <link rel="import" href="/htk-matrix1-dropmenu-editor.html">

*/

import * as Constants from './htk-constants.js'
import { HtkComponent, copy } from './htk-component.js'

const template = document.createElement('template');
template.innerHTML = `
<div id="dmatrix1">
    <table border="0">
        <tr>
            <td>
                <button type="button" id="functionLogicDone">Function Logic Done</button>
            </td>
        </tr>
        <tr>
            <td>
        <input type="text" id="orNameInput"></input>
              <button id="addOrButton">+</button>
              <button id="removeOrButton">-</button>
      </td>
      <td>
                <select id="finalOrSelect">
                </select>

            </td>
        </tr>
        <tr>
            <td>
                <button type="button" id="addRowButton">Add Element</button>
                <button type="button" id="removeRowButton">Remove Element</button>
      </td>
      <td>
                <button type="button" id="addLogicButton">Add Logic</button>
                <button type="button" id="removeLogicButton">Remove Logic</button>
            </td>
        </tr>
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
    class LsFinalOr extends HtkComponent {

      /**
       * @brief Constructor. NOOP.
       */
      constructor() {
        super();
      }

      checkValue() {
        if (this.orSelect.selectedIndex >= 0) {
          var tempValue = [this.value[this.orSelect.selectedIndex][1], this.value[this.orSelect.selectedIndex][2]];
          var tempInitValue = [undefined, undefined];
          if (this.initValue !== undefined) {
            if (this.initValue[this.orSelect.selectedIndex] !== undefined) {
              tempInitValue = [this.initValue[this.orSelect.selectedIndex][1], this.initValue[this.orSelect.selectedIndex][2]];
            }
          }
          var matrices = [this.matrix1, this.matrix2];
          var tempPlantValue = [undefined, undefined];
          if (this.plantValue !== undefined) {
            if (this.plantValue[this.orSelect.selectedIndex] !== undefined) {
              tempPlantValue = [this.plantValue[this.orSelect.selectedIndex][1], this.plantValue[this.orSelect.selectedIndex][2]];
            }
          }
          var tempRefValue = [undefined, undefined];
          if (this.referenceValue !== undefined) {
            if (this.referenceValue[this.orSelect.selectedIndex] !== undefined) {
              tempRefValue = [this.referenceValue[this.orSelect.selectedIndex][1], this.referenceValue[this.orSelect.selectedIndex][2]];
            }
          }
          for (var c = 0; c < tempValue.length; c++) {
            for (var h = 0; h < tempValue[c].length; h++) {
              for (var k = 0; k < tempValue[c][0].length; k++) {
                var id = "#menu_" + h.toString() + k.toString();
                var myCell = matrices[c].tbl.querySelector(id);
                if (myCell !== null) {
                  myCell.style.color = Constants.STANDARD_FCOLOR;
                  if (tempInitValue[c] !== undefined) {
                    if (tempInitValue[c][h] !== undefined) {
                      if (tempInitValue[c][h][k] !== undefined) {

                        if (tempValue[c][h][k] != tempInitValue[c][h][k]) {
                          myCell.style.color = Constants.DIFF_INIT_CHANGED_COLOR;
                        }
                      }
                    }
                  }
                  if (tempPlantValue[c] !== undefined && tempRefValue[c] !== undefined) {
                    if (tempPlantValue[c][h] !== undefined) {
                      if (tempPlantValue[c][h][k] !== undefined) {
                        if (tempRefValue[c][h] !== undefined) {
                          if (tempRefValue[c][h][k] !== undefined) {
                            if (!this.compareWithReference(tempValue[c][h][k], tempPlantValue[c][h][k], tempRefValue[c][h][k])) {
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
          }
        }
      }


      updateValue(userChanged) {
        this.value[this.orSelect.selectedIndex][1] = copy(this.matrix1.value);
        this.value[this.orSelect.selectedIndex][2] = copy(this.matrix2.value);
        this.checkValue();

        if (userChanged) {
          this.fireValueChanged("value");
          this.updateRemote(this.getValue());
        }
      }


      domLoaded() {
        var preprocessingId = this.getAttribute("data-preprocessingId");
        var htkCompArray = document._frameComponents[preprocessingId];
        this.preprocessing = htkCompArray[0];


        var assignmentId = this.getAttribute("data-assignmentId");
        var htkCompArray = document._frameComponents[assignmentId];
        this.assignment = htkCompArray[0];

        var logicId = this.getAttribute("data-logicId");
        var htkCompArray = document._frameComponents[logicId];
        this.logic = htkCompArray[0];


        var matrix1Id = this.getAttribute("data-m1Id");
        var htkCompArray = document._frameComponents[matrix1Id];
        this.matrix1 = htkCompArray[0];


        var matrix2Id = this.getAttribute("data-m2Id");
        var htkCompArray = document._frameComponents[matrix2Id];
        this.matrix2 = htkCompArray[0];


        this.matrix1.refreshAllCellsDimensions("150px", "25px")
        this.matrix1.showHideButtons(false);

        this.matrix2.refreshAllCellsDimensions("150px", "25px")
        this.matrix2.showHideButtons(false);


        this.matrix1.addAddRowCallback(this);
        this.matrix1.addRemoveRowCallback(this);

        this.matrix2.addAddRowCallback(this);
        this.matrix2.addRemoveRowCallback(this);

        this.matrix1.addUpdateValueCallback(this);
        this.matrix2.addUpdateValueCallback(this);

        this.matrix1.addRefreshCallback(this);
        this.matrix2.addRefreshCallback(this);
      }

      addRowCallback() {
        this.updateValue();
      }

      addColCallback() {
        this.updateValue();
      }

      removeRowCallback() {
        this.updateValue();
      }

      removeColCallback() {
        this.updateValue();
      }

      scheduleChanged(x) {
        //refresh or enum
        while (this.orSelect.hasChildNodes()) {
          this.orSelect.removeChild(this.orSelect.childNodes[0]);
        }

        var len = this.value.length;
        for (var i = 0; i < len; i++) {
          //add to the select the option in the input box
          var option = document.createElement("option");
          option.text = this.value[i][0];
          option.value = this.value[i][0];
          this.orSelect.appendChild(option);
        }
        this.orSelect.selectedIndex = 0;
        this.matrix1.value = copy(this.value[this.orSelect.selectedIndex][1]);
        this.matrix2.value = copy(this.value[this.orSelect.selectedIndex][2]);
        this.matrix1.refresh();
        this.matrix2.refresh();

        var options = new Array(this.preprocessing.matrix1.value.length + this.assignment.value.length);
        var cnt = 0;
        //refresh the matrix1 enum
        if (this.preprocessing !== null) {
          for (var k = 0; k < this.preprocessing.matrix1.value.length; k++) {
            options[cnt] = this.preprocessing.matrix1.value[k][0];
            cnt++;
          }
        }
        if (this.assignment !== null) {
          for (var k = 0; k < this.assignment.value.length; k++) {
            var option = document.createElement("option");
            options[cnt] = this.assignment.value[k];
            cnt++;
          }
        }

        this.matrix1.refreshEnum(options);
        this.matrix1.refresh()
      }



      variablesInfoLoaded() {
        //refresh or enum
        while (this.orSelect.hasChildNodes()) {
          this.orSelect.removeChild(this.orSelect.childNodes[0]);
        }

        var len = this.value.length;
        for (var i = 0; i < len; i++) {
          //add to the select the option in the input box
          var option = document.createElement("option");
          option.text = this.value[i][0];
          option.value = this.value[i][0];
          this.orSelect.appendChild(option);
        }
        this.orSelect.selectedIndex = 0;
        this.matrix1.value = copy(this.value[this.orSelect.selectedIndex][1]);
        this.matrix2.value = copy(this.value[this.orSelect.selectedIndex][2]);
        this.matrix1.refresh();
        this.matrix2.refresh();

        var options = new Array(this.preprocessing.matrix1.value.length + this.assignment.value.length);
        var cnt = 0;
        //refresh the matrix1 enum
        if (this.preprocessing !== null) {
          for (var k = 0; k < this.preprocessing.matrix1.value.length; k++) {
            options[cnt] = this.preprocessing.matrix1.value[k][0];
            cnt++;
          }
        }
        if (this.assignment !== null) {
          for (var k = 0; k < this.assignment.value.length; k++) {
            var option = document.createElement("option");
            options[cnt] = this.assignment.value[k];
            cnt++;
          }
        }

        this.matrix1.refreshEnum(options);
        this.matrix1.refresh()
      }


      /**
       * @brief See HtkComponent.refresh
       */
      refresh() {
        this.checkValue();
      }

      /**
       * @brief See HtkComponent.setValue
       */
      setValue(elementsToSet, updateRemote = true) {
        super.setValue(elementsToSet.slice(0), updateRemote);
        this.initialised = true;
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
        /*
            super.setReadOnly(isReadOnly);
            this.addRowButton.disabled = isReadOnly;
            this.removeRowButton.disabled = isReadOnly;*/
      }

      /**
       * @brief See HtkComponent.getTemplate
       */
       getTemplate() {
         var templateContent = template.content;
         return templateContent;
       }


      testCallback() {
        var input = parseInt(this.testInput.value, 2);
        var res = false;
        var nFunctions = this.assignment.value.length;
        this.initialised = false;
        var nElements = this.matrix1.value.length;
        for (var j = 0; j < nFunctions; j++) {
          var functionName = this.assignment.value[j];
          var nSignals = this.preprocessing.matrix1.value.length;

          var found = false;
          for (var n = 0;
            (n < nElements) && (!found); n++) {
            found = (functionName === this.matrix1.value[n][0]);
          }
          var inputFun = 0;
          if (found) {
            for (var i = 0;
              (i < nSignals); i++) {
              var signalName = this.preprocessing.matrix1.value[i][0];
              var nSignalsInFunction = this.assignment.matrix.value.length;
              for (var h = 0; h < nSignalsInFunction; h++) {
                if (signalName == this.assignment.matrix.value[h][j]) {
                  if ((input & (1 << i)) != 0) {
                    inputFun |= (1 << (h));
                  }
                }
              }
            }
            res |= this.logic.testCallback(inputFun, j);
          }
        }

        var nSignals = this.preprocessing.matrix1.value.length;

        for (var i = 0; i < nSignals; i++) {
          var signalName = this.preprocessing.matrix1.value[i][0];
          var foundSignal = false;
          for (var k = 0;
            (k < nElements) && (!foundSignal); k++) {
            foundSignal = (signalName === this.matrix1.value[k][0]);
          }
          if (foundSignal) {
            res |= ((input & (1 << i)) != 0);
          }
        }
        this.testOutput.value = res;
        this.testOutput.innerHTML = "" + res;
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

        this.addRowButton = this.shadowRoot.querySelector("#addRowButton");
        this.addRowButton.onclick = function() {
          this.matrix1.addRowCallback();
          this.matrix2.addRowCallback();
        }.bind(this);

        this.removeRowButton = this.shadowRoot.querySelector("#removeRowButton");
        this.removeRowButton.onclick = function() {
          this.matrix1.removeRowCallback();
          this.matrix2.removeRowCallback();
        }.bind(this);

        this.orNameInput = this.shadowRoot.querySelector("#orNameInput");
        this.orNameInput.setAttribute("contenteditable", "true");
        this.orNameInput.style.textAlign = "right";

        this.orSelect = this.shadowRoot.querySelector("#finalOrSelect");

        this.orSelect.addEventListener("click", function(e) {
          this.matrix1.value = copy(this.value[this.orSelect.selectedIndex][1]);
          this.matrix2.value = copy(this.value[this.orSelect.selectedIndex][2]);
          this.matrix1.refresh();
          this.matrix2.refresh();
        }.bind(this));



        this.addOrButton = this.shadowRoot.querySelector("#addOrButton");
        this.addOrButton.onclick = function() {
          //add to the select the option in the input box
          var option = document.createElement("option");
          option.text = this.orNameInput.value;
          option.value = this.orNameInput.value;
          this.orSelect.appendChild(option);

          //add empty value
          var temp = copy(this.value);
          var matrixTemp1 = new Array(1);
          matrixTemp1[0] = new Array(1);
          matrixTemp1[0][0] = this.matrix1.enum.getChoices()[0];

          var matrixTemp2 = new Array(1);
          matrixTemp2[0] = new Array(1);
          matrixTemp2[0][0] = this.matrix2.enum.getChoices()[0];

          var orName = option.text;
          var matrixArrTemp = [orName, matrixTemp1, matrixTemp2];

          this.value.push(matrixArrTemp);
          this.fireValueChanged("value");
          this.updateRemote(this.getValue());
        }.bind(this);


        this.removeOrButton = this.shadowRoot.querySelector("#removeOrButton");
        this.removeOrButton.onclick = function() {
          var lastChildIndex = this.orSelect.childElementCount - 1;
          this.orSelect.removeChild(this.orSelect.childNodes[lastChildIndex]);

          //refresh my matrix
          this.value.pop();
          this.fireValueChanged("value");
          this.updateRemote(this.getValue());
        }.bind(this);

        this.functionLogicButton = this.shadowRoot.querySelector("#functionLogicDone");
        this.functionLogicButton.onclick = function() {
          var options = new Array(this.preprocessing.matrix1.value.length + this.assignment.value.length);
          var cnt = 0;
          //refresh the matrix1 enum
          if (this.preprocessing !== null) {
            for (var k = 0; k < this.preprocessing.matrix1.value.length; k++) {
              options[cnt] = this.preprocessing.matrix1.value[k][0];
              cnt++;
            }
          }
          if (this.assignment !== null) {
            for (var k = 0; k < this.assignment.value.length; k++) {
              var option = document.createElement("option");
              options[cnt] = this.assignment.value[k];
              cnt++;
            }
          }
          this.matrix1.refreshEnum(options);
        }.bind(this);

        this.addLogicButton = this.shadowRoot.querySelector("#addLogicButton");
        this.addLogicButton.onclick = function() {
          //add a logic to the elements of matrix2
          /*var choices=this.matrix2.enum.getChoices();
          var nChoices=choices.length;
          var options=new Array(nChoices+1);
          var max=0;
          for(var i=0; i<nChoices; i++){
          	if(parseInt(choices[i])>max){
          		max=parseInt(choices[i]);
          	}
          	options[i]=choices[i];
          }
          options[nChoices]=max+1;
          this.matrix2.refreshEnum(options);*/
          this.matrix2.addColCallback();
        }.bind(this);

        this.removeLogicButton = this.shadowRoot.querySelector("#removeLogicButton");
        this.removeLogicButton.onclick = function() {
          //remove a logic to the elements of matrix2
          /*
          var choices=this.matrix2.enum.getChoices();
          var nChoices=choices.length;
          var options=new Array(nChoices-1);
          var max=0;
          for(var i=0; i<nChoices; i++){
          	if(parseInt(choices[i])>max){
          		max=parseInt(choices[i]);
          	}
          }
          for(var i=0; i<nChoices; i++){
          	if(parseInt(choices[i])!=max){
          		options[i]=choices[i];
          	}
          }
          this.matrix2.refreshEnum(options);*/
          this.matrix2.removeColCallback();
        }.bind(this);

        this.testInput = this.shadowRoot.querySelector("#testInput");
        this.testInput.setAttribute("contenteditable", "true");
        this.testInput.style.textAlign = "right";

        this.testButton = this.shadowRoot.querySelector("#testButton");
        this.testOutput = this.shadowRoot.querySelector("#testOutput");
        this.testOutput.style.textAlign = "right";

        this.testButton.onclick = function() {
          this.testCallback();

        }.bind(this);
      }
    }

    /**
     * @brief Registers the element.
     */
    window.customElements.define('ls-final-or', LsFinalOr);
