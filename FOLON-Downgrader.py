import sys
import subprocess
import shutil
import os
import Utility as Util
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon

from LoadScreenFuncs import LoadingThread, LoadingTranslucentScreen


class Communicate(QObject):
    closeLoading = pyqtSignal()


class ScreenThread(LoadingThread):
    # Thanks to Yousef Azizi for his PyQtLoadingscreen script

    def __init__(
        self,
        Function,
        PostFunction=None,
        Window=None,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._Function = Function
        self._Window = Window
        if callable(PostFunction):
            self.finished.connect(lambda: PostFunction())

    def run(self):
        Util.Loading = True
        if self._Window != None:
            Func = self._Function
            self = self._Window
            Func(self)
        else:
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

    def Loading(self, Function, text="Loading..", PostFunction=None, Window=None):
        self.__loadingTranslucentScreen = LoadingTranslucentScreen(
            parent=self, description_text=text
        )
        self.__loadingTranslucentScreen.setDescriptionLabelDirection("Bottom")
        self.__thread = ScreenThread(
            Function,
            PostFunction=PostFunction,
            Window=Window,
            loading_screen=self.__loadingTranslucentScreen,
        )
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
        self.PasswordEntry = QLineEdit()
        self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.PasswordEntry.returnPressed.connect(self.SteamSubmit)
        self.PasswordCheck = QCheckBox()
        self.PasswordCheck.setChecked(True)
        self.PasswordCheck.stateChanged.connect(self.ChangeHiddenPassword)

        LoginButton = QPushButton(text="Login to Steam")
        LoginButton.pressed.connect(self.SteamSubmit)

        layout.addRow("Username:", self.UsernameEntry)
        layout.addRow("Password:", self.PasswordEntry)
        layout.addRow("Password hidden:", self.PasswordCheck)
        layout.addRow(LoginButton)

        self.tab1.setLayout(layout)

    # Steam Functions

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
                PostFunction=self.activate_tab_2,
            )

    def SetupSteam(self):
        import zipfile
        import pathlib

        if not os.path.isdir("FOLON-Downgrader-Files"):
            os.mkdir("FOLON-Downgrader-Files")
        if os.path.isdir("FOLON-Downgrader-Files/SteamFiles"):
            shutil.rmtree("FOLON-Downgrader-Files/SteamFiles")

        pathlib.Path.mkdir("FOLON-Downgrader-Files/SteamFiles")

        if Util.IsWindows():
            os.system(
                'curl -sqL "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip" -o FOLON-Downgrader-Files/steamcmd.zip'
            )
            with zipfile.ZipFile("FOLON-Downgrader-Files/steamcmd.zip", "r") as zip_ref:
                zip_ref.extractall("FOLON-Downgrader-Files/SteamFiles/")

            os.system("FOLON-Downgrader-Files/SteamFiles/steamcmd.exe +quit")
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
        if (
            b"You can also enter this code at any time using 'set_steam_guard_code'"
            in p.communicate()[0]
        ):
            self.SteamDialog()
        elif (
            bytes(f"Logging in user '{Username}' to Steam Public...OK", "UTF-8")
            in p.communicate()[0]
        ):
            self.LoginFinish()

        elif bytes("rate limit", "UTF-8") in p.communicate()[0]:
            self.OpenRateDialog()

        elif b"FAILED (Invalid Password)" in p.communicate()[0]:
            self.PasswordFail()

    def SteamDialog(self):
        Util.Loading = False
        self.SteamGDlg = QDialog()
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

    def LoginFinish(self):
        Util.Loading = False
        try:
            self.SteamGDlg.close()
        except:
            pass
        self.FinishedLogging = True

    def PasswordFail(self):
        Util.Loading = False
        try:
            self.LoadingDialog.close()
        except:
            pass
        self.SteamPDlg = QDialog()
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
            self.LoginFinish()

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
                lambda: self.CopyFiles(self.index),
                text=f"Moving depot[{self.index+1}/14]",
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
                f"{os.getcwd()}/DownloadFallout4.txt",
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

        """if Util.IsWindows():
                                    subprocess.run(
                                        [
                                            "FOLON-Downgrader-Files/SteamFiles/steamcmd.exe",
                                            "+login",
                                            f'{Settings["Username"]}',
                                            f"{self.PasswordEntry.text()}",
                                            "+download_depot",
                                            f"377160",
                                            f"{self.Depots[index][0]}",
                                            f"{self.Depots[index][1]}",
                                            "+quit",
                                        ]
                                    )
                                else:
                                    subprocess.run(
                                        [
                                            "FOLON-Downgrader-Files/SteamFiles/steamcmd.sh",
                                            "+login",
                                            f'{Settings["Username"]}',
                                            f"{self.PasswordEntry.text()}",
                                            "+force_install_dir", 
                                            "../csgo_ds",
                                            "+runscript",
                                            f"{os.getcwd}/DownloadFallout4.txt",
                                            "+quit",
                                        ]
                                    )"""

    def CopyFiles(self, index):
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
    app = QApplication(sys.argv)
    CSSFile = Util.resource_path("FOLON.css")
    with open(CSSFile, "r") as fh:
        app.setStyleSheet(fh.read())

    ex = MainWindow()
    ex.setMinimumWidth(750)
    ex.setMinimumHeight(575)
    ex.setMaximumWidth(750)
    ex.setMaximumHeight(575)
    ex.show()

    # Redirect stdout to a file
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
