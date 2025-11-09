# Author: nexora-droid (Ashlesh Deshmukh)
# Year Created: 2025
# Created for MOONSHOT
# Hope you like it! Heres how to run it:
# Run pip3 install -r requirements.txt first
# Then go to terminal and run
# python main.py
import hashlib
import getpass
import pwinput
import time
import json
import sys
from importlib.resources import files
#import firebase_admin
#from firebase_admin import firestore, credentials
from datetime import datetime, timedelta

systemname = ""
active = True
USER_FILE = files("nasa_admin_cli").joinpath("users.json")
MISSION_FILE = files("nasa_admin_cli").joinpath("missions.json")
#cred = credentials.Certificate('firebasekey.json')
#firebase_admin.initialize_app(cred)
SIM_RATIO = 4

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def user_exists(username):
    try:
        with open(USER_FILE, "r") as f:
            users = load_users()
            return username in users
    except FileNotFoundError:
        return False

def check_password(username, password):
    hashed_password = hash_password(password)
    try:
        with open(USER_FILE, "r") as f:
            user = load_users()
        return user.get(username) == hashed_password
    except FileNotFoundError:
        return False

def add_user(username, password):
    hashed_password = hash_password(password)
    try:
        with open(USER_FILE, "r") as f:
            users = load_users()
    except FileNotFoundError:
        users = {}
    users[username] = hashed_password

    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)


def load():
    max_dots = 3
    dots = 0
    increasing = True
    wait = 0
    while True:
        print("\rInitializing System" + "." * dots + " " * (max_dots - dots), end="", flush=True)
        time.sleep(0.5)

        if increasing:
            dots += 1
            if dots == max_dots:
                increasing = False
            wait += 1
        else:
            dots = 0
            if dots == 0:
                increasing = True
            wait += 1
        if wait == 13:
            print("\nSystem Initialized")
            break

def loginsystem():
    while True:
        try:
            with open(USER_FILE, "r") as f:
                pass
        except FileNotFoundError:
            with open(USER_FILE, "w") as f:
                json.dump({}, f)
        while True:
            name = input("Login Username: ")
            if user_exists(name):
                try:
                    password = pwinput.pwinput(prompt="Login Password:")
                except Exception:
                    password = input("(visible to you only) ")
                if check_password(name, password):
                    print("Login Successful!")
                    global systemname
                    systemname = name
                    system()
                    break
                else:
                    print("Login Unsuccessful! Incorrect Password!")
            else:
                print("User does not exist, proceeding to account creation!")
                while True:
                    try:
                        password = pwinput.pwinput(prompt="Create a Password:")
                        confirm = pwinput.pwinput(prompt="Confirm Password:")
                    except Exception:
                        password = input("(visible to you only) ")
                        confirm = input("(visible to you only) ")
                    if password != confirm:
                        print("Passwords do not match! Try again!")
                    elif password == "":
                        print("Password cannot be empty! Try again!")
                    else:
                        add_user(name, password)
                        print("Account created successfully! You can now login!")
                        break

def create_mission(name, launch_date):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
    except FileNotFoundError:
        missions = {}

    missions[name] = {
        "name": name,
        "launch_date": launch_date,
        "created_on": datetime.now().isoformat(),
        "user": systemname,
        "launched": False
    }
    with open(MISSION_FILE, "w") as f:
        json.dump(missions, f, indent=4)

    print(f"\nMission Created Successfully! Predicted launch date{launch_date}")


def list_mission():
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
    except FileNotFoundError:
        print("No Missions Found!")
        return

    if not missions:
        print("No Missions Found!")
        return

    print("All missions:")
    for mission_name, missions in missions.items():
        print(f"- Mission: {mission_name} --> Predicted Launch Date: {missions['launch_date']}")

def launch_mission(mission_name):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
    except FileNotFoundError:
        print("No Missions Found!")

    if mission_name not in missions:
        print(f"Mission {mission_name} does not exist")
        return
    mission = missions[mission_name]
    if mission.get("launched", False):
        print(f"Mission {mission_name} already launched!")
        return

    mission["launched"] = True
    mission["start_time"] = datetime.now().isoformat()
    mission["progress"] = 0
    mission["fuel"] = 100

    missions[mission_name] = mission

    with open(MISSION_FILE, "w") as f:
        json.dump(missions, f, indent=4)

    print(f"Mission: {mission_name} launched!")

