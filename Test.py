from PyQt6.QtWidgets import *


class MainWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.resize(700, 410)
        self.setWindowTitle("Youtube_mp3_Converter")

        # Widgets

        # Top Label
        top_label = QLabel()
        top_label.setText("Youtube mp3 \nConverter")  # +

        """ 
        speicherort_label = QLabel()                       
        speicherort_label.setText("welcher Speicherort")
        test_label = QLabel()
        test_label.setText("test")
        """

        self.widget = QWidget()  # +
        layout_h = QHBoxLayout(self.widget)  # +

        # line edit
        self.speicherort_input = QLineEdit()
        # push buttons
        self.speicherort_button = QPushButton("Speicherort_bestaetigen")

        layout_h.addWidget(self.speicherort_input)  # +
        layout_h.addWidget(self.speicherort_button)  # +

        # layout
        layout = QFormLayout()
        self.setLayout(layout)
        layout.addRow(top_label, self.widget)  # +
        #        layout.addRow(self.speicherort_input, self.speicherort_button )

        RateDialog = QDialog(self)
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


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle("fusion")
    w = MainWindow()
    w.show()
    sys.exit(app.exec())
