import os
import sys
from PySide6 import QtCore, QtGui, QtWidgets

from quizer import QuizMaster, Quiz


class Ui_QuizMaker(QtWidgets.QMainWindow):
    def __init__(self, parent=None):
        super(Ui_QuizMaker, self).__init__(parent)
        self.setWindowTitle('Quiz Maker')
        self.setMinimumSize(400, 560)
        # tool bar
        self.toolBar = QtWidgets.QToolBar()
        self.aNewQuiz = QtGui.QAction("New", self)
        self.aOpenQuiz = QtGui.QAction("Open", self)
        self.aNewQuiz.setShortcut("Ctrl+N")
        self.aOpenQuiz.setShortcut("Ctrl+O")
        self.aNewQuiz.triggered.connect(self.newQuiz)
        self.aOpenQuiz.triggered.connect(self.openQuiz)
        self.toolBar.addAction(self.aNewQuiz)
        self.toolBar.addAction(self.aOpenQuiz)
        self.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)

        #layout
        self.frame = QtWidgets.QFrame()
        self.setCentralWidget(self.frame)

        self.gridLayout = QtWidgets.QGridLayout(self.frame)
        self.quizNameBox = QtWidgets.QLabel("Open quiz or make new quiz to get started")
        nameFont = QtGui.QFont()
        nameFont.setBold(True)
        self.quizNameBox.setFont(nameFont)
        self.gridLayout.addWidget(self.quizNameBox)
        
        self.listView = QtWidgets.QListWidget()
        self.listView.itemDoubleClicked.connect(self.editQuestion)
        self.gridLayout.addWidget(self.listView)

        self.addQuestion = QtWidgets.QPushButton("Add Questions")
        self.gridLayout.addWidget(self.addQuestion)

        self.addQuestion.clicked.connect(self.add)

        self.show()

    def newQuiz(self):
        self.quizPath = QtWidgets.QFileDialog.getSaveFileName(self, "New Quiz", "", "Quizzes (*.json)")[0]
        if self.quizPath:
            self.listView.clear()
            self.quiz = Quiz(path=self.quizPath + ".json")
            self.quizNameBox.setText(os.path.basename(self.quizPath))

    def openQuiz(self):
        self.quizPath = QtWidgets.QFileDialog.getOpenFileName(self, "Open Quiz", "", "Quizzes (*.json)")[0]
        self.quiz = Quiz(self.quizPath)
        quizName = os.path.splitext(os.path.basename(self.quizPath))[0]
        self.quizNameBox.setText(quizName)
        self.refreshView()

    def saveQuiz(self):
        self.quiz.saveQuiz()

    def editQuestion(self):
        question = str(self.listView.currentRow() + 1)
        self.dialog = QnAWidget()
        q = self.quiz.data[question]["question"]
        self.dialog.question.setText(q)
        form = self.quiz.data[question]["form"]
        if form == "written":
            self.dialog.addChoice(self.quiz.data[question]["answer"][0])
        elif form == "multipleChoice":
            self.dialog.multipleChoice()
            for a in  self.quiz.data[question]["answer"]:
                self.dialog.addChoice(a)
        else:
            pass
        self.dialog.trigger[str, list].connect(self.addToQuiz)
        self.deleteQuestion()

    def deleteQuestion(self):
        q = str(self.listView.currentRow() + 1)
        self.quiz.deleteQuestion(q)
        self.refreshView()
    
    def add(self):
        self.addDialog = AnswerTypeDialog()
        self.addDialog.clicked[str].connect(self.qna)
        
    def qna(self, reply):
        self.reply = reply
        self.dialog = QnAWidget(reply)
        self.dialog.addChoice()
        self.dialog.trigger[str, list].connect(self.addToQuiz)

    def addToQuiz(self, q, a):
        try:
            self.quiz.addQuestion(q, a, self.reply)
        except AttributeError:
            self.newQuiz()
        self.refreshView()
        self.saveQuiz()

    def refreshView(self):
        self.listView.clear()
        for question in self.quiz.data:
            self.listView.addItem(self.quiz.data[question]["question"])

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)
        mEdit = menu.addAction("Edit")
        mEdit.triggered.connect(self.editQuestion)
        mDelete = menu.addAction("Delete")
        mDelete.triggered.connect(self.deleteQuestion)
        menu.exec_(event.globalPos())


