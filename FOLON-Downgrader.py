import sys
import subprocess
import shutil
import os
import Utility as Util
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
import argparse

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
        print("Thread id", QThread.currentThread())
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


class MainWindow(QMainWindow):
    def __init__(self, steampath=None):
        super().__init__()
        self.TabIndex = 1
        Settings = Util.Read_Settings()
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

        self.tab3 = QWidget()
        self.stacklayout.addWidget(self.tab3)
        self.tab3UI()

        self.InstallProgress = QProgressBar(self)
        self.InstallProgress.setFormat("Locate SteamApps folder")
        print(Settings["Steps"])
        self.InstallProgress.setObjectName("DowngraderProgress")
        self.InstallProgress.setRange(0, Settings["Steps"])
        self.InstallProgress.setValue(1)

        button_layout.addWidget(self.InstallProgress)

        widget = QWidget()
        widget.setLayout(pagelayout)
        self.setCentralWidget(widget)

        if steampath != None:
            self.SteamPath = steampath
            self.activate_tab_2()
        else:
            self.SteamPath = "."

    def activate_tab_2(self):
        self.TabIndex += 1
        self.stacklayout.setCurrentIndex(1)
        self.InstallProgress.setFormat("Login to Steam")
        self.InstallProgress.setValue(self.TabIndex)

    def activate_tab_3(self):
        if self.FinishedLogging:
            self.TabIndex += 1
            self.stacklayout.setCurrentIndex(2)
            self.InstallProgress.setFormat("Downgrade Fallout 4")
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

    def tab1UI(self):
        Settings = Util.Read_Settings()
        layout = QFormLayout()

        Header = QLabel("Please put in the path to your Steam folder.")
        Header.setFont(QFont("Overseer", 30))
        layout.addRow(Header)
        layout.addRow(
            QLabel(
                "<p>To downgrade Fallout 4 we will need the path to steam your (or where you'd want Fallout 4 installed),</p>"
            )
        )
        layout.addRow(
            QLabel(
                '<p>The folder <b>should</b> be the one containing a "Steamapps" folder.</p>'
            )
        )

        self.PathSubmit = QPushButton(text="Continue")

        self.PathSubmit.pressed.connect(self.SubmitPath)

        hbox = QHBoxLayout()

        self.PathEntry = QLineEdit()
        self.PathEntry.returnPressed.connect(self.SubmitPath)
        if Settings["SteamPath"] != "":
            self.PathEntry.setText(Settings["SteamPath"])
            self.PathSubmit.setEnabled(True)
        else:
            self.PathSubmit.setEnabled(False)
        self.PathEntry.textChanged.connect(self.edit_text_changed1)

        self.PathButton = QPushButton()
        self.PathButton.setIcon(QIcon(Util.resource_path("img/folder.svg")))
        self.PathButton.pressed.connect(self.GetDirectory)

        hbox.addWidget(self.PathEntry)
        hbox.addWidget(self.PathButton)

        layout.addRow(QLabel("Steam Path:"), hbox)
        layout.addRow(self.PathSubmit)

        self.tab1.setLayout(layout)

    def edit_text_changed1(self, text):
        if self.PathEntry.text() == "":
            self.PathSubmit.setEnabled(False)
        else:
            self.PathSubmit.setEnabled(True)

    def GetDirectory(self):
        folderpath = QFileDialog.getExistingDirectory(self, "Select Folder")
        print(folderpath)
        self.PathEntry.setText(folderpath)

    def SubmitPath(self):
        if os.path.isdir(self.PathEntry.text()):
            if "steamapps" in str(os.listdir(self.PathEntry.text())):
                Settings = Util.Read_Settings()
                Settings["SteamPath"] = self.PathEntry.text()
                Util.Write_Settings(Settings)
                self.activate_tab_2()
            else:
                self.WrongPathDialog2(self.PathEntry.text())
        else:
            self.WrongPathDialog1()

    def WrongPathDialog1(self):
        self.PathWrong1Dialog = QDialog(self)
        PathWrong1DialogLayout = QVBoxLayout()

        PathWrong1DialogLayout.addWidget(QLabel("This is not a valid Folder"))
        ReturnButton = QPushButton(text="Return")
        ReturnButton.pressed.connect(lambda: self.PathWrong1Dialog.close())
        PathWrong1DialogLayout.addWidget(ReturnButton)
        self.PathWrong1Dialog.setLayout(PathWrong1DialogLayout)
        self.PathWrong1Dialog.exec()

        print("Not valid dir")

    def WrongPathDialog2(self, path):
        self.PathWrong2Dialog = QDialog(self)
        PathWrong2DialogLayout = QVBoxLayout()
        PathWrong2DialogLayout.addWidget(
            QLabel(f"<b>{path}</b> does not contain a steamapps folder")
        )
        PathWrong2DialogLayout.addWidget(
            QLabel("Would you like to use the folder anyway?")
        )
        PathWrong2DialogLayout.addWidget(
            QLabel("(This just downloads fallout 4 to the folder)")
        )
        ReturnButton = QPushButton(text="Return")
        ReturnButton.pressed.connect(lambda: self.PathWrong2Dialog.close())
        ContinueButton = QPushButton(text="Continue")
        ContinueButton.pressed.connect(lambda: self.WrongPathDialog3(path))
        ContinueButton.pressed.connect(lambda: self.PathWrong2Dialog.close())

        HBox = QHBoxLayout()
        HBox.addWidget(ReturnButton)
        HBox.addWidget(ContinueButton)
        PathWrong2DialogLayout.addItem(HBox)

        self.PathWrong2Dialog.setLayout(PathWrong2DialogLayout)
        self.PathWrong2Dialog.exec()

    def WrongPathDialog3(self, path):
        try:
            f = open(path + "/FOLON-Downgrader-TestFile", "w")
            f.write("Testing...")
            f.close()
            f = open(path + "/FOLON-Downgrader-TestFile", "r")
            print(f.read())
            f.close()
            os.remove(path + "/FOLON-Downgrader-TestFile")
        except:
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

    def tab2UI(self):
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
        Settings = Util.Read_Settings()
        self.UsernameEntry.setText(Settings["Username"])
        self.UsernameEntry.returnPressed.connect(self.GoToPassword)
        self.UsernameEntry.textChanged.connect(self.edit_text_changed2)
        self.PasswordEntry = QLineEdit()
        self.PasswordEntry.setEchoMode(QLineEdit.EchoMode.Password)
        self.PasswordEntry.returnPressed.connect(self.SteamSubmit)
        self.PasswordEntry.textChanged.connect(self.edit_text_changed2)
        self.PasswordCheck = QCheckBox()
        self.PasswordCheck.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.PasswordCheck.setChecked(True)
        self.PasswordCheck.stateChanged.connect(self.ChangeHiddenPassword)

        self.LoginButton = QPushButton(text="Login to Steam")
        self.LoginButton.setEnabled(False)
        self.LoginButton.pressed.connect(self.activate_tab_3)

        layout.addRow("Username:", self.UsernameEntry)
        layout.addRow("Password:", self.PasswordEntry)
        layout.addRow("Password hidden:", self.PasswordCheck)
        layout.addRow(self.LoginButton)

        self.tab2.setLayout(layout)

    def edit_text_changed2(self, text):
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

        if os.path.isdir("FOLON-Downgrader-Files/SteamFiles"):
            shutil.rmtree("FOLON-Downgrader-Files/SteamFiles")

        os.mkdir("FOLON-Downgrader-Files/SteamFiles")

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
            QLabel("<p>To authorize your identity Steam has sent a code to your</p>")
        )

        SteamGDlgLayout.addItem(
            labelbox1,
            1,
            0,
            1,
            2,
        )
        labelbox2 = QVBoxLayout()
        labelbox2.addWidget(
            QLabel("<p>Steam app, please enter authorise and enter it here.</p>")
        )
        SteamGDlgLayout.addItem(
            labelbox2,
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

        GuardSpacer = QSpacerItem(20, 20)
        LineBox = QHBoxLayout()
        LineBox.addItem(GuardSpacer)
        LineBox.addWidget(self.GuardEntry)
        LineBox.addItem(GuardSpacer)

        GuardButton = QPushButton(text="Submit")
        GuardButton.pressed.connect(self.GuardSubmit)

        GuardBox = QVBoxLayout()
        GuardBox.addWidget(GuardButton)

        # SteamGDlgLayout.addWidget(GuardLabel, 3, 0)
        SteamGDlgLayout.addItem(LineBox, 3, 0, 1, 2)
        SteamGDlgLayout.addItem(GuardBox, 4, 0, 1, 2)
        self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
        self.SteamGDlg.setLayout(SteamGDlgLayout)
        self.GuardEntry.setFocus()
        self.SteamGDlg.exec()

    def SteamGuideDialog(self, parent):
        if not self.shown:
            self.SGDIndex = 1
            self.GuideDialog = QDialog(parent)
            GuideBox = QVBoxLayout()
            button_layout = QHBoxLayout()
            self.SteamGuideLayout = QStackedLayout()

            GuideBox.addLayout(self.SteamGuideLayout)
            GuideBox.addLayout(button_layout)

            Page1 = QWidget()
            Page1Layout = QGridLayout()

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

            Page1Layout.addWidget(GuideLabel1)
            Page1Layout.addWidget(GuideLabel2)
            Page1Layout.addWidget(ImageLabel1)

            Page1.setLayout(Page1Layout)

            Page2 = QWidget()
            Page2Layout = QGridLayout()

            GuideLabel3 = QLabel("<p>Click on the shield icon in the bottom bar</p>")
            GuideLabel4 = QLabel('<p>Then "Show Steam Guard code".</p>')
            GuideLabel5 = QLabel("<p>When prompted about a security warning simply</p>")
            GuideLabel6 = QLabel('<p>click Show Steam Guard code" again.</p>')

            ImageLabel2 = QLabel(text="2")
            ImageLabel3 = QLabel(text="3")
            ImageLabel2.setObjectName("ImageLabel")
            ImageLabel3.setObjectName("ImageLabel")

            SteamShow = QPixmap(Util.resource_path("img/SteamShow.png")).scaled(
                350, 127
            )
            SteamConfirm = QPixmap(Util.resource_path("img/SteamConfirm.png")).scaled(
                350, 275
            )

            ImageLabel2.setPixmap(SteamShow)
            ImageLabel3.setPixmap(SteamConfirm)

            Page2Layout.addWidget(GuideLabel3)
            Page2Layout.addWidget(GuideLabel4)
            Page2Layout.addWidget(ImageLabel2)
            Page2Layout.addWidget(GuideLabel5)
            Page2Layout.addWidget(GuideLabel6)
            Page2Layout.addWidget(ImageLabel3)

            Page2.setLayout(Page2Layout)

            Page3 = QWidget()
            Page3Layout = QVBoxLayout()

            GuideLabel7 = QLabel("<p>You should end up on this screen,</p>")
            GuideLabel8 = QLabel(
                "<p>enter the code on your screen into the text field.</p>"
            )
            GuideLabel9 = QLabel(
                "<p>Do <b>NOT</b> enter a code after it's dissapeared.</p>"
            )

            ImageLabel4 = QLabel(text="4")
            ImageLabel4.setObjectName("ImageLabel")

            SteamCode = QPixmap(Util.resource_path("img/SteamCode.png")).scaled(
                350, 344
            )

            ImageLabel4.setPixmap(SteamCode)
            Page3Layout.addWidget(GuideLabel7)
            Page3Layout.addWidget(GuideLabel8)
            Page3Layout.addWidget(ImageLabel4)

            Page3.setLayout(Page3Layout)

            self.SGDBBtn = QPushButton()
            self.SGDBBtn.setEnabled(False)
            self.SGDBBtn.setIcon(
                QIcon(Util.resource_path("img/arrow-left-Disabled.svg"))
            )
            self.SGDBBtn.pressed.connect(lambda: self.SteamGUideCrement("-1"))
            button_layout.addWidget(self.SGDBBtn)

            self.SGDFBtn = QPushButton()
            self.SGDFBtn.setIcon(QIcon(Util.resource_path("img/arrow-right.svg")))
            self.SGDFBtn.pressed.connect(lambda: self.SteamGUideCrement("1"))
            button_layout.addWidget(self.SGDFBtn)

            self.SteamGuideLayout.addWidget(Page1)
            self.SteamGuideLayout.addWidget(Page2)
            self.SteamGuideLayout.addWidget(Page3)

            self.GuideDialog.setLayout(GuideBox)
            self.GuideDialog.move(parent.x() + parent.width(), parent.y())
            self.GuideDialog.show()
        else:
            self.GuideDialog.close()
        self.shown = not self.shown

    def SteamGUideCrement(self, Unit):
        if Unit == "1":
            if not self.SGDIndex >= 3:
                self.SGDIndex += 1
            if self.SGDIndex >= 3:
                self.SGDFBtn.setEnabled(False)
                self.SGDFBtn.setIcon(
                    QIcon(Util.resource_path("img/arrow-right-Disabled.svg"))
                )
            else:
                self.SGDBBtn.setEnabled(True)
                self.SGDBBtn.setIcon(QIcon(Util.resource_path("img/arrow-left.svg")))
        elif Unit == "-1":
            if not self.SGDIndex <= 1:
                self.SGDIndex -= 1
            if self.SGDIndex <= 1:
                self.SGDBBtn.setEnabled(False)
                self.SGDBBtn.setIcon(
                    QIcon(Util.resource_path("img/arrow-left-Disabled.svg"))
                )
            else:
                self.SGDFBtn.setEnabled(True)
                self.SGDFBtn.setIcon(QIcon(Util.resource_path("img/arrow-right.svg")))
        FunctionName = f"SteamGuideTab{self.SGDIndex}"
        func = getattr(self, FunctionName)
        func()

    def SteamGuideTab1(self):
        self.SteamGuideLayout.setCurrentIndex(0)

    def SteamGuideTab2(self):
        self.SteamGuideLayout.setCurrentIndex(1)

    def SteamGuideTab3(self):
        self.SteamGuideLayout.setCurrentIndex(2)

    def LoginFinish(self):
        Util.Loading = False
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

    def GuardSteamInit(self):
        self.Loading(
            self.GuardSteam,
            text="Loading Steam backend",
            PostFunction=self.LoginPopups,
        )

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
        print(p.communicate()[0])
        if b"OK" in p.communicate()[0]:
            Settings["LoginResult"] = "Success"
            Util.Write_Settings(Settings)
            self.LoginPopups()

        elif bytes("Rate Limit Exceeded", "UTF-8") in p.communicate()[0]:
            self.OpenRateDialog()

    def OpenRateDialog(self):
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

    def tab3UI(self):
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

        self.tab3.setLayout(layout)

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

        InstallProcess = subprocess.Popen(
            command,
            shell=False,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )

        while InstallProcess.poll() is None:
            nextline = InstallProcess.stdout.readline()
            if b"Depot download complete" in nextline:
                self.index += 1
                if self.index < len(self.Depots):
                    print("Done")
            elif b"Rate Limit Exceeded" in nextline:
                self.RateDialog()
            elif nextline == "":
                continue
            print(nextline.strip())

    def CopyFiles(self):
        for i in self.Depots:
            Depot = i
            try:
                if Util.IsBundled():
                    Destination = self.SteamPath
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


def main(steampath=None):
    if not os.path.isdir("FOLON-Downgrader-Files"):
        os.mkdir("FOLON-Downgrader-Files")
    # else:
    # shutil.rmtree("FOLON-Downgrader-Files")
    # os.mkdir("FOLON-Downgrader-Files")
    shutil.copy(Util.resource_path("img/check.svg"), "FOLON-Downgrader-Files/")

    app = QApplication(sys.argv)
    CSSFile = Util.resource_path("FOLON.css")
    with open(CSSFile, "r") as fh:
        app.setStyleSheet(fh.read())
    SetupFont()
    if steampath != None:
        ex = MainWindow(steampath)
    else:
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
        Settings = Util.Read_Settings()
        Settings["Steps"] = 3
        Util.Write_Settings(Settings)
        main(args.path)
    else:
        Settings = Util.Read_Settings()
        Settings["Steps"] = 4
        Util.Write_Settings(Settings)
        main()
