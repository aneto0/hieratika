import json
#Manage an easier integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle

db = dataset.connect('sqlite:////tmp/pmc-server.db')

#Create all the tables
users = db["users"]
if not users.exists:
    db.query("CREATE TABLE users (id TEXT, name TEXT, password TEXT, PRIMARY KEY (id))")

    db.query("CREATE TABLE groups (id TEXT, name TEXT, PRIMARY KEY (id))")
    
    db.query("CREATE TABLE pages (id TEXT, name TEXT, description TEXT, PRIMARY KEY (id))")

    db.query("CREATE TABLE variables(id TEXT, type TEXT, description TEXT, initialValue TEXT, numberOfElements TEXT, library BOOLEAN, epicsPV BOOLEAN, value TEXT, PRIMARY KEY(id))")

    db.query("CREATE TABLE permissions(variable_id TEXT, group_id TEXT NOT NULL, PRIMARY KEY(variable_id, group_id), FOREIGN KEY (variable_id) REFERENCES variables(id), FOREIGN KEY(group_id) REFERENCES groups(id))")

    db.query("CREATE TABLE validations(fun TEXT, variable_id TEXT, description TEXT, parameters TEXT, PRIMARY KEY(fun, variable_id), FOREIGN KEY (variable_id) REFERENCES variables(id))")

    db.query("CREATE TABLE group_members(group_id, user_id, PRIMARY KEY (group_id, user_id), FOREIGN KEY (group_id) REFERENCES groups(id), FOREIGN KEY (user_id) REFERENCES users(id))")

    db.query("CREATE TABLE schedules (id TEXT, user_id TEXT, name TEXT, description TEXT, page_id TEXT, PRIMARY KEY (id, user_id), FOREIGN KEY (user_id) REFERENCES users(id), FOREIGN KEY (page_id) REFERENCES pages(id))")

    db.query("CREATE TABLE schedule_variables (variable_id TEXT, schedule_id TEXT, user_id TEXT, value TEXT, PRIMARY KEY (variable_id, schedule_id, user_id), FOREIGN KEY (variable_id) REFERENCES variables(id), FOREIGN KEY (schedule_id, user_id) REFERENCES schedules(id, user_id))");

    db.query("CREATE INDEX schedule_id_user_id ON schedule_variables(user_id,schedule_id)")

    db.query("CREATE TABLE libraries (id TEXT, variable_id TEXT, user_id TEXT, value TEXT, description TEXT, PRIMARY KEY (id, variable_id, user_id), FOREIGN KEY (variable_id) REFERENCES variables(id), FOREIGN KEY (user_id) REFERENCES users(id))");

    db.query("CREATE TABLE logins (token_id TEXT, user_id TEXT, last_interaction_time INTEGER, PRIMARY KEY (token_id), FOREIGN KEY (user_id) REFERENCES users(user_id))")

variables = db["variables"]
validations = db["validations"]
permissions = db["permissions"]
schedules = db["schedules"]
pages = db["pages"]
scheduleVariables = db["schedule_variables"]
groups = db["groups"]
groupMembers = db["group_members"]
libraries = db["libraries"]

