// Hieratika Plant Builder Javascript functions
// Author: Luca Porzio

var tabList = [];

function newConfig() {
  $('#intro').hide(500);
  $('#instructions').show(500);
  $('#plantDetailsForm').show(500);
}

function savePlantDetails() {
  document.getElementById("pName").disabled = true;
  document.getElementById("pDesc").disabled = true;
  document.getElementById("sVersion").disabled = true;
  document.getElementById("sdd").disabled = true;
  document.getElementById("pVersion").disabled = true;

  $('#instructions').hide(500);
  $('#plantDetailsForm').hide(500);

  $('#configdiv').show(500);
  $('#addPlant').show(500);

}

function addPlantSystem() {
  // jQuery html select
  let psName = document.getElementById("psName");
  tabList.push(psName.value);
  // Refreshing template
  $('.tab').template({
    'tabList': tabList
  });
  // Adding tab template
  let htmlTab = $("#template-tabcontent").html();
  $(htmlTab).appendTo('#configdiv');
  // Setting ids
  let tabContentId = psName.value + "_tab";
  document.getElementById("newTabContent").id = tabContentId;
}

// onclick action on tab buttons
function openTab(evt, tabName) {
  let i, tabcontent, tablinks;
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
