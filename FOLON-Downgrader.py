import sys
import shutil
import os
import stat
import Utility as Util
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from QLines import *
import argparse
import pexpect.popen_spawn

from LoadScreenFuncs import LoadingThread, LoadingTranslucentScreen


class Communicate(QObject):
    closeLoading = pyqtSignal()


class ScreenThread(LoadingThread):
    def __init__(
        self,
        Function,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self._Function = Function

    def run(self):
        self._Function()


def SetupFont():
    import zipfile

    if not os.path.isdir("FOLON-Downgrader-Files/Fonts"):
        os.system(
            'curl -sqL "https://dl.dafont.com/dl/?f=overseer" -o FOLON-Downgrader-Files/overseer.zip'
        )
        with zipfile.ZipFile("FOLON-Downgrader-Files/overseer.zip", "r") as zip_ref:
            zip_ref.extractall("FOLON-Downgrader-Files/Fonts")
        os.remove("FOLON-Downgrader-Files/overseer.zip")

    QFontDatabase.addApplicationFont("FOLON-Downgrader-Files/Fonts/Overseer.otf")


def SetupSteam():
    import zipfile

    if not os.path.isdir("FOLON-Downgrader-Files/SteamFiles"):
        if Util.IsWindows():
            os.system(
                'curl -sqL "https://github.com/coffandro/DepotDownloader/releases/download/release/DepotDownloader-windows-x64.zip" -o FOLON-Downgrader-Files/steam.zip'
            )

        else:
            os.system(
                'curl -sqL "https://github.com/coffandro/DepotDownloader/releases/download/release/DepotDownloader-linux-x64.zip" -o FOLON-Downgrader-Files/steam.zip'
            )

        with zipfile.ZipFile("FOLON-Downgrader-Files/steam.zip", "r") as zip_ref:
            zip_ref.extractall("FOLON-Downgrader-Files/SteamFiles/")
        os.remove("FOLON-Downgrader-Files/steam.zip")


class MainWindow(QMainWindow):
    def __init__(self, steampath=None):
        super().__init__()
        self.centralWidget = QWidget()
        self.centralWidget.setObjectName("centralWidget")

        self.TabIndex = 1
        Settings = Util.Read_Settings()
        self.setWindowTitle("FOLON Fallout 4 downgrader")
        FOLONIcon = QIcon(Util.resource_path("img/FOLON256.png"))
        self.setWindowIcon(FOLONIcon)

        pagelayout = QVBoxLayout()
        top_layout = QHBoxLayout()
        bottom_layout = QHBoxLayout()
        self.stacklayout = QStackedLayout()

        pagelayout.addLayout(top_layout)
        pagelayout.addLayout(self.stacklayout)
        pagelayout.addLayout(bottom_layout)

        self.SubmitButton = QPushButton(text="Continue")
        self.SubmitButton.resize(
            self.SubmitButton.sizeHint().width(), self.SubmitButton.sizeHint().height()
        )
        self.SubmitButton.pressed.connect(self.ContinueAction)

        bottom_layout.addWidget(QLabel("<small>Developed by Cornelius Rosenaa</small>"))
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.SubmitButton)

        self.tab1 = QWidget()
        self.tab1.setObjectName("Tab")
        self.stacklayout.addWidget(self.tab1)
        self.tab1UI()

        self.tab2 = QWidget()
        self.tab2.setObjectName("Tab")
        self.stacklayout.addWidget(self.tab2)
        self.tab2UI()

        self.tab3 = QWidget()
        self.tab3.setObjectName("Tab")
        self.stacklayout.addWidget(self.tab3)
        self.tab3UI()

        self.tab4 = QWidget()
        self.tab4.setObjectName("Tab")
        self.stacklayout.addWidget(self.tab4)
        self.tab4UI()

        self.InstallProgress = QProgressBar(self)
        self.InstallProgress.setFormat("Locate SteamApps folder")
        self.InstallProgress.setObjectName("DowngraderProgress")
        self.InstallProgress.setRange(0, Settings["Steps"])
        self.InstallProgress.setValue(1)

        top_layout.addWidget(self.InstallProgress)

        self.centralWidget.setLayout(pagelayout)
        self.setCentralWidget(self.centralWidget)

        ArguemntPath = False
        if steampath != None:
            ArguemntPath = True
            self.SteamPath = steampath

            self.activate_tab_2()

    def ContinueAction(self):
        if self.TabIndex == 1:
            self.SubmitPath()
        elif self.TabIndex == 2:
            self.SteamSubmit()
        elif self.TabIndex == 4:
            self.Finish()

    def activate_tab_2(self):  # GUI Backend
        self.TabIndex = 2
        self.stacklayout.setCurrentIndex(1)
        self.SubmitButton.setEnabled(False)
        self.SubmitButton.setText("Login to Steam")
        self.InstallProgress.setFormat("Login to Steam")
        self.InstallProgress.setValue(self.TabIndex)

    def activate_tab_3(self):  # GUI Backend
        if self.FinishedLogging:
            self.TabIndex = 3
            self.stacklayout.setCurrentIndex(2)
            self.SubmitButton.hide()
            self.InstallProgress.setFormat("Downgrade Fallout 4")
            self.InstallProgress.setValue(self.TabIndex)

    def activate_tab_4(self):  # GUI Backend
        self.TabIndex = 4
        self.stacklayout.setCurrentIndex(3)
        self.SubmitButton.show()
        self.SubmitButton.setText("Finish!")
        self.InstallProgress.setFormat("Bethesda, Bethesda Never Changes")
        self.InstallProgress.setValue(self.TabIndex)

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
    # STEAM PATH                                                                             #
    ##########################################################################################

    def tab1UI(self):  # GUI
        Settings = Util.Read_Settings()
        layout = QFormLayout()

        Header = QLabel("Please put in the path to your Steam folder.")
        Header.setFont(QFont("Overseer", 30))
        layout.addRow(Header)
        layout.addRow(
            QLabel(
                "<p>To downgrade Fallout 4 we will need the path to Fallout 4 folder your (or where you'd want Fallout 4 installed),</p>"
            )
        )
        layout.addRow(
            QLabel(
                "<p>The folder <b>should</b> be the one containing a Fallout4.exe file.</p>"
            )
        )

        hbox = QHBoxLayout()
        hboxwidget = QWidget()

        self.PathEntry = QLineEdit()
        self.PathEntry.returnPressed.connect(self.SubmitPath)
        self.PathEntry.setObjectName("InsideTextBox")
        if Settings["SteamPath"] != "":
            self.PathEntry.setText(Settings["SteamPath"])
            self.SubmitButton.setEnabled(True)
        else:
            self.SubmitButton.setEnabled(False)
        self.PathEntry.textChanged.connect(self.edit_text_changed1)

        self.PathButton = QPushButton()
        self.PathButton.setIcon(QIcon(Util.resource_path("img/folder.svg")))
        self.PathButton.setObjectName("PathButton")
        self.PathButton.pressed.connect(self.GetDirectory)

        hbox.addWidget(self.PathEntry)
        hbox.addWidget(self.PathButton)
        hboxwidget.setObjectName("TextBox")
        hboxwidget.setLayout(hbox)

        layout.addRow(QLabel("Steam Path:"), hboxwidget)

        self.tab1.setLayout(layout)

    def edit_text_changed1(self, text):  # GUI Backend
        if self.PathEntry.text() == "":
            self.SubmitButton.setEnabled(False)
        else:
            self.SubmitButton.setEnabled(True)

    def GetDirectory(self):  # GUI Backend
        if not Util.WhereSteam() == False:
            folderpath = QFileDialog.getExistingDirectory(
                self,
                "Select Folder",
                Util.WhereSteam()[0],
            )
        else:
            folderpath = QFileDialog.getExistingDirectory(self, "Select Folder")
        print(folderpath)
        self.PathEntry.setText(folderpath)

    def SubmitPath(self):  # GUI Backend
        if os.path.isdir(self.PathEntry.text()):
            self.WrongPathDialog2(self.PathEntry.text())
        else:
            self.WrongPathDialog1()

    def WrongPathDialog1(self):  # GUI
        self.PathWrong1Dialog = QDialog(self)
        PathWrong1DialogLayout = QVBoxLayout()

        PathWrong1DialogLayout.addWidget(QLabel("This is not a valid Folder"))
        ReturnButton = QPushButton(text="Return")
        ReturnButton.pressed.connect(lambda: self.PathWrong1Dialog.close())
        PathWrong1DialogLayout.addWidget(ReturnButton)
        self.PathWrong1Dialog.setLayout(PathWrong1DialogLayout)
        self.PathWrong1Dialog.exec()

        print("Not valid dir")

    def WrongPathDialog2(self, path):  # GUI Backend
        if Util.IsWritable(path):
            if "Fallout4.exe" in os.listdir(path):
                Settings = Util.Read_Settings()
                Settings["SteamPath"] = self.PathEntry.text()
                self.SteamPath = Settings["SteamPath"]
                Util.Write_Settings(Settings)
                self.activate_tab_2()
            else:
                self.PathWrong2Dialog = QDialog(self)
                PathWrong2DialogLayout = QVBoxLayout()
                PathWrong2DialogLayout.addWidget(
                    QLabel("Folder does not contain Fallout4.exe")
                )
                PathWrong2DialogLayout.addWidget(
                    QLabel("Please choose a valid Fallout 4 folder")
                )
                ReturnButton = QPushButton(text="Return")
                ReturnButton.pressed.connect(lambda: self.PathWrong2Dialog.close())
                PathWrong2DialogLayout.addWidget(ReturnButton)

                self.PathWrong2Dialog.setLayout(PathWrong2DialogLayout)
                self.PathWrong2Dialog.exec()
        else:
            self.PathWrong3Dialog = QDialog(self)
            PathWrong3DialogLayout = QVBoxLayout()
            PathWrong3DialogLayout.addWidget(
                QLabel(f"You do not own the <b>{path}</b> folder")
            )
            PathWrong3DialogLayout.addWidget(
                QLabel(f"Please try to take ownership of this folder and try again.")
            )
            ReturnButton = QPushButton(text="Return")
            ReturnButton.pressed.connect(lambda: self.PathWrong3Dialog.close())

            PathWrong3DialogLayout.addWidget(ReturnButton)

            self.PathWrong3Dialog.setLayout(PathWrong3DialogLayout)
            self.PathWrong3Dialog.exec()

    ##########################################################################################
    # STEAM LOGIN                                                                            #
    ##########################################################################################

    def tab2UI(self):  # GUI
        self.FinishedLogging = False

        layout = QFormLayout()

        Header = QLabel("Please log into Steam before downgrading Fallout 4.")
        Header.setFont(QFont("Overseer", 30))
        layout.addRow(Header)
        layout.addRow(
            QLabel(
                "<p>To downgrade Fallout 4 we will need to download files via Steam, please login to do so.</p>"
            )
        )

        self.UsernameEntry = QLineEdit()
        self.UsernameEntry.returnPressed.connect(self.GoToPassword)
        self.UsernameEntry.textChanged.connect(self.edit_text_changed2)
        self.UsernameEntry.setObjectName("TextBox")

        self.PasswordEntry = QLineEdit()
        self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.PasswordEntry.returnPressed.connect(self.SteamSubmit)
        self.PasswordEntry.textChanged.connect(self.edit_text_changed2)
        self.PasswordEntry.setObjectName("TextBox")

        self.PasswordCheck = QCheckBox()
        self.PasswordCheck.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.PasswordCheck.setChecked(True)
        self.PasswordCheck.stateChanged.connect(self.ChangeHiddenPassword)

        layout.addRow("Username:", self.UsernameEntry)
        layout.addRow("Password:", self.PasswordEntry)
        layout.addRow("Password hidden:", self.PasswordCheck)

        self.tab2.setLayout(layout)

    def edit_text_changed2(self, text):  # GUI Backend
        if self.UsernameEntry.text() == "" or self.PasswordEntry.text() == "":
            self.SubmitButton.setEnabled(False)
        else:
            self.SubmitButton.setEnabled(True)

    def GoToPassword(self):  # GUI Backend
        self.PasswordEntry.setFocus()

    def ChangeHiddenPassword(self):  # GUI Backend
        if self.PasswordCheck.isChecked():
            self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        else:
            self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Normal)

    def SteamSubmit(self):  # Steam
        if not os.path.isdir("FOLON-Downgrader-Files/SteamFiles/"):
            self.Loading(
                SetupSteam,
                text="Loading Steam backend",
                PostFunction=self.SteamSubmit,
            )
        else:
            self.Loading(
                self.LoginSteam,
                text="Logging into Steam",
                UseResult=True,
                PostFunction=self.LoginPopups,
            )

    def LoginSteam(self):  # Steam
        self.Password = self.PasswordEntry.text()
        self.Username = self.UsernameEntry.text()

        if Util.IsWritable("FOLON-Downgrader-Files/SteamFiles"):
            if Util.IsWindows():
                self.DepotDownloader = (
                    "FOLON-Downgrader-Files/SteamFiles/DepotDownloader.exe"
                )
            else:
                self.DepotDownloader = (
                    "FOLON-Downgrader-Files/SteamFiles/DepotDownloader"
                )
                if os.path.isfile(self.DepotDownloader):
                    st = os.stat(self.DepotDownloader)
                    os.chmod(
                        self.DepotDownloader,
                        st.st_mode | stat.S_IEXEC,
                    )

        if os.path.isfile(self.DepotDownloader):
            self.Steam = pexpect.popen_spawn.PopenSpawn(
                f'{self.DepotDownloader} -username "{self.Username}" -password "{self.Password}" -remember-password -app 377160 -depot 377162 -dir FOLON-Downgrader-Files/SteamFiles',
                logfile=sys.stdout.buffer,
                timeout=120,
            )

            self.Wait()

    def Wait(self):
        index = self.Steam.expect(
            [
                pexpect.EOF,
                "auth code sent",
                "Steam Mobile App",
                "RateLimitExceeded",
                "InvalidPassword.",
                pexpect.TIMEOUT,
            ],
        )
        if index == 0:
            Settings["LoginResult"] = "Success"
            Util.Write_Settings(Settings)
        elif index == 1:
            Settings["LoginResult"] = "Guard"
            Util.Write_Settings(Settings)
        elif index == 2:
            Settings["LoginResult"] = "Guard2"
            Util.Write_Settings(Settings)
        elif index == 3:
            Settings["LoginResult"] = "Rate"
            Util.Write_Settings(Settings)
        elif index == 4:
            Settings["LoginResult"] = "PasswordFail"
            Util.Write_Settings(Settings)
        elif index == 5:
            Settings["LoginResult"] = "PasswordFail"
            Util.Write_Settings(Settings)

    def LoginPopups(self):  # Steam
        Settings = Util.Read_Settings()
        result = Settings["LoginResult"]
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
        
        try:
            self.SteamGDlg.close()
        except:
            pass

    def SteamDialog(self):  # GUI
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
        self.GuardEntry.setMaxLength(5)
        self.GuardButton = QPushButton(text="Submit")
        self.GuardButton.pressed.connect(self.GuardSubmitInit)

        self.SteamGDlgLayout.addRow(QLabel("<p>Steam guard code:</p>"), self.GuardEntry)
        self.SteamGDlgLayout.addRow(self.GuardButton)
        self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
        self.SteamGDlg.setLayout(self.SteamGDlgLayout)
        self.SteamGDlg.exec()

    def SteamDialog2(self):  # GUI
        self.shown = False
        Util.Loading = False
        self.SteamGDlg = QDialog(self)
        SteamGDlgLayout = QGridLayout()

        HelpBox = QVBoxLayout()

        HelpButton = QPushButton()
        HelpButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        HelpButton.setIcon(QIcon(Util.resource_path("img/info.svg")))
        HelpButton.pressed.connect(lambda: self.SteamGuideDialog(self.SteamGDlg))

        HelpBox.addWidget(HelpButton, alignment=Qt.AlignRight)

        HelpLabel = QLabel("<h3>Please authorise Steam guard.</h3>")

        SteamGDlgLayout.addWidget(HelpLabel, 0, 0)
        SteamGDlgLayout.addItem(HelpBox, 0, 1)

        labelbox1 = QVBoxLayout()
        labelbox1.addWidget(
            QLabel("<p>Please open your steam app and authorise your login</p>")
        )
        labelbox1.addWidget(QLabel("<p>Also make sure the capitalization</p>"))
        labelbox1.addWidget(QLabel("<p>of your username and password are correct</p>"))

        SteamGDlgLayout.addItem(
            labelbox1,
            1,
            0,
            1,
            2,
        )

        GuardButton = QPushButton(text="Submit")
        GuardButton.pressed.connect(self.LoginSteam)
        SteamGDlgLayout.addWidget(
            GuardButton,
            2,
            0,
            1,
            2,
        )

        GuardLabel = QLabel("<p>Steam guard code:</p>")
        GuardLabel.setObjectName("Guard2Label")

        self.GuardEntry = QLineEdit()
        self.GuardEntry.setObjectName("Guard2Entry")
        self.GuardEntry.setPlaceholderText("Steam guard code")
        self.GuardEntry.setFocus(True)

        self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
        self.SteamGDlg.setLayout(SteamGDlgLayout)
        self.GuardEntry.setFocus()
        self.SteamGDlg.exec()

    def SteamGuideDialog(self, parent):  # GUI
        if not self.shown:
            self.SGDIndex = 1
            self.GuideDialog = QDialog(parent)
            GuideBox = QVBoxLayout()
            button_layout = QHBoxLayout()
            self.SteamGuideLayout = QStackedLayout()

            GuideBox.addLayout(self.SteamGuideLayout)
            GuideBox.addLayout(button_layout)

            GuideLabel1 = QLabel(
                "<p>To authorize please open the Steam app on your phone</p>"
            )
            GuideLabel2 = QLabel("<p>and click Approve.</p>")
            ImageLabel1 = QLabel(text="1")
            ImageLabel1.setObjectName("ImageLabel")
            SteamAuth = QPixmap(Util.resource_path("img/SteamAuth.png")).scaled(
                350, 414
            )

            ImageLabel1.setPixmap(SteamAuth)

            GuideBox.addWidget(GuideLabel1)
            GuideBox.addWidget(GuideLabel2)
            GuideBox.addWidget(ImageLabel1)

            self.GuideDialog.setLayout(GuideBox)
            self.GuideDialog.move(parent.x() + parent.width(), parent.y())
            self.GuideDialog.show()
        else:
            self.GuideDialog.close()
        self.shown = not self.shown

    def LoginFinish(self):  # Steam
        try:
            self.SteamGDlg.close()
        except:
            pass
        try:
            self.GuideDialog.close()
        except:
            pass
        self.FinishedLogging = True
        self.activate_tab_3()

    def PasswordFail(self):  # GUI
        Util.Loading = False
        try:
            self.LoadingDialog.close()
        except:
            pass
        self.SteamPDlg = QDialog(self)
        self.SteamPDlgLayout = QFormLayout()

        self.SteamPDlgLayout.addRow(QLabel("<h3>Incorrect Auth.</h3>"))
        self.SteamPDlgLayout.addRow(QLabel("<p>Please check if your username.</p>"))
        self.SteamPDlgLayout.addRow(QLabel("<p>and password are correct</p>"))
        self.SteamPDlg.setWindowTitle("Steam Password Dialog")
        self.SteamPDlg.setLayout(self.SteamPDlgLayout)
        self.SteamPDlg.exec()

    def GuardSubmitInit(self):  # Steam
        self.Loading(
            self.GuardSubmit,
            text=f"Logging in",
            PostFunction=self.LoginPopups,
        )

    def GuardSubmit(self):  # Steam
        Settings = Util.Read_Settings()
        Username = self.Username
        Password = self.Password
        print(self.GuardEntry.text())

        self.Steam.sendline(f"{self.GuardEntry.text()}\n")

        print("Wait 2 started")
        index = self.Steam.expect(
            [
                "Done!",
                "incorrect",
                "RateLimitExceeded",
                "Steam Failed",
                pexpect.TIMEOUT,
            ],
        )
        if index == 0:
            Settings["LoginResult"] = "Success"
            Util.Write_Settings(Settings)
        elif index == 1:
            Settings["LoginResult"] = "Guard"
            Util.Write_Settings(Settings)
        elif index == 2:
            Settings["LoginResult"] = "Rate"
            Util.Write_Settings(Settings)
        elif index == 3:
            self.GuardSubmit()
        elif index == 4:
            Settings["LoginResult"] = "Rate"
            Util.Write_Settings(Settings)
        print("Wait 2 ended")

    def OpenRateDialog(self):  # GUI
        try:
            self.SteamGDlg.close()
        except:
            pass
        try:
            self.GuideDialog.close()
        except:
            pass
        RateDialog = QDialog()
        RateDialogLayout = QFormLayout()
        RateDialogLayout.addRow(QLabel("<h1>You are being Rate limited</h1>"))
        RateDialogLayout.addRow(
            QLabel(
                "<p>This is most likely because of repeated failed login attempts.</p>"
            )
        )
        RateDialogLayout.addRow(QLabel("<p>If you have not logged in repeatedly</p>"))
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

    def CloseRateDialog(self):  # GUI Backend
        sys.exit()

    ##########################################################################################
    # Installation                                                                           #
    ##########################################################################################

    def tab3UI(self):  # GUI
        self.Depots = [
            # Main game
            [377161, 7497069378349273908],
            [377162, 5847529232406005096],
            [377163, 5819088023757897745],
            [377164, 2178106366609958945],
            # Workshops
            [435880, 1255562923187931216],
            # Automatron
            [435870, 1691678129192680960],
            [435871, 5106118861901111234],
        ]
        self.DownloadIndex = 0
        self.SteamFiles = "FOLON-Downgrader-Files/SteamFiles/depots"
        self.Downloaded = 0
        layout = QFormLayout()

        Header = QLabel("Downgrade Fallout 4")
        Header.setFont(QFont("Overseer", 30))
        layout.addRow(Header)
        layout.addRow(
            QLabel(
                "<p>The following button can take quite a while, please <b>be patient</b>.</p>"
            )
        )

        InstallButton = QPushButton(
            text="Downgrade Fallout 4 (This will take a long time)"
        )
        InstallButton.pressed.connect(self.InstallInit)
        layout.addRow(InstallButton)

        self.tab3.setLayout(layout)

    def InstallInit(self):
        if self.DownloadIndex < len(self.Depots):
            self.Loading(
                lambda: self.Install(self.DownloadIndex),
                text=f"Downloading depot[{self.DownloadIndex+1}/{len(self.Depots)}]",
                PostFunction=self.InstallInit,
            )
        elif self.Downloaded == 1:
            self.Loading(
                self.RemoveCC,
                text=f"Removing Creation Club content",
                PostFunction=self.InstallInit,
            )
        elif self.Downloaded == 2:
            self.activate_tab_4()

    def Install(self, index):
        self.Steam.timeout = None
        self.Steam = pexpect.popen_spawn.PopenSpawn(
            f'{self.DepotDownloader} -username "{self.Username}" -password "{self.Password}" -remember-password -app 377160 -depot {self.Depots[index][0]} -manifest "{self.Depots[index][1]}" -dir "{self.SteamPath}" -validate',
            logfile=sys.stdout.buffer,
            timeout=None,
        )
        self.Wait3()

    def Wait3(self):
        index = self.Steam.expect(
            [
                "Disconnected from Steam",
                "RateLimitExceeded",
                pexpect.TIMEOUT,
            ],
        )
        if index == 0:
            self.DownloadIndex += 1
            if self.DownloadIndex == len(self.Depots):
                self.Downloaded += 1
        elif index == 1:
            Settings["InstallResult"] = "Rate"
            Util.Write_Settings(Settings)
        elif index == 2:
            Settings["InstallResult"] = "Rate"
            Util.Write_Settings(Settings)

    def RemoveCC(self):
        for i in os.listdir(self.SteamPath + "/data"):
            if i[:2] == "cc":
                os.remove(self.SteamPath + "/data/" + i)
        self.Downloaded += 1

    ##########################################################################################
    # FINIS STAGE                                                                            #
    ##########################################################################################

    def tab4UI(self):  # GUI
        layout = QGridLayout()

        TextLayout = QVBoxLayout()
        Header = QLabel("Done Downgrading")
        Header.setFont(QFont("Overseer", 30))
        TextLayout.addWidget(Header)
        TextLayout.addWidget(
            QLabel("<p>Thanks for using the Downgrader,</p>"),
        )
        TextLayout.addWidget(
            QLabel("<p>if you found any issues or just wanna chat.</p>")
        )
        TextLayout.addWidget(
            QLabel("<p>Join the Discord server!</p>"),
        )
        layout.addItem(TextLayout)

        icon = QIcon(Util.resource_path("img/FOLON256.png"))
        self.DiscordButton = QPushButton()
        self.DiscordButton.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.DiscordButton.setIcon(icon)
        self.DiscordButton.setIconSize(QSize(200, 200))

        self.DiscordButton.pressed.connect(self.OpenDiscord)

        layout.addWidget(self.DiscordButton, 0, 1, 1, 1)

        separator_horizontal = QHSeparationLine()
        layout.addWidget(separator_horizontal, 1, 0, 1, 2)

        self.tab4.setLayout(layout)

    def OpenDiscord(self):
        from webbrowser import open

        open("https://discord.gg/GtmKaR8")

    def Finish(self):
        self.close()
        if Util.IsBundled():
            os.execv(sys.executable, sys.argv + ["--clean", self.SteamPath])
        else:
            os.execv(
                sys.executable, ["python"] + sys.argv + ["--clean", self.SteamPath]
            )


