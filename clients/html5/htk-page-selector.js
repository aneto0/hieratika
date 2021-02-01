/*
 date: 26/01/2021
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

import HtkHelper from './htk-helper.js'
import { HtkDialogs } from './htk-dialogs.js'

const template = document.createElement('template');
template.innerHTML = `
  <dialog id="dpagesselector">
    <div id="divpages">
      <table style="border-style:solid;border-width:1px;width: 100%">
        <tr>
          <td>
          Pages
          </td>
          <td>
          Description
          </td>
        </tr>
        <tr>
          <td><select id="pageselect" size="20" style="width:150px;overflow-x:scroll"></select></td>
          <td id="descriptionarea" style="width:250px;vertical-align:top;background-color:#F5F5F5"></td>
        </tr>
      </table>
        <table style="border-style:solid;border-width:0px;width: 100%">
        <tr>
          <td style="padding-top:20px;">
            <button title="OK" id="okbtn">OK</button>
            <button title="Cancel" id="cancelbtn">Cancel</button>
          </td>
        </tr>
      </table>
    </div>
  </dialog>
`;

/**
 * @brief A dialog which allows to select a new Hieratika page to be displayed (amonsgst all the Hieratika pages returned by the server.
 */
class HtkPageSelector extends HTMLElement {

  /**
   * @brief Constructor. NOOP.
   */
  constructor() {
    super();
  }

  /**
   * @brief Registers the dialog.
   */
  connectedCallback() {
    var templateContent = template.content;
    const root = this.attachShadow({
      mode: 'open'
    });
    root.appendChild(templateContent.cloneNode(true));

    this.pageName = "";
    this.diag = this.shadowRoot.querySelector("#dpagesselector");
    this.pageSelect = this.shadowRoot.querySelector("#pageselect");
    this.pageSelect.onclick = function() {
      this.updatePageDescription();
    }.bind(this);

    this.descriptionArea = this.shadowRoot.querySelector("#descriptionarea");
    this.okButton = this.shadowRoot.querySelector("#okbtn");
    this.okButton.onclick = function() {
      var page = this.pageSelect[this.pageSelect.selectedIndex].pageInfo;
      this.okCallbackFunction(page);
      this.diag.close();
    }.bind(this);

    var cancelButton = this.shadowRoot.querySelector("#cancelbtn");
    cancelButton.onclick = function() {
      this.diag.close();
    }.bind(this);
  }

  /**
   * @brief Updates the page description against the currently user selected page.
   */
  updatePageDescription() {
    if (this.pageSelect.selectedIndex >= 0) {
      this.okButton.disabled = false;
      this.descriptionArea.innerHTML = this.pageSelect[this.pageSelect.selectedIndex].pageInfo.description;
    }
  }

  /**
   * @brief Shows the dialog.
   * @param[in] okCallbackFun the function to call if the user selects OK.
   */
  show(okCallbackFun) {
    this.pageSelect.innerHTML = "";
    this.okCallbackFunction = okCallbackFun;
    this.okButton.disabled = true;
    var htkDialog = new HtkDialogs();
    htkDialog.showWaitDialog();
    HtkHelper.getPages(
      function(pagesJson) {
        for (var p in pagesJson) {
          var option1 = document.createElement("option");
          var pageName = pagesJson[p].name;
          option1.text = pageName;
          option1.value = pageName;
          option1.pageInfo = pagesJson[p];
          this.pageSelect.appendChild(option1);
        }
        htkDialog.closeWaitDialog();
        this.diag.showModal();
      }.bind(this),
      function() {
        htkDialog.closeWaitDialog();
        htkDialog.showErrorDialog("Failed to get the pages. Unknown error, check the server logs.");
      }
    );
  }
}

/**
 * @brief Registers the element.
 */
 /**
  * @brief Registers the element.
  */
customElements.define('htk-page-selector', HtkPageSelector);
