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
        <link rel="import" href="/htk-abstract-input.html">
        <link rel="import" href="/htk-helper.html">
        <link rel="import" href="/htk-schedule-selector.html">
*/

/* Be sure that htk-scheduel selector is included in the main document */


;
import * as Constants from './htk-constants.js'
import { HtkAbstractInput } from './htk-abstract-input.js'

const template = document.createElement('template');
template.innerHTML = `
<htk-schedule-selector id="scheduleselector"></htk-schedule-selector>
<button type="button" id="bschedule"></button>
`;


                /**
                 * @brief A button which opens a htk-schedule-selector. The value of this component is the UID of the selected schedule.
                 */
                class HtkScheduleButton extends HtkAbstractInput {

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
                        var configName = this.getAttribute("data-config-name");
                        this.scheduleSelector = this.shadowRoot.querySelector("#scheduleselector");
                        this.scheduleSelector.setPageName(configName);
                        this.buttonInput = this.shadowRoot.querySelector("#bschedule");
                        this.buttonInput.style.background = Constants.STANDARD_BCOLOR;
                        this.buttonInput.addEventListener("click", function (e) {
                            this.scheduleSelector.show(this.scheduleChanged.bind(this), !this.isReadOnly(), false);
                        }.bind(this));
                        this.currentSchedule = undefined;
                    }

                    /**
                     * @brief Callback function called when the selected schedule changes.
                     */
                    scheduleChanged(schedule) {
                        this.currentSchedule = schedule;
                        this.setValue(schedule.uid);
                    }

                    /**
                     * @brief See HtkComponent.refresh.
                     */
                    refresh() {
                        if (this.currentSchedule !== undefined) {
                            this.buttonInput.innerHTML = this.currentSchedule.name;
                            this.checkValues(this.buttonInput);
                        }
                    }

                    /**
                     * @brief See HtkComponent.setValue.
                     */
                    setValue (valueToSet, updateRemote = true) {
                        super.setValue(valueToSet, updateRemote);
                        if (Array.isArray(valueToSet)) {
                            if (valueToSet.length > 0) {
                                valueToSet = valueToSet[0];
                            }
                            else {
                                valueToSet = "";
                            }
                        }
                        if (valueToSet !== undefined) {
                            if (valueToSet.length > 0) {
                                this.buttonInput.disabled = true;
                                window.htkHelper.getSchedule(
                                    valueToSet,
                                    function(schedule) {
                                        this.buttonInput.disabled = false;
                                        this.currentSchedule = schedule;
                                        this.refresh();
                                    }.bind(this),
                                    function(response) {
                                        this.buttonInput.disabled = false;
                                        this.currentSchedule = undefined;
                                    }.bind(this)
                                );
                            }
                        }
                    }

                    /**
                     * @brief See HtkComponent.getValue
                     */
                    getValue() {
                        var value = "";
                        if (this.currentSchedule !== undefined) {
                            value = this.currentSchedule.uid;
                        }
                        return value;
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
                 window.customElements.define('htk-schedule-button', HtkScheduleButton);
