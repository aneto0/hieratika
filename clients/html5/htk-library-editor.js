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
        <link rel="import" href="/htk-dialogs.html">
        <link rel="import" href="/htk-helper.html">
*/

;
import { HtkDialogs } from './htk-dialogs.js';

const template = document.createElement('template');
template.innerHTML = `
<dialog id="dselector">
    <iframe id="iframeeditor" style="width: 100%;border-style:solid;border-width:1px;"></iframe>
    </br>
    <table style="border-style:solid;border-width:1px;width: 100%">
        <tr>
            <td><select id="uselect" name="uselect"></select></td>
            <td><select id="lselect" name="lselect"></select></td>
            <td><button id="saveButton">Save...</button>
            <td><button id="deleteButton">Delete...</button></td>
            <td><button id="obsoleteButton">Obsolete...</button></td>
            <td><input type="checkbox" id="obsoleteCheckBox" value="obsolete">Show obsolete?</input></td>
        </tr>
        <tr>
            <td colspan="7"><textarea rows="2" cols="60" id="descriptionTextArea" title="Description"></textarea></td>
        </tr>
        <tr>
        </tr>
    </table>
    </br>
    <table style="border-style:solid;border-width:1px;width: 100%">
        <tr>
            <td><button id="tselectorOK">OK</button><button id="tselectorCancel">Cancel</button></td>
        </tr>
    </table>
</dialog>
`;


/**
 * @brief An editor which is capable of rendering a library content (by displaying its associated page) and of managing libraries (creation, deletion, ...).
 * @details The editor must be owned by a component which inherits from HtkLibrary.
 * @details The library content is to be edited by the page returned by /pages/[librarytype].html where librarytype is the value returned by owner.getLibraryType().
 */
export class HtkLibraryEditor extends HTMLElement {

    /**
     * @brief Constructor. NOOP.
     */
    constructor() {
        super();
        this.htkDialog = new HtkDialogs();
    }

    /**
     * @brief Gets the UID of the library currently selected by the user (with name libraryName).
     * @param[in] libraryName the library to get the UID.
     */
    getLibraryUID (libraryName) {
        var allLibraries = this.availableLibraries;
        var lib = allLibraries.find(function (element) {
            return (element.name === libraryName);
        });
        var libUID = undefined;
        if (lib !== undefined) {
            libUID = lib.uid;
        }
        return libUID;
    }

    /**
     * @brief Queries all the variables that are available for a given user.
     * @param[in] username the username to query.
     * @param[in] readyFun the function to be called when the libraries are available to be shown.
     */
    populateLibraries (username, readyFun) {
        window.htkHelper.getLibraries(
            this.owner.getLibraryType(),
            username,
            function (availableLibraries) {
                this.availableLibraries = availableLibraries;
                this.librarySelector.innerHTML = "";
                for (var i=0; i<this.availableLibraries.length; i++) {
                    var library = this.availableLibraries[i];
                    if ((!library.obsolete) || (library.obsolete && this.obsoleteCheckBox.checked)) {
                        var option = document.createElement( 'option' );
                        option.uid = library.uid;
                        option.value = library.name;
                        option.text = library.name;
                        option.obsolete = library.obsolete;
                        if (library.obsolete) {
                            option.style = "color:red";
                        }
                        option.description = library.description;
                        this.librarySelector.add(option);
                    }
                }
                readyFun();
            }.bind(this),
            function (response) {
                console.log(response);
            }
        );
    }

    /**
     * @brief Gets all the users that are available in the system and selected the libraryUser.
     * @param[in] libraryUser the user that is to be selected.
     */
    populateUsers(libraryUser) {
        if (this.userSelector.options.length === 0) {
            var allUsers = window.htkHelper.getAllUsers();
            for (var u in allUsers) {
                var option1 = document.createElement("option");
                var username = allUsers[u].username;
                option1.text = username;
                option1.value = username;
                this.userSelector.appendChild(option1);
            }
        }
        this.userSelector.value = libraryUser;
    }

    /**
     * @brief Opens the editor and displays the selected library (libraryValue of libraryUser).
     * @param[in] libraryUser the owner of the library.
     * @param[in] libraryValue the name of the library.
     */
    showEditor (libraryUser, libraryValue) {
        var user = window.htkHelper.getUser();
        this.deleteButton.disabled = (libraryUser !== user.username);
        this.obsoleteButton.disabled = (libraryUser !== user.username);

        HtkDialogs.showWaitDialog();
        this.populateUsers(libraryUser);
        this.populateLibraries(libraryUser, function() {
            this.librarySelector.value = libraryValue;
            this.editLibrary();
            HtkDialogs.closeWaitDialog();
            this.diag.showModal();
        }.bind(this));
    }

