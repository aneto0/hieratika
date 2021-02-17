/*
 date: 02/02/2021
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
        <link rel="import" href="/htk-library.html">
        <link rel="import" href="/htk-library-editor.html">

*/

/* Be sure to import htk-library-editor in the main document */

import * as Constants from './htk-constants.js';
import { HtkLibrary } from './htk-library.js'

const template = document.createElement('template');
template.innerHTML = `
<htk-library-editor id="tlibrary-editor"></htk-library-editor>
<button type="button" id="blibrary"></button>
`;

                /**
                 * @brief A button which opens a htk-library-editor. The value of this component is the name of the selected library (username/libraryname).
                 */
                class HtkLibraryButton extends HtkLibrary {

                    /**
                     * @brief Constructor. NOOP.
                     */
                    constructor() {
                        super();
                    }

                    /**
                     * @brief See HtkComponent.connectedCallback.
                     */
                    connectedCallback () {
                        super.connectedCallback();
                        this.buttonInput = this.shadowRoot.querySelector("#blibrary");
                        this.buttonInput.style.background = Constants.STANDARD_BCOLOR;
                        this.buttonInput.addEventListener("click", function (e) {
                            this.showLibraryEditor();
                        }.bind(this));
                        this.attachLibraryHandler();
                    }

                    /**
                     * @brief See HtkComponent.refresh.
                     */
                    refresh() {
                        this.buttonInput.innerHTML = this.value;
                        this.checkValues(this.buttonInput);
                    }

                    /**
                     * @brief See HtkComponent.getValue.
                     */
                    getValue() {
                        return this.buttonInput.innerHTML;
                    }

                    /**
                     * @brief See HtkComponent.getTemplate.
                     */
                    getTemplate() {
                      var templateContent = template.content;
                      return templateContent;
                    }

                    /**
                     * @brief This function is called by the HtkLibraryEditor when the user selects a new library. The value displayed by the button is updated to the newLibraryName.
                     * @param[in] libraryOwner the username which owns the library.
                     * @param[in] newLibraryName the library name.
                     */
                    libraryChanged (libraryOwner, newLibraryName) {
                        if (!this.isReadOnly()) {
                            this.buttonInput.innerHTML = newLibraryName;
                            this.setValue(libraryOwner + "/" + newLibraryName);
                            this.checkValues(this.buttonInput);
                        }
                    }
                }

                /**
                 * @brief Registers the element.
                 */
                 window.customElements.define('htk-library-button', HtkLibraryButton);