def check_progress(mission_name):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
            mission = missions.get(mission_name)
    except FileNotFoundError:
        print("No Missions Found!")
        return

    if missions.get("launched", False):
        print("Mission has not been launched yet!")
        return

    start_time = datetime.fromisoformat(mission['start_time'])
    elapsed_realminutes = (datetime.now() - start_time).total_seconds()/60
    flight_minutes = elapsed_realminutes * SIM_RATIO
    total_flighttime = 120
    progress = min((flight_minutes / total_flighttime)*100, 100)
    fuel = max(100 - progress, 0)
    mission["progress"] = progress
    mission["fuel"] = fuel

    if progress >= 100:
        mission["landed"] = True
        print(f"Mission {mission_name}\n"
              f"Progress: 100%\n"
              f"Fuel Remaining: 0%\n"
              f"Status: Landed!")
    else:
        print(f'Mission Info\n'
              f'Mission Name: {mission["name"]}\n'
              f'Progress: {progress:.2f}%\n'
              f'Fuel Remaining: {fuel:.2f}%\n')

    missions[mission_name] = mission
    with open(MISSION_FILE, "w") as f:
        json.dump(missions, f, indent=4)


def delete_mission(mission_name):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
            mission = missions.get(mission_name)
    except FileNotFoundError:
        print("Mission not found!")
    if mission_name not in missions:
        print(f"Mission {mission_name} does not exist")
        return
    del missions[mission_name]
    with open(MISSION_FILE, "w") as f:
        json.dump(missions, f, indent=4)
    print(f"Mission {mission_name} deleted!")


def summary(mission_name):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
    except FileNotFoundError:
        print("Mission not found!")
        return
    if mission_name not in missions:
        print(f"Mission {mission_name} does not exist")
        return
    mission = missions[mission_name]
    print(f"Mission: {mission_name} --> Launch Date: {mission['launch_date']} --> User: you! --> Launched: {mission['launched']}")
def update(mission_name, new_date):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
    except FileNotFoundError:
        print("Mission not found!")
        return
    if mission_name not in missions:
        print(f"Mission {mission_name} does not exist")
        return

    mission = missions[mission_name]
    mission["launch_date"] = new_date
    missions[mission_name] = mission
    with open(MISSION_FILE, "w") as f:
        json.dump(missions, f, indent=4)

def load_mission():
    try:
        with MISSION_FILE.open("r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
def load_users():
    try:
        with USER_FILE.open("r") as f:
            content = f.read().strip()
            if not content:
                return {}
            return json.loads(content)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}
def rename(mission_name, new_mission_name):
    try:
        with open(MISSION_FILE, "r") as f:
            missions = load_mission()
    except FileNotFoundError:
        print("Mission not found!")
        return
    if mission_name not in missions:
        print(f"Mission {mission_name} does not exist")
        return
    if new_mission_name in missions:
        print(f"Mission {new_mission_name} already exists!")
        return

    missions[new_mission_name] = missions.pop(mission_name)
    with open(MISSION_FILE, "w") as f:
        json.dump(missions, f, indent=4)
        print(f"Mission {new_mission_name} renamed to {mission_name}")

def system():
    isOn = True
    print("Welcome Admin! Type help to view list of available commands")
    while isOn:
        commandline = input(f"/system/NASA/admin/{systemname}/ $ ").strip().lower()
        if commandline == "help":
            print("\n\nAvailable Commands:\n"
                  "help:\n"
                  "\tlists all commands available\n"
                  "exit:\n"
                  "\tExits program, and logs out. Re-run to start again.\n"
                  "status\n"
                  "\tShows system health, and uptime\n"
                  "---------\n"
                  "create>\n"
                  "\tCreates a new mission\n"
                  "launch\n"
                  "\tLaunches mission (user-specific only)\n"
                  "list_missions\n"
                  "\tLists missions created by you!\n"
                  "progress\n"
                  "\tCheck progress of your mission\n"
                  "delete\n"
                  "\tDeletes or cancels mission\n"
                  "summary\n"
                  "\tSummarizes a given mission\n"
                  "update\n"
                  "\tUpdates predicated launch date\n"
                  "rename\n"
                  "\tUpdates mission name")
        if commandline == "exit":
            isOn = False
            sys.exit()
        elif commandline == "status":
            global active
            print(f"Active: {active}")
        elif commandline == "create":
            mission_name = input("Mission name: ")
            launch_date = input("Predicted Launch date: ")
            create_mission(mission_name, launch_date)
        elif commandline == "list_missions":
            list_mission()
        elif commandline== "launch":
            mission_name = input("Mission name: ")
            launch_mission(mission_name)
        elif commandline == "delete":
            mission_name = input("Mission name: ")
            delete_mission(mission_name)
        elif commandline == "update":
            mission_name = input("Mission name: ")
            new_date = input("New mission date: ")
            update(mission_name, new_date)
        elif commandline == "summary":
            mission_name = input("Mission name: ")
            summary(mission_name)
        elif commandline == "progress":
            mission_name = input("Mission name: ")
            check_progress(mission_name)
        elif commandline == "rename":
            mission_name = input("Mission name: ")
            newname = input("New mission name: ")
            rename(mission_name, newname)
def main():
    load()
    loginsystem()
if __name__ == "__main__":
    main()