    /**
     * @brief Retrieves the library values for the library with name libraryName.
     * @param[in] libraryName the name of the library.
     * @param[in] successFn the function to be called when the libraries are available.
     */
    getLibrary(libraryName, successFn) {
        var libraryUID = this.getLibraryUID(libraryName);
        if (libraryUID !== undefined) {
            if (libraryName.length > 0) {
                window.htkHelper.getLibraryVariablesValues(
                    libraryUID,
                    successFn,
                    function (response) {
                        HtkDialogs.closeWaitDialog();
                        HtkDialogs.showErrorDialog("Failed to get library variables values. Unknown error, check the server logs.");
                    }
                );
            }
        }
    }

    /**
     * @brief Populates the editor components with the values that are stored for a given library instance and if required (valueOnly = false) also retrieve and set the plant and reference values.
     * @param[in] valueOnly if false, retrieve and set the plant and reference values.
     */
    editLibrary (valueOnly = false) {
        var editorComponents = this.iFrameEditor.contentDocument._frameComponents;
        if (editorComponents !== undefined) {
            if (!valueOnly) {
                var ownerReference = this.owner.getReference();
                var ownerReferenceValue = this.owner.getReferenceValue();
                var ownerInitialValue = this.owner.getInitialValue();
                var ownerPlantValue = this.owner.getPlantValue();
                if (ownerReference !== "none") {
                    if (ownerReferenceValue !== undefined) {
                        HtkDialogs.showWaitDialog();
                        this.getLibrary(ownerReferenceValue, function (variables) {
                            var keys = Object.keys(variables);
                            for (var i in keys) {
                                var variableName = keys[i];
                                var variableValue = variables[keys[i]];
                                var comps = editorComponents[variableName];
                                for (var c in comps) {
                                    comps[c].setReferenceValue(variableValue);
                                }
                            }
                            HtkDialogs.closeWaitDialog();
                        }.bind(this));
                    }
                }
                if (ownerInitialValue !== undefined) {
                    HtkDialogs.showWaitDialog();
                    this.getLibrary(ownerInitialValue, function (variables) {
                        var keys = Object.keys(variables);
                        for (var i in keys) {
                            var variableName = keys[i];
                            var variableValue = variables[keys[i]];
                            var comps = editorComponents[variableName];
                            for (var c in comps) {
                                comps[c].setInitialValue(variableValue);
                            }
                        }
                        HtkDialogs.closeWaitDialog();
                    }.bind(this));
                }
                if (ownerPlantValue !== undefined) {
                    HtkDialogs.showWaitDialog();
                    this.getLibrary(ownerPlantValue, function (variables) {
                        var keys = Object.keys(variables);
                        for (var i in keys) {
                            var variableName = keys[i];
                            var variableValue = variables[keys[i]];
                            var comps = editorComponents[variableName];
                            for (var c in comps) {
                                comps[c].setPlantValue(variableValue);
                            }
                        }
                        HtkDialogs.closeWaitDialog();
                    }.bind(this));
                }
            }
            if (this.librarySelector.selectedIndex >= 0) {
                HtkDialogs.showWaitDialog();
                var option = this.librarySelector.options[this.librarySelector.selectedIndex];
                var libraryName = option.text;
                this.getLibrary(libraryName, function (variables) {
                    var keys = Object.keys(variables);
                    for (var i in keys) {
                        var variableName = keys[i];
                        var variableValue = variables[keys[i]];
                        var comps = editorComponents[variableName];
                        for (var c in comps) {
                            comps[c].setValue(variableValue);
                        }
                    }
                    this.descriptionTextArea.value = option.description;
                    HtkDialogs.closeWaitDialog();
                }.bind(this));
            }
        }
    }

