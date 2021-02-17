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
	<link rel="import" href="/htk-component.html">
	<link rel="import" href="/htk-matrix-dropmenu-editor.html">
	<link rel="import" href="/htk-array-editor.html">
	<link rel="import" href="/htk-input.html">
*/

import * as Constants from './htk-constants.js'

import { HtkComponent } from './htk-component.js'
import { HtkValidationType } from './htk-validation.js'

			/**
			 * @brief Array editor component.
			 */
			class FalconOpi extends HtkComponent {

				/**
				 * @brief Constructor. NOOP.
				 */
				constructor() {
					super();
				}

				domLoaded() {

					// this.firstLevTabs = [];
					// this.nFirstLevTabs = 0;
					// while (1) {
					// 	var varName = "data-tab_" + this.nFirstLevTabs;
					// 	var varNameId = this.getAttribute(varName);
					// 	var htkCompArray = document.getElementById(varNameId);
					// 	if ((htkCompArray == null) || (htkCompArray == undefined)) {
					// 		break;
					// 	}
					// 	this.firstLevTabs.push(htkCompArray);
					// 	this.firstLevTabs[this.nFirstLevTabs].onclick = function(e) {
					// 		var caller = e.target || e.srcElement;
					// 		var tabNameX = caller.id + "_tab";
					// 		this.openTab(tabNameX);
					// 	}.bind(this);
					// 	this.nFirstLevTabs++;
					// }

					var tot = 0;

					this.nRuMainFields = 12;
					this.ru_main = new Array(this.nRuMainFields);

					for (var i = 0; i < this.nRuMainFields; i++) {
						var varName = "data-ru_main_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.ru_main[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.ru_main[i]);
						this.ru_main[i].validations = validations;
						// this.ru_main[i].setUpdateValFun(this, tot + i);
						this.ru_main[i].setReadOnly(false);
					}
					tot += this.nRuMainFields;

					this.nRuAlarmsFields = 28;
					this.ru_alarms = new Array(this.nRuAlarmsFields);

					for (var i = 0; i < this.nRuAlarmsFields; i++) {
						var varName = "data-ru_alarms_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.ru_alarms[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.ru_alarms[i]);
						this.ru_alarms[i].validations = validations;

						// this.ru_alarms[i].setUpdateValFun(this, tot + i);
						this.ru_alarms[i].setReadOnly(false);
					}
					tot += this.nRuAlarmsFields;


					this.nRuCwsAlarmsFields = 44;
					this.ru_cws_alarms = new Array(this.nRuCwsAlarmsFields);

					for (var i = 0; i < this.nRuCwsAlarmsFields; i++) {
						var varName = "data-ru_cws_alarms_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.ru_cws_alarms[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.ru_cws_alarms[i]);
						this.ru_cws_alarms[i].validations = validations;

						// this.ru_cws_alarms[i].setUpdateValFun(this, tot + i);
						this.ru_cws_alarms[i].setReadOnly(false);
					}
					tot += this.nRuCwsAlarmsFields;

					this.nBpsFields = 13;
					this.bps = new Array(this.nBpsFields);


					for (var i = 0; i < this.nBpsFields; i++) {
						var varName = "data-bps_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.bps[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.bps[i]);
						this.bps[i].validations = validations;

						// this.bps[i].setUpdateValFun(this, tot + i);
						this.bps[i].setReadOnly(false);
					}
					tot += this.nBpsFields;


					this.nCspFields = 8;
					this.cps = new Array(this.nCspFields);

					for (var i = 0; i < this.nCspFields; i++) {
						var varName = "data-cps_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.cps[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.cps[i]);
						this.cps[i].validations = validations;

						// this.cps[i].setUpdateValFun(this, tot + i);
						this.cps[i].setReadOnly(false);
					}

					//three checkboxes are mutual exclusive
					// this.cps[1].setEnableOnly(true);
					// this.cps[2].setEnableOnly(true);
					// this.cps[3].setEnableOnly(true);


					tot += this.nCspFields;

					this.nGcspFields = 8;
					this.gcps = new Array(this.nGcspFields);

					for (var i = 0; i < this.nGcspFields; i++) {
						var varName = "data-gcps_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.gcps[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.gcps[i]);
						this.gcps[i].validations = validations;

						// this.gcps[i].setUpdateValFun(this, tot + i);
						this.gcps[i].setReadOnly(false);
					}
					// this.gcps[1].setEnableOnly(true);
					// this.gcps[2].setEnableOnly(true);
					// this.gcps[3].setEnableOnly(true);


					tot += this.nGcspFields;


					this.nHvpsFields = 7;
					this.hvps = new Array(this.nHvpsFields);


					for (var i = 0; i < this.nHvpsFields; i++) {
						var varName = "data-hvps_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.hvps[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.hvps[i]);
						this.hvps[i].validations = validations;

						// this.hvps[i].setUpdateValFun(this, tot + i);
						this.hvps[i].setReadOnly(false);
					}
					tot += this.nHvpsFields;



					this.nIps1Fields = 5;
					this.ips1 = new Array(this.nIps1Fields);

					for (var i = 0; i < this.nIps1Fields; i++) {
						var varName = "data-ips1_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.ips1[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.ips1[i]);
						this.ips1[i].validations = validations;

						// this.ips1[i].setUpdateValFun(this, tot + i);
						this.ips1[i].setReadOnly(false);
					}
					tot += this.nIps1Fields;

					this.nIps2Fields = 5;
					this.ips2 = new Array(this.nIps2Fields);


					for (var i = 0; i < this.nIps2Fields; i++) {
						var varName = "data-ips2_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.ips2[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.ips2[i]);
						this.ips2[i].validations = validations;

						// this.ips2[i].setUpdateValFun(this, tot + i);
						this.ips2[i].setReadOnly(false);
					}
					tot += this.nIps2Fields;



					this.nPmp1Fields = 10;
					this.pmp1 = new Array(this.nPmp1Fields);

					for (var i = 0; i < this.nPmp1Fields; i++) {
						var varName = "data-pmp1_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.pmp1[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.pmp1[i]);
						this.pmp1[i].validations = validations;

						// this.pmp1[i].setUpdateValFun(this, tot + i);
						this.pmp1[i].setReadOnly(false);
					}
					tot += this.nPmp1Fields;


					this.nPmp2Fields = 10;
					this.pmp2 = new Array(this.nPmp2Fields);

					for (var i = 0; i < this.nPmp2Fields; i++) {
						var varName = "data-pmp2_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.pmp2[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.pmp2[i]);
						this.pmp2[i].validations = validations;

						// this.pmp2[i].setUpdateValFun(this, tot + i);
						this.pmp2[i].setReadOnly(false);
					}
					tot += this.nPmp2Fields;


					this.nRfilFields = 7;
					this.rfil = new Array(this.nRfilFields);


					for (var i = 0; i < this.nRfilFields; i++) {
						var varName = "data-rfil_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.rfil[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.rfil[i]);
						this.rfil[i].validations = validations;

						// this.rfil[i].setUpdateValFun(this, tot + i);
						this.rfil[i].setReadOnly(false);
					}
					tot += this.nRfilFields;


					this.nRscmFields = 3;
					this.rscm = new Array(this.nRscmFields);


					for (var i = 0; i < this.nRscmFields; i++) {
						var varName = "data-rscm_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.rscm[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.rscm[i]);
						this.rscm[i].validations = validations;

						// this.rscm[i].setUpdateValFun(this, tot + i);
						this.rscm[i].setReadOnly(false);
					}
					tot += this.nRscmFields;



					this.nRswpFields = 3;
					this.rswp = new Array(this.nRswpFields);

					for (var i = 0; i < this.nRswpFields; i++) {
						var varName = "data-rswp_" + i;
						var varNameId = this.getAttribute(varName);
						var htkCompArray = document._frameComponents[varNameId];
						this.rswp[i] = htkCompArray[0];

						var validations = new HtkValidationType(this.rswp[i]);
						this.rswp[i].validations = validations;

						// this.rswp[i].setUpdateValFun(this, tot + i);
						this.rswp[i].setReadOnly(false);
					}
					tot += this.nRswpFields;

					// this.openTab("RU_Main_tab");

				}

				variablesInfoLoaded() {
					for (var i = 0; i < this.nRuMainFields; i++) {
						this.value[0][i] = this.ru_main[i].value;
					}
					for (var i = 0; i < this.nRuAlarmsFields; i++) {
						this.value[1][i] = this.ru_alarms[i].value;
					}

					for (var i = 0; i < this.nRuCwsAlarmsFields; i++) {
						this.value[2][i] = this.ru_cws_alarms[i].value;
					}

					for (var i = 0; i < this.nBpsFields; i++) {
						this.value[3][i] = this.bps[i].value;
					}

					for (var i = 0; i < this.nCpsFields; i++) {
						this.value[4][i] = this.cps[i].value;
					}

					for (var i = 0; i < this.nGcpsFields; i++) {
						this.value[5][i] = this.gcps[i].value;
					}

					for (var i = 0; i < this.nHvpsFields; i++) {
						this.value[6][i] = this.hvps[i].value;
					}

					for (var i = 0; i < this.nIps1Fields; i++) {
						this.value[7][i] = this.ips1[i].value;
					}

					for (var i = 0; i < this.nIps2Fields; i++) {
						this.value[8][i] = this.ips2[i].value;
					}

					for (var i = 0; i < this.nPmp1Fields; i++) {
						this.value[9][i] = this.pmp1[i].value;
					}

					for (var i = 0; i < this.nPmp2Fields; i++) {
						this.value[10][i] = this.pmp2[i].value;
					}

					for (var i = 0; i < this.nRfilFields; i++) {
						this.value[11][i] = this.rfil[i].value;
					}

					for (var i = 0; i < this.nRscmFields; i++) {
						this.value[12][i] = this.rscm[i].value;
					}

					for (var i = 0; i < this.nRswpFields; i++) {
						this.value[13][i] = this.rswp[i].value;
					}
					this.fireValueChanged("value");
					this.updateRemote(this.getValue());
				}

				scheduleChanged(x) {
					this.variablesInfoLoaded();
				}



				// openTab(tabName) {
				// 	var i, tabcontent, tablinks;
				// 	tabcontent = document.getElementsByClassName("tabcontent");
				// 	for (i = 0; i < tabcontent.length; i++) {
				// 		tabcontent[i].style.display = "none";
				// 	}
				// 	tablinks = document.getElementsByClassName("tablinks");
				// 	for (i = 0; i < tablinks.length; i++) {
				// 		tablinks[i].className = tablinks[i].className.replace(" active", "");
				// 	}
				// 	document.getElementById(tabName).style.display = "block";
				// 	//evt.currentTarget.className += " active";
				// }

				checkValue() {}




				checkBpsValues() {
					for (var i = 0; i < this.nBpsFields; i++) {
						this.bps[i].checkAllValues();
					}


					var ret = true;
					var t = [this.bps[5], this.bps[6], this.bps[7]];
					var ru = [this.bps[2], this.bps[3], this.bps[4]];
					var rd = this.bps[1];
					var v = [this.bps[8], this.bps[9], this.bps[10]];
					var pl = this.bps[0];
					var isPlSec = this.bps[11];
					var isVariableVolt = this.bps[12];

					//check that the voltages and times are positive
					for (var i = 0;
						(i < 11) && (ret); i++) {
						ret = (this.bps[i].value >= 0);
						if (!ret) {
							this.bps[i].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
						}
					}

					//chack that (t1+ru1)<=t2 && (t2+ru2)<=t3 && (t3+ru3+rd)<=pl
					if (ret) {
						ret = ((t[0].value + ru[0].value / 1000.0) <= (t[1].value));
						if (!ret) {
							t[0].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
							t[1].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
							ru[0].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
						}
					}
					if (ret) {
						ret = ((t[1].value + ru[1].value / 1000.0) <= t[2].value);
						if (!ret) {
							t[1].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
							t[2].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
							ru[1].textInput.style.backgroundColor = Constants.ERROR_BCOLOR;
						}
					}
					if (ret) {
						var plTemp = pl.value;
						if (isPlSec.value > 0) {
							plTemp *= 1000.0;
						}
						ret = ((t[2].value + ru[2].value / 1000.0 + rd.value / 1000.0) <= plTemp);
						if (!ret) {
							t[2].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
							ru[2].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
							rd.textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
							pl.textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						}
					}
					//check that all the 100<ru<1000 us
					if (ret) {
						ret = (ru[0].value >= 100) && (ru[0].value <= 1000);
						if (!ret) {
							ru[0].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						}
					}
					if (ret) {
						ret = (ru[1].value >= 100) && (ru[1].value <= 1000);
						if (!ret) {
							ru[1].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						}
					}
					if (ret) {
						ret = (ru[2].value >= 100) && (ru[2].value <= 1000);
						if (!ret) {
							ru[2].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						}
					}
					if (ret) {
						ret = (rd.value >= 100) && (rd.value <= 1000);
						if (!ret) {
							rd.textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						}
					}

					//check that if "VariableBodyVoltage=false" all times and voltages are equal
					if (ret) {
						if (isVariableVolt.value == 0) {
							ret = (t[0].value == 0);
							if (!ret) {
								t[0].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
							}
							if (ret) {
								ret = (v[1].value == v[2].value);
								if (!ret) {
									v[1].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
									v[2].textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
								}
							}
						}
					}
				}


				chekMutualTdk(caller, valIndex) {
					//assume checkboxes are consecutive and put here the beg index
					var begIndex = 1;
					if ((caller >= begIndex) && (caller < begIndex + 3)) {
						//reset all checkboxes
						for (var i = 0; i < 3; i++) {
							this.value[valIndex][begIndex + i] = 0;
							if (valIndex == 4) {
								if ((begIndex + i) == caller) {
									this.cps[caller].setValue(1);
								} else {
									this.cps[begIndex + i].setValue(0);
								}
							}
							if (valIndex == 5) {
								if ((begIndex + i) == caller) {
									this.gcps[caller].setValue(1);
								} else {
									this.gcps[begIndex + i].setValue(0);
								}
							}
						}
						this.value[valIndex][caller] = 1;
					}
				}


				checkTdkValues(val) {
					for (var i = 0; i < val.length; i++) {
						val[i].checkAllValues();
					}
					var spVoltage = val[6];
					var limDown = val[7];
					var limUp = val[4];
					var ret = ((spVoltage.value >= limDown.value) && (spVoltage.value <= limUp.value));
					if (!ret) {
						spVoltage.textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						limDown.textInput.style.backgroundColor = Constant.ERROR_BCOLOR;
						limUp.textInput.style.backgroundColor = Constant.ERROR_BCOLOR;

					}
					return ret;
				}

				/**
				 * @brief Checks if the component style should be updated due to a value change and executes all the validation functions.
				 * @details For each element array, performs the same actions described in HtkAbstractInput.updateMatrix.
				 * @param[in] userChanged true if the value update was triggered by a user action.
				 */
				updateValue(userChanged, caller) {
					var tot = 0;
					if ((caller >= tot) && (caller < this.nRuMainFields)) {
						this.value[0][caller] = this.ru_main[caller].value;
					}

					tot += this.nRuMainFields;
					if ((caller >= tot) && (caller < (tot + this.nRuAlarmsFields))) {
						this.value[1][caller - tot] = this.ru_alarms[caller - tot].value;
					}

					tot += this.nRuAlarmsFields;
					if ((caller >= tot) && (caller < (tot + this.nRuCwsAlarmsFields))) {
						this.value[2][caller - tot] = this.ru_cws_alarms[caller - tot].value;
					}

					tot += this.nRuCwsAlarmsFields;
					if ((caller >= tot) && (caller < (tot + this.nBpsFields))) {
						if (this.checkBpsValues()) {
							this.value[3][caller - tot] = this.bps[caller - tot].value;
						}
					}

					tot += this.nBpsFields;

					if ((caller >= tot) && (caller < (tot + this.nCspFields))) {
						if (this.checkTdkValues(this.cps)) {
							this.value[4][caller - tot] = this.cps[caller - tot].value;
						}
						this.chekMutualTdk(caller - tot, 4);
					}
					tot += this.nCspFields;
					if ((caller >= tot) && (caller < (tot + this.nGcspFields))) {
						if (this.checkTdkValues(this.gcps)) {
							this.value[5][caller - tot] = this.gcps[caller - tot].value;
						}
						this.chekMutualTdk(caller - tot, 5);
					}
					tot += this.nGcspFields;
					if ((caller >= tot) && (caller < (tot + this.nHvpsFields))) {
						this.value[6][caller - tot] = this.hvps[caller - tot].value;
					}
					tot += this.nHvpsFields;
					if ((caller >= tot) && (caller < (tot + this.nIps1Fields))) {
						this.value[7][caller - tot] = this.ips1[caller - tot].value;
					}

					tot += this.nIps1Fields;
					if ((caller >= tot) && (caller < (tot + this.nIps2Fields))) {
						this.value[8][caller - tot] = this.ips2[caller - tot].value;
					}

					tot += this.nIps2Fields;
					if ((caller >= tot) && (caller < (tot + this.nPmp1Fields))) {
						this.value[9][caller - tot] = this.pmp1[caller - tot].value;
					}

					tot += this.nPmp1Fields;
					if ((caller >= tot) && (caller < (tot + this.nPmp2Fields))) {
						this.value[10][caller - tot] = this.pmp2[caller - tot].value;
					}

					tot += this.nPmp2Fields;
					if ((caller >= tot) && (caller < (tot + this.nRfilFields))) {
						this.value[11][caller - tot] = this.rfil[caller - tot].value;
					}

					tot += this.nRfilFields;
					if ((caller >= tot) && (caller < (tot + this.nRscmFields))) {
						this.value[12][caller - tot] = this.rscm[caller - tot].value;
					}

					tot += this.nRscmFields;
					if ((caller >= tot) && (caller < (tot + this.nRswpFields))) {
						this.value[13][caller - tot] = this.rswp[caller - tot].value;
					}


					if (userChanged) {
						this.fireValueChanged("value");
						this.updateRemote(this.getValue());
					}

				}




				/**
				 * @brief See HtkComponent.refresh
				 */
				refresh() {

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
					super.setReadOnly(isReadOnly);
				}

				/**
				 * @brief See HtkComponent.getTemplate
				 */
				getTemplate() {
          var templateContent = undefined;
          return templateContent;
				}


				assignmentNameDoneRefresh() {}


				/**
				 * @brief See HtkComponent.connectedCallback
				 */
				connectedCallback() {
					super.connectedCallback();
					window.htkHelper.addVariablesInfoLoadedListener(this);
					// window.htkHelper.addScheduleChangedListener(this);
				}
			}

			/**
			 * @brief Registers the element.
			 */
       window.customElements.define('htk-falcon-opi', FalconOpi);