with open("plant-variables.json") as jsonFile:
    plantVariablesDBJSon = json.load(jsonFile)
    for plantJSon in plantVariablesDBJSon["plants"]:
        variablesJSon = plantJSon["variables"]
        for variableJSon in variablesJSon:
            isLibrary = (variableJSon["library"] == "true")
            isEpicsPV = (variableJSon["epicsPV"] == "true")
            variable = {
                "id": variableJSon["name"],
                "type": variableJSon["type"],
                "description": "",
                "initialValue": pickle.dumps(variableJSon["initialValue"]),
                "numberOfElements": pickle.dumps(variableJSon["numberOfElements"]),
                "library": isLibrary,
                "epicsPV": isEpicsPV 
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


user = {
    "id": "codac-dev-1",
    "name": "Developer"
}
users.upsert(user, ["id"])

user = {
    "id": "codac-dev-2",
    "name": "Developer"
}
users.upsert(user, ["id"])

group = {
    "id": "experts-1",
    "name": "Experts of type 1"
}
groups.upsert(group, ["id"])

group = {
    "id": "experts-2",
    "name": "Experts of type 2"
}
groups.upsert(group, ["id"])

groupMember = {
    "group_id": "experts-1",
    "user_id": "codac-dev-1"
}
groupMembers.upsert(groupMember, ["group_id", "user_id"])
groupMember = {
    "group_id": "experts-2",
    "user_id": "codac-dev-2"
}
groupMembers.upsert(groupMember, ["group_id", "user_id"])

page = {
    "id": "ps-example-1",
    "name": "ps-example-1",
    "description": "One example of a page"
}
pages.upsert(page, ["id"])

page = {
    "id": "ps-example-2",
    "name": "ps-example-2",
    "description": "Another example of a page"
}
pages.upsert(page, ["id"])


with open("schedules.json") as jsonFile:
    schedulesDBJSon = json.load(jsonFile)
    schedulesJSon = schedulesDBJSon["schedules"]
    for scheduleJSon in schedulesJSon:
        schedule = {
            "id": scheduleJSon["name"],
            "user_id": scheduleJSon["owner"],
            "name": scheduleJSon["name"],
            "description": scheduleJSon["description"],
            "page_id": "ps-example-1"
        }
        schedules.upsert(schedule, ["id", "user_id"])
        variablesJSon = scheduleJSon["variables"]
        for variableJSon in variablesJSon:
            variable = {
                "variable_id": variableJSon["name"],
                "schedule_id": scheduleJSon["name"],
                "user_id": scheduleJSon["owner"],
                "value": pickle.dumps(variableJSon["value"])
            }
            scheduleVariables.upsert(variable, ["variable_id", "schedule_id", "user_id"])

with open("libraries.json") as jsonFile:
    librariesDBJSon = json.load(jsonFile)
    librariesJSon = librariesDBJSon["libraries"]
    for libraryJSon in librariesJSon:
        variablesLibJSon = libraryJSon["libraries"]
        for variableLibJSon in variablesLibJSon:
            library = {
                "id": variableLibJSon["name"], 
                "variable_id": libraryJSon["variable"], 
                "user_id": variableLibJSon["owner"],
                "description": variableLibJSon["description"],
                "value": pickle.dumps(variableLibJSon["values"])
            }
            libraries.upsert(library, ["id", "variable_id", "user_id"])

nCols = 10
idx = 1
maxIdx = 1000
maxIdxHTML = 500
sourceVarId = "PLANT1::VAR1"
destPlantId = "PLANT2"
newScheduleName = "schedule-3"
newSchedulePage = "ps-example-2"
newScheduleOwner = "codac-dev-2"

db.begin()
schedule = {
    "id": newScheduleName,
    "user_id": newScheduleOwner,
    "name": newScheduleName,
    "description": "...",
    "page_id": "ps-example-2"
}
schedules.upsert(schedule, ["id", "user_id"])

while (idx < maxIdx):
    varId = "VAR" + str(idx)
    varName = destPlantId + "::" + varId
    db.query("INSERT INTO variables(id, type, description, initialValue, numberOfElements, library, epicsPV, value) SELECT '" + varName + "', variables.type, variables.description, variables.initialValue, variables.numberOfElements, variables.library, 0, variables.value FROM variables WHERE variables.id='" + sourceVarId + "'")
    db.query("INSERT INTO validations(fun, variable_id, description, parameters) SELECT validations.fun, '" + varName + "', validations.description, validations.parameters FROM validations WHERE validations.variable_id='" + sourceVarId + "'")
    
    db.query("INSERT INTO permissions(variable_id, group_id) VALUES('" + varName + "','experts-2')")
    idx = idx + 1

    variable = {
        "variable_id": varName,
        "schedule_id": newScheduleName,
        "user_id": newScheduleOwner,
        "value": pickle.dumps(str(idx % 10))
    }
    scheduleVariables.upsert(variable, ["variable_id", "schedule_id", "user_id"])

db.commit()

validation = validations.find_one(variable_id="PLANT2::VAR1", fun="checkMax")
validation["parameters"] = pickle.dumps("allPMCComponents[\"PLANT1::VAR1\"].getPlantValue()")
validations.upsert(validation, ["variable_id", "fun"])

with open("static/ps-example-2.html", "w") as f:
    f.write("<table border=\"0\">\n<tr><td><pmc-input id=\"PLANT1::VAR1\" name=\"PLANT1::VAR1\"></pmc-input></td></tr><tr>\n") 
    idx = 1
    while (idx < maxIdxHTML):
        if (idx % nCols == 0):
            if (idx > 0):
                f.write("\n</tr>\n") 
            f.write("<tr>\n") 

        varName = destPlantId + "::" + "VAR" + str(idx)
        f.write("<td>" + varName + "</td>")
        f.write("<td><pmc-input id=\"" + varName + "\" name=\"" + varName + "\"></pmc-input></td>")
        idx = idx + 1
    f.write("</table>\n") 