def main(steampath=None):
    if not os.path.isdir("FOLON-Downgrader-Files"):
        os.mkdir("FOLON-Downgrader-Files")
    shutil.copy(Util.resource_path("img/check.svg"), "FOLON-Downgrader-Files/")
    shutil.copy(
        Util.resource_path("img/FOLONBackground.png"), "FOLON-Downgrader-Files/"
    )

    app = QApplication(sys.argv)
    CSSFile = Util.resource_path("FOLON.css")
    with open(CSSFile, "r") as fh:
        app.setStyleSheet(fh.read())
    SetupFont()
    if steampath != None:
        ex = MainWindow(steampath)
    else:
        ex = MainWindow()
    ex.setMaximumWidth(ex.width())
    ex.setMaximumHeight(ex.height())
    ex.show()

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
    parser.add_argument(
        "-c",
        "--clean",
        required=False,
        metavar="",
        help="Clean directory, takes over everything else.",
    )
    args = parser.parse_args()

    if args.clean:
        Util.CleanUp(args.clean)
    elif args.path:
        Settings = Util.Read_Settings()
        Settings["Steps"] = 3
        Util.Write_Settings(Settings)
        main(args.path)
    else:
        Settings = Util.Read_Settings()
        Settings["Steps"] = 4
        Util.Write_Settings(Settings)
        main()