    /**
     * @brief See HtkComponents.connectedCallbace.
     */
    connectedCallback() {
        // Get template
        var templateContent = template.content;
        const root = this.attachShadow({mode: 'open'});
        root.appendChild(templateContent.cloneNode(true));

        this.availableLibraries = [];

        this.diag = this.shadowRoot.querySelector("#dselector");
        this.librarySelector = this.shadowRoot.querySelector("#lselect");
        this.userSelector = this.shadowRoot.querySelector("#uselect");
        this.okButton = this.shadowRoot.querySelector("#tselectorOK");
        var cancelButton = this.shadowRoot.querySelector("#tselectorCancel");
        this.saveButton = this.shadowRoot.querySelector("#saveButton");
        this.deleteButton = this.shadowRoot.querySelector("#deleteButton");
        this.obsoleteButton = this.shadowRoot.querySelector("#obsoleteButton");
        this.obsoleteCheckBox = this.shadowRoot.querySelector("#obsoleteCheckBox");
        this.descriptionTextArea = this.shadowRoot.querySelector("#descriptionTextArea");
        this.deleteButton.disabled = true;
        this.obsoleteButton.disabled = true;

        this.okButton.onclick = function() {
            var selectedUser = this.userSelector.options[this.userSelector.selectedIndex].text;
            var selectedLibrary = this.librarySelector.options[this.librarySelector.selectedIndex].text;
            this.owner.libraryChanged(selectedUser, selectedLibrary);
            this.diag.close();
        }.bind(this); //bind is needed to make sure that the "this" is still valid in the context of the callback

        this.deleteButton.onclick = function() {
            var libraryName = "";
            if (this.librarySelector.selectedIndex >= 0) {
                var option = this.librarySelector.options[this.librarySelector.selectedIndex];
                var libraryName = option.text;
                var ok = HtkDialogs.showConfirmDialog("Are you sure you want to delete the library " + libraryName + "?");
                if (ok) {
                    HtkDialogs.showWaitDialog();
                    var libraryUID = this.getLibraryUID(libraryName);
                    window.htkHelper.deleteLibrary(
                        libraryUID,
                        function () {
                            var user = window.htkHelper.getUser();
                            this.populateLibraries(user.username, function() {
                                if (this.availableLibraries.length > 0) {
                                    var selectedLibrary = this.availableLibraries[0].name;
                                    this.librarySelector.value = selectedLibrary;
                                }
                                this.editLibrary();
                                HtkDialogs.closeWaitDialog();
                            }.bind(this));
                        }.bind(this),
                        function (response) {
                            HtkDialogs.closeWaitDialog();
                        }
                    );
                }
            }
            else {
                HtkDialogs.showErrorDialog("Please select a library first");
            }
        }.bind(this);

        this.obsoleteCheckBox.onclick = function() {
            HtkDialogs.showWaitDialog();
            var user = window.htkHelper.getUser();
            this.populateLibraries(user.username, function() {
                if (this.availableLibraries.length > 0) {
                    var selectedLibrary = this.availableLibraries[0].name;
                    this.librarySelector.value = selectedLibrary;
                }
                this.editLibrary();
                HtkDialogs.closeWaitDialog();
            }.bind(this));
        }.bind(this);

        this.obsoleteButton.onclick = function() {
            var libraryName = "";
            if (this.librarySelector.selectedIndex >= 0) {
                var option = this.librarySelector.options[this.librarySelector.selectedIndex];
                var libraryName = option.text;
                var ok = HtkDialogs.showConfirmDialog("Are you sure you want to obsolete the library " + libraryName + "?");
                if (ok) {
                    HtkDialogs.showWaitDialog();
                    var libraryUID = this.getLibraryUID(libraryName);
                    window.htkHelper.obsoleteLibrary(
                        libraryUID,
                        function () {
                            var user = window.htkHelper.getUser();
                            this.populateLibraries(user.username, function() {
                                if (this.availableLibraries.length > 0) {
                                    var selectedLibrary = this.availableLibraries[0].name;
                                    this.librarySelector.value = selectedLibrary;
                                }
                                this.editLibrary();
                                HtkDialogs.closeWaitDialog();
                            }.bind(this));
                        }.bind(this),
                        function (response) {
                            HtkDialogs.closeWaitDialog();
                        }
                    );
                }
            }
            else {
                HtkDialogs.showErrorDialog("Please select a library first");
            }
        }.bind(this);


        cancelButton.onclick = function() {
            this.diag.close();
        }.bind(this); //bind is needed to make sure that the "this" is still valid in the context of the callback

        this.userSelector.onchange = function() {
            HtkDialogs.showWaitDialog();
            var selectedUser = this.userSelector.options[this.userSelector.selectedIndex].text;
            var user = window.htkHelper.getUser();
            this.deleteButton.disabled = (selectedUser !== user.username);
            this.obsoleteButton.disabled = (selectedUser !== user.username);
            this.populateLibraries(selectedUser, function() {
                if (this.availableLibraries.length > 0) {
                    var selectedLibrary = this.availableLibraries[0].name;
                    this.librarySelector.value = selectedLibrary;
                }
                this.editLibrary();
                HtkDialogs.closeWaitDialog();
            }.bind(this));
        }.bind(this);

        this.librarySelector.onchange = function() {
            this.editLibrary(true);
        }.bind(this);

        this.iFrameEditor = this.shadowRoot.querySelector("#iframeeditor");
        this.saveButton.onclick = function() {
            var editorComponents = this.iFrameEditor.contentDocument._frameComponents;
            var libraryName = "";
            if (this.librarySelector.selectedIndex >= 0) {
                var option = this.librarySelector.options[this.librarySelector.selectedIndex];
                libraryName = option.text;
            }
            var saveAsName = HtkDialogs.showInputDialog("Please insert the new library name:", libraryName);
            if (saveAsName !== null) {
                var description = this.descriptionTextArea.value;
                var variables = {};
                for (var key in editorComponents) {
                    var comps = editorComponents[key];
                    //The same id might be used in different components...
                    for (var c in comps) {
                        variables[comps[c].id] = comps[c].getValue();
                    }
                }
                HtkDialogs.showWaitDialog();
                window.htkHelper.saveLibrary(
                    this.owner.getLibraryType(),
                    saveAsName,
                    description,
                    variables,
                    function (library) {
                        if (library.uid !== undefined) {
                            var optionsAsArray = Array.apply(null, this.librarySelector.options).map(function(el){return el.text;});
                            if(optionsAsArray.indexOf(saveAsName) == -1) {
                                var option = document.createElement( 'option' );
                                option.uid = library.uid;
                                option.value = library.name;
                                option.text = library.name;
                                option.description = library.description;
                                this.librarySelector.add(option);
                                this.librarySelector.value = saveAsName;
                                this.availableLibraries.push(library);
                            }
                            alert("Library created successfully!");
                        }
                        HtkDialogs.closeWaitDialog();
                    }.bind(this),
                    function (response) {
                        HtkDialogs.closeWaitDialog();
                    }
                );
            }
        }.bind(this);
    }

