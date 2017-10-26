import json
#Manage an easier integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle

def importVariable(variableJSon, db, idx):
    isLibrary = (variableJSon["isLibrary"] == "true")
    isLivePV = (variableJSon["isLiveVariable"] == "true")
    isStruct = (variableJSon["isStruct"] == "true")
    variable = {
        "id": variableJSon["name"],
        "type": variableJSon["type"],
        "description": variableJSon["description"],
        "value": pickle.dumps(variableJSon["value"]),
        "numberOfElements": pickle.dumps(variableJSon["numberOfElements"]),
        "library": isLibrary,
        "liveVariable": isLivePV,
        "isStruct": isStruct 
    }
    if (isStruct):
        variable["id"] = variable["id"] + "@" + str(idx)

        

def importVariables(jsonFileName, db):
    with open(jsonFileName) as jsonFile:
        plantVariablesDBJSon = json.load(jsonFile)
        variablesJSon = plantVariablesDBJSon["variables"]
        for variableJSon in variablesJSon:
            isLibrary = (variableJSon["isLibrary"] == "true")
            isLivePV = (variableJSon["isLiveVariable"] == "true")
            isStruct = (variableJSon["isStruct"] == "true")
            variable = {
                "id": variableJSon["name"],
                "type": variableJSon["type"],
                "description": variableJSon["description"],
                "value": pickle.dumps(variableJSon["value"]),
                "numberOfElements": pickle.dumps(variableJSon["numberOfElements"]),
                "library": isLibrary,
                "liveVariable": isLivePV,
                "isStruct": isStruct 
            }
            variables.upsert(variable, ["id"])
            if "validation" in variableJSon:
                validationsJSon = variableJSon["validation"]
                for validationJSon in validationsJSon:
                    validation = {
                        "fun": validationJSon["fun"],
                        "variable_id": variableJSon["name"],
                        "description": validationJSon["description"],
                        "parameters": pickle.dumps(validationJSon["parameters"])  
                    }
                    validations.upsert(validation, ["fun", "variable_id"])
            permission = {
                "variable_id": variableJSon["name"],
                "group_id": "experts-1"
            }
            permissions.upsert(permission, ["variable_id", "group_id"])


if __name__ == "__main__":
    db = dataset.connect('sqlite:////tmp/pmc-server.db')
    importPlantVariables("plant-variables.json", db)

