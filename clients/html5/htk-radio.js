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
  <link rel="import" href="/htk-abstract-input.html">
*/

/*
   <htk-radio-group id='CPS@RADIO'>
      <htk-radio-box label="Arm" id='CPS@FOLDBACK_A0'></htk-radio-box>
      <htk-radio-box label="Cancel" id='CPS@FOLDBACK_C0'></htk-radio-box>
      <htk-radio-box label="Release" id='CPS@FOLDBACK_R0'></htk-radio-box>
  </htk-radio-group>
*/

import * as Constants from './htk-constants.js'

const template = document.createElement('template');
template.innerHTML = `
  <input type="radio" id="rinput"></input>
`;


      /**
       * @brief A radio box component.
       */
      class HtkRadioBox extends HtkAbstractInput {

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
          this.radioInput = this.shadowRoot.querySelector("#rinput");
          this.value = 0;
          this.radioInput.checked = false;
          this.radioInput.addEventListener("click", function(e) {
            if (this.radioInput.checked == true) {
              this.setValue(1);
            } else {
              this.setValue(0);
            }
          }.bind(this));
          if (this.hasAttribute('label')) {
            this.label = document.createElement('label');
            this.label.innerText = this.getAttribute('label');
            this.shadowRoot.appendChild(this.label);
          }
        }

        getTemplate() {
          var templateContent = template.content;
          return templateContent;
        }


        static get observedAttributes() {
          return ['checked'];
        }

        attributeChangedCallback(attrName, oldVal, newVal) {
          if (newVal == "true") {
            this.radioInput.checked = true;
            this.value = 1;
          } else {
            this.radioInput.checked = false;
            this.value = 0;
          }
          this.refresh();
        }

        /**
         * @brief See HtkComponent.getValue.
         */
        getValue() {
          var rValue = this.value;
          var typeValue = this.getTypeValue();
          return parent.htkHelper.textToTypeValue(rValue, typeValue);
        }

        /**
         * @brief See HtkComponent.setReadOnly.
         */
        setReadOnly(isReadOnly) {
          super.setReadOnly(isReadOnly);
          this.radioInput.disabled = isReadOnly;
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
          this.fireValueChanged(HtkComponent.VALUE_CHANGED);
          if (updateRemote) {
            this.updateRemote(valueToSet);
          }
          this.refresh();
        }


        setReferenceValue(referenceToSet) {
          this.referenceValue = this.getTheCorrectValue(referenceToSet);
          this.fireValueChanged(HtkComponent.VALUE_CHANGED_REFERENCE);
          this.refresh();
        }

        setPlantValue(plantValueToSet) {
          this.plantValue = this.getTheCorrectValue(plantValueToSet);
          this.fireValueChanged(HtkComponent.VALUE_CHANGED_PLANT);
          this.refresh();
        }

        checkAllValues() {
          this.checkValues(this.radioInput);
        }

        /**
         * @brief See HtkComponent.refresh.
         */
        refresh() {
          if (this.value > 0) {
            this.radioInput.checked = true;
          } else {
            this.radioInput.checked = false;
          }
          this.checkValues(this.radioInput);
        }

        checkValues(component) {
          if (component === undefined) {
            component = this;
          }
          //If the current value does not match the initial value set the font color blue
          if (!this.compareValues(this.getValue(), this.getInitialValue())) {
            this.label.style.color = Constants.DIFF_INIT_CHANGED_COLOR;
          } else {
            this.label.style.color = Constants.STANDARD_FCOLOR;
          }
          var newBackgroundColor = "transparent";
          if (!this.compareWithReference(this.getValue(), this.getPlantValue(), this.getReferenceValue())) {
              newBackgroundColor = Constants.PLANT_OR_REF_CHANGED_COLOR;
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
              newBackgroundColor = Constants.ERROR_BCOLOR;
              titleString = "Failed @ " + this.validations[errorIdx].getValidationFunction();
          }
          this.label.style.backgroundColor = newBackgroundColor;

          var titleString = this.toString();
          component.title = titleString;
        }
      }

      customElements.define('htk-radio-box', HtkRadioBox);

      /**
       * @brief A Radio group component.
       */
      class HtkRadioGroup extends HTMLElement {

        /**
         * @brief Constructor. NOOP.
         */
        constructor() {
          super();
        }

        /**
         * @brief See HtkComponent.
         */
        connectedCallback() {
          this.setAttribute('role', 'radiogroup');
          this._selected = 0;
          this.radios = Array.from(this.querySelectorAll('htk-radio-box'));
          // Wait for DOM loaded
          document.addEventListener('DOMContentLoaded', function(e) {
            for (let i = 0; i < this.radios.length; i++) {
              this.radios[i].setAttribute('checked', false);
              // Register on radiobox components
              document._frameComponents[this.radios[i].id][0].addValueChangedListener(this);
            }
          }.bind(this));
        }

        setSelected(idx) {
          if (isFinite(this.getSelected())) {
            // Set the old button to false
            var previousSelected = this.radios[this.getSelected()];
            previousSelected.setAttribute('checked', false);
          }
          // Set the new button true and focus it
          var newSelected = this.radios[idx];
          newSelected.setAttribute('checked', true);
          newSelected.focus();
          this._selected = idx;
        }

        getSelected() {
          return this._selected;
        }

        valueChanged(source, typeOfChange) {
          if (typeOfChange == HtkComponent.VALUE_CHANGED) {
            if (source.getValue() == 1) {
              for (let i = 0; i < this.radios.length; i++) {
                if (this.radios[i].id == source.id) {
                  this.setSelected(i);
                }
              }
            }
          }
        }
      }
      /**
       * @brief Registers the element.
       */
       customElements.define('htk-radio-group', HtkRadioGroup);