    /**
     * @brief Sets the HtkLibrary component that is managing this editor.
     * @param[in] owner an HtkLibrary component.
     */
    setOwnerComponent(owner) {
        this.owner = owner;
        var libraryType = owner.getLibraryType();
        var editorUrl = "/pages/" + libraryType + ".html?" + new Date().getTime(); //new Date... to force reloading with no caching
        this.iFrameEditor.onload = function(evt) {
            this.iFrameLoaded(libraryType);
        }.bind(this);
        this.iFrameEditor.src = editorUrl;

    }

    /**
     * @brief Callback function which is called when the iframe that displays the library type has loaded.
     * @param[in] libraryType the type of the library.
     */
    iFrameLoaded(libraryType) {
        //Note that we want HtkComponents to the scope of each iframe
        var editorComponents = this.iFrameEditor.contentDocument._frameComponents;
        var allVariableIds = [];
        for (var k in editorComponents) {
            allVariableIds.push(k)
        }
        window.htkHelper.getLibraryVariablesInfo(
            libraryType,
            allVariableIds,
            function (variables) {
                var user = window.htkHelper.getUser();
                for (var i in variables) {
                    var variable = variables[i];
                    var targetElements = editorComponents[variable.name];
                    if (targetElements != null) {
                        for (var j in targetElements) {
                            targetElements[j].setVariable(variable);
                            targetElements[j].checkUserAllowedToWrite(user);
                        }
                    }
                }
            }.bind(this),
            function () {
                HtkDialogs.showErrorDialog("Failed to get library variables info. Unknown error, check the server logs.");
            }
        );
        for (var i=0; i<editorComponents.length; i++) {
            var htkCompArray = editorComponents[i];
            for (var j=0; j<htkCompArray.length; j++) {
                htkCompArray[j].domLoaded();
            }
        }
    }

    /**
     * @brief Enables/disables the button which allows to select a new library.
     * @param[in] isReadOnly see HtkComponents.setReadOnly
     */
    setReadOnly (isReadOnly) {
        this.okButton.disabled = isReadOnly;
    }

    /**
     * @brief Updates the reference on all the private iframe HtkComponents.
     * @param[in] referenceToSet the new reference against which to compare the components values.
     */
    setReference(referenceToSet) {
        var editorComponents = this.iFrameEditor.contentDocument._frameComponents;
        if (editorComponents !== undefined) {
            for (var i=0; i<editorComponents.length; i++) {
                var htkCompArray = editorComponents[i];
                for (var j=0; j<htkCompArray.length; j++) {
                    htkCompArray[j].setReference(referenceToSet);
                }
            }
        }
    }

    /**
     * @brief Enables/disables the button which allows to select a new library.
     * @param[in] isUserAllowedToWrite see HtkComponents.setUserAllowedToWrite
     */
    setUserAllowedToWrite (isUserAllowedToWrite) {
        this.okButton.disabled = !isUserAllowedToWrite;
    }
}

/**
 * @brief Registers the element.
 */
 window.customElements.define('htk-library-editor', HtkLibraryEditor);