class AnswerTypeDialog(QtWidgets.QDialog):
    ''' Dialog for selecting response to question type '''
    clicked = QtCore.Signal(str)

    def __init__(self, parent=None):
        super(AnswerTypeDialog, self).__init__()
        self.resize(366, 56)
        self.layout = QtWidgets.QHBoxLayout()
        self.writtenBtn = QtWidgets.QPushButton()
        self.layout.addWidget(self.writtenBtn)
        self.trueFalseBtn = QtWidgets.QPushButton()
        self.layout.addWidget(self.trueFalseBtn)
        self.multChoiceBtn = QtWidgets.QPushButton()
        self.layout.addWidget(self.multChoiceBtn)
        self.setLayout(self.layout)

        self.retranslateUi()

        self.writtenBtn.clicked.connect(lambda: self.setChoice("written"))
        self.trueFalseBtn.clicked.connect(lambda: self.setChoice("trueOrFalse"))
        self.multChoiceBtn.clicked.connect(lambda: self.setChoice("multipleChoice"))

        self.show()

    def retranslateUi(self):
        _translate = QtCore.QCoreApplication.translate
        self.setWindowTitle(_translate("Dialog", "Select Answer Type"))
        self.writtenBtn.setText(_translate("Dialog", "Written"))
        self.trueFalseBtn.setText(_translate("Dialog", "True or False"))
        self.multChoiceBtn.setText(_translate("Dialog", "Multiple Choice"))

    def setChoice(self, choice):
        self.clicked.emit(choice)
        self.close()


class QnAWidget(QtWidgets.QDialog):
    trigger = QtCore.Signal(str, list)
    
    def __init__(self, form=None, parent=None):
        super(QnAWidget, self).__init__(parent)
        self.choices = []

        self.setWindowTitle("Set QnA")
        self.layout = QtWidgets.QVBoxLayout()
        self.qLayout = QtWidgets.QVBoxLayout()
        self.layout.addLayout(self.qLayout)
        self.setLayout(self.layout)
        self.nameLbl = QtWidgets.QLabel("Question:")
        self.question = QtWidgets.QLineEdit()
        self.answerLbl = QtWidgets.QLabel("Answer:")
        self.qLayout.addWidget(self.nameLbl)
        self.qLayout.addWidget(self.question)
        self.qLayout.addWidget(self.answerLbl)

        if form == "multipleChoice":
            self.multipleChoice()
        elif form == "trueOrFalse":
            self.trueFalse()

        #buttons
        self.okBtn = QtWidgets.QPushButton("Ok")
        self.cancelBtn = QtWidgets.QPushButton("Cancel")
        self.okBtn.clicked.connect(self.returnQuestion)
        self.cancelBtn.clicked.connect(lambda: self.close())
        self.btnLayout = QtWidgets.QHBoxLayout()
        self.btnLayout.addWidget(self.cancelBtn, 0)
        self.btnLayout.addWidget(self.okBtn, 1)
        self.layout.addLayout(self.btnLayout)

        self.show()

    def trueFalse(self):
        self.trueBtn = QtWidgets.QPushButton("True")
        self.falseBtn = QtWidgets.QPushButton("False")
        self.trueBtn.clicked.connect(self.returnQuestion)
        self.falseBtn.clicked.connect(self.returnQuestion)
        self.layout.addWidget(self.addBtn)

    def multipleChoice(self):
        self.addBtn = QtWidgets.QPushButton("+")
        self.addBtn.clicked.connect(self.addChoice)
        self.layout.addWidget(self.addBtn)

    def addChoice(self, text=None):
        self.choices.append(QtWidgets.QLineEdit())
        self.qLayout.addWidget(self.choices[-1])
        if text:
            self.choices[-1].setText(text)

    def returnQuestion(self):
        question = self.question.text()
        answers = [c.text() for c in self.choices]
        if question and answers != [""]:
            self.trigger.emit(question, answers)
            self.close()


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = Ui_QuizMaker()
    window.show()
    sys.exit(app.exec_())