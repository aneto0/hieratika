import json
#Manage an easier integration with SQLAlchemy
import dataset
#To serialize arrays into the database
import pickle

db = dataset.connect('sqlite:////tmp/pmc-server.db')

#Create all the tables
plants = db["plants"]
if not plants.exists:
    db.query("CREATE TABLE plants(id TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT)")

    db.query("CREATE TABLE plant_variables(id TEXT, plant_id TEXT, type TEXT, description TEXT, initialValue TEXT, numberOfElements TEXT, library BOOLEAN, epicsPV BOOLEAN, PRIMARY KEY(id, plant_id), FOREIGN KEY (plant_id) REFERENCES plants(id))")

    db.query("CREATE INDEX id_plant_id ON plant_variables(id,plant_id)")

    db.query("CREATE TABLE validations(fun TEXT, variable_id TEXT, plant_id TEXT, description TEXT, parameters TEXT, PRIMARY KEY(fun, variable_id, plant_id), FOREIGN KEY (variable_id, plant_id) REFERENCES plant_variables(id, plant_id))")

    db.query("CREATE TABLE users (id TEXT, name TEXT, password TEXT, PRIMARY KEY (id))")

    db.query("CREATE TABLE groups (id TEXT, name TEXT, PRIMARY KEY (id))")

    db.query("CREATE TABLE group_members(group_id, user_id, PRIMARY KEY (group_id, user_id), FOREIGN KEY (group_id) REFERENCES groups(id), FOREIGN KEY (user_id) REFERENCES users(id))")

    db.query("CREATE TABLE schedules (id TEXT, user_id TEXT, name TEXT, description TEXT, PRIMARY KEY (id, user_id), FOREIGN KEY (user_id) REFERENCES users(id))")

    db.query("CREATE TABLE schedule_variables (variable_id TEXT, plant_id TEXT, schedule_id TEXT, user_id TEXT, value TEXT, PRIMARY KEY (variable_id, plant_id, schedule_id, user_id), FOREIGN KEY (variable_id, plant_id) REFERENCES plant_variables(id, plant_id), FOREIGN KEY (schedule_id, user_id) REFERENCES schedules(id, user_id))");

    db.query("CREATE INDEX schedule_id_user_id ON schedule_variables(user_id,schedule_id)")

    db.query("CREATE TABLE libraries (id TEXT, plant_id TEXT, variable_id TEXT, user_id TEXT, value TEXT, description TEXT, PRIMARY KEY (id, plant_id, variable_id, user_id), FOREIGN KEY (variable_id, plant_id) REFERENCES plant_variables(id, plant_id), FOREIGN KEY (user_id) REFERENCES users(id))");


plants = db["plants"]
plantVariables = db["plant_variables"]
validations = db["validations"]
schedules = db["schedules"]
scheduleVariables = db["schedule_variables"]
users = db["users"]
groups = db["groups"]
groupMembers = db["group_members"]
libraries = db["libraries"]

with open("plant-variables.json") as jsonFile:
    plantVariablesDBJSon = json.load(jsonFile)
    for plantJSon in plantVariablesDBJSon["plants"]:
        plant = {
            "id": plantJSon["id"],
            "name": plantJSon["id"],
            "description": ""
        }
        plants.upsert(plant, ["id"])

        variablesJSon = plantJSon["variables"]
        for variableJSon in variablesJSon:
            isLibrary = (variableJSon["library"] == "true")
            isEpicsPV = (variableJSon["epicsPV"] == "true")
            variable = {
                "id": variableJSon["name"],
                "plant_id": plantJSon["id"],
                "type": variableJSon["type"],
                "description": "",
                "initialValue": pickle.dumps(variableJSon["initialValue"]),
                "numberOfElements": pickle.dumps(variableJSon["numberOfElements"]),
                "library": isLibrary,
                "epicsPV": isEpicsPV 
            }
            plantVariables.upsert(variable, ["id", "plant_id"])

            if "validation" in variableJSon:
                validationsJSon = variableJSon["validation"]
                for validationJSon in validationsJSon:
                    validation = {
                        "fun": validationJSon["fun"],
                        "variable_id": variableJSon["name"],
                        "plant_id": plantJSon["id"],
                        "description": validationJSon["description"],
                        "parameters": pickle.dumps(validationJSon["parameters"])  
                    }
                    validations.upsert(validation, ["fun", "variable_id", "plant_id"])


user = {
    "id": "codac-dev-1",
    "name": "Developer"
}
users.upsert(user, ["id"])

group = {
    "id": "experts-1",
    "name": "Experts of type 1"
}
groups.upsert(group, ["id"])

groupMember = {
    "group_id": "experts-1",
    "user_id": "codac-dev-1"
}
groupMembers.upsert(groupMember, ["group_id", "user_id"])

with open("schedules.json") as jsonFile:
    schedulesDBJSon = json.load(jsonFile)
    schedulesJSon = schedulesDBJSon["schedules"]
    for scheduleJSon in schedulesJSon:
        schedule = {
            "id": scheduleJSon["name"],
            "user_id": scheduleJSon["owner"],
            "name": scheduleJSon["name"],
            "description": scheduleJSon["description"]
        }
        schedules.upsert(schedule, ["id", "user_id"])
        variablesJSon = scheduleJSon["variables"]
        for variableJSon in variablesJSon:
            variable = {
                "variable_id": variableJSon["name"],
                "plant_id": variableJSon["plant"],
                "schedule_id": scheduleJSon["name"],
                "user_id": scheduleJSon["owner"],
                "value": pickle.dumps(variableJSon["value"])
            }
            scheduleVariables.upsert(variable, ["variable_id", "plant_id", "schedule_id", "user_id"])

with open("libraries.json") as jsonFile:
    librariesDBJSon = json.load(jsonFile)
    librariesJSon = librariesDBJSon["libraries"]
    for libraryJSon in librariesJSon:
        variablesLibJSon = libraryJSon["libraries"]
        for variableLibJSon in variablesLibJSon:
            library = {
                "id": variableLibJSon["name"], 
                "plant_id": libraryJSon["plant"], 
                "variable_id": libraryJSon["variable"], 
                "user_id": variableLibJSon["owner"],
                "description": variableLibJSon["description"],
                "value": pickle.dumps(variableLibJSon["values"])
            }
            libraries.upsert(library, ["id", "plant_id", "variable_id", "user_id"])

