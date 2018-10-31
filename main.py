import sys

from PyQt5.QtWidgets import QApplication

from ui import Popup, SystemTrayIcon

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    window = SystemTrayIcon()
    sys.exit(app.exec_())
