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
		SteamLocations.append(f"{home}/.var/app/com.valvesoftware.Steam/.local/share/Steam")
	if os.path.isdir(f"{home}/.steam/steam"):
		print("Local install")
		steamfounds += 1
		SteamLocations.append(f"{home}/.steam/steam")

	if steamfounds == 0:
		return False
	else:
		return SteamLocations


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


def Write_Settings(settings):
	import json
	import os

	if not os.path.isdir(".FOLON-Downgrader-Files"):
		os.mkdir(".FOLON-Downgrader-Files")
	with open(".FOLON-Downgrader-Files/Settings.json", "w") as f:
		json.dump(settings, f)


def Read_Settings():
	import json

	# Read Settings
	try:
		f = open(".FOLON-Downgrader-Files/Settings.json")

		# returns JSON object as
		# a dictionary
		settings = json.load(f)

		# Closing file
		f.close()
	except:
		settings = {"Username": ""}

	return settings

def check_event(event, callback):
    print('.', end='')
    if event.is_set():
        # thread task is completed
        callback()
    else:
        # check again 100 ms (adjust this to suit your case) later
        root.after(100, check_event, event, callback)

if __name__ == "__main__":
	print(WhereSteam())
	print(IsBundled())
	print(IsWindows())