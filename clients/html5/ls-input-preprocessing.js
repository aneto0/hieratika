/*
 date: 11/02/2021
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
       <link rel="import" href="/htk-matrix-dropmenu-editor.html">
*/

import * as Constants from './htk-constants.js'
import { HtkComponent } from './htk-component.js'

const template = document.createElement('template');
template.innerHTML = `
<div id="dmatrix">
    <table border="0">
        <tr>
            <td>
                <button type="button" id="addRowButton">Add Row</button>
                <button type="button" id="removeRowButton">Remove Row</button>
            </td>
        </tr>
    </table>
</div>
`;

      /**
       * @brief Array editor component.
       */
      class LsInputPreprocessing extends HtkComponent {

        /**
         * @brief Constructor. NOOP.
         */
        constructor() {
          super();
        }


        checkValue() {
          //error if two signals with the same name
          for (var i = 0; i < this.matrix1.value.length; i++) {
            var toCheck = this.matrix1.value[i][0];
            for (var j = i + 1; j < this.matrix1.value.length; j++) {
              if (toCheck === this.matrix1.value[j][0]) {
                var id = "#menu_" + i.toString() + "0";
                var myCell = this.matrix1.tbl.querySelector(id);
                myCell.style.color = Constants.ERROR_BCOLOR;
                var id = "#menu_" + j.toString() + "0";
                var myCell = this.matrix1.tbl.querySelector(id);
                myCell.style.color = Constants.ERROR_BCOLOR;
              }
            }
          }
        }

        domLoaded() {
          var m1Id = this.getAttribute("data-m1Id");
          var m2Id = this.getAttribute("data-m2Id");
          var m3Id = this.getAttribute("data-m3Id");

          var htkCompArray = document._frameComponents[m1Id];
          this.matrix1 = htkCompArray[0];
          var htkCompArray = document._frameComponents[m2Id];
          this.matrix2 = htkCompArray[0];
          var htkCompArray = document._frameComponents[m3Id];
          this.matrix3 = htkCompArray[0];

          this.matrix1.addRefreshCallback(this);

          this.matrix1.showHideButtons(false);
          this.matrix2.showHideButtons(false);
          this.matrix3.showHideButtons(false);

          this.matrix1.refreshAllCellsDimensions("150px", "25px");
          this.matrix2.refreshAllCellsDimensions("250px", "25px");
          this.matrix3.refreshAllCellsDimensions("200px", "25px");

          this.addRowButton = this.shadowRoot.querySelector("#addRowButton");
          this.addRowButton.onclick = function() {
            this.matrix1.addRowCallback();
            this.matrix2.addRowCallback();
            this.matrix3.addRowCallback();
          }.bind(this);

          this.removeRowButton = this.shadowRoot.querySelector("#removeRowButton");
          this.removeRowButton.onclick = function() {
            this.matrix1.removeRowCallback();
            this.matrix2.removeRowCallback();
            this.matrix3.removeRowCallback();
          }.bind(this);
        }


        /**
         * @brief See HtkComponent.refresh
         */
        refresh() {
          if (this.matrix1.initialised !== undefined) {
            if (this.initialised && this.matrix1.initialised) {
              this.checkValue();
            }
          }
        }

        /**
         * @brief See HtkComponent.setValue
         */
        setValue(elementsToSet, updateRemote = true) {
          if (elementsToSet.length > 0) {
            super.setValue(elementsToSet.slice(0), updateRemote);
            this.initialised = true;
          }
        }

        /**
         * @brief See HtkComponent.setInitialValue
         */
        setInitialValue(initialValueToSet) {
          if (initialValueToSet.length > 0) {
            super.setInitialValue(initialValueToSet.slice(0));
          }
        }

        /**
         * @brief See HtkComponent.setPlantValue
         */
        setPlantValue(plantValueToSet) {
          if (plantValueToSet.length > 0) {
            super.setPlantValue(plantValueToSet.slice(0));
          }
        }

        /**
         * @brief See HtkComponent.setReferenceValue
         */
        setReferenceValue(referenceValueToSet) {
          if (referenceValueToSet.length > 0) {
            super.setReferenceValue(referenceValueToSet.slice(0));
          }
        }

        /**
         * @brief See HtkComponent.setReadOnly
         */
        setReadOnly(isReadOnly) {
          //super.setReadOnly(isReadOnly);
          //this.addRowButton.disabled = isReadOnly;
          //this.removeRowButton.disabled = isReadOnly;
        }

        /**
         * @brief See HtkComponent.getTemplate
         */
         getTemplate() {
           var templateContent = template.content;
           return templateContent;
         }


        /**
         * @brief See HtkComponent.createdCallback
         */
        createdCallback() {
          super.createdCallback();
          this.numberOfElements = 0;
          this.initialised = false;
        }
      }

      /**
       * @brief Registers the element.
       */
      window.customElements.define('ls-input-preprocessing', LsInputPreprocessing);
