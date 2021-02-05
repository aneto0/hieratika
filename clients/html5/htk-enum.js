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
<select id="tselect" name="tselect"></select>
`;

    /**
     * @brief Enum editor component implemented using an HTML select.
     */
    class HtkEnum extends HtkAbstractInput {

        /**
         * @brief Constructor. NOOP.
         */
        constructor() {
            super();
        }

        /**
         * @brief See HtkComponent.createdCallback
         */
        connectedCallback () {
            super.connectedCallback();
            this.select = this.shadowRoot.querySelector("#tselect");
            this.select.addEventListener("input", function (e) {
                var selectedValue = this.select[this.select.selectedIndex].value;
                this.setValue(selectedValue);
            }.bind(this));
            this.choices = [];
        }

        /**
         * @brief See HtkComponent.getTemplate
         */
         getTemplate() {
           var templateContent = template.content;
           return templateContent;
         }

        /**
         * @brief See HtkComponent.setVariable.
         */
        setVariable (variable) {
            super.setVariable(variable);
            if ("choices" in variable) {
                this.setChoices(variable.choices);
            }
        }

        /**
         * @brief Adds all the available options to the selector.
         */
        setChoices(choices) {
            this.choices = choices;
            this.select.innerHTML = "";
            for (var i=0; i<this.choices.length; i++) {
                var option = document.createElement("option");
                option.text = choices[i];
                option.value = choices[i];
                this.select.appendChild(option);
            }
            this.select.value = this.getValue();
        }

        /**
         * @brief Sets the selected choice visible on the component.
         */
        refresh() {
            this.select.value = this.value;
            this.checkValues(this.select);
        }

        /**
         * @brief Sets the select as read only.
         */
        setReadOnly (isReadOnly) {
            super.setReadOnly(isReadOnly);
            this.select.disabled = isReadOnly;
        }

    }

    /**
     * @brief Registers the element.
     */
     customElements.define('htk-enum', HtkEnum);
