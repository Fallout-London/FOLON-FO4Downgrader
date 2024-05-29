import sys
import subprocess
import shutil
import os
import Utility as Util
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon
import argparse

from LoadScreenFuncs import LoadingThread, LoadingTranslucentScreen


class Communicate(QObject):
    closeLoading = pyqtSignal()


class ScreenThread(LoadingThread):
    # Thanks to Yousef Azizi for his PyQtLoadingscreen script

    def __init__(
        self,
        Function,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        print("Thread id", QThread.currentThread())
        self._Function = Function

    def run(self):
        self._Function()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FOLON Fallout 4 downgrader")
        FOLONIcon = QIcon(Util.resource_path("FOLON-Downgrader-Files/img/FOLON256.png"))
        self.setWindowIcon(FOLONIcon)

        pagelayout = QVBoxLayout()
        button_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(button_layout)
        pagelayout.addLayout(self.stacklayout)

        self.tab1 = QWidget()
        self.stacklayout.addWidget(self.tab1)
        self.tab1UI()

        self.tab2 = QWidget()
        self.stacklayout.addWidget(self.tab2)
        self.tab2UI()

        self.InstallProgress = QProgressBar(self)
        self.InstallProgress.setFormat("Login to Steam")
        self.InstallProgress.setValue(10)
        button_layout.addWidget(self.InstallProgress)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

    def activate_tab_2(self):
        if self.FinishedLogging:
            self.stacklayout.setCurrentIndex(1)
            self.InstallProgress.setValue(20)

    #########################################################################################
    # GENERAL GUI                                                                           #
    #########################################################################################

    def Loading(
        self,
        Function,
        text="Loading..",
        PostFunction=None,
        Window=None,
        UseResult=False,
    ):
        self.__loadingTranslucentScreen = LoadingTranslucentScreen(
            parent=self, description_text=text
        )
        self.__thread = ScreenThread(
            Function,
            loading_screen=self.__loadingTranslucentScreen,
        )
        if PostFunction != None:
            self.__thread.finished.connect(PostFunction)
        self.__thread.start()

    ##########################################################################################
    # STEAM LOGIN                                                                            #
    ##########################################################################################

    def tab1UI(self):
        self.FinishedLogging = False

        layout = QFormLayout()

        layout.addRow(
            QLabel("<h1>Please log into Steam before downgrading Fallout 4.</h1>")
        )
        layout.addRow(
            QLabel(
                "<p>To downgrade Fallout 4 we will need to download files via Steam, please login to do so.</p>"
            )
        )

        self.UsernameEntry = QLineEdit()
        Settings = Util.Read_Settings()
        self.UsernameEntry.setText(Settings["Username"])
        self.UsernameEntry.returnPressed.connect(self.GoToPassword)
        self.UsernameEntry.textChanged.connect(self.edit_text_changed)
        self.PasswordEntry = QLineEdit()
        self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.PasswordEntry.returnPressed.connect(self.SteamSubmit)
        self.PasswordEntry.textChanged.connect(self.edit_text_changed)
        self.PasswordCheck = QCheckBox()
        self.PasswordCheck.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.PasswordCheck.setChecked(True)
        self.PasswordCheck.stateChanged.connect(self.ChangeHiddenPassword)

        self.LoginButton = QPushButton(text="Login to Steam")
        self.LoginButton.setEnabled(False)
        self.LoginButton.pressed.connect(self.SteamSubmit)

        layout.addRow("Username:", self.UsernameEntry)
        layout.addRow("Password:", self.PasswordEntry)
        layout.addRow("Password hidden:", self.PasswordCheck)
        layout.addRow(self.LoginButton)

        self.tab1.setLayout(layout)

    # Steam Functions

    def edit_text_changed(self, text):
        if self.UsernameEntry.text() == "" or self.PasswordEntry.text() == "":
            self.LoginButton.setEnabled(False)
        else:
            self.LoginButton.setEnabled(True)

    def GoToPassword(self):
        self.PasswordEntry.setFocus()

    def ChangeHiddenPassword(self):
        if self.PasswordCheck.isChecked():
            self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Normal)

    def SteamSubmit(self):
        Settings = Util.Read_Settings()
        Settings["Username"] = self.UsernameEntry.text()
        self.Password = self.PasswordEntry.text()
        Util.Write_Settings(Settings)
        self.LoginSteamInit()

    def LoginSteamInit(self):
        print("main id", QThread.currentThread())
        if not os.path.isdir("FOLON-Downgrader-Files/SteamFiles/"):
            self.Loading(
                self.SetupSteam,
                text="Loading Steam backend",
                PostFunction=self.LoginSteamInit,
            )
        else:
            self.Loading(
                self.LoginSteam,
                text="Logging into Steam",
                UseResult=True,
                PostFunction=self.LoginPopups,
            )

    def SetupSteam(self):
        import zipfile
        import pathlib

        if os.path.isdir("FOLON-Downgrader-Files/SteamFiles"):
            shutil.rmtree("FOLON-Downgrader-Files/SteamFiles")

        pathlib.Path.mkdir("FOLON-Downgrader-Files/SteamFiles")

        if Util.IsWindows():
            os.system(
                'curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -o FOLON-Downgrader-Files/steamcmd.zip'
            )
            with zipfile.ZipFile("FOLON-Downgrader-Files/steamcmd.zip", "r") as zip_ref:
                zip_ref.extractall("FOLON-Downgrader-Files/SteamFiles/")

            os.system("FOLON-Downgrader-Files\\SteamFiles\\steamcmd.exe +quit")
        else:
            os.system(
                'curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz" | tar zxvf - -C FOLON-Downgrader-Files/SteamFiles'
            )
            os.system("FOLON-Downgrader-Files/SteamFiles/steamcmd.sh +quit")

    def LoginSteam(self):
        Settings = Util.Read_Settings()
        Username = Settings["Username"]
        Password = self.Password

        if Util.IsWindows():
            if os.path.isfile("FOLON-Downgrader-Files/SteamFiles/steamcmd.exe"):
                p = subprocess.Popen(
                    [
                        "FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                        "+login",
                        f"{Username}",
                        f"{Password}",
                        "+quit",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
        else:
            if os.path.isfile("FOLON-Downgrader-Files/SteamFiles/steamcmd.sh"):
                p = subprocess.Popen(
                    [
                        "FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                        "+login",
                        f"{Username}",
                        f"{Password}",
                        "+quit",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                )
        p.communicate(b"quit")
        print(p.communicate()[0])
        if (
            b"You can also enter this code at any time using 'set_steam_guard_code'"
            in p.communicate()[0]
        ):
            Settings["LoginResult"] = "Guard"
            Util.Write_Settings(Settings)
        elif (
            b"Enter the current code from your Steam Guard Mobile Authenticator app"
            in p.communicate()[0]
        ):
            Settings["LoginResult"] = "Guard2"
            Util.Write_Settings(Settings)
        elif (
            bytes(f"Logging in user '{Username}' to Steam Public...OK", "UTF-8")
            in p.communicate()[0]
        ):
            Settings["LoginResult"] = "Success"
            Util.Write_Settings(Settings)

        elif bytes("Rate Limit", "UTF-8") in p.communicate()[0]:
            Settings["LoginResult"] = "Rate"
            Util.Write_Settings(Settings)

        elif b"FAILED (Invalid Password)" in p.communicate()[0]:
            Settings["LoginResult"] = "PasswordFail"
            Util.Write_Settings(Settings)

    def LoginPopups(self):
        Settings = Util.Read_Settings()
        result = Settings["LoginResult"]
        print(result)
        if result == "Guard":
            self.SteamDialog()
        elif result == "Guard2":
            self.SteamDialog2()
        elif result == "Success":
            self.LoginFinish()
        elif result == "Rate":
            self.OpenRateDialog()
        elif result == "PasswordFail":
            self.PasswordFail()

    def SteamDialog(self):
        Util.Loading = False
        self.SteamGDlg = QDialog(self)
        self.SteamGDlgLayout = QFormLayout()

        self.SteamGDlgLayout.addRow(
            QLabel("<h3>Please enter your Steam guard code.</h3>")
        )
        self.SteamGDlgLayout.addRow(
            QLabel("<p>To authorize your identity Steam has sent a code</p>")
        )
        self.SteamGDlgLayout.addRow(
            QLabel("<p>to either your mail or phone, please enter it here.</p>")
        )

        self.GuardEntry = QLineEdit()
        self.GuardButton = QPushButton(text="Submit")
        self.GuardButton.pressed.connect(self.GuardSubmit)

        self.SteamGDlgLayout.addRow(QLabel("<p>Steam guard code:</p>"), self.GuardEntry)
        self.SteamGDlgLayout.addRow(self.GuardButton)
        self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
        self.SteamGDlg.setLayout(self.SteamGDlgLayout)
        self.SteamGDlg.exec()

    def SteamDialog2(self):
        Util.Loading = False
        self.SteamGDlg = QDialog(self)
        self.SteamGDlgLayout = QFormLayout()

        self.SteamGDlgLayout.addRow(
            QLabel("<h3>Please enter your Steam guard code.</h3>")
        )
        self.SteamGDlgLayout.addRow(
            QLabel("<p>To authorize your identity Steam has sent a code</p>")
        )
        self.SteamGDlgLayout.addRow(
            QLabel(
                "<p>to either your Authenticator app, please enter authorise and enter it here.</p>"
            )
        )

        self.GuardEntry = QLineEdit()
        self.GuardButton = QPushButton(text="Submit")
        self.GuardButton.pressed.connect(self.GuardSubmit)

        self.SteamGDlgLayout.addRow(QLabel("<p>Steam guard code:</p>"), self.GuardEntry)
        self.SteamGDlgLayout.addRow(self.GuardButton)
        self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
        self.SteamGDlg.setLayout(self.SteamGDlgLayout)
        self.SteamGDlg.exec()

    def LoginFinish(self):
        Util.Loading = False
        try:
            self.SteamGDlg.close()
        except:
            pass
        self.FinishedLogging = True
        self.activate_tab_2()

    def PasswordFail(self):
        Util.Loading = False
        try:
            self.LoadingDialog.close()
        except:
            pass
        self.SteamPDlg = QDialog(self)
        self.SteamPDlgLayout = QFormLayout()

        self.SteamPDlgLayout.addRow(QLabel("<h3>Incorrect Password.</h3>"))
        self.SteamPDlgLayout.addRow(QLabel("<p>Please re-enter the password.</p>"))
        self.SteamPDlgLayout.addRow(
            QLabel("<p>Remember to <b>check</b> if it is correct.</p>")
        )
        self.SteamPDlg.setWindowTitle("Steam Password Dialog")
        self.SteamPDlg.setLayout(self.SteamPDlgLayout)
        self.SteamPDlg.exec()

    def GuardSteam(self):
        Settings = Util.Read_Settings()

        if Util.IsWindows():
            p = subprocess.Popen(
                f'FOLON-Downgrader-Files/SteamFiles/steamcmd.exe +login "{Settings["Username"]}" "{self.PasswordEntry.text()}" +quit',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        else:
            p = subprocess.Popen(
                f'FOLON-Downgrader-Files/SteamFiles/steamcmd.sh +login "{Settings["Username"]}" "{self.PasswordEntry.text()}" +quit',
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        p.communicate(b"quit")

    def GuardSubmit(self):
        Settings = Util.Read_Settings()
        print(self.GuardEntry.text())
        import subprocess

        if Util.IsWindows():
            p = subprocess.Popen(
                [
                    "FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                    "+login",
                    f'{Settings["Username"]}',
                    f"{self.PasswordEntry.text()}",
                    f"{self.GuardEntry.text()}",
                    "+quit",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        else:
            p = subprocess.Popen(
                [
                    "FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                    "+login",
                    f'{Settings["Username"]}',
                    f"{self.PasswordEntry.text()}",
                    f"{self.GuardEntry.text()}",
                    "+quit",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
            )
        Code = self.GuardEntry.text()
        p.communicate(bytes(Code + "\n", "UTF-8"))
        if (
            bytes(
                f"Logging in user '{Settings['Username']}' to Steam Public...OK",
                "UTF-8",
            )
            in p.communicate()[0]
        ):
            Settings["LoginResult"] = "Success"
            Util.Write_Settings(Settings)
            self.LoginPopups()

        elif bytes("rate limit", "UTF-8") in p.communicate()[0]:
            self.OpenRateDialog()

    def OpenRateDialog(self):
        try:
            self.SteamGDlg.close()
        except:
            pass
        RateDialog = QDialog()
        RateDialogLayout = QFormLayout()
        RateDialogLayout.addRow(QLabel("<h1>You are being rate limited</h1>"))
        RateDialogLayout.addRow(
            QLabel("<p>This is most likely because of an error in the installer</p>")
        )
        LinkLabel = QLabel(
            "<a href='https://discord.gg/GtmKaR8'>Please report it to the Discord server</a>"
        )
        LinkLabel.setOpenExternalLinks(True)
        RateDialogLayout.addRow(LinkLabel)
        RateDialogLayout.addRow(QLabel("And ping @Coffandro for help"))

        RateDialogButton = QPushButton(text="Close")
        RateDialogButton.pressed.connect(self.CloseRateDialog)
        RateDialogLayout.addRow(RateDialogButton)

        RateDialog.setLayout(RateDialogLayout)
        RateDialog.exec()

    def CloseRateDialog(self):
        sys.exit()

    ##########################################################################################
    # Installation                                                                           #
    ##########################################################################################

    def tab2UI(self):
        # Thanks to Zerratar for reference implementation in his FO4-Downgrader
        self.Depots = [
            # Main game
            [377161, 7497069378349273908],
            [377162, 5847529232406005096],
            [377163, 5819088023757897745],
            [377164, 2178106366609958945],
            # Wasteland W
            [435880, 1255562923187931216],
            # Automatron
            [435870, 1691678129192680960],
            [435871, 5106118861901111234],
            # Contraptions W
            [480630, 5527412439359349504],
            # Far harbour
            [435881, 1207717296920736193],
            [435882, 8482181819175811242],
            # Vault tec
            [480631, 6588493486198824788],
            [393885, 5000262035721758737],
            # Nuka world
            [490650, 4873048792354485093],
            [393895, 7677765994120765493],
        ]
        if Util.IsWindows():
            self.SteamFiles = (
                "FOLON-Downgrader-Files/SteamFiles/steamapps/content/app_377160"
            )
        else:
            self.SteamFiles = (
                "FOLON-Downgrader-Files/SteamFiles/linux32/steamapps/content/app_377160"
            )
        self.index = 0
        layout = QFormLayout()

        SteamLabel = QLabel(text=str(Util.WhereSteam()))
        layout.addRow(SteamLabel)

        InstallButton = QPushButton(
            text="Downgrade Fallout 4 (This will take a long time)"
        )
        InstallButton.pressed.connect(self.InstallInit)
        layout.addRow(InstallButton)

        self.tab2.setLayout(layout)

    def Load(self):
        self.Loading(
            lambda: time.sleep(5),
            text=f"Moving depot[{self.index+1}/14]",
            PostFunction=self.InstallInit,
        )

    def InstallInit(self):
        if not os.path.isdir(f"{self.SteamFiles}"):
            self.Loading(
                lambda: self.Install(self.index),
                text=f"Downloading depot[{self.index+1}/14]",
                PostFunction=self.InstallInit,
            )
        else:
            self.Loading(
                self.CopyFiles,
                text=f"Moving depot",
            )

    def Install(self, index):
        Settings = Util.Read_Settings()
        if Util.IsWindows():
            command = [
                "FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                "+login",
                f'{Settings["Username"]}',
                f"{self.PasswordEntry.text()}",
                "+force_install_dir",
                "../csgo_ds",
                "+runscript",
                Util.resource_path("DownloadFallout4.txt"),
                "+quit",
            ]
        else:
            command = [
                "FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                "+login",
                f'{Settings["Username"]}',
                f"{self.PasswordEntry.text()}",
                "+force_install_dir",
                "../csgo_ds",
                "+runscript",
                Util.resource_path("DownloadFallout4.txt"),
                "+quit",
            ]

        process = subprocess.Popen(
            command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )

        while process.poll() is None:
            nextline = process.stdout.readline()
            if b"Depot download complete" in nextline:
                self.index += 1
                if self.index < 14:
                    print("Done")
            elif nextline == "":
                continue
            print(nextline.strip())

    def CopyFiles(self):
        for i in self.Depots:
            Depot = i
            try:
                if Util.IsBundled():
                    Destination = "."
                else:
                    Destination = "../Fallout 4"
                if not os.path.isdir(Destination):
                    mkdir(Destination)

                print("Started Depot:", Depot[0])
                for a in os.listdir(f"{self.SteamFiles}/depot_{Depot[0]}"):
                    if os.path.isdir(f"{self.SteamFiles}/depot_{Depot[0]}/{a}"):
                        for b in os.listdir(f"{self.SteamFiles}/depot_{Depot[0]}/{a}"):
                            if not os.path.isdir(f"{Destination}/{a}"):
                                os.mkdir(f"{Destination}/{a}")
                            shutil.move(
                                f"{self.SteamFiles}/depot_{Depot[0]}/{a}/{b}",
                                f"{Destination}/{a}/{b}",
                            )
                    else:
                        shutil.move(
                            f"{self.SteamFiles}/depot_{Depot[0]}/{a}",
                            f"{Destination}/{a}",
                        )
                    print("moved:", a)
                shutil.rmtree(f"{self.SteamFiles}/depot_{Depot[0]}")
                print("Finished Depot:", Depot)
            except:
                print("Skipped Depot:", Depot)
        shutil.rmtree(self.SteamFiles)


def main():
    if not os.path.isdir("FOLON-Downgrader-Files"):
        os.mkdir("FOLON-Downgrader-Files")
    else:
        shutil.rmtree("FOLON-Downgrader-Files")
        os.mkdir("FOLON-Downgrader-Files")
    shutil.copy(Util.resource_path("img/check-solid.svg"), "FOLON-Downgrader-Files/")

    app = QApplication(sys.argv)
    CSSFile = Util.resource_path("FOLON.css")
    with open(CSSFile, "r") as fh:
        app.setStyleSheet(fh.read())
    ex = MainWindow()
    # ex.setMinimumWidth(750)
    # ex.setMinimumHeight(575)
    # ex.setMaximumWidth(750)
    # ex.setMaximumHeight(575)
    ex.show()

    # Redirect stdout to a file
    sys.exit(app.exec())


def directory(raw_path):
    if not os.path.isdir(raw_path):
        raise argparse.ArgumentTypeError(
            '"{}" is not an existing directory'.format(raw_path)
        )
    return os.path.abspath(raw_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A Fallout 4 downgrader application by Team FOLON"
    )
    parser.add_argument(
        "-p",
        "--path",
        required=False,
        metavar="",
        type=directory,
        help="Path to steam(The directory containing a SteamApps folder)",
    )
    args = parser.parse_args()

    if args.path:
        print(os.listdir(args.path))
        main()
    else:
        main()
