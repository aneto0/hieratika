/*
 date: 25/01/2021
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
        <link rel="import" href="/htk-wait-dialog.html">
*/

/**
 * @brief Collection of Hieratika standard dialogs.
 */
export default class HtkDialogs {

    /**
     * @brief Constructor. NOOP.
     */
    constructor() {

    }

    static createDialog() {
      this.waitDialog = document.createElement("htk-wait-dialog");
      document.body.appendChild(this.waitDialog);
    }

    /**
     * @brief Shows a modal wait dialog.
     */
    static showWaitDialog() {
        this.waitDialog.showModal();
    }

    /**
     * @brief Closes the modal wait dialog which was previously shown using showWaitDialog.
     */
    static closeWaitDialog() {
        this.waitDialog.close();
    }

    /**
     * @brief Shows an information dialog.
     * @param[in] msg the message to display.
     */
    static showInformationDialog(msg) {
        alert(msg);
    }

    /**
     * @brief Shows an information dialog.
     * @param[in] msg the message to display.
     */
    static showErrorDialog(msg) {
        alert(msg);
    }

    /**
     * @brief Shows an input dialog.
     * @param[in] msg the message to display.
     * @param[in] defaultValue the default value to show on the text input box.
     * @return the user answer or null if the user has pressed cancel.
     */
    static showInputDialog(msg, defaultValue = "") {
        return prompt(msg, defaultValue);
    }

    /**
     * @brief Shows a confirm dialog.
     * @param[in] msg the message to display.
     * @return true if the user pressed OK, false otherwise.
     */
    static showConfirmDialog(msg) {
        return confirm(msg);
    }


}
