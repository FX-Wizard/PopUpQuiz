import os
import sys
from functools import partial

from PySide2 import QtCore, QtGui, QtWidgets

from quizer import Quiz, QuizMaster
from maker import Ui_QuizMaker

class Popup(QtWidgets.QWidget):
    trigger = QtCore.Signal(str)

    def __init__(self, message, parent=None):
        super(Popup, self).__init__(parent)

        VBox = QtWidgets.QVBoxLayout()
        dialog = QtWidgets.QWidget()
        VBox.addWidget(dialog)
        self.setLayout(VBox)

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint | # Hide window borders
                            #QtCore.Qt.WindowDoesNotAcceptFocus | # doesnt steal focus
                            QtCore.Qt.WindowStaysOnTopHint | # keep window on top
                            QtCore.Qt.SplashScreen) # hide in task bar

        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)

        width = 200
        height = 85
        self.setMinimumSize(width, height)
        self.setStyleSheet(open("style.qss", "r").read())

        self.textBody = QtWidgets.QLabel(self)
        self.textBody.setWordWrap = True
        self.textBody.setAlignment(QtCore.Qt.AlignHCenter)
        self.textBody.setText(message)
        
        # Layout
        self.layout = QtWidgets.QGridLayout()
        self.layout.setSpacing(10)
        self.layout.addWidget(self.textBody, 2, 0)
        dialog.setLayout(self.layout)

        # reposition on screen
        screenSize = QtWidgets.QDesktopWidget().screenGeometry()
        x = screenSize.width()
        y = screenSize.height()
        if sys.platform.startswith('linux'):
            self.move(x, y)
        else:
            self.move(x - width, y - height)

        self.show()

    def returnResponse(self):
        if self.replyBox:
            answer = self.replyBox.text()
        else:
            self.close()
        if answer:
            self.trigger.emit(answer)
            self.close()

    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_Escape:
            self.close()

        elif event.key() == QtCore.Qt.Key_Return:
            self.returnResponse()


class PopupWritten(Popup):
    def __init__(self, message):
        super(PopupWritten, self).__init__(message)
        self.replyBox = QtWidgets.QLineEdit(self)
        self.replyBox.setAlignment(QtCore.Qt.AlignHCenter)
        self.layout.addWidget(self.replyBox, 3, 0)


class PopupTrueFalse(Popup):
    def __init__(self, message):
        super(PopupTrueFalse, self).__init__(message)

        self.tfLayout = QtWidgets.QHBoxLayout()
        self.trueBtn = QtWidgets.QPushButton("True")
        self.falseBtn = QtWidgets.QPushButton("False")
        self.tfLayout.addWidget(self.trueBtn, 0)
        self.tfLayout.addWidget(self.falseBtn, 1)
        self.layout.addLayout(self.tfLayout, 3, 0)
        self.trueBtn.clicked.connect(lambda: self.returnResponse("true"))
        self.falseBtn.clicked.connect(lambda: self.returnResponse("false"))

    def returnResponse(self, answer):
        self.trigger.emit(answer)
        self.close()


class PopupMultipleChoice(Popup):
    def __init__(self, message):
        super(PopupMultipleChoice, self).__init__(message[0])
        self.buttons = []
        for i, text in enumerate(message):
            self.buttons.append(QtWidgets.QRadioButton(text))
            self.buttons[i].clicked.connect(partial(lambda: self.returnResponse(text)))
            self.layout.addWidget(self.buttons[i])

    def returnResponse(self, answer):
        self.trigger.emit(answer)
        self.close()


class PopupMessage(Popup):
    def __init__(self, message):
        super(PopupMessage, self).__init__(message)
        self.message = message
        self.setStyle()
        self.timer = QtCore.QTimer()
        self.timer.start(5000)
        self.timer.timeout.connect(self.closePopup)

    def mousePressEvent(self, event):
        self.closePopup()

    def closePopup(self):
        self.timer.stop()
        self.close()

    def keyPressEvent(self, event):
        if event.key():
            self.close()

    def setStyle(self):
        if "Wrong" in self.message:
            self.setStyleSheet(""" .QWidget {
                background-color: #b30000;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: #680000;
            } """)
        else:
            self.setStyleSheet(""" .QWidget {
                background-color: #1eb300;
                border-style: outset;
                border-width: 2px;
                border-radius: 10px;
                border-color: #008311;
            } """)


