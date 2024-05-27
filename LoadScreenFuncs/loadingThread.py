import time

from PyQt5.QtCore import QObject, QThread, pyqtSignal
from PyQt5.QtWidgets import QWidget

from LoadScreenFuncs.loadingTranslucentScreen import LoadingTranslucentScreen


class LoadingThread(QThread):
    loadingSignal = pyqtSignal()

    def __init__(self, loading_screen: LoadingTranslucentScreen, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.__loadingTranslucentScreen = loading_screen
        self.__loadingTranslucentScreen.setParentThread(self)
        self.started.connect(self.__loadingTranslucentScreen.start)
        self.finished.connect(self.__loadingTranslucentScreen.stop)
        self.started.connect(
            self.__loadingTranslucentScreen.makeParentDisabledDuringLoading
        )
        self.finished.connect(
            self.__loadingTranslucentScreen.makeParentDisabledDuringLoading
        )

    def run(self):
        time.sleep(5)
