import os
import sys
import json
import random
import time
import threading

import collections

class QuizMaster(object):
    timer = 5
    
    def __init__(self):
        try:
            with open("config.cfg", "r") as f:
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
            with open("config.cfg", "w") as f:
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

    def loadQuiz(self):
        return self.config["quizzes"][0]

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
            print("json exception")
            self.data = {}
        self.path = path
        totalQuestions = int(10 * len(self.data.keys()) / 100)
        self.previouslyAsked = collections.deque(maxlen=totalQuestions)


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
        if self.data.keys():
            total = [int(i) for i in (self.data.keys())]
            # get next free index
            free = set(range (1, total[-1])) - set(total)
            if free:
                index = free
            else:
                index = str(len(total) + 1)
        elif self.data == {}:
            index = "1"
        self.data[index] = {"question": question,
                            "answer": answer,
                            "form": form,
                            "timesCorrect": 0,
                            "timesIncorrect": 0}
        self.saveQuiz()

    def deleteQuestion(self, question):
        del self.data[question]

    def pickUpQuestion(self):
        questions = [i for i in (self.data.keys())]
        num = random.choice(questions)
        return self.data[str(num)]

    def askQuestion(self):
        self.quiz = self.pickUpQuestion()
        while self.quiz in self.previouslyAsked:
            self.quiz = self.pickUpQuestion()
        self.previouslyAsked.extend(self.quiz)
        question = self.quiz["question"]
        form = self.quiz["form"]
        return question, form

    def checkAnswer(self, response):
        answerList = self.quiz["answer"]
        for answer in answerList:
            if response.lower() in answer.lower():
                self.quiz["timesCorrect"] += 1
                self.saveQuiz()
                return "Correct!"
            else:
                self.quiz["timesIncorrect"] += 1
                self.saveQuiz()
                return "Wrong!\n{}".format(answerList)
        