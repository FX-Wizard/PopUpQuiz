import os
import unittest
from quizer import Quiz, QuizMaster


class QuizTest(unittest.TestCase):
    
    # def testMakeNewQuiz(self):
    #     testQuiz = Quiz("test.qiz")

    def setUp(self):
        self.testQuiz = Quiz("test.qiz")

    def testAddQuestion(self):
        self.testQuiz.addQuestion("test1", "test1", "written")

    def testAddTrueFalseQuestion(self):
        self.testQuiz.addQuestion("test2", "test2", "trueOrFalse")
    
    def testaddMultipleChoiceQuestion(self):
        self.testQuiz.addQuestion("test3", "test3", "multipleChoice")

    def testSaveQuiz(self):
        self.testQuiz.saveQuiz()
        # os.path.isfile()

    def testLoadQuiz(self):
        self.testQuiz = None
        self.testQuiz = Quiz("test.qiz")

    def testAskQuestion(self):
        self.testQuiz.askQuestion()

    def testAnswerRight(self):
        question = self.testQuiz.askQuestion()
        answer = self.testQuiz.quiz["answer"]
        self.assertEqual(self.testQuiz.checkAnswer(answer), "Correct!")

    def testAnswerWrong(self):
        pass

    def tearDown(self):
        os.unlink("test.qiz")


if __name__ == "__main__":
    unittest.main()