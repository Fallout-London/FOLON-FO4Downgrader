def init():
    global LoginResult
    global Loading
    InstallSteps = 2
    Loading = False


def WhereSteam():
    import os
    from pathlib import Path

    home = str(Path.home())

    SteamLocations = []
    steamfounds = 0

    if os.path.isdir("C:/Program Files/Steam/"):
        print("32 bit install")
        steamfounds += 1
        SteamLocations.append("C:/Program Files/Steam/")
    if os.path.isdir("C:/Program Files (x86)/Steam/steamapps/"):
        print("64 bit install")
        steamfounds += 1
        SteamLocations.append("C:/Program Files (x86)/Steam/")
    if os.path.isdir(f"{home}/.var/app/com.valvesoftware.Steam/.local/share/Steam"):
        print("Flatpak install")
        steamfounds += 1
        SteamLocations.append(
            f"{home}/.var/app/com.valvesoftware.Steam/.local/share/Steam"
        )
    if os.path.isdir(f"{home}/.steam/steam"):
        print("Local install")
        steamfounds += 1
        SteamLocations.append(f"{home}/.steam/steam")

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
        settings = {"Username": "", "LoginResult": ""}

    return settings


if __name__ == "__main__":
    print(WhereSteam())
    print(CountFiles("."))
    print(resource_path("."))
    from os import listdir

    print(listdir(resource_path(".")))
    print(IsBundled())
    print(IsWindows())
