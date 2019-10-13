import urllib
from bs4 import BeautifulSoup
import winsound
import requests
import webbrowser
import time
from PIL import ImageGrab
from PIL import Image
import time
import datetime
import os
from PIL import Image
import pytesseract
import argparse
import cv2
import numpy as np
import os
import time
import itertools
from string import punctuation
import re
from threading  import Thread
import pyautogui
start = time.time()

####
# taking screenShot
####
takeScreenshot = True
pytesseract.pytesseract.tesseract_cmd = 'C:/Program Files (x86)/Tesseract-OCR/tesseract'


# take screenShot
if(takeScreenshot):
    print("Taking Screenshots")
    time.sleep(1)
    winsound.Beep(500,500)
    #img = ImageGrab.grab(bbox=(1,150,1190-529,840))
    img = ImageGrab.grab(bbox=(529,150,1190,840))

    img.save("screenshot.png")

# do image processing and text finding
image = cv2.imread("screenshot.png")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
gray = cv2.threshold(gray, 0, 255,0)[1]
gray = cv2.medianBlur(gray, 3)
kernel = np.ones((3, 3), np.uint8)
gray = cv2.dilate(gray, kernel, iterations=1)

cv2.imwrite("result_bw.png", gray)
print("Finished Screenshots")
# 4 worked the best
text = pytesseract.image_to_string(Image.open("result_bw.png"),config="--psm 4")
print(text)
#time.sleep(2)
# some text processing
erroneus = ["1","F-","|","-"]
replace  = ["I","F","I","F"]
alpha = "ABCDEFGHIJKLMNOPQRSTUVWXY"

# This bit fixes any stuck together letters
text = text.split("\n")
for k in range(5):
    for i in range(len(text)):
        for j in range(len(text[i])-1):
            if(text[i][j] in alpha and text[i][j+1] in alpha):
                text[i] = text[i][:j+1] + " " + text[i][j+1:]
                break
# This bit replaces mis read letters
for i in range(len(text)):
    text[i] = text[i].split()
    for j in range(len(text[i])):
        if(text[i][j] in erroneus):
            text[i][j] = replace[erroneus.index(text[i][j])]

# Rmoves the things that arn't letters
for i in range(len(text)):
    for j in range(len(text[i])):
        for k in range(len(text[i][j])):
            print(text[i][j][k])
            if(text[i][j][k] not in alpha):
                text[i][j] = text[i][j][:k] + text[i][j][k+1:]
                break


