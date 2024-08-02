import sys
import Utility as Util

# sys.excepthook = Util.oops

import shutil
import os
import stat
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import QIcon, QPixmap, QFont, QFontDatabase
from QLines import *
import argparse
from wakepy import keep
import subprocess
import urllib.request, zipfile, io, tarfile

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
    url = "https://dl.dafont.com/dl/?f=overseer"
    with urllib.request.urlopen(url) as dl_file:
        with open("FOLON-Downgrader-Files/overseer.zip", "wb") as out_file:
            out_file.write(dl_file.read())

    with zipfile.ZipFile("FOLON-Downgrader-Files/overseer.zip", "r") as zip_ref:
        zip_ref.extractall("FOLON-Downgrader-Files/Fonts/")
    os.remove("FOLON-Downgrader-Files/overseer.zip")

    QFontDatabase.addApplicationFont("FOLON-Downgrader-Files/Fonts/Overseer.otf")


def SetupSteam():
    if not os.path.isdir("FOLON-Downgrader-Files/SteamFiles"):
        if Util.IsWindows():
            url = "https://steamcdn-a.akamaihd.net/client/installer/steamcmd.zip"
        else:
            url = (
                "https://steamcdn-a.akamaihd.net/client/installer/steamcmd_linux.tar.gz"
            )

        with urllib.request.urlopen(url) as dl_file:
            with open("FOLON-Downgrader-Files/steam.zip", "wb") as out_file:
                out_file.write(dl_file.read())

        if Util.IsWindows():
            with zipfile.ZipFile("FOLON-Downgrader-Files/steam.zip", "r") as zip_ref:
                zip_ref.extractall("FOLON-Downgrader-Files/SteamFiles/")
            Steam = subprocess.Popen(
                "FOLON-Downgrader-Files/SteamFiles/steamcmd.exe +quit"
            )
        else:
            with tarfile.open("FOLON-Downgrader-Files/steam.zip", "r") as tar:
                tar.extractall("FOLON-Downgrader-Files/SteamFiles/")
            Steam = subprocess.Popen(
                "FOLON-Downgrader-Files/SteamFiles/steamcmd.sh +quit"
            )

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
        ProgressDir="",
        ProgressMax=0,
        UseResult=False,
    ):
        self.__loadingTranslucentScreen = LoadingTranslucentScreen(
            parent=self,
            ProgressDir=ProgressDir,
            ProgressMax=ProgressMax,
            description_text=text,
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
        self.SteamGuardCode = ""

        layout = QFormLayout()

        Header = QLabel("Please log into Steam before downgrading Fallout 4.")
        Header.setFont(QFont("Overseer", 30))
        layout.addRow(Header)
        layout.addRow(
            QLabel(
                "<p>To downgrade Fallout 4 we will need to download files via Steam, please login to do so.</p>"
            )
        )
        layout.addRow(
            QLabel("<p>If you have ' or \" in it please preface it with \\.</p>")
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

        CheckBoxes = QWidget()
        CheckLayout = QHBoxLayout()

        CheckLayout.addWidget(QLabel("Password hidden:"))
        CheckLayout.addWidget(self.PasswordCheck)

        self.SteamGuardCheck = QCheckBox()
        self.SteamGuardCheck.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.SteamGuardCheck.setChecked(True)

        CheckLayout.addWidget(QLabel("Using mobile Steam Guard:"))
        CheckLayout.addWidget(self.SteamGuardCheck)

        CheckLayout.addStretch()

        CheckBoxes.setLayout(CheckLayout)

        layout.addRow("Username:", self.UsernameEntry)
        layout.addRow("Password:", self.PasswordEntry)
        layout.addRow(CheckBoxes)

        Box = QHBoxLayout()

        AlertIcon = QLabel()
        AlertIcon.setPixmap(QPixmap(Util.resource_path("img/Alert.svg")))

        AlertLabel = QLabel(
            "<a style='color:White' href='https://github.com/Fallout-London/FOLON-FO4Downgrader/blob/main/Manually.md'>You can also do this process manually if you'd like.</a>"
        )
        AlertLabel.setOpenExternalLinks(True)

        Box.addWidget(AlertIcon)
        Box.addWidget(AlertLabel)
        Box.addStretch()

        layout.addRow(Box)

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
        self.Password = self.PasswordEntry.text()
        self.Username = self.UsernameEntry.text()

        if not os.path.isdir("FOLON-Downgrader-Files/SteamFiles/"):
            self.Loading(
                SetupSteam,
                text="Loading Steam backend",
                PostFunction=self.SteamSubmit,
            )
        else:
            if self.SteamGuardCheck.isChecked():
                self.SteamDialog()
            else:
                self.InstallInit()

    def LoginPopups(self):  # Steam
        Settings = Util.Read_Settings()
        result = Settings["LoginResult"]
        print(result)
        if result == "Guard":
            self.SteamDialog()
        elif result == "Success":
            self.LoginFinish()
        elif result == "Rate":
            self.OpenRateDialog()
        elif result == "PasswordFail":
            self.PasswordFail()

    def SteamDialog(self):  # GUI
        try:
            self.SteamGDlg.close()
            del self.SteamGDlg
        except:
            pass
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

        HelpLabel = QLabel("<h3>Please enter Steam guard.</h3>")

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
            QLabel("<p>Steam app or email, please enter enter it here.</p>")
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
        self.GuardEntry.setObjectName("TextBox")
        self.GuardEntry.setPlaceholderText("Steam guard code")
        self.GuardEntry.setFocus(True)

        GuardSpacer = QSpacerItem(20, 20)
        LineBox = QHBoxLayout()
        LineBox.addItem(GuardSpacer)
        LineBox.addWidget(self.GuardEntry)
        LineBox.addItem(GuardSpacer)

        GuardButton = QPushButton(text="Downgrade Fallout 4")
        GuardButton.pressed.connect(self.GuardSubmit)

        GuardBox = QVBoxLayout()
        GuardBox.addWidget(GuardButton)

        # SteamGDlgLayout.addWidget(GuardLabel, 3, 0)
        SteamGDlgLayout.addItem(LineBox, 3, 0, 1, 2)
        SteamGDlgLayout.addItem(GuardBox, 4, 0, 1, 2)
        self.SteamGDlg.setWindowTitle("Steam Guard Dialog")
        self.SteamGDlg.setLayout(SteamGDlgLayout)
        self.GuardEntry.setFocus()
        self.SteamGDlg.show()

    def GuardSubmit(self):
        Settings = Util.Read_Settings()
        Settings["LoginResult"] = ""
        Util.Write_Settings(Settings)
        self.DownloadFailed = False
        self.SteamGDlg.close()
        self.SteamGuardCode = self.GuardEntry.text()
        self.InstallInit()

    def SteamGuideDialog(self, parent):  # GUI
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

    def SteamGUideCrement(self, Unit):  # GUI Backend
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

    def SteamGuideTab1(self):  # GUI Backend
        self.SteamGuideLayout.setCurrentIndex(0)

    def SteamGuideTab2(self):  # GUI Backend
        self.SteamGuideLayout.setCurrentIndex(1)

    def SteamGuideTab3(self):  # GUI Backend
        self.SteamGuideLayout.setCurrentIndex(2)

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
        self.SteamPDlg.show()

    def GuardSubmitInit(self):  # Steam
        try:
            self.SteamGDlg.close()
        except:
            pass
        try:
            self.GuideDialog.close()
        except:
            pass

        self.Loading(
            self.GuardSubmit,
            text=f"Logging in",
            PostFunction=self.LoginPopups,
        )

    def OpenStorageDialog(self):  # GUI
        try:
            self.SteamGDlg.close()
        except:
            pass
        try:
            self.GuideDialog.close()
        except:
            pass
        self.StorageDialog = QDialog()
        StorageDialogLayout = QFormLayout()
        StorageDialogLayout.addRow(QLabel("<h1>Not enough storage</h1>"))
        StorageDialogLayout.addRow(
            QLabel(
                "<p>You do not have enough storage on the drive with the downgrader,</p>"
            )
        )
        StorageDialogLayout.addRow(
            QLabel("<p>please move it to one with at least 28gb free.</p>")
        )
        StorageDialogLayout.addRow(
            QLabel("<p>(It does not matter if it's the one with Fallout 4 on it)</p>")
        )

        StorageDialogButton = QPushButton(text="Return")
        StorageDialogButton.pressed.connect(self.CloseStorageDialog)
        StorageDialogLayout.addRow(StorageDialogButton)

        self.StorageDialog.setLayout(StorageDialogLayout)
        self.StorageDialog.exec()

    def CloseStorageDialog(self):
        self.StorageDialog.close()

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
        RateDialogLayout.addRow(QLabel("And ask in Downgrader-Bugs for help"))

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
        self.SteamFiles = "FOLON-Downgrader-Files/SteamFiles/depots"
        self.Downloaded = 0
        self.DownloadFailed = False
        layout = QFormLayout()
        layout.addRow(
            QLabel(
                "<p>The following button can take quite a while, please <b>be patient</b>.</p>"
            )
        )

        InstallButton = QPushButton(
            text="Downgrade Fallout 4 \n(This will take a long time)"
        )
        InstallButton.setObjectName("InstallButton")
        InstallButton.setFont(QFont("Overseer", 25))
        InstallButton.pressed.connect(self.OpenDepotsDialog)
        layout.addRow(InstallButton)

        self.tab3.setLayout(layout)

    def OpenDepotsDialog(self):  # GUI
        try:
            self.SteamGDlg.close()
        except:
            pass
        try:
            self.GuideDialog.close()
        except:
            pass
        self.DepotDialog = QDialog()
        DepotDialogLayout = QFormLayout()
        DepotDialogLayout.addRow(QLabel("<h1>Check steam before proceeding</h1>"))
        DepotDialogLayout.addRow(
            QLabel("<p>You are about to download a large amount of data,</p>")
        )
        DepotDialogLayout.addRow(
            QLabel("<p>please check steam if you own every dlc except</p>")
        )
        DepotDialogLayout.addRow(QLabel("<p>for the texture pack on steam.</p>"))

        DepotDialogButton = QPushButton(text="Return")
        DepotDialogButton.pressed.connect(self.CloseDepotDialog)

        DepotSubmitButton = QPushButton(text="Continue")
        DepotSubmitButton.pressed.connect(self.InstallInit)

        DepotDialogLayout.addRow(DepotDialogButton, DepotSubmitButton)

        self.DepotDialog.setLayout(DepotDialogLayout)
        self.DepotDialog.show()

    def CloseDepotDialog(self):
        self.DepotDialog.close()

    def InstallInit(self):
        Settings = Util.Read_Settings()
        print(self.DownloadFailed)
        if self.DownloadFailed:
            result = Settings["LoginResult"]
            print(result)
            if result == "Guard":
                self.SteamDialog()
            elif result == "Rate":
                self.OpenRateDialog()
            elif result == "PasswordFail":
                self.activate_tab_2()
        else:
            if self.Downloaded == 0:
                Settings["LoginResult"] = ""
                Util.Write_Settings(Settings)
                self.DownloadFailed = False
                self.Loading(
                    self.Install,
                    text=f"Downloading depots, grab a cuppa tea, innit'",
                    ProgressDir="FOLON-Downgrader-Files/SteamFiles/steamapps/content/app_377160",
                    ProgressMax=117,
                    PostFunction=self.InstallInit,
                )
            elif self.Downloaded == 1:
                self.Loading(
                    self.MoveFiles,
                    text=f"Moving files to {self.SteamPath}",
                    ProgressDir="FOLON-Downgrader-Files/SteamFiles/steamapps/content/app_377160",
                    ProgressMax=117,
                    PostFunction=self.InstallInit,
                )
            elif self.Downloaded == 2:
                self.Loading(
                    self.RemoveCC,
                    text=f"Removing Creation Club content",
                    PostFunction=self.InstallInit,
                )
            elif self.Downloaded == 3:
                self.Loading(
                    self.RemoveHD,
                    text=f"Removing Texture Pack DLC",
                    PostFunction=self.InstallInit,
                )
            elif self.Downloaded == 4:
                self.activate_tab_4()

    def Install(self):
        try:
            self.SteamGDlg.close()
        except:
            pass

        if Util.IsWindows():
            self.DepotDownloader = "FOLON-Downgrader-Files/SteamFiles/steamcmd.exe"
        else:
            self.DepotDownloader = "FOLON-Downgrader-Files/SteamFiles/steamcmd.sh"
            if os.path.isfile(self.DepotDownloader):
                st = os.stat(self.DepotDownloader)
                os.chmod(
                    self.DepotDownloader,
                    st.st_mode | stat.S_IEXEC,
                )

        FilePath = "./FOLON-Downgrader-Files/DepotsList.txt"
        with open(FilePath, "r") as file:
            lines = file.readlines()

        with open(FilePath, "w") as file:
            file.write("@ShutdownOnFailedCommand 0\n")
            file.write("@NoPromptForPassword 1\n")
            if self.SteamGuardCode == "":
                file.write(f'login "{self.Username}" "{self.Password}"\n')
            else:
                file.write(
                    f'login "{self.Username}" "{self.Password}" "{self.SteamGuardCode}"\n'
                )
            file.writelines(lines)
        with keep.presenting():
            try:
                with subprocess.Popen(
                    [
                        self.DepotDownloader,
                        "+runscript",
                        "../DepotsList.txt",
                        "+validate",
                        "+quit",
                    ],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                ) as p:
                    stdout, stderr = p.communicate()
            except subprocess.SubprocessError as e:
                print(f"An error occurred: {e}")

        output = p.communicate()[0].decode("utf-8")
        print(output)
        if (
            "set_steam_guard_code" in output
            or "Steam Guard Mobile Authenticator app" in output
            or "two-factor" in output
        ):
            Settings["LoginResult"] = "Guard"
            Util.Write_Settings(Settings)
            self.DownloadFailed = True
        elif "(Rate Limit Exceeded)" in output:
            Settings["LoginResult"] = "Rate"
            Util.Write_Settings(Settings)
            self.DownloadFailed = True
        elif "(Invalid Login Auth Code)" in output:
            Settings["LoginResult"] = "Guard"
            Util.Write_Settings(Settings)
            self.DownloadFailed = True
        elif "(Invalid Password)" in output:
            Settings["LoginResult"] = "PasswordFail"
            Util.Write_Settings(Settings)
            self.DownloadFailed = True
        else:
            self.Downloaded += 1

        with open(FilePath, "r") as file:
            data = file.read().splitlines(True)

        with open(FilePath, "w") as file:
            file.writelines(data[3:])

    def MoveFiles(self):
        for i in os.listdir(
            "FOLON-Downgrader-Files/SteamFiles/steamapps/content/app_377160"
        ):
            Util.MoveFiles(
                f"FOLON-Downgrader-Files/SteamFiles/steamapps/content/app_377160/{i}",
                self.SteamPath,
            )
        self.Downloaded += 1

    def RemoveCC(self):
        for i in os.listdir(self.SteamPath + "/Data"):
            if i[:2] == "cc":
                os.remove(self.SteamPath + "/Data/" + i)
        self.Downloaded += 1

    def RemoveHD(self):
        for i in os.listdir(self.SteamPath + "/Data"):
            if i[:22] == "DLCUltraHighResolution":
                os.remove(self.SteamPath + "/Data/" + i)
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
        Util.BlockUpdates()

        try:
            print(self.SteamPath)
        except:
            self.SteamPath = Util.WhereSteam()[0]

        if Util.IsBundled():
            os.execv(sys.executable, sys.argv + ["--clean", self.SteamPath])
        else:
            os.execv(
                sys.executable, ["python"] + sys.argv + ["--clean", self.SteamPath]
            )


def main(steampath=None):
    if os.path.isfile("FOLON-Downgrader-Files/SteamFiles/DepotDownloader.exe"):
        shutil.rmtree("FOLON-Downgrader-Files/SteamFiles")

    if not os.path.isdir("FOLON-Downgrader-Files"):
        os.mkdir("FOLON-Downgrader-Files")
    shutil.copy(Util.resource_path("img/check.svg"), "FOLON-Downgrader-Files/")
    shutil.copy(
        Util.resource_path("img/FOLONBackground.png"), "FOLON-Downgrader-Files/"
    )
    shutil.copy(Util.resource_path("DepotsList.txt"), "FOLON-Downgrader-Files/")

    app = QApplication(sys.argv)
    CSSFile = Util.resource_path("FOLON.css")
    with open(CSSFile, "r") as fh:
        app.setStyleSheet(fh.read())

    if Util.bytesto(shutil.disk_usage(".")[2], "g") < 28:
        MainWindow().OpenStorageDialog()
        return

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
        help="Path to steam(The directory containing a Fallout4.exe file)",
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
