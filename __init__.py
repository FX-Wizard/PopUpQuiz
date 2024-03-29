import sys

from PySide6 import QtWidgets

from ui import Popup, SystemTrayIcon

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = SystemTrayIcon()
    sys.exit(app.exec())
