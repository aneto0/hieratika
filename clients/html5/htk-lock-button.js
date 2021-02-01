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
        <link rel="import" href="/htk-helper.html">
        <link rel="import" href="/htk-schedule-selector.html">
*/

import * as Constants from './htk-constants.js'

const template = document.createElement('template');
template.innerHTML = `
<style>
    @import url("/css/font-awesome-4.7.0/css/font-awesome.min.css");
</style>
<button type="button" id="block" style="font-size:24px;border:none"><i id="bicon" class="fa fa-unlock"></i></button>
`;

  /**
   * @brief A button which renders an Hieratike Lock type.
   */
  class HtkLockButton extends HtkAbstractInput {

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
          this.buttonLock = this.shadowRoot.querySelector("#block");
          this.buttonLock.addEventListener("click", function (e) {
              if (!this.isReadOnly()) {
                  var value = this.getValue();
                  if (value === undefined) {
                      value = "1";
                  }
                  var intValue = parseInt(value);
                  if (intValue === 1) {
                      this.setValue(0);
                  }
                  else if (intValue === 0) {
                      this.setValue(1);
                  }
              }
          }.bind(this));
          this.buttonIcon = this.shadowRoot.querySelector("#bicon");
          this.buttonLock.style.background = Constants.STANDARD_BCOLOR;
      }

      /**
       * @brief See HtkComponent.refresh.
       */
      refresh() {
          var value = this.getValue();
          if (value === undefined) {
              value = "1";
          }
          var intValue = parseInt(value);
          if (intValue === 1) {
              this.buttonIcon.className = "fa fa-lock";
          }
          else if (intValue === 0) {
              this.buttonIcon.className = "fa fa-unlock";
          }
          else {
              this.buttonIcon.className = "fa fa-lock";
          }
          this.checkValues(this.buttonIcon);
          this.buttonIcon.style.background = Constants.STANDARD_BCOLOR;
          if (this.isReadOnly()) {
              this.buttonIcon.style.color = "LightGray";
          }
          if (intValue === -1) {
              this.buttonIcon.style.color = "red";
          }
      }

      /**
       * @brief See HtkComponent.setValue
       */
      setValue (elementsToSet, updateRemote=true) {
          var intValue = parseInt(elementsToSet);
          var locked = (intValue != 0);
          if (intValue === -1) {
              this.setEditable(false);
          }
          super.setValue(elementsToSet, updateRemote);
          this.fireLockedStatusChanged(locked);
      }

      /**
       *
       */
      setEditable (editable) {
          var intValue = parseInt(this.getValue());
          if (intValue === -1) {
              editable = false;
          }
          super.setEditable(editable);
      }

      /**
       * @brief See HtkComponent.getTemplate
       */
       getTemplate() {
         var templateContent = template.content;
         return templateContent;
       }
  }

  /**
   * @brief Registers the element.
   */
   customElements.define('htk-lock-button', HtkLockButton);
