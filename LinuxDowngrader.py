import sys
from getpass import getpass
import Utility as Util
import shutil
import os
import stat
import argparse
import subprocess
import urllib.request, zipfile, io, tarfile


def Linux(
    Path: str = "",
    Username: str = "",
    Password: str = "",
    SteamAuth: bool = False,
    SteamInstalled: bool = False,
):
    global open
    if Path == "":
        Path = input("What is the path to Fallout4?: ")
        if not os.path.isdir(Path):
            print("Please input a path")
            Linux()
        elif Path == "":
            print("Please input a path")
            Linux()
        elif not "Fallout4.exe" in os.listdir(Path):
            print("Fallout4.exe not in folder")
            Linux()

    if os.path.isdir(f"{Path}/SteamFiles"):
        shutil.rmtree(f"{Path}/SteamFiles")

    print("Downloading steam...")
    os.mkdir(f"{Path}/SteamFiles")

    url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"

    if os.path.isfile(f"{Path}/SteamFiles/steamcmd.sh"):
        st = os.stat(f"{Path}/SteamFiles/steamcmd.sh")
        os.chmod(
            f"{Path}/SteamFiles/steamcmd.sh",
            st.st_mode | stat.S_IEXEC,
        )
        st = os.stat(f"{Path}/SteamFiles/linux32/steamcmd")
        os.chmod(
            f"{Path}/SteamFiles/linux32/steamcmd",
            st.st_mode | stat.S_IEXEC,
        )
        LibArray = [
            "libdl.so.2",
            "librt.so.1",
            "libm.so.6",
            "libpthread.so.0",
            "libc.so.6",
            "/lib/ld-linux.so.2",
        ]

        result = subprocess.run(["ldconfig", "-p"], capture_output=True, text=True)

        for i in LibArray:
            if i in result.stdout:
                print(i, i in result.stdout)
            else:
                raise Exception(f"Missing {i}, please just google it.")

    with urllib.request.urlopen(url) as dl_file:
        with open(f"{Path}/SteamFiles/steamcmd_linux.tar.gz", "wb") as out_file:
            out_file.write(dl_file.read())

    with tarfile.open(f"{Path}/SteamFiles/steamcmd_linux.tar.gz", "r") as tar:
        tar.extractall(f"{Path}/SteamFiles/")
    os.remove(f"{Path}/SteamFiles/steamcmd_linux.tar.gz")
    print("Downloaded Steam!")

    if Username == "":
        print(
            'If " or \\ is in either your username or password preface it with another \\'
        )
        Username = input("What is your Steam Username?: ")
        if Username == "":
            Linux(Path=Path, SteamInstalled=True)

    if Password == "":
        Password = getpass("What is your Steam Password?: ")
        if Password == "":
            Linux(Path=Path, Username=Username, SteamInstalled=True)

    SteamGuardBool = False

    if not SteamAuth:
        SteamGuardPrompt1 = input("Do you have steam guard on mobile? (Y/N): ").lower()
        if (
            "y" in SteamGuardPrompt1
            or "yes" in SteamGuardPrompt1
            or "true" in SteamGuardPrompt1
        ):
            SteamGuardBool = True
        elif (
            "n" in SteamGuardPrompt1
            or "no" in SteamGuardPrompt1
            or "false" in SteamGuardPrompt1
        ):
            SteamGuardBool = False

        SteamGuardPrompt2 = input("Do you have steam guard on email? (Y/N): ").lower()
        if (
            "y" in SteamGuardPrompt2
            or "yes" in SteamGuardPrompt2
            or "true" in SteamGuardPrompt2
        ):
            subprocess.run(
                ["./steamcmd.sh", "+login", f"{Username}", f"{Password}", "+quit"],
                cwd=f"{Path}/SteamFiles/",
            )
            Linux(
                Path=Path,
                Username=Username,
                Password=Password,
                SteamAuth=True,
                SteamInstalled=True,
            )
        elif (
            "n" in SteamGuardPrompt2
            or "no" in SteamGuardPrompt2
            or "false" in SteamGuardPrompt2
        ):
            SteamGuardBool = False

    SteamGuardCode = False
    if SteamGuardBool or SteamAuth:
        SteamGuardCode = input("What is your Steam Guard code?: ")
        if SteamGuardCode == "":
            print(
                "(If you didn't get an email after about 5 minutes you should say Y, sometimes you don't need a code)"
            )
            Bool = input("Code is empty, are you sure? (Y/N):").lower()
            if "n" in Bool or "no" in Bool or "false" in Bool:
                Linux(
                    Path=Path, Username=Username, Password=Password, SteamInstalled=True
                )

    url = "https://github.com/Fallout-London/FOLON-FO4Downgrader/releases/download/BackendFiles/DepotsList.txt"
    with urllib.request.urlopen(url) as dl_file:
        with open(f"{Path}/SteamFiles/DepotsList.txt", "wb") as out_file:
            out_file.write(dl_file.read())

    if SteamGuardCode != False:
        P = subprocess.run(
            [
                "./steamcmd.sh",
                "+login",
                f"{Username}",
                f"{Password}",
                f"{SteamGuardCode}",
                "+runscript",
                f"{Path}/SteamFiles/DepotsList.txt",
                "+quit",
            ],
            cwd=f"{Path}/SteamFiles/",
        )
    else:
        P = subprocess.run(
            [
                "./steamcmd.sh",
                "+login",
                f"{Username}",
                f"{Password}",
                "+runscript",
                f"{Path}/SteamFiles/DepotsList.txt",
                "+quit",
            ],
            cwd=f"{Path}/SteamFiles/",
        )

    print("####################################")
    print("            MOVING FILES            ")
    print("####################################")

    for i in os.listdir(f"{Path}/SteamFiles/linux32/steamapps/content/app_377160"):
        Util.MoveFiles(
            f"{Path}/SteamFiles/linux32/steamapps/content/app_377160/{i}",
            Path,
        )

    print("####################################")
    print("   Removing creation club content   ")
    print("####################################")

    for i in os.listdir(Path + "/Data"):
        if i[:2] == "cc":
            print("Removing" + i)
            os.remove(Path + "/Data/" + i)

    print("####################################")
    print("      Removing Texture Pack DLC     ")
    print("####################################")

    for i in os.listdir(Path + "/Data"):
        if i[:22] == "DLCUltraHighResolution":
            print("Removing" + i)
            os.remove(Path + "/Data/" + i)

    print("####################################")
    print("                Done                ")
    print("####################################")

    import webbrowser

    webbrowser.open("https://fallout4london.com/release/")