class Grid:

    def __init__(self,data):

        # starting position
        self.cursorX = 2
        self.cursorY = 2

        self.data = data
        if(len(self.data) != 5):
            print("\n\n\nScreenShot Error\n\n\n")
            print("\n Len: ",len(self.data))
            print(self)
            time.sleep(10)
        else:
            print("\n\n\nData Read Well\n\n\n")
        self.size = len(self.data)


        self.moves = []

        # these list will fill up and do
        # stuff as time progresses
        self.banRows = []
        self.banColumns = []

        # the final position
        self.answer =  [["A","B","C","D","E"],
                        ["F","G","H","I","J"],
                        ["K","L","M","N","O"],
                        ["P","Q","R","S","T"],
                        ["U","V","W","X","Y"]]

        # in what order each letter should be put in
        #self.order =   ["A","B","C","F","G","H","K","L","M","P","Q","R","D","I","N","S","E","J","O","U","V","W","X","Y","T",]

        # new order (get it)
        self.order =   ["A","B","C","D","F",
                        "G","H","I","K","L",
                        "M","N","P","Q","R",
                        "S","E","J","O","U",
                        "V","W","X","Y","T",]
        # where each letter should initially be directed to
        # this will make all the insertions happen

        #self.insertPos = [[0,3],[0,3],[0,3],[1,3],[1,3],[1,3],[2,3],[2,3],[2,3],[3,3],[3,3],[3,3],]

        self.insertPos = [[0,0],[0,1],[0,2],[0,3],
                          [1,4],[1,4],[1,4],[1,4],
                          [2,4],[2,4],[2,4],[2,4],
                          [3,4],[3,4],[3,4],[3,4],
                          [4,4],[4,4],[4,4],[4,4],
                          [4,4],[4,4],[4,4],[4,4],]

    def __str__(self):
        # makes things normal again
        printout = "\n"
        for row in self.data:
            for item in row:
                printout+=item + " "
            printout+="\n"
        printout += "\n\nCursor: "
        printout += str(self.cursorX)
        printout += ":"
        printout += str(self.cursorY)
        return printout


    def adjustCursor(self):
        """ When the cursors get into negative numbers
            this sorts them out again """
        if(self.cursorX < 0):
            self.cursorX += 5
        if(self.cursorY < 0):
            self.cursorY += 5
        if(self.cursorX > 4):
            self.cursorX -= 5
        if(self.cursorY > 4):
            self.cursorY -= 5
        return self.cursorX,self.cursorY

    def moveColumn(self,col,amount):
        """Shifts a column col by amount amount"""
        amount = self.deferAmount(amount)
        if(self.cursorX == col):
            self.cursorX,self.cursorY = self.adjustCursor()
            col = self.cursorX
        if(self.cursorY == col):
            self.cursorX,self.cursorY = self.adjustCursor()
            col = self.cursorY
        print("Moving column ",col," by ",amount)


        temp = [row[col] for row in self.data][:]
        for i in range(self.size):
            self.data[i][col] = temp[(i+amount)%self.size]
        # adds the moves to the move bank
        for i in range(abs(amount)):
            if(amount > 0):
                self.moves.append("w")
                self.cursorY -= 1
                #print("Cursor: ",self.cursorX,self.cursorY)
            else:
                self.moves.append("s")
                self.cursorY += 1
                #print("Cursor: ",self.cursorX,self.cursorY)
        self.cursorX,self.cursorY = self.adjustCursor()
        return self.data
    def moveRow(self,row,amount):
        """Shifts a row row by amount amount"""
        if(self.cursorX == row):
            self.cursorX,self.cursorY = self.adjustCursor()
            row = self.cursorX
        if(self.cursorY == row):
            self.cursorX,self.cursorY = self.adjustCursor()
            row = self.cursorY
        amount = self.deferAmount(amount)
        print("Moving row ",row," by ",amount)
        temp = self.data[row][:]
        for i in range(self.size):
            self.data[row][i] = temp[(i-amount)%self.size]
        # adds the moves to the move bank
        for i in range(abs(amount)):
            if(amount > 0):
                self.moves.append("d")
                self.cursorX += 1
                #print("Cursor: ",self.cursorX,self.cursorY)
            else:
                self.moves.append("a")
                self.cursorX -= 1
                #print("Cursor: ",self.cursorX,self.cursorY)
        return self.data


    def deferAmount(self,amount):
        """ Given a number, if its quicker to go
            backwards, then will go backwards"""
        if(amount >= 3):
            return amount - 5
        elif(amount <= -3):
            return amount + 5
        else:
            return amount

    def getLetterLoc(self,letter):
        """Finds the array indexes of a letter location"""
        for i in range(self.size):
            for j in range(self.size):
                if(self.data[i][j] == letter):
                    return([i,j])

    def navigateCursor(self,letter):
        """Writes down the moves needed to move
           the cursor onto the next letter you want"""
        letterPos = self.getLetterLoc(letter)
        print("Starting ")
        #print(letterPos,self.cursorX,self.cursorY)
        # this makes the letter finding be done in the least amount
        # of moves, making the whole solve quicker
        if(letterPos[1] > self.cursorX and letterPos[1] >= self.cursorX + 3):
            letterPos[1] -= 5
            #print("letterPos[1] -= 5")
        elif(letterPos[1] < self.cursorX and letterPos[1] <= self.cursorX - 3)    :
            letterPos[1] += 5
            #print("letterPos[1] += 5")

        if(letterPos[0] > self.cursorY and letterPos[0] >= self.cursorY + 3 ):
            letterPos[0] -= 5
            #print("letterPos[0] -= 5")
        elif(letterPos[0] < self.cursorY and letterPos[0] <= self.cursorY - 3):
            letterPos[0] += 5
            #print("letterPos[0] += 5")

        while(letterPos != [self.cursorY,self.cursorX]):
             if(letterPos[1] > self.cursorX):
                 self.moves.append("right")
                 #print("Right")
                 self.cursorX += 1
             if(letterPos[1] < self.cursorX):
                 self.moves.append("left")
                 #print("Left")
                 self.cursorX -= 1
             if(letterPos[0] > self.cursorY):
                 self.moves.append("down")
                 #print("down")
                 self.cursorY += 1
             if(letterPos[0] < self.cursorY):
                 self.moves.append("up")
                 #print("up")
                 self.cursorY -= 1
        self.adjustCursor()
        #print(letterPos,self.cursorX,self.cursorY)
        #time.sleep(1)

    def moveLetterToLocation(self,number):
        """Given a letter, it will move cursor
           to the letters location, then move the letter
           to the final position"""

        print("\n\n\n New Letter:  ",number,":",self.order[number]," Cursor: ",self.cursorX,self.cursorY,"\n\n\n")
        print(self)
        self.navigateCursor(self.order[number])
        targetSquare = self.insertPos[number]

        print("Cursor: ",self.cursorX,self.cursorY)
        print("Target Square: ",targetSquare)


        if(self.cursorY == targetSquare[0] and self.cursorX == targetSquare[1]):
            print("Letter already in position")
            if(number > 18):
                self.data = self.moveRow(targetSquare[0],-1)
            elif(number >17):
                # this is only for when the letter is O
                self.data = self.moveColumn(targetSquare[1],2)
            elif(number > 15):
                self.data = self.moveColumn(targetSquare[1],1)
            elif(number > 3):
                self.data = self.moveRow(targetSquare[0],-1)


        else:
            # the first 4 ones can be done in an even easier way
            if(number < 4):

                # the easiest case
                if(self.cursorY > 0):
                    print("This is the easy case")
                    self.data = self.moveRow(self.cursorY,targetSquare[1] - self.cursorX)
                    self.data = self.moveColumn(self.cursorX,self.cursorY - targetSquare[0])
                # this is the harder case
                else:
                    print("This is the hard case")
                    self.firstAlgorithm()
                    self.data = self.moveRow(self.cursorY,targetSquare[1] - self.cursorX)
                    self.data = self.moveColumn(self.cursorX,self.cursorY - targetSquare[0])
                print(self)
                #time.sleep(1)
            # these are the algs for the standard row insertions
            elif(number < 16):
                    # does alg if box is in an awkward place
                    if(targetSquare[0] == self.cursorY and targetSquare[1] > self.cursorX):
                        self.firstAlgorithm()


                    # if target y <= current cursor y
                    #    and target x > current cursor x
                    if(targetSquare[0] >= self.cursorY and targetSquare[1] < self.cursorX):
                        #now just move the thing down and carry on
                        self.moveItemBelowTarget(self.cursorY - targetSquare[0] - 1)


                    self.data = self.moveRow(self.cursorY,targetSquare[1] - self.cursorX)
                    self.data = self.moveColumn(self.cursorX,self.cursorY - targetSquare[0])
                    # final insertion for the square
                    self.data = self.moveRow(targetSquare[0],-1)
                    return self.data

            # these are the algs for the last column insertion
            elif(number < 19):
                print("Vertical line")
                # easy case
                if(self.cursorY >= self.insertPos[number][0]):
                    print("Easy Case")
                    self.data = self.moveRow(self.cursorY,targetSquare[1] - self.cursorX)
                    self.data = self.moveColumn(self.cursorX,self.cursorY - targetSquare[0] + 1)

                else:
                    print("")
                    self.secondAlgorithm()
                    self.data = self.moveRow(self.cursorY,targetSquare[1] - self.cursorX)
                    self.data = self.moveColumn(self.cursorX,self.cursorY - targetSquare[0] + 1)

                if(number == 18):
                    # this just needs to be done at the end of this secion
                    self.data = self.moveColumn(4,1)
            # for the last bit of the puzzle
            else:

                print("Final Case")

                # standard case
                if(self.cursorY == 3):
                    print("Standard Case")
                    self.moveColumn(self.cursorX,-1)
                    self.moveRow(self.cursorY,-1)
                    self.moves.append("right")
                    self.cursorX += 1
                    self.moveColumn(self.cursorX,1)

                # hard case
                else:
                    print("Hard Case")
                    self.thirdAlgorithim()




    def moveItemBelowTarget(self,amount):
        """When a block is in a tricky position, moves it down,
           before starting the algorithm"""
        print("Moving below with value of ",amount)
        # down until below
        self.moveColumn(self.cursorX,amount)

    def firstAlgorithm(self):
        """This goes through the moves to get out of a sticky situation"""
        #           s,d,up,left,w,right,down,down
        # s
        self.moveColumn(self.cursorX,-1)
        # d
        self.moveRow(self.cursorY,1)
        # up
        self.moves.append("up")
        self.cursorY -= 1
        # left
        self.moves.append("left")
        self.cursorX -= 1
        # w
        self.moveColumn(self.cursorX,1)
        # right
        self.moves.append("right")
        self.cursorX += 1
        # down down
        self.moves.append("down")
        self.moves.append("down")
        self.cursorY += 2

    def secondAlgorithm(self):
        """The algorithm for the verical column insert"""
        # want to move the current letter to
        # bottom right n times
        #  move 'a'
        # move 'right   '
        # move the opposite way n times
        # move the oppiste way again using arrow keys n times
        # left
        # d
        # w
        # will be used later
        moveDownValue = -1 * (4 - self.cursorY)
        # move to bottom right
        self.moveColumn(self.cursorX,moveDownValue)
        # a
        self.moveRow(self.cursorY,-1)
        # right
        self.moves.append("right")
        self.cursorX += 1
        # move right column back to normal
        self.moveColumn(self.cursorX,-moveDownValue)
        # put cursor back over letter
        for i in range(abs(moveDownValue)):
            self.moves.append("down")
            self.cursorY += 1
        # left
        self.moves.append("left")
        self.cursorX -= 1
        # d
        self.moveRow(self.cursorY,1)
        # w
        self.moveColumn(self.cursorX,1)

    def thirdAlgorithim(self):
        """This is for the final bottom row"""
        # move current item until in 5th row n times
        # move that column move
        # move cursor to bottom row and move -n times
        # move 5th column back up
        # and move to the lefft
        moveRightValue = (4 - self.cursorX)
        # move so characters is in 5th row
        self.moveRow(self.cursorY,moveRightValue)
        # move column move
        self.moveColumn(self.cursorX,-1)
        # up
        self.moves.append("up")
        self.cursorY -= 1
        # move things back into place
        self.moveRow(self.cursorY,-moveRightValue)
        for i in range(moveRightValue):
            self.moves.append("right")
            self.cursorX += 1
        #move column back into place
        self.moveColumn(self.cursorX,1)

        #move cursor back down
        self.moves.append("down")
        self.cursorY += 1
        # move new item to front of list
        self.moveRow(self.cursorY,-1)

    def inputMoves(self,delay):
        """Go through the generated list
           and input all the keys to solve the squares"""
        print("\nDoing moves: ",self.moves)
        if(delay == 0):
            pyautogui.press(self.moves)
            winsound.Beep(500,500)
        else:
            for i in range(0,len(self.moves),4):
                pyautogui.press(self.moves[i:i+4])
                time.sleep(delay)


grid = Grid(text)
alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
for i in range(23):
    print(grid)
    grid.moveLetterToLocation(i)
print(grid)
#print(grid.moves)
winsound.Beep(500,500)
time.sleep(7)
winsound.Beep(500,500)
grid.inputMoves(0.00001)