class QuizTimer(object):
    def __init__(self, delay, callback):
        self.delay = delay * 60000 #millisecond to second
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(callback)

    def start(self):
        self.timer.start(self.delay)

    def stop(self):
        self.timer.stop()

    def update(self, time):
        self.stop()
        self.delay = time * 60000
        self.start()


class SetInterval(QtWidgets.QWidget):
    trigger = QtCore.Signal(int)

    def __init__(self):
        super(SetInterval, self).__init__()
        self.setWindowTitle("Set Timer Interval")

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        label = QtWidgets.QLabel("Set time in minutes")
        self.layout.addWidget(label)

        self.timeSetter = QtWidgets.QSpinBox()
        self.timeSetter.setValue(self.getTime())
        self.layout.addWidget(self.timeSetter)

        buttonLayout = QtWidgets.QHBoxLayout()
        self.layout.addLayout(buttonLayout)
        okButton = QtWidgets.QPushButton("Ok")
        cancelButton = QtWidgets.QPushButton("cancel")
        buttonLayout.addWidget(okButton)
        buttonLayout.addWidget(cancelButton)
        okButton.clicked.connect(self.setTime)
        cancelButton.clicked.connect(lambda: self.close())
        
        self.show()

    def setTime(self):
        time = self.timeSetter.value()
        QuizMaster().setQuestionTime(time)
        self.trigger.emit(time)
        self.close()

    def getTime(self):
        time = QuizMaster().getQuestionTime()
        return time


class SystemTrayIcon(QtWidgets.QSystemTrayIcon):

    def __init__(self):
        super(SystemTrayIcon, self).__init__()
        if sys.platform.startswith('linux'):
            self.setIcon(QtGui.QIcon("{}/icon.png".format(os.getcwd())))
        elif sys.platform.startswith('darwin'):
            self.setIcon(QtGui.QIcon("{}/icon.png".format(os.getcwd())))
        else:
            self.setIcon(QtGui.QIcon("{}/icon.ico".format(os.getcwd())))
        # try:

        # except:
            # self.setIcon(QtGui.QIcon.fromTheme("document-save"))

        # initialize quiz
        quizmaster = QuizMaster()
        self.quiz = Quiz(quizmaster.loadQuiz())
        time = QuizMaster().getQuestionTime()
        self.timer = QuizTimer(time, self.showPopup)
        self.timer.start()
        
        # context menu stuff
        self.activated.connect(self.leftClickEvent)
        self.menu = QtWidgets.QMenu()
        self.mAsk = self.menu.addAction("Ask Question", self.showPopup)
        self.mPause = self.menu.addAction("Pause", lambda: self.pauseResume("Pause"))
        self.mSetTime = self.menu.addAction("Set Timer", self.setTimer)
        self.mQmaker = self.menu.addAction("Quiz Maker", self.showQuizMaker)
        self.mQuit = self.menu.addAction("Quit", lambda: sys.exit())
        self.setContextMenu(self.menu)
        self.show()

    def leftClickEvent(self, event):
        if event == self.Trigger:
            self.showPopup()

    def showPopup(self):
        # self.timer.stop()
        question, form = self.quiz.askQuestion()
        if form == "trueFalse":
            self.popup = PopupTrueFalse(question)
        elif form == "multipleChoice":
            self.popup = PopupMultipleChoice(question)
        else:
            self.popup = PopupWritten(question)
        self.popup.trigger[str].connect(self.getAnswer)
        
    def getAnswer(self, answer):
        score = self.quiz.checkAnswer(answer)
        self.popup = PopupMessage(score)

    def setTimer(self):
        self.setTimerDialog = SetInterval()
        self.setTimerDialog.trigger[int].connect(self.timer.update)

    def pauseResume(self, action=None):
        if action == "Pause":
            self.timer.stop()
            self.mResume = self.menu.addAction("Resume", lambda: self.pauseResume("Resume"))
            self.menu.insertAction(self.mPause, self.mResume)
            self.menu.removeAction(self.mPause)
        else:
            self.timer.start()
            self.mPause = self.menu.addAction("Pause", lambda: self.pauseResume("Pause"))
            self.mPause = self.menu.insertAction(self.mResume, self.mPause)
            self.menu.removeAction(self.mResume)

    def showQuizMaker(self):
        self.quizMaker = Ui_QuizMaker()
