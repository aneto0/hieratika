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

import * as Constants from './htk-constants.js'
import { HtkAbstractInput } from './htk-abstract-input.js'

const template = document.createElement('template');
template.innerHTML = `
  <input type="checkbox" id="tinput"></input>
`;

      /**
       * @brief A check box component.
       */
      class HtkCheckBox extends HtkAbstractInput {

        /**
         * @brief Constructor. NOOP.
         */
        constructor() {
          super();
        }

        /**
         * @brief See HtkComponent.createdCallback.
         */
        connectedCallback() {
          super.createdCallback();

          // this.onlyEnable = false;
          this.checkInput = this.shadowRoot.querySelector("#tinput");
          this.checkInput.addEventListener("click", function(e) {
            if (this.checkInput.checked == true) {
              this.setValue(1);
            } else {
              if (!this.onlyEnable) {
                this.setValue(0);
              }
            }
          }.bind(this));
          // add a fixed width span for validations
          this.validationSpan = document.createElement('span');
          this.validationSpan.style.width = "12px";
          this.validationSpan.style.height = "12px";
          this.validationSpan.style.display = "inline-block";
          this.shadowRoot.appendChild(this.validationSpan);
        }

        /**
         * @brief See HtkComponent.getTemplat.
         */
         getTemplate() {
           var templateContent = template.content;
           return templateContent;
         }

        /**
         * @brief See HtkComponent.refresh.
         */
        refresh() {
          if (this.value > 0) {
            this.checkInput.checked = true;
          } else {
            this.checkInput.checked = false;
          }
          this.checkValues(this.checkInput);
        }

        /**
         * @brief See HtkComponent.getValue.
         */
        getValue() {
          var txtValue = this.value;
          var typeValue = this.getTypeValue();
          return parent.htkHelper.textToTypeValue(txtValue, typeValue);
        }

        /**
         * @brief See HtkComponent.setReadOnly.
         */
        setReadOnly(isReadOnly) {
          super.setReadOnly(isReadOnly);
          this.checkInput.disabled = isReadOnly;
        }

        getTheCorrectValue(valueToSet) {
          var val = valueToSet;
          if (Array.isArray(valueToSet)) {
            val = valueToSet[0];
          }
          return val;
        }

        setValue(valueToSet, updateRemote = true) {
          this.value = this.getTheCorrectValue(valueToSet);
          this.fireValueChanged(Constants.VALUE_CHANGED);
          if (updateRemote) {
            this.updateRemote(valueToSet);
          }
          this.refresh();
        }


        setReferenceValue(referenceToSet) {
          this.referenceValue = this.getTheCorrectValue(referenceToSet);
          this.fireValueChanged(Constants.VALUE_CHANGED_REFERENCE);
          this.refresh();
        }

        setPlantValue(plantValueToSet) {
          this.plantValue = this.getTheCorrectValue(plantValueToSet);
          this.fireValueChanged(Constants.VALUE_CHANGED);
          this.refresh();
        }

        // setEnableOnly(isOnlyEnable) {
        //   this.onlyEnable = isOnlyEnable;
        // }

        checkAllValues() {
          this.checkValues(this.checkInput);
        }

        checkValues(component) {
          if (component === undefined) {
            component = this;
          }
          //If the current value does not match the initial value set the font color blue
          if (!this.compareValues(this.getValue(), this.getInitialValue())) {
            this.validationSpan.style.backgroundColor = Constants.DIFF_INIT_CHANGED_COLOR;
          } else {
            this.validationSpan.style.backgroundColor = "transparent";
          }
          var error = false;
          var errorIdx = 0;
          if (this.validations !== undefined) {
            for (errorIdx = 0;
              (errorIdx < this.validations.length) && (!error); errorIdx++) {
              if (this.validations[errorIdx].test !== undefined) {
                error = !this.validations[errorIdx].test();
              } else {
                console.log("Invalid validation function for " + this.id);
              }
            }
          }
          var titleString = this.toString();
          if (error) {
              errorIdx--;
              this.validationSpan.style.backgroundColor = Constants.ERROR_BCOLOR;
              titleString = "Failed @ " + this.validations[errorIdx].getValidationFunction();
          }
          component.title = titleString;
        }
      }

      /**
       * @brief Registers the element.
       */
       customElements.define('htk-checkbox', HtkCheckBox);
