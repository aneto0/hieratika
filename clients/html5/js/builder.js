// Hieratika Plant Builder Javascript functions
//Author: Luca Porzio

function newConfig() {
  document.getElementById("btnNewConfig").style.display = "none";
  document.getElementById("instructions").style.display = "block";
  document.getElementById("intro").style.display = "none";
  document.getElementById("plantDetailsForm").style.display = "block";
}

function savePlantDetails() {
  document.getElementById("pName").disabled = true;
  document.getElementById("pDesc").disabled = true;
  document.getElementById("sVersion").disabled = true;
  document.getElementById("sdd").disabled = true;
  document.getElementById("pVersion").disabled = true;
  document.getElementById("configdiv").style.display = "block";
}

function loadHTML() {
  var title = "PLANT SYSTEM CONFIGURATION";
  let html = $("#template-single").html();
  $(html).appendTo('#configdiv');
}
