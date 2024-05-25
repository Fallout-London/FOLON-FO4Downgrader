def WhereSteam():
	from pathlib import Path
	home = str(Path.home())

	SteamLocations = []

	if os.path.isdir("C:/Program Files/Steam/steamapps/"):
		print("32 bit install")
		steamfounds += 1
		SteamLocations.append("C:/Program Files/Steam/steamapps/")
	elif os.path.isdir("C:/Program Files (x86)/Steam/steamapps/"):
		print("64 bit install")
		steamfounds += 1
		SteamLocations.append("C:/Program Files (x86)/Steam/steamapps/")
	elif os.path.isdir(f"{home}/.var/app/com.valvesoftware.Steam"):
		print("Flatpak install")
		steamfounds += 1
		SteamLocations.append(f"{home}/.var/app/com.valvesoftware.Steam")
	elif os.path.isdir(f"{home}/.steam"):
		print("Local install")
		steamfounds += 1
		SteamLocations.append(f"{home}/.steam")

	if steamfounds == 0:
		return false
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

	if not os.path.isdir(".FOLON-Installer-Files"):
		os.mkdir(".FOLON-Installer-Files")
	with open(".FOLON-Installer-Files/Settings.json", "w") as f:
		json.dump(settings, f)


def Read_Settings():
	import json

	# Read Settings
	try:
		f = open(".FOLON-Installer-Files/Settings.json")

		# returns JSON object as
		# a dictionary
		settings = json.load(f)

		# Closing file
		f.close()
	except:
		settings = {"Username": ""}

	return settings