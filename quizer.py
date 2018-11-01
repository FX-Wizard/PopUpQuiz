import os
import sys
import json
import random
import time
import threading


class QuizMaster(object):
    timer = 5
    
    def __init__(self):
        try:
            with open("config.json", "r") as f:
                self.config = json.load(f)
        except IOError:
            self.config = {}
            self.config["timer"] = self.timer

        # for quiz in self.config["quizzes"]:
        #     if quiz["name"] in activeList:
        #         self.quizList.append(quiz)

        self.setQuestionTime(self.config["timer"])

    def saveConfig(self):
        self.config["timer"] = self.timer
        try:
            with open("config.json", "w") as f:
                json.dump(self.config, f, sort_keys=True, indent=4)
        except IOError as error:
            raise error

    def activateQuiz(self, quiz):
        self.config["quizzes"][quiz]["active"] = True

    def deactivateQuiz(self, quiz):
        self.config["quizzes"][quiz]["active"] = False

    def newQuiz(self, path):
        quiz = os.path.basename(path)
        self.config["quizzes"][quiz] = {
            "path": path,
            "active": True}
        return Quiz(path)

    def loadQuiz(self, path):
        pass

    @classmethod
    def getQuestionTime(cls):
        time = cls.timer
        return time

    @classmethod
    def setQuestionTime(cls, time):
        cls.timer = time


class Quiz(object):

    def __init__(self, path="questions.json"):
        try:
            with open(path, "r") as f:
                self.data = json.load(f)
        except:
            self.data = {}
        self.path = path

    def saveQuiz(self):
        try:
            with open(self.path, "w") as f:
                json.dump(self.data, f, sort_keys=True, indent=4)
        except IOError as error:
            raise error

    def addQuestion(self, question, answer, form):
        '''
        @param form = written, trueOrFalse, multipleChoice
        '''
        total = [int(i) for i in (self.data.keys())]
        # get next free index
        free = set(range (1, total[-1])) - set(total)
        if free:
            index = free
        else:
            index = str(len(total) + 1)
        self.data[index] = {"question": question,
                            "answer": answer,
                            "form": form,
                            "timesCorrect": 0,
                            "timesIncorrect": 0}
        self.saveQuiz()

    def deleteQuestion(self, question):
        del self.data[question]

    def askQuestion(self):
        questions = [i for i in (self.data.keys())]
        num = random.choice(questions)
        self.quiz = self.data[str(num)]
        question = self.quiz["question"]
        form = self.quiz["form"]
        return question, form

    def checkAnswer(self, response):
        answer = self.quiz["answer"]
        if response in answer:
            self.quiz["timesCorrect"] += 1
            self.saveQuiz()
            return "Correct!"
        else:
            self.quiz["timesIncorrect"] += 1
            self.saveQuiz()
            return "Wrong!"
        