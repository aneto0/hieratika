/*
 date: 26/01/2021
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
const template = document.createElement('template');
template.innerHTML = `
  <dialog id="dwaitdialog">
      <img src="../icons/ajax-loader.gif"></img>
  </dialog>
`;


/**
 * @brief A modal dialog which displays a wait icon.
 */
export class HtkWaitDialog extends HTMLElement {
    constructor() {
        super();
    }

    /**
     * @brief See HTMLElement.createdCallback
     */
    connectedCallback () {
        var templateContent = template.content;
        const root = this.attachShadow({mode: 'open'});
        root.appendChild(templateContent.cloneNode(true));

        this.diag = root.querySelector('#dwaitdialog');
    }

    /**
     * @brief Shows the dialog.
     */
    showModal() {
        if (!this.diag.open) {
            this.diag.showModal();
        }
    }

    /**
     * @brief Closes the dialog.
     */
    close() {
        if (this.diag.open) {
            this.diag.close();
        }
    }
}

window.customElements.define('htk-wait-dialog', HtkWaitDialog);
