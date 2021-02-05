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
  <link rel="import" href="/htk-abstract-input.html">
  */
import { HtkAbstractInput } from './htk-abstract-input.js'

const template = document.createElement('template');
template.innerHTML = `
  <dialog id="dwaitdialog">
      <input type="text" id="tinput"></input>
  </dialog>
`;

      /**
       * @brief A text input component.
       */
      class HtkInput extends HtkAbstractInput {

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
          super.connectedCallback();
          this.textInput = this.shadowRoot.querySelector("#tinput");
          this.textInput.style.width = "100%";
          this.textInput.addEventListener("input", function(e) {
            this.setValue(this.textInput.value);
          }.bind(this));
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
          this.textInput.value = this.value;
          this.checkValues(this.textInput);
        }

        /**
         * @brief See HtkComponent.getValue.
         */
        getValue() {
          var txtValue = this.textInput.value;
          var typeValue = this.getTypeValue();
          return parent.htkHelper.textToTypeValue(txtValue, typeValue);
        }

        /**
         * @brief See HtkComponent.setReadOnly.
         */
        setReadOnly(isReadOnly) {
          super.setReadOnly(isReadOnly);
          this.textInput.disabled = isReadOnly;
        }

      }

      /**
       * @brief Registers the element.
       */
       customElements.define('htk-input', HtkInput);
