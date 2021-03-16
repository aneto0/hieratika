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
import { HtkAbstractInput } from './htk-abstract-input.js';

const template = document.createElement('template');
template.innerHTML = `
<textarea rows="10" cols="50" id="ttextarea">
`;

/**
 * @brief A text input component.
 */
export class HtkTextArea extends HtkAbstractInput {

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
        this.textArea = this.shadowRoot.querySelector("#ttextarea");
        this.textArea.addEventListener("input", function (e) {
            this.setValue(this.textArea.value);
        }.bind(this));
        var rows = this.getAttribute("data-rows");
        if (rows !== null) {
            this.textArea.rows = rows;
        }
        var cols = this.getAttribute("data-cols");
        if (cols !== null) {
            this.textArea.cols = cols;
        }
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
        this.textArea.value = this.value;
        this.checkValues(this.textArea);
    }

    /**
     * @brief See HtkComponent.getValue.
     */
    getValue() {
        var txtValue = this.textArea.value;
        var typeValue = this.getTypeValue();
        return parent.htkHelper.textToTypeValue(txtValue, typeValue);
    }

    /**
     * @brief See HtkComponent.setReadOnly.
     */
    setReadOnly (isReadOnly) {
        super.setReadOnly(isReadOnly);
        this.textArea.disabled = isReadOnly;
    }
}
/**
 * @brief Registers the element.
 */
window.customElements.define('htk-textarea', HtkTextArea);
