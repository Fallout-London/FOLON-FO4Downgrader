from urllib.request import urlopen

from PyQt6.QtCore import QThread
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton


class Downloader(QThread):

    def __init__(self, url, filename):
        super().__init__()
        self._url = url
        self._filename = filename

    def run(self):
        # Open the URL address.
        with urlopen(self._url) as r:
            with open(self._filename, "wb") as f:
                # Read the remote file and write the local one.
                f.write(r.read())


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Threaded File Download with PyQt")
        self.resize(400, 300)
        self.label = QLabel("Press the button to start the download.",
            self)
        self.label.setGeometry(20, 20, 200, 25)
        self.button = QPushButton("Start download", self)
        self.button.move(20, 60)
        self.button.pressed.connect(self.initDownload)

    def initDownload(self):
        self.label.setText("Downloading file...")
        # Disable the button while downloading the file.
        self.button.setEnabled(False)
        # Execute the download in a new thread.
        self.downloader = Downloader(
            "https://www.python.org/ftp/python/3.7.2/python-3.7.2.exe",
            "python-3.7.2.exe"
        )
        # Qt will invoke the `downloadFinished()` method once the
        # thread has finished.
        self.downloader.finished.connect(self.downloadFinished)
        print(self.downloader.start())

    def downloadFinished(self):
        self.label.setText("¡File downloaded!")
        # Restore the button.
        self.button.setEnabled(True)
        # Delete the thread when no longer needed.
        del self.downloader


if __name__ == "__main__":
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
