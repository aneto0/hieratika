/*
 date: 04/01/2018
 author: Andre' Neto

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

import * as Constants from './htk-constants.js'
import HtkHelper from './htk-helper.js'

const template = document.createElement('template');
template.innerHTML = `
  <div id="darray">
      <table border="0">
          <tr>
              <td>
                  <table border="1" id="tarray">
                      <tr></tr>
                  </table>
              </td>
              <td>
                  <button type="button" id="addButton">+</button>
                  <button type="button" id="removeButton">-</button>
              </td>
          </tr>
      </table>
  </div>
`;

  /**
   * @brief Array editor component.
   */
  class HtkArrayEditor extends HtkComponent {

    /**
     * @brief Constructor. NOOP.
     */
    constructor() {
      super();
    }

    /**
     * @brief Checks if the component style should be updated due to a value change and executes all the validation functions.
     * @details For each element array, performs the same actions described in HtkAbstractInput.checkValues.
     * @param[in] userChanged true if the value update was triggered by a user action.
     */
    checkValues(userChanged) {
      //If the current value does not match the initial value set the font color blue
      var row = this.tbl.rows[0];
      var initialValue = this.getInitialValue();
      var refValue = this.getReferenceValue();
      var plantValue = this.getPlantValue();
      var typeValue = this.getTypeValue();
      for (var i = 0;
        (i < this.numberOfElements); i++) {
        var cell = row.cells[i];
        if (cell !== undefined) {
          var cellValue = cell.innerHTML;
          var numberValue = HtkHelper.textToTypeValue(cellValue, typeValue);
          if (numberValue === undefined) {
            numberValue = cellValue;
          }
          this.value[i] = numberValue;
          var cellInitValue = "";
          if (initialValue !== undefined) {
            cellInitValue = initialValue[i];
          }
          if (!this.compareValues(cellValue, cellInitValue)) {
            cell.style.color = Constants.DIFF_INIT_CHANGED_COLOR;
          } else {
            cell.style.color = Constants.STANDARD_FCOLOR;
          }

          cell.setAttribute("contenteditable", this.isReadOnly() ? "false" : "true");
          var cellRefValue = "";
          if (refValue !== undefined) {
            cellRefValue = refValue[i];
          }
          var cellPlantValue;
          if (plantValue !== undefined) {
            cellPlantValue = plantValue[i];
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
      if (userChanged) {
        this.fireValueChanged("value");
        this.updateRemote(this.getValue());
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
          (i < this.numberOfElements); i++) {
          var cell = row.cells[i];
          if (cell !== undefined) {
            cell.style.backgroundColor = Constants.ERROR_BCOLOR;
          }
        }
        errorIdx--;
        this.title = "Failed @ " + this.validations[errorIdx].getValidationFunction();
      } else {
        this.title = this.toString();
      }
    }

    /**
     * @brief See HtkComponent.refresh
     */
    refresh() {
      if (this.getValue() !== undefined) {
        var elementsToSet = this.getValue();
        var row = this.tbl.rows[0];
        var createRow = false;
        if ((row.cells.length !== elementsToSet.length)) {
          createRow = true;
        }
        if (createRow) {
          this.tbl.deleteRow(0);
          this.setNumberOfElements(elementsToSet.length);
          row = this.tbl.insertRow(0);
          for (var i = 0; i < elementsToSet.length; i++) {
            var col = row.insertCell(i);
            col.innerHTML = "" + elementsToSet[i];
            col.style.width = "20px";
            col.style.textAlign = "right";
            col.addEventListener("input", function(e) {
              this.checkValues(true);
            }.bind(this));
          }
        } else {
          for (var i = 0; i < elementsToSet.length; i++) {
            var col = row.cells[i];
            col.innerHTML = elementsToSet[i];
          }
        }
        this.checkValues(false);
      }
    }

    /**
     * @brief See HtkComponent.setValue
     */
    setValue(elementsToSet, updateRemote = true) {
      super.setValue(this.sliceArray(elementsToSet), updateRemote);
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
      this.addButton.disabled = isReadOnly;
      this.removeButton.disabled = isReadOnly;
    }

    /**
     * @brief See HtkComponent.getTemplate
     */
    getTemplate() {
      var templateContent = template.content;
      return templateContent;
    }

    /**
     * @brief See HtkComponent.connectedCallback
     */
    connectedCallback() {
      super.connectedCallback();
      this.addButton = this.shadowRoot.querySelector("#addButton");
      this.tbl = this.shadowRoot.querySelector("#tarray");
      this.addButton.onclick = function() {
        var row = this.tbl.rows[0];
        var col = row.insertCell();
        this.numberOfElements++;
        col.setAttribute("contenteditable", "true");
        col.style.width = "20px";
        col.style.textAlign = "right";
        col.addEventListener("input", function(e) {
          this.checkValues(true);
        }.bind(this));
        this.checkValues(true);
      }.bind(this);

      this.removeButton = this.shadowRoot.querySelector("#removeButton");
      this.removeButton.onclick = function() {
        var row = this.tbl.rows[0];
        if (row.cells.length > 0) {
          row.deleteCell(row.cells.length - 1);
        }
        this.numberOfElements--;
        this.setValue(this.value.slice(0, this.numberOfElements));
        this.checkValues(true);
      }.bind(this);
    }

    /**
     * @brief Utility function which slices the array based on its original size.
     */
    sliceArray(arrayToSlice) {
      //Make a shallow copy!
      var ret = arrayToSlice;
      if (arrayToSlice !== undefined) {
        if (arrayToSlice.length > 0) {
          var arrayOfStr = (typeof(arrayToSlice[0]) === "string");
          var sliceAt0 = (arrayToSlice[0].length !== undefined);
          if ((sliceAt0) && (!arrayOfStr)) {
            ret = arrayToSlice[0].slice(0);
          } else {
            ret = arrayToSlice.slice(0);
          }
        }
      } else {
        Logger.warn(this.id + ": arrayToSlice is undefined");
      }
      return ret;
    }

  }

  /**
   * @brief Registers the element.
   */
  customElements.define('htk-array-editor', HtkArrayEditor);
