import hashlib
import os
import sys
import json

DepotFileList = {
    "337161": [
        "Data/Fallout4 - Meshes.ba2",
        "Data/Fallout4 - Sounds.ba2",
        "Data/Video/AGILITY.bk2",
        "Data/Video/CHARISMA.bk2",
        "Data/Video/ENDURANCE.bk2",
        "Data/Video/GameIntro_V3_B.bk2",
        "Data/Video/INTELLIGENCE.bk2",
        "Data/Video/LUCK.bk2",
        "Data/Video/MainMenuLoop.bk2",
        "Data/Video/PERCEPTION.bk2",
        "Data/Video/STRENGTH.bk2",
        "installscript.vdf",
    ],
    "337162": [
        "Fallout4.exe",
    ],
    "337163": [
        "bink2w64.dll",
        "cudart64_75.dll",
        "Data/Fallout4 - Animations.ba2",
        "Data/Fallout4 - Geometry.csg",
        "Data/Fallout4 - Interface.ba2",
        "Data/Fallout4 - Materials.ba2",
        "Data/Fallout4 - Meshes.ba2",
        "Data/Fallout4 - MeshesExtra.ba2",
        "Data/Fallout4 - Misc.ba2",
        "Data/Fallout4 - Nvflex.ba2",
        "Data/Fallout4 - Shaders.ba2",
        "Data/Fallout4 - Startup.ba2",
        "Data/Fallout4 - Textures1.ba2",
        "Data/Fallout4 - Textures2.ba2",
        "Data/Fallout4 - Textures3.ba2",
        "Data/Fallout4 - Textures4.ba2",
        "Data/Fallout4 - Textures5.ba2",
        "Data/Fallout4 - Textures6.ba2",
        "Data/Fallout4 - Textures7.ba2",
        "Data/Fallout4 - Textures8.ba2",
        "Data/Fallout4 - Textures9.ba2",
        "Data/Fallout4.cdx",
        "Data/Fallout4.esm",
        "Fallout4.ccc",
        "Fallout4/Fallout4Prefs.ini",
        "Fallout4IDs.ccc",
        "Fallout4Launcher.exe",
        "flexExtRelease_x64.dll",
        "flexRelease_x64.dll",
        "GFSDK_GodraysLib.x64.dll",
        "GFSDK_SSAO_D3D11.win64.dll",
        "High.ini",
        "Low.ini",
        "Medium.ini",
        "msvcp110.dll",
        "msvcr110.dll",
        "nvdebris.txt",
        "nvToolsExt64_1.dll",
        "steam_api64.dll",
        "Ultra.ini",
    ],
    "377164": [
        "Data/Fallout4 - Voices.ba2",
        "Data/Video/Endgame_FEMALE_A.bk2",
        "Data/Video/Endgame_FEMALE_B.bk2",
        "Data/Video/Endgame_MALE_A.bk2",
        "Data/Video/Endgame_MALE_B.bk2",
        "Data/Video/Intro.bk2",
        "Fallout4_Default.ini",
    ],
    "435870": [
        "Data/DLCRobot - Geometry.csg",
        "Data/DLCRobot - Main.ba2",
        "Data/DLCRobot - Textures.ba2",
        "Data/DLCRobot.cdx",
    ],
    "435871": [
        "Data/DLCRobot - Voices_en.ba2",
        "Data/DLCRobot.esm",
    ],
    "435880": [
        "Data/DLCworkshop01 - Geometry.csg",
        "Data/DLCworkshop01 - Main.ba2",
        "Data/DLCworkshop01 - Textures.ba2",
        "Data/DLCworkshop01.cdx",
        "Data/DLCworkshop01.esm",
    ],
    "435882": [
        "Data/DLCCoast - Voices_en.ba2",
        "Data/DLCCoast.esm",
    ],
    "480630": [
        "Data/DLCworkshop02 - Main.ba2",
        "Data/DLCworkshop02 - Textures.ba2",
        "Data/DLCworkshop02.esm",
    ],
    "480631": [
        "Data/DLCworkshop03 - Geometry.csg",
        "Data/DLCworkshop03 - Main.ba2",
        "Data/DLCworkshop03 - Textures.ba2",
        "Data/DLCworkshop03.cdx",
    ],
    "393885": [
        "Data/DLCworkshop03 - Voices_en.ba2",
        "Data/DLCworkshop03.esm",
    ],
    "393895": [
        "Data/DLCNukaWorld - Voices_en.ba2",
        "Data/DLCNukaWorld.esm",
    ],
    "435881": [
        "Data/DLCCoast - Geometry.csg",
        "Data/DLCCoast - Main.ba2",
        "Data/DLCCoast - Textures.ba2",
        "Data/DLCCoast.cdx",
    ],
    "490650": [
        "Data/DLCNukaWorld - Geometry.csg",
        "Data/DLCNukaWorld - Main.ba2",
        "Data/DLCNukaWorld - Textures.ba2",
        "Data/DLCNukaWorld.cdx",
    ],
}


def GetDepotName(path):
    if path[:9] == "Fallout4/":
        path = path[9:]
    global DepotFileList
    for a in DepotFileList:
        for b in DepotFileList[a]:
            if path == b:
                return a


def list_files_walk(start_path="."):
    FileArray = []
    for root, dirs, files in os.walk(start_path):
        for file in files:
            FileArray.append(os.path.join(root, file).replace("\\", "/"))

    return FileArray


if len(sys.argv) < 2:
    sys.exit("Usage: %s folder" % sys.argv[0])

if not os.path.exists(sys.argv[1]):
    sys.exit('ERROR: Folder "%s" was not found!' % sys.argv[1])

path = sys.argv[1].replace("\\", "/").replace("./", "")

data = {}
data["FilePairs"] = []
DataArray = []

for i in list_files_walk(path):
    with open(i, "rb") as f:
        md5 = hashlib.md5()

        while True:
            chunk = f.read(16 * 1024)
            if not chunk:
                break
            md5.update(chunk)

        data["FilePairs"].append([i, md5.hexdigest(), GetDepotName(i)])
        with open("Checksums.json", "w") as OutputFile:
            OutputFile.writelines("")
            json.dump(data, OutputFile)

        print(i + " MD5: " + md5.hexdigest() + " In depot " + GetDepotName(i))


try:
    input("Press enter to terminate the program")
except:
    pass
