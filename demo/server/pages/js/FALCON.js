/*
 * FALCON.html Javascript File
 */

/******************
 * User functions *
 ******************/

// onclick action on tab buttons
function openTab(evt, tabName) {
  var i, tabcontent, tablinks;
  tabcontent = document.getElementsByClassName("tabcontent");
  for (i = 0; i < tabcontent.length; i++) {
    tabcontent[i].style.display = "none";
  }
  tablinks = document.getElementsByClassName("tablinks");
  for (i = 0; i < tablinks.length; i++) {
    tablinks[i].className = tablinks[i].className.replace("active", "");
  }
  document.getElementById(tabName).style.display = "block";
  evt.currentTarget.className += " active";
}
// open first tab by default
document.getElementById("RU_Main").click();

/************************
 * Validation functions *
 ************************/
function setValidations() {
  // BPS
  // Getting components
  var t = [document._frameComponents['BPS@TIME_1_REA0'],
    document._frameComponents['BPS@TIME_2_REA0'],
    document._frameComponents['BPS@TIME_3_REA0']
  ];

  var ru = [document._frameComponents['BPS@RAMP_UP_TI0'],
    document._frameComponents['BPS@RAMP_UP_TI1'],
    document._frameComponents['BPS@RAMP_UP_TI2']
  ];

  var rd = document._frameComponents['BPS@RAMP_DOWN_0'];

  var v = [document._frameComponents['BPS@VOLTAGE_LE0'],
    document._frameComponents['BPS@VOLTAGE_LE1'],
    document._frameComponents['BPS@VOLTAGE_LE2']
  ];

  var pl = document._frameComponents['BPS@PULSE_LENG0'];

  var isPlSec = document._frameComponents['BPS@PL_IN_SEC_0'];

  var isVariableVolt = document._frameComponents['BPS@VAR_BODY_V0'];

  // Validation: time positive
  t[0].setValidations("'BPS@TIME_1_REA0' > 0");
  t[1].setValidations("'BPS@TIME_2_REA0' > 0");
  t[2].setValidations("'BPS@TIME_3_REA0' > 0");

  // Validation: voltage positive
  v[0].setValidations("'BPS@VOLTAGE_LE0' > 0");
  v[1].setValidations("'BPS@VOLTAGE_LE1' > 0");
  v[2].setValidations("'BPS@VOLTAGE_LE2' > 0");

  // Validation: (t0+ru0)<=t1
  t[0].setValidations("('BPS@TIME_1_REA0' + 'BPS@RAMP_UP_TI0') <= 'BPS@TIME_2_REA0'");
  ru[0].setValidations("('BPS@TIME_1_REA0' + 'BPS@RAMP_UP_TI0') <= 'BPS@TIME_2_REA0'");
  t[1].setValidations("('BPS@TIME_1_REA0' + 'BPS@RAMP_UP_TI0') <= 'BPS@TIME_2_REA0'");

  // Validation: (t1+ru1)<=t2
  t[1].setValidations("('BPS@TIME_2_REA0' + 'BPS@RAMP_UP_TI1') <= 'BPS@TIME_3_REA0'");
  ru[1].setValidations("('BPS@TIME_2_REA0' + 'BPS@RAMP_UP_TI1') <= 'BPS@TIME_3_REA0'");
  t[2].setValidations("('BPS@TIME_2_REA0' + 'BPS@RAMP_UP_TI1') <= 'BPS@TIME_3_REA0'");

  // Validation: (t2+ru2+rd)<=pl
  t[2].setValidations("('BPS@TIME_3_REA0' + 'BPS@RAMP_UP_TI2' + 'BPS@RAMP_DOWN_0') <= 'BPS@PULSE_LENG0'");
  ru[2].setValidations("('BPS@TIME_3_REA0' + 'BPS@RAMP_UP_TI2' + 'BPS@RAMP_DOWN_0') <= 'BPS@PULSE_LENG0'");
  rd.setValidations("('BPS@TIME_3_REA0' + 'BPS@RAMP_UP_TI2' + 'BPS@RAMP_DOWN_0') <= 'BPS@PULSE_LENG0'");
  pl.setValidations("('BPS@TIME_3_REA0' + 'BPS@RAMP_UP_TI2' + 'BPS@RAMP_DOWN_0') <= 'BPS@PULSE_LENG0'");

  // Validation: 100<ru<1000
  ru[0].setValidations(["('BPS@RAMP_UP_TI0' >= 100)", "('BPS@RAMP_UP_TI0' <= 1000)"]);
  ru[1].setValidations(["('BPS@RAMP_UP_TI1' >= 100)", "('BPS@RAMP_UP_TI1' <= 1000)"]);
  ru[2].setValidations(["('BPS@RAMP_UP_TI2' >= 100)", "('BPS@RAMP_UP_TI2' <= 1000)"]);

  // Validation: 100<rd<1000
  rd.setValidations(["('BPS@RAMP_DOWN_0' >= 100)", "('BPS@RAMP_DOWN_0' <= 1000)"]);
}
