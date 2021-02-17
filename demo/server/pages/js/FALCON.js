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

// BPS Pulse Length transformation
var plSec = document._frameComponents['BPS@PL_IN_SEC_0'][0];
plSec.addEventListener("click", function(e) {
  let plLength = document._frameComponents['BPS@PULSE_LENG0'][0];
  let newValue = undefined;
  if (plSec.getValue() == 1) {
    newValue = (plLength.getValue() * 1000);
  } else {
    newValue = (plLength.getValue() / 1000);
  }
  plLength.setValue(newValue);
});
