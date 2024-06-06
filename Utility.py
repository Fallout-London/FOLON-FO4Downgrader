def init():
    global Loading
    Loading = False


def IsWritable(path):
    import os

    try:
        f = open(path + "/FOLON-Downgrader-TestFile", "w")
        f.write("Testing...")
        f.close()
        f = open(path + "/FOLON-Downgrader-TestFile", "r")
        f.read()
        f.close()
        os.remove(path + "/FOLON-Downgrader-TestFile")
        return True
    except:
        return False


def WhereSteam():
    import os
    from pathlib import Path

    home = str(Path.home())

    SteamLocations = []
    steamfounds = 0

    if os.path.isdir("C:/Program Files/Steam/steamapps/common"):
        steamfounds += 1
        SteamLocations.append("C:/Program Files/Steam/steamapps/common")
    if os.path.isdir("C:/Program Files (x86)/Steam/steamapps/common"):
        steamfounds += 1
        SteamLocations.append("C:/Program Files (x86)/Steam/steamapps/common")
    if os.path.isdir(
        f"{home}/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common"
    ):
        steamfounds += 1
        SteamLocations.append(
            f"{home}/.var/app/com.valvesoftware.Steam/.local/share/Steam/steamapps/common"
        )
    if os.path.isdir(f"{home}/.steam/steam/steamapps/common"):
        steamfounds += 1
        SteamLocations.append(f"{home}/.steam/steam/steamapps/common")

    if steamfounds == 0:
        return False
    else:
        return SteamLocations


def resource_path(relative_path):
    import sys
    import os

    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    if IsWindows():
        return os.path.join(base_path, relative_path).replace("/", "\\")
    else:
        return os.path.join(base_path, relative_path)


def IsBundled():
    import sys

    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return True
    else:
        return False


def IsWindows():
    import sys

    if hasattr(sys, "getwindowsversion"):
        return True
    else:
        return False


def CountFiles(Directory):
    import os

    try:
        Directory = str(Directory)
        if os.path.isdir(Directory):
            file_count = sum(len(files) for _, _, files in os.walk(Directory))
            return file_count
        else:
            return False
    except:
        return False


def Write_Settings(settings):
    import json
    import os

    if not os.path.isdir("FOLON-Downgrader-Files"):
        os.mkdir("FOLON-Downgrader-Files")

    with open("FOLON-Downgrader-Files/Settings.json", "w") as f:
        json.dump(settings, f)

    f = open("FOLON-Downgrader-Files/Settings.json")
    LocalSettings = json.load(f)
    f.close()
    if settings != LocalSettings:
        raise Exception("SETTINGS WRONG")


def Read_Settings():
    import json

    # Read Settings
    try:
        f = open("FOLON-Downgrader-Files/Settings.json")

        # returns JSON object as
        # a dictionary
        settings = json.load(f)

        # Closing file
        f.close()
    except:
        settings = {
            "Username": "",
            "LoginResult": "",
            "Steps": 4,
            "SteamPath": "",
        }

    return settings


def CleanUp(Path):
    import shutil
    from time import sleep

    sleep(10)
    shutil.rmtree("FOLON-Downgrader-Files")
    try:
        shutil.rmtree(Path + "/.DepotDownloader")
    except:
        pass
    try:
        shutil.rmtree("__pycache__")
    except:
        pass
    BlockUpdates()


def BlockUpdates():
    for i in WhereSteam():
        try:
            FilePath = i.replace("/common", "/appmanifest_377160.acf")
            print(FilePath)
            os.chmod(FilePath, stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
        except:
            pass


if __name__ == "__main__":
    print(WhereSteam())
    print(CountFiles("."))
    print(resource_path("."))
    from os import listdir, walk

    print(listdir(resource_path(".")))
    print(IsBundled())
    print(IsWindows())
