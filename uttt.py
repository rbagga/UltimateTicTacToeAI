#print#print#print(from time import sleep
#from math import inf
from random import randint
import random
import copy

class ultimateTicTacToe:
    def __init__(self):
        """
        Initialization of the game.
        """
        self.board=[['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_'],
                    ['_','_','_','_','_','_','_','_','_']]
        self.maxPlayer='X'
        self.minPlayer='O'
        self.maxDepth=3
        #The start indexes of each local board
        self.globalIdx=[(0,0),(0,3),(0,6),(3,0),(3,3),(3,6),(6,0),(6,3),(6,6)]

        #Start local board index for reflex agent playing
        self.startBoardIdx=4
        #self.startBoardIdx=randint(0,8)

        #utility value for reflex offensive and reflex defensive agents
        self.winnerMaxUtility=10000
        self.twoInARowMaxUtility=500
        self.preventThreeInARowMaxUtility=100
        self.cornerMaxUtility=30

        self.winnerMinUtility=-10000
        self.twoInARowMinUtility=-100
        self.preventThreeInARowMinUtility=-500
        self.cornerMinUtility=-30

        self.explored = 0
        self.currPlayer=True


        #CUSTOM VARIABLES & FUNCTIONS
        #self.initalLastMove = (4, 4)
        self.lastMovePlayed = (4,4)
        self.utilErrorValue = -123456
        self.minPlayerSmart = False
        self.maxPlayerSmart = False
        self.statesExplored = 0
        #self.movesList = []
        self.gameBoardList = []

    """
    this function returns the globalidx of the next box the next move must be
    played in, given the coordinate of the last move played.
    """
    def getNextPlayBox(self):
        x = (self.lastMovePlayed[0] % 3) * 3
        y = (self.lastMovePlayed[1] % 3) * 3
        return (x,y)

    """
    this function returns the globalIdx of the currentPlayBox.
    """
    def getCurrentPlayBox(self):
        x = int (self.lastMovePlayed[0] / 3) * 3
        y = int (self.lastMovePlayed[1] / 3) * 3
        #print("LAST move", end = "")
        #print(self.lastMovePlayed)
        #print("translates to: ")
        #print((x,y))
        return ((x,y))
    """
    this function returns an array where each element is a tuple, where
    tuple[0] = the numpy array of the board grid with a new mark placed on it
    tuple[1] = the tuple of the coordinate of the new position.
    """

    def getNextBoards(self, board, isMax):
        nextBoards = []
#        copy = copy.deepcopy(board)

        if (self.checkMovesLeft()):
            xbox = self.getNextPlayBox()[0]
            ybox = self.getNextPlayBox()[1]

        # print("HELLO WTF")
        # for point in self.getNextPoints():
        #     print(point)

        #print(" ")
        for point in self.getNextPoints():
            current_copy = copy.deepcopy(self.board)
            if (isMax):
                current_copy[point[0]][point[1]] = 'O'
            else:
                current_copy[point[0]][point[1]] = 'X'

            nextBoards.append((current_copy, point))

        return nextBoards



    """
    returns an array of tuple coords of
    valid moves in the box that must be played in next.

    """
    def getNextPoints(self):

        nextPoints = []

        xbox = self.getNextPlayBox()[0]
        ybox = self.getNextPlayBox()[1]

        for i in range(3):
            for j in range(3):
                if self.board[xbox + i][ybox  + j] == '_':
                    current_copy = copy.deepcopy(self.board)
                    next = (xbox + i, ybox + j)
                    nextPoints.append(next)

        return nextPoints



    """
    returns the utility score of a self.board state.
    coordinates represented as (x,y), where x=col, y=row; but board coords are like: board[row][col]
    gets the 'smart' utility, so only considers both the X scores and O scores. Still uses rule hierarchy
    """
    def getSmartUtility(self, locBoard):
        winner = self.checkWinner()
        if winner > 0:
            return 10000 #rule 1
        elif winner < 0:
            return -100000
        else:

            utility = 0
            #xbox = getNextPlayBox()[0]
            #ybox = getNextPlayBox()[1]
            xbox = 0
            ybox = 0

            maxPlayer = 'X'
            minPlayer = 'O'

            #the score is rated by levels. if a higher rule is in effect, the lower rule should be disregarded
            #X = offensive agent, O = defensive agent

            #check 2 in row, incr utility score by 500 for X, or decr score by 100 for O, for each unblocked 2 in a row (rule 2)
            #if blocked opponent's 2-in-a-row, then incr score by 100 for X, or decr score by 500 for O

            rule2UtilX = 0
            useRule2X = 0 #swap to 1 for the first time rule2UtilX is changed
            rule3UtilX = 0 #calc these in the same loop to save time, if useRule2X is 1, then rule3UtilX is unused

            rule2UtilO = 0
            useRule2O = 0 #swap to 1 for the first time rule2UtilO is changed
            rule3UtilO = 0  #calc this in the same loop to save time, if useRule2O is 1, then rule3UtilO is unused

            accepted = {}
            for row in range(ybox, ybox+9):
                for col in range(xbox, xbox+9):
                    curPos = (col, row)
                    accepted[curPos] = []

            for yFullBoard in range(0, 3):
                ybox = 3*yFullBoard
                for xFullBoard in range(0, 3):
                    xbox = 3*xFullBoard
                    for row in range(ybox, ybox+3):
                        for col in range(xbox, xbox+3):
                            spot = locBoard[row][col]
                            curPos = (col, row)
                            if spot=='_': #nothing here or this spot has already been confirmed to be in a row, so we want to avoid double counting
                                continue
                            elif spot==maxPlayer: #offensive agent 'X'
                                rowSeqCoord = self.checkEWSeq(locBoard, curPos, maxPlayer, minPlayer, xbox) #check row seq
                                if rowSeqCoord is not None and rowSeqCoord[1]==(-1,-1):
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        #print("X row")
                                        rule2UtilX += 500
                                        if useRule2X == 0:
                                            useRule2X = 1
                                elif rowSeqCoord is not None and rowSeqCoord[1]!=(-1,-1):
                                    #we check rowSeqCoord[1] because we care about O blocking for the smart getUtility function
                                    #print("O block row X")
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        rule2UtilO -= 500
                                        if useRule2O == 0:
                                            useRule2O = 1
                                colSeqCoord = self.checkNSSeq(locBoard, curPos, maxPlayer, minPlayer, ybox) #check col seq
                                if colSeqCoord is not None and colSeqCoord[1]==(-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        #print("X col")
                                        rule2UtilX += 500
                                        if useRule2X == 0:
                                            useRule2X = 1
                                elif colSeqCoord is not None and colSeqCoord[1]!=(-1,-1):
                                    #we check colSeqCoord[1] because we care about O blocking for the smart getUtility function
                                    #print("O block col X")
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        rule2UtilO -= 500
                                        if useRule2O == 0:
                                            useRule2O = 1
                                diagSeqList = self.checkDiagSeq(locBoard, curPos, maxPlayer, minPlayer, (xbox, ybox)) #check diag seq
                                if len(diagSeqList[0]) != 0:
									#if len(diagSeqList[1])==0:
                                        #print("Something went wrong in getSmartUtility, diag lens don't match")
                                    if len(diagSeqList[1])==1 and diagSeqList[1][0]==(-1,-1):
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            #print("X diag")
                                            rule2UtilX += 500
                                            if useRule2X == 0:
                                                useRule2X = 1
                                    elif len(diagSeqList[1])==1 and diagSeqList[1][0]!=(-1,-1):
                                        #print("O block diag X")
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            rule2UtilO -= 500
                                            if useRule2O == 0:
                                                useRule2O = 1
                                    elif len(diagSeqList[1])>1:
                                        for x in range(len(diagSeqList[0])):
                                            second = diagSeqList[0][x]
                                            block = diagSeqList[1][x]
                                            if block == (-1,-1):
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    #print("X diag")
                                                    rule2UtilX += 500
                                                    if useRule2X == 0:
                                                        useRule2X = 1
                                            else:
                                                #print("O block diag X")
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    rule2UtilO -= 500
                                                    if useRule2O == 0:
                                                        useRule2O = 1
                                #calc rule3Util for later if becomes necessity
                                #check if corner, if yes, then incr by 30
                                if (col%3==0 and row%3==0) or (col%3==2 and row%3==0) or (col%3==0 and row%3==2) or (col%3==2 and row%3==2):
                                    rule3UtilX += 30
                            elif spot==minPlayer: #defensive agent 'O', we use this only to find instances of X blocking
                                rowSeqCoord = self.checkEWSeq(locBoard, curPos, minPlayer, maxPlayer, xbox)
                                if rowSeqCoord is not None and rowSeqCoord[1]==(-1,-1):
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        #print("O row")
                                        rule2UtilO -= 100
                                        if useRule2O == 0:
                                            useRule2O = 1
                                elif rowSeqCoord is not None and rowSeqCoord[1]!=(-1,-1):
                                    #we check rowSeqCoord[1] because we care about the blocking X, but don't add to setAccepted because we want to be able to check for 2-in-row later if necessary, since X blocking doesn't cause double counting
                                    #print("X block row O")
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        rule2UtilX += 100
                                        if useRule2X == 0:
                                            useRule2X = 1
                                colSeqCoord = self.checkNSSeq(locBoard, curPos, minPlayer, maxPlayer, ybox)
                                if colSeqCoord is not None and colSeqCoord[1]==(-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        #print("O col")
                                        rule2UtilO -= 100
                                        if useRule2O == 0:
                                            useRule2O = 1
                                elif colSeqCoord is not None and colSeqCoord[1]!=(-1,-1):
                                    #print("X block col O")
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        rule2UtilX += 100
                                        if useRule2X == 0:
                                            useRule2X = 1
                                diagSeqList = self.checkDiagSeq(locBoard, curPos, minPlayer, maxPlayer, (xbox, ybox))
                                if len(diagSeqList[0]) != 0:
									#if len(diagSeqList[1]) == 0:
                                        #print("Something went wrong in getSmartUtility, diag lens don't match, minPlayer")
                                    if len(diagSeqList[1])==1 and diagSeqList[1][0]==(-1,-1):
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            #print("O diag")
                                            rule2UtilO -= 100
                                            if useRule2O == 0:
                                                useRule2O = 1
                                    elif len(diagSeqList[1])==1 and diagSeqList[1][0]!=(-1,-1):
                                        #print("X block diag O")
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            rule2UtilX += 100
                                            if useRule2X == 0:
                                                useRule2X = 1
                                    elif len(diagSeqList[1])>1:
                                        for x in range(len(diagSeqList[0])):
                                            second = diagSeqList[0][x]
                                            block = diagSeqList[1][x]
                                            if block == (-1,-1):
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    #print("O diag")
                                                    rule2UtilO -= 100
                                                    if useRule2O == 0:
                                                        useRule2O = 1
                                            else:
                                                #print("X block diag O")
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    rule2UtilX += 100
                                                    if useRule2X == 0:
                                                        useRule2X = 1
                                #check if corner, if yes, then decr by 30
                                if (col%3==0 and row%3==0) or (col%3==2 and row%3==0) or (col%3==0 and row%3==2) or (col%3==2 and row%3==2):
                                    rule3UtilO -= 30




            #check corners #rule 3 (only if none of rule 2 is satisfied)
            #If X, incr score by 30 if corner taken
            #If O, decr score by 30 if corner taken
            #replacing the rule hierarchy scoring system with counting the 3rd rule as well
            if useRule2X != 0:
                utility = rule2UtilX
            else:
                utility = rule3UtilX
            if useRule2O != 0:
                utility += rule2UtilO
            else:
                utility += rule3UtilO

            return (utility)

            """
    returns the utility score of a board state.
    coordinates represented as (x,y), where x=col, y=row; but board coords are like: board[row][col]
    gets the dumb utility, so only considers the O scores and disregards X scores entirely. Still uses rule hierarchy
    """
    def getOUtility(self, locBoard):
        #self.explored += 1
        # print("o util called")
        winner = self.checkWinner()
        #if winner > 0:
        #     return 10000
        if winner < 0:
            return -10000
        else:
            utility = 0
            xbox = 0
            ybox = 0
            rule2Util = 0
            useRule2 = 0
            rule3Util = 0
            accepted = {}
            for row in range(ybox, ybox+9):
                for col in range(xbox, xbox+9):
                    curPos = (col, row)
                    accepted[curPos] = []

            for yFullBoard in range(0, 3):
                ybox = 3*yFullBoard
                for xFullBoard in range(0, 3):
                    xbox = 3*xFullBoard
                    for row in range(ybox, ybox+3):
                        for col in range(xbox, xbox+3):
                            spot = locBoard[row][col]
                            curPos = (col, row)
                            #print("The curPos is: ", curPos, end="")
                            #print(", and the (col, row) is: ", (col, row))
                            if spot=='_': #nothing here
                                continue
                            elif spot==self.minPlayer: #defensive agent 'O'
                                rowSeqCoord = self.checkEWSeq(locBoard, curPos, self.minPlayer, self.maxPlayer, xbox) #check row seq
                                if rowSeqCoord is not None and rowSeqCoord[1] == (-1,-1): #there is a two-in-a-row and there isn't a blocking X
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        rule2Util -= 100
                                        if useRule2 == 0:
                                            useRule2 = 1
                                colSeqCoord = self.checkNSSeq(locBoard, curPos, self.minPlayer, self.maxPlayer, ybox) #check col seq
                                if colSeqCoord is not None and colSeqCoord[1] == (-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        rule2Util -= 100
                                        if useRule2 == 0:
                                            useRule2 = 1
                                diagSeqList = self.checkDiagSeq(locBoard, curPos, self.minPlayer, self.maxPlayer, (xbox, ybox)) #check diag seq
                                if len(diagSeqList[0]) != 0: #there is at least 1 two-in-a-row
                                    #if len(diagSeqList[1]) == 0:
                                        #print("Something went wrong in getOUtility, diag lens don't match")
                                    if len(diagSeqList[0])==1 and diagSeqList[1][0]==(-1,-1): #curPos is a corner, so there can only be one diagonal seq and the seq is unblocked
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            rule2Util -= 100
                                            if useRule2 == 0:
                                                useRule2 = 1
                                    elif len(diagSeqList[0])>1:
                                        for x in range(len(diagSeqList[0])):
                                            second = diagSeqList[0][x]
                                            block = diagSeqList[1][x]
                                            if block==(-1,-1):
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    rule2Util -= 100
                                                    if useRule2 == 0:
                                                        useRule2 = 1
                                #calc rule3Util for later if becomes necessity
                                #check if corner, if yes, then incr by 30
                                #if (col%3==0 and row%3==0) or (col%3==2 and row%3==0) or (col%3==0 and row%3==2) or (col%3==2 and row%3==2):
                                if (col == xbox and row == ybox) or (col == xbox+2 and row == ybox) or (col == xbox and row == ybox+2) or (col == xbox+2 and row == ybox+2):
                                    # print("corner evaluated at: ", end = "")
                                    # print((col, row))
                                    # print("xbox: ", xbox, end="")
                                    # print(", ybox: ", ybox)
                                    rule3Util -= 30
                            elif spot==self.maxPlayer: #offensive agent 'X', we use this only to find instances of O blocking
                                rowSeqCoord = self.checkEWSeq(locBoard, curPos, self.maxPlayer, self.minPlayer, xbox)
                                if rowSeqCoord is not None and rowSeqCoord[1] == (-1,-1):
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                elif rowSeqCoord is not None and rowSeqCoord[1] != (-1,-1):
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        rule2Util -= 500
                                        if useRule2 == 0:
                                            useRule2 = 1
                                colSeqCoord = self.checkNSSeq(locBoard, curPos, self.maxPlayer, self.minPlayer, ybox)
                                if colSeqCoord is not None and colSeqCoord[1] == (-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                elif colSeqCoord is not None and colSeqCoord[1] != (-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        rule2Util -= 500
                                        if useRule2 == 0:
                                            useRule2 = 1
                                diagSeqList = self.checkDiagSeq(locBoard, curPos, self.maxPlayer, self.minPlayer, (xbox, ybox))
                                if len(diagSeqList[0]) != 0:
    								#if len(diagSeqList[1]) == 0:
                                        # print("Something went wrong in getOUtility, diag lens don't match; spot is minPlayer")
                                    if len(diagSeqList[0])==1 and diagSeqList[1][0]==(-1,-1): #curPos is a corner, so there can only be one diagonal seq and the seq is unblocked
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                    elif len(diagSeqList[0])==1 and diagSeqList[1][0]!=(-1,-1):
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            rule2Util -= 500
                                            if useRule2 ==0:
                                                useRule2 = 1
                                    elif len(diagSeqList[0])>1:
                                        for x in range(len(diagSeqList[0])):
                                            second = diagSeqList[0][x]
                                            block = diagSeqList[1][x]
                                            if block==(-1,-1):
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                            else:
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    rule2Util -= 500
                                                    if useRule2 == 0:
                                                        useRule2 = 1




        #check corners #rule 3 (only if none of rule 2 is satisfied)
        #If X, incr score by 30 if corner taken
        #If O, decr score by 30 if corner taken
        if useRule2 != 0:
            utility = rule2Util
        else:
            utility = rule3Util

        return utility

        #check corners #rule 3 (only if none of rule 2 is satisfied)
        #If X, incr score by 30 if corner taken
        #If O, decr score by 30 if corner taken
        #replacing the rule hierarchy scoring system with counting the 3rd rule as well
        if useRule2X != 0:
            utility = rule2UtilX
        else:
            utility = rule3UtilX
        if useRule2O != 0:
            utility += rule2UtilO
        else:
            utility += rule3UtilO

        return utility

            #return rule2UtilX + rule3UtilX + rule2UtilO + rule3UtilO




    """
    returns the utility score of a board state.
    coordinates represented as (x,y), where x=col, y=row; but board coords are like: board[row][col]
    gets the dumb utility, so only considers the X scores and disregards O scores entirely. Still uses rule hierarchy
    TODO: fix bug: when there is a blocked 2-in-a-row, the function (smart too) gives full points for the row, instead of zero, or corner points
    """
    """
    returns the utility score of a board state.
    coordinates represented as (x,y), where x=col, y=row; but board coords are like: board[row][col]
    gets the dumb utility, so only considers the X scores and disregards O scores entirely. Still uses rule hierarchy
    TODO: fix bug: when there is a blocked 2-in-a-row, the function (smart too) gives full points for the row, instead of zero, or corner points
    """
    def getUtility(self, locBoard):
        # print("LELLO?")
        #self.explored += 1
        # print(" x util called")
        winner = self.checkWinner()
        if winner > 0:
            #print("nvm")
            return 10000 #rule 1
        # elif winner < 0:
        #     print("nvm")
        #     #return -10000
        else:

            utility = 0
            xbox = 0
            ybox = 0

            #the score is rated by levels. if a higher rule is in effect, the lower rule should be disregarded
            #X = offensive agent, O = defensive agent

            #check 2 in row, incr utility score by 500 for X, or decr score by 100 for O, for each unblocked 2 in a row (rule 2)
            #if blocked opponent's 2-in-a-row, then incr score by 100 for X, or decr score by 500 for O

            rule2Util = 0
            useRule2 = 0 #swap to 1 for the first time rule2Util is changed
            rule3Util = 0 #calc these in the same loop to save time, if useRule2 is 1, then rule3Util is unused

            accepted = {}
            for row in range(ybox, ybox+9):
                for col in range(xbox, xbox+9):
                    curPos = (col, row)
                    accepted[curPos] = []

            for yFullBoard in range(0, 3):
                ybox = 3*yFullBoard
                for xFullBoard in range(0, 3):
                    xbox = 3*xFullBoard
                    for row in range(ybox, ybox+3):
                        for col in range(xbox, xbox+3):
                            spot = locBoard[row][col]
                            curPos = (col, row)
                            #print("The curPos is: ", curPos, end="")
                            #print(", and the (col, row) is: ", (col, row))
                            if spot=='_': #nothing here
                                continue
                            elif spot==self.maxPlayer: #offensive agent 'X'
                                rowSeqCoord = self.checkEWSeq(locBoard, curPos, self.maxPlayer, self.minPlayer, xbox) #check row seq
                                if rowSeqCoord is not None and rowSeqCoord[1] == (-1,-1): #there is a two-in-a-row and there isn't a blocking O
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        rule2Util += 500
                                        if useRule2 == 0:
                                            useRule2 = 1
                                colSeqCoord = self.checkNSSeq(locBoard, curPos, self.maxPlayer, self.minPlayer, ybox) #check col seq
                                if colSeqCoord is not None and colSeqCoord[1] == (-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        rule2Util += 500
                                        if useRule2 == 0:
                                            useRule2 = 1
                                diagSeqList = self.checkDiagSeq(locBoard, curPos, self.maxPlayer, self.minPlayer, (xbox, ybox)) #check diag seq
                                if len(diagSeqList[0]) != 0: #there is at least 1 two-in-a-row
    								#if len(diagSeqList[1]) == 0:
                                        # print("Something went wrong in getUtility, diag lens don't match")
                                    if len(diagSeqList[0])==1 and diagSeqList[1][0]==(-1,-1): #curPos is a corner, so there can only be one diagonal seq and the seq is unblocked
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            rule2Util += 500
                                            if useRule2 == 0:
                                                useRule2 = 1
                                    elif len(diagSeqList[0])>1:
                                        for x in range(len(diagSeqList[0])):
                                            second = diagSeqList[0][x]
                                            block = diagSeqList[1][x]
                                            if block==(-1,-1):
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    rule2Util += 500
                                                    if useRule2 == 0:
                                                        useRule2 = 1
                                #calc rule3Util for later if becomes necessity
                                #check if corner, if yes, then incr by 30
                                #if (col%3==0 and row%3==0) or (col%3==2 and row%3==0) or (col%3==0 and row%3==2) or (col%3==2 and row%3==2):
                                if (col == xbox and row == ybox) or (col == xbox+2 and row == ybox) or (col == xbox and row == ybox+2) or (col == xbox+2 and row == ybox+2):
                                    # print("corner evaluated at: ", end = "")
                                    # print((col, row))
                                    # print("xbox: ", xbox, end="")
                                    # print(", ybox: ", ybox)
                                      rule3Util += 30
                            elif spot==self.minPlayer: #defensive agent 'O', we use this only to find instances of X blocking
                                rowSeqCoord = self.checkEWSeq(locBoard, curPos, self.minPlayer, self.maxPlayer, xbox)
                                if rowSeqCoord is not None and rowSeqCoord[1] == (-1,-1):
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                elif rowSeqCoord is not None and rowSeqCoord[1] != (-1,-1):
                                    if rowSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(rowSeqCoord[0])
                                        if curPos not in accepted[rowSeqCoord[0]]:
                                            accepted[rowSeqCoord[0]].append(curPos)
                                        rule2Util += 100
                                        if useRule2 == 0:
                                            useRule2 = 1
                                colSeqCoord = self.checkNSSeq(locBoard, curPos, self.minPlayer, self.maxPlayer, ybox)
                                if colSeqCoord is not None and colSeqCoord[1] == (-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                elif colSeqCoord is not None and colSeqCoord[1] != (-1,-1):
                                    if colSeqCoord[0] not in accepted[curPos]:
                                        accepted[curPos].append(colSeqCoord[0])
                                        if curPos not in accepted[colSeqCoord[0]]:
                                            accepted[colSeqCoord[0]].append(curPos)
                                        rule2Util += 100
                                        if useRule2 == 0:
                                            useRule2 = 1
                                diagSeqList = self.checkDiagSeq(locBoard, curPos, self.minPlayer, self.maxPlayer, (xbox, ybox))
                                if len(diagSeqList[0]) != 0:
                                    if len(diagSeqList[1]) == 0:
                                        print("Something went wrong in getUtility, diag lens don't match; spot is minPlayer")
                                    if len(diagSeqList[0])==1 and diagSeqList[1][0]==(-1,-1): #curPos is a corner, so there can only be one diagonal seq and the seq is unblocked
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                    elif len(diagSeqList[0])==1 and diagSeqList[1][0]!=(-1,-1):
                                        if diagSeqList[0][0] not in accepted[curPos]:
                                            accepted[curPos].append(diagSeqList[0][0])
                                            if curPos not in accepted[diagSeqList[0][0]]:
                                                accepted[diagSeqList[0][0]].append(curPos)
                                            rule2Util += 100
                                            if useRule2 ==0:
                                                useRule2 = 1
                                    elif len(diagSeqList[0])>1:
                                        for x in range(len(diagSeqList[0])):
                                            second = diagSeqList[0][x]
                                            block = diagSeqList[1][x]
                                            if block==(-1,-1):
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                            else:
                                                if second not in accepted[curPos]:
                                                    accepted[curPos].append(second)
                                                    if curPos not in accepted[second]:
                                                        accepted[second].append(curPos)
                                                    rule2Util += 100
                                                    if useRule2 == 0:
                                                        useRule2 = 1




                #check corners #rule 3 (only if none of rule 2 is satisfied)
                #If X, incr score by 30 if corner taken
                #If O, decr score by 30 if corner taken
            if useRule2 != 0:
                utility = rule2Util
            else:
                utility = rule3Util

            return utility
    """
    checks for two in a row on the curr row for the player at that point
    returns None if no 2-in-a-row, otherwise list of coords, where first is the coord of the second symbol and the second is the coord of the blocking symbol if it exists, (-1,-1) if not
    player = 'X' or 'O'
    opp = opposing player = 'O' or 'X'
    """
    def checkEWSeq(self, locBoard, coord, player, opp, localStartCol):
        coordCol = coord[0]
        coordRow = coord[1]
        if coordCol == localStartCol and locBoard[coordRow][coordCol+1] == player:
            #first col, only check one to right (no winner, since checked before this call)
            if locBoard[coordRow][coordCol+2]=='_':
                return [(coordCol+1, coordRow), (-1,-1)]
            elif locBoard[coordRow][coordCol+2]==opp:
                return [(coordCol+1, coordRow), (coordCol+2, coordRow)]
        elif coordCol == localStartCol and locBoard[coordRow][coordCol+2] == player:
            if locBoard[coordRow][coordCol+1]=='_':
                return [(coordCol+2, coordRow), (-1,-1)]
            elif locBoard[coordRow][coordCol+1]==opp:
                return [(coordCol+2, coordRow), (coordCol+1, coordRow)]
        elif coordCol == localStartCol+1: #middle col
            if locBoard[coordRow][coordCol+1] == player and locBoard[coordRow][coordCol-1]=='_':
                return [(coordCol+1, coordRow), (-1,-1)]
            elif locBoard[coordRow][coordCol-1]==player and locBoard[coordRow][coordCol+1] == '_':
                return [(coordCol-1, coordRow), (-1,-1)]
            elif locBoard[coordRow][coordCol+1] == player and locBoard[coordRow][coordCol-1]==opp:
                return [(coordCol+1, coordRow), (coordCol-1, coordRow)]
            elif locBoard[coordRow][coordCol-1]==player and locBoard[coordRow][coordCol+1] == opp:
                return [(coordCol-1, coordRow), (coordCol+1, coordRow)]

        elif coordCol == localStartCol+2 and locBoard[coordRow][coordCol-1] == player: #right most col
            if locBoard[coordRow][coordCol-2] == '_':
                return [(coordCol-1, coordRow), (-1,-1)]
            elif locBoard[coordRow][coordCol-2]==opp:
                return [(coordCol-1, coordRow), (coordCol-2, coordRow)]
        elif coordCol == localStartCol+2 and locBoard[coordRow][coordCol-2] == player:
            if locBoard[coordRow][coordCol-1] == '_':
                return [(coordCol-2, coordRow), (-1,-1)]
            elif locBoard[coordRow][coordCol-1] == opp:
                return [(coordCol-2, coordRow), (coordCol-1, coordRow)]

        return None

    """
    checks for two in a row on the curr col for the player at that point
    returns None if no 2-in-a-row, otherwise list of coords, where first is the coord of the second symbol and the second is the coord of the blocking symbol if it exists, (-1, -1) if not
    player = 'X' or 'O'
    opp = opposing player = 'O' or 'X'
    """
    def checkNSSeq(self, locBoard, coord, player, opp, localStartRow):
        coordCol = coord[0]
        coordRow = coord[1]
        if coordRow == localStartRow and locBoard[coordRow+1][coordCol] == player:
            #first row, only check one down (no winner, since checked before this call)
            if locBoard[coordRow+2][coordCol] == '_':
                return [(coordCol, coordRow+1), (-1,-1)]
            elif locBoard[coordRow+2][coordCol] == opp:
                return [(coordCol, coordRow+1), (coordCol, coordRow+2)]
        elif coordRow == localStartRow and locBoard[coordRow+2][coordCol] == player:
            if locBoard[coordRow+1][coordCol] == '_':
                return [(coordCol, coordRow+2), (-1,-1)]
            elif locBoard[coordRow+1][coordCol] == opp:
                return [(coordCol, coordRow+2), (coordCol, coordRow+1)]
        elif coordRow == localStartRow+1: #middle row
            if locBoard[coordRow+1][coordCol] == player and locBoard[coordRow-1][coordCol]=='_':
                return [(coordCol, coordRow+1), (-1,-1)]
            elif locBoard[coordRow-1][coordCol] == player and locBoard[coordRow+1][coordCol]=='_':
                return [(coordCol, coordRow-1), (-1,-1)]
            elif locBoard[coordRow+1][coordCol] == player and locBoard[coordRow-1][coordCol]==opp:
                return [(coordCol, coordRow+1), (coordCol, coordRow-1)]
            elif locBoard[coordRow-1][coordCol] == player and locBoard[coordRow+1][coordCol]==opp:
                return [(coordCol, coordRow-1), (coordCol, coordRow+1)]
        elif coordRow == localStartRow+2 and locBoard[coordRow-1][coordCol]==player: #last row
            if locBoard[coordRow-2][coordCol]=='_':
                return [(coordCol, coordRow-1), (-1,-1)]
            elif locBoard[coordRow-2][coordCol]==opp:
                return [(coordCol, coordRow-1), (coordCol, coordRow-2)]
        elif coordRow == localStartRow+2 and locBoard[coordRow-2][coordCol]==player:
            if locBoard[coordRow-1][coordCol]=='_':
                return [(coordCol, coordRow-2), (-1,-1)]
            elif locBoard[coordRow-1][coordCol] == opp:
                return [(coordCol, coordRow-2), (coordCol, coordRow-1)]
        return None

    """
    checks for two in a row on the curr diagonal
    if in the middle then checks both diagonal directions
    if not on a diagonal or no two in a row, then returns None
    otherwise returns a list of list of the coord.s (only possible for more than one coord if coord is in the center, so could have two), where the first list is a list of coords that complete the 2-in-a-row and the second list is a list of coordinates that block, empty list of none exists
    player = 'X' or 'O'
    opp = opposing player = 'O' or 'X'
    localStart = (localStartCol, localStartRow)
    """
    def checkDiagSeq(self, locBoard, coord, player, opp, localStart):
        #print(locBoard)
        localStartCol = localStart[0]
        localStartRow = localStart[1]
        coordCol = coord[0]
        coordRow = coord[1]
        center = locBoard[localStartRow+1][localStartCol+1]

        if coordRow == localStartRow and coordCol == localStartCol and center == player: #coord is top left
            #coord is top left, second is middle
            if locBoard[coordRow+2][coordCol+2] == '_':
                return [[(localStartCol+1, localStartRow+1)], [(-1,-1)]]
            elif locBoard[coordRow+2][coordCol+2]==opp:
                return [[(localStartCol+1, localStartRow+1)], [(coordCol+2, coordRow+2)]]
        elif coordRow == localStartRow and coordCol == localStartCol and locBoard[localStartRow+2][localStartCol+2] == player:
            #coord is top left and second is bottom right
            if center == '_':
                return [[(localStartCol+2, localStartRow+2)], [(-1,-1)]]
            elif center == opp:
                return [[(localStartCol+2, localStartRow+2)], [(localStartCol+1, localStartRow+1)]]
        elif coordRow == localStartRow and coordCol == localStartCol+2 and center == player: #coord is top right
            #print("ALRIGHTFARHANLETSSEEIFURIGHT")
            #coord is top right and second is middle
            if locBoard[coordRow+2][coordCol-2] == '_':
                return [[(localStartCol+1, localStartRow+1)], [(-1,-1)]]
            elif locBoard[coordRow+2][coordCol-2]==opp:
                return [[(localStartCol+1, localStartRow+1)], [(coordCol-2, coordRow+2)]]
        elif coordRow == localStartRow and coordCol == localStartCol+2 and locBoard[localStartRow+2][localStartCol] == player:
            #coord is top right and second is bottom left
            if center == '_':
                return [[(localStartCol, localStartRow+2)], [(-1,-1)]]
            elif center == opp:
                return [[(localStartCol, localStartRow+2)], [(localStartCol+1, localStartRow+1)]]
        elif coordRow == localStartRow+2 and coordCol == localStartCol and center == player: #coord is bottom left
            if locBoard[localStartRow][localStartCol+2] == '_':
                return [[(localStartCol+1, localStartRow+1)], [(-1,-1)]]
            elif locBoard[localStartRow][localStartCol+2]==opp:
                return [[(localStartCol+1, localStartRow+1)], [(localStartCol+2, localStartRow)]]
        elif coordRow == localStartRow+2 and coordCol == localStartCol and locBoard[localStartRow][localStartCol+2] == player:
            #coord is bottom left and second is top right
            if center == '_':
                return [[(localStartCol+2, localStartRow)], [(-1,-1)]]
            elif center == opp:
                return [[(localStartCol+2, localStartRow)], [(localStartCol+1, localStartRow+1)]]
        elif coordRow == localStartRow+2 and coordCol == localStartCol+2 and center == player: #coord is bottom right
            if locBoard[localStartRow][localStartCol]=='_':
                return [[(localStartCol+1, localStartRow+1)], [(-1,-1)]]
            elif locBoard[localStartRow][localStartCol]==opp:
                return [[(localStartCol+1, localStartRow+1)], [(localStartCol, localStartRow)]]
        elif coordRow == localStartRow+2 and coordCol == localStartCol+2 and locBoard[localStartRow][localStartCol] == player:
            #coord is bottom right and second is top left
            if center == '_':
                return [[(localStartCol, localStartRow)], [(-1,-1)]]
            elif center == opp:
                return [[(localStartCol, localStartRow)], [(localStartCol+1, localStartRow+1)]]
        elif coordRow==localStartRow+1 and coordCol==localStartCol+1: #coord is center
            #print("LOCBOARD AT TOP RIGHT: ", end = "")
            #print((coordRow - 1, coordCol + 1))
            #print("valueeee: ")
            #print(locBoard[coordRow - 1][coordCol+1])
            #print("CENTERCENTERCENTERCENTERCENTERCENTERCENTERCENTERCENTERCENTERCENTERCENTER")
            ret = [[],[]]
            if locBoard[coordRow-1][coordCol-1] == player: #player is top left
                #print("BADBADBADBADBADBADBADBADBAD")
                ret[0].append((coordCol-1, coordRow-1))
                if locBoard[coordRow+1][coordCol+1]==opp: #bottom right
                    ret[1].append((coordCol+1, coordRow+1))
                else:
                    ret[1].append((-1,-1))
            elif locBoard[coordRow-1][coordCol+1] == player: #player is top right
                #print("JUGGAJUICEJUGGAJUICEJUGGA")
                ret[0].append((coordCol+1, coordRow-1))
                if locBoard[coordRow+1][coordCol-1]==opp: #bottom left
                    ret[1].append((coordCol-1, coordRow+1))
                else:
                    ret[1].append((-1,-1))
            elif locBoard[coordRow+1][coordCol-1] == player: #player is bottom left
                ret[0].append((coordCol-1, coordRow+1))
                if locBoard[coordRow-1][coordCol+1]==opp:
                    ret[1].append((coordCol+1, coordRow-1))
                else:
                    ret[1].append((-1,-1))
            elif locBoard[coordRow+1][coordCol+1]==player: #player is bottom right
                ret[0].append((coordCol+1, coordRow+1))
                if locBoard[coordRow-1][coordCol-1]==opp:
                    ret[1].append((coordCol-1, coordRow-1))
                else:
                    ret[1].append((-1,-1))
            #this is in row major order
            return ret

        return [[],[]]




        #END CUSTOM VARIABLES
    def printGameBoard(self):
        """
        This function prints the current game board.
        """
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[:3]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[3:6]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in self.board[6:9]])+'\n')

    def boardPrinter(self, xboard):
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in xboard[:3]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in xboard[3:6]])+'\n')
        print('\n'.join([' '.join([str(cell) for cell in row]) for row in xboard[6:9]])+'\n')
		#print("end.")


    def evaluatePredifined(self, isMaxer):
		#print(isMaxer)
        """
        This function implements the evaluation function for ultimate tic tac toe for predifined agent.
        input args:
        isMax(bool): boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        score(float): estimated utility score for maxPlayer or minPlayer
        """
        #YOUR CODE HERE


        if (not isMaxer):
            #print("HELLO????")
            return self.getOUtility(self.board)
        else:
            return self.getUtility(self.board)


    def evaluateDesigned(self, isMax):
        """
        This function implements the evaluation function for ultimate tic tac toe for your own agent.
        input args:
        isMax(bool): boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        score(float): estimated utility score for maxPlayer or minPlayer
        """
        #YOUR CODE HERE
        if (isMax):
            max = self.winnerMinUtility
            for xboard in self.getNextBoards(self.board, isMax):

                util = self.getSmartUtility(self.board) #change this to getSmartUtility
                if util > max:
                    max = util
            return max

        else:
            min = self.winnerMaxUtility
            for xboard in self.getNextBoards(self.board, isMax):
                util = self.getSmartUtility(self.board) #change this to getSmartUtility
                if util < min:
                    min = util
            return min


    def checkMovesLeft(self):
        """
        This function checks whether any legal move remains on the board.
        output:
        movesLeft(bool): boolean variable indicates whether any legal move remains
                        on the board.
        """
        #YOUR CODE HERE
        xbox = self.getNextPlayBox()[0]
        ybox = self.getNextPlayBox()[1]


        for i in range(3):
            for j in range(3):
                if ((self.board[xbox + i][ybox + j]) == '_'):
                    return True


        return False

    def checkWinner(self):
        #Return termimnal node status for maximizer player 1-win,0-tie,-1-lose
        """
        This function checks whether there is a winner on the board.
        output:
        winner(int): Return 0 if there is no winner.
        Return 1 if maxPlayer is the winner.
        Return -1 if miniPlayer is the winner.
        """
        #YOUR CODE HERE
        #print("HI I AM CHECKWINNER BOARD CURRENTLY LOOKS LIKE")
        #self.printGameBoard()
        #for individual box
        for idx in self.globalIdx:
            curr_i = idx[0]
            curr_j = idx[1]


            #vertical win check
            #print("vertical cehck")
            sum = 0
            for i in range(3):
                sum = 0
                for j in range(3):
                    if self.board[curr_i + i][curr_j + j] == 'X':
                        sum += 1
                    elif self.board[curr_i + i][curr_j + j] == 'O':
                        #-print(sum)
                        sum += -1
                if (sum == 3):
                    return 1 #maxPlayer is winner
                elif (sum == -3):
                    return -1 #minPlayer is winner
                sum = 0
            #print("horizontal check")
            #horizontal win check
            for j in range(3):
                sum = 0
                for i in range(3):
                    if self.board[curr_i + i][curr_j + j] == 'X':
                        sum += 1
                    elif self.board[curr_i + i][curr_j + j] == 'O':
                        sum += -1

                if (sum == 3):
                    return 1 #maxPlayer is winner
                elif(sum <= -3):
                    return -1 #minPlayer is winner


            #diagonal win checks
            #print("diagoanl")
            sum = 0
            for x in range(3):
                if self.board[curr_i + x][curr_j + x] == 'X':
                    sum += 1
                elif self.board[curr_i + x][curr_j + x] == 'O':
                    sum += -1
            if (sum == 3):
                return 1 #maxPlayer is winner
            elif (sum == -3):
                return -1 #minPlayer is winner


            sum = 0
            for x in range(3):
                if self.board[(curr_i + 2 - x)][curr_j + x] == 'X':
                    sum += 1
                elif self.board[(curr_i + 2) - x][curr_j + x] == 'O':
                    sum += -1
                #print(sum)
            if (sum == 3):
                return 1
            elif (sum == -3):
                return -1


        #print("ohno")
        return 0


    def alphabeta(self,depth,currBoardIdx,alpha,beta,isMax):
        #print("alphabeta call")
        #self.explored += 1
        """"
        This function implements alpha-beta algorithm for ultimate tic-tac-toe game.
        input args:
        depth(int): current depth level
        currBoardIdx(int): current local board index
        alpha(float): alpha value
        beta(float): beta value
        isMax(bool):boolean variable indicates whether it's maxPlayer or minPlayer.
                     True for maxPlayer, False for minPlayer
        output:
        bestValue(float):the bestValue that current player may have
        """

        #YOUR CODE HERE
        moveChosen = (-1, -1)
        expand = 0
        if (depth == 3):


            #print("BOARD BEING EVALD")
            #self.printGameBoard()
            self.explored += 1
            if not isMax:
                if self.maxPlayerSmart:
                    # print("calling true function")
                    return self.evaluateDesigned(True)
                else:
                    # print("hello mister")
                    # print(self.evaluatePredifined(True))
                    return self.evaluatePredifined(True)
            else:
                if self.minPlayerSmart:
                    return self.evaluateDesigned(False)
                else:
                    # print("hello mister scott")
                    return self.evaluatePredifined(False)
        elif isMax:
            max_eval =(self.winnerMinUtility * 10) #sentinel value

            for point in self.getNextPoints():
                # print(point)
                expand += 1
                boardCopy = copy.deepcopy(self.board)
                #listCopy = copy.deepcopy(self.movesList)
                self.board[point[0]][point[1]] = 'X'
                pointCopy = copy.deepcopy(self.lastMovePlayed)
                self.lastMovePlayed = point
                nextBox = self.getNextPlayBox()
                max_eval_copy = max_eval
                # print("eval at", point)
                eval = self.alphabeta((depth + 1), nextBox, alpha, beta, False)
                # print(eval)
                self.lastMovePlayed = pointCopy
                self.board = boardCopy
                playBox = self.getNextPlayBox()
                max_eval = max(max_eval, eval)
                alpha = max(alpha, eval)

                """if the child state was better than the previous state, will always be true for the first time called
                so it will always choose a child state.
                """

                #pruning
                if (alpha >= beta):
                    break

                if (max_eval >= max_eval_copy):

                    if (max_eval == max_eval_copy):
                        self_copy_2 = copy.deepcopy(self)
                        self_copy_2.board = copy.deepcopy(boardCopy)
                        #print("wtf", self_copy_2)
                        self_copy_1 = copy.deepcopy(self)
                        self_copy_1.board = copy.deepcopy(boardCopy)
                        self_copy_2.board[point[0]][point[1]] = 'X'
                        self_copy_1.board[moveChosen[0]][moveChosen[1]] = 'X'

                        value1 = self_copy_1.getUtility(self_copy_1.board)
                        value2 = self_copy_2.getUtility(self_copy_2.board)

                        if (value1 < value2 or value2 >= 10000):
                            moveChosen = point
                    else:
                        moveChosen = point


            self.lastMovePlayed = moveChosen
            self.board = boardCopy
            #self.movesList = listCopy
            #print(self.movesList)
            self.board[moveChosen[0]][moveChosen[1]] = 'X'
            #self.movesList.append(copy.deepcopy(moveChosen))
            self.gameBoardList.append(copy.deepcopy(self.board))

            #print("returning max", )
            return max_eval #ALSO STORE SOMEWHERE WHAT NEXT BOARD WAS CHOSEN!!!

        else:
            #print("min call")
            min_eval = (self.winnerMaxUtility * 10) #sentinel value
            for point in self.getNextPoints():
                boardCopy = copy.deepcopy(self.board)
                #listCopy  = copy.deepcopy(self.movesList)
                self.board[point[0]][point[1]] = 'O'
                pointCopy = copy.deepcopy(self.lastMovePlayed)
                self.lastMovePlayed = point
                nextBox = self.getNextPlayBox()
                min_eval_copy = min_eval

                eval = self.alphabeta((depth + 1), nextBox, alpha, beta, True)
                self.lastMovePlayed = pointCopy
                self.board = boardCopy
                #self.movesList = listCopy
                self.board[point[0]][point[1]] = '_'
                min_eval = min(min_eval, eval)
                beta = min(beta, eval)

                #pruning
                if (alpha >= beta):
                    break

                if (min_eval <= min_eval_copy or min_eval <= -10000):
                    if (min_eval == min_eval_copy):
                        self_copy_2 = copy.deepcopy(self)
                        self_copy_2.board = copy.deepcopy(boardCopy)
                        self_copy_1 = copy.deepcopy(self)
                        self_copy_1.board = copy.deepcopy(boardCopy)

                        self_copy_2.board[point[0]][point[1]] = 'O'
                        self_copy_1.board[moveChosen[0]][moveChosen[1]] = 'O'

                        value1 = self_copy_1.getOUtility(self_copy_1.board)
                        value2 = self_copy_2.getOUtility(self_copy_2.board)
                        #self_copy_2.printGameBoard()
                        #print("getOUtility value2", value2)

                        if (value1 > value2 or (value2 <= -10000)):
                            # print("value1, ", value1)
                            # print(moveChosen)
                            # print("value2", value2)
                            # print(point)
                            moveChosen = point
                            break
                    else:
                        moveChosen = point

                # else:
                    # if point == (2,0):
                        # print("min_eval",  min_eval)
                        # print("is not better than", min_eval_copy)
            self.lastMovePlayed = moveChosen
            self.board = boardCopy
            #self.movesList = listCopy
            #self.movesList.append(moveChosen)
            #print(self.movesList)
            self.board[moveChosen[0]][moveChosen[1]] = 'O'
            self.gameBoardList.append(copy.deepcopy(self.board))

            #print("returning min:", min_eval)
            return min_eval


    def minimax(self, depth, currBoardIdx, isMax):
            """"
            This function implements alpha-beta algorithm for ultimate tic-tac-toe game.
            input args:
            depth(int): current depth level
            currBoardIdx(int): current local board index
            alpha(float): alpha value
            beta(float): beta value
            isMax(bool):boolean variable indicates whether it's maxPlayer or minPlayer.
                         True for maxPlayer, False for minPlayer
            output:
            bestValue(float):the bestValue that current player may have
            """

            #YOUR CODE HERE
            moveChosen = (-1, -1)
            expand = 0
            if (depth == 3):


                #print("BOARD BEING EVALD")
                #self.printGameBoard()
                self.explored += 1
                if not isMax:
                    if self.maxPlayerSmart:
                        # print("calling true function")
                        return self.evaluateDesigned(True)
                    else:
                        # print("hello mister")
                        # print(self.evaluatePredifined(True))
                        return self.evaluatePredifined(True)
                else:
                    if self.minPlayerSmart:
                        return self.evaluateDesigned(False)
                    else:
                        # print("hello mister scott")
                        return self.evaluatePredifined(False)
            elif isMax:
                "LMAO?"
                max_eval =(self.winnerMinUtility * 10) #sentinel value

                for point in self.getNextPoints():
                    # print(point)
                    expand += 1
                    boardCopy = copy.deepcopy(self.board)
                    #listCopy = copy.deepcopy(self.movesList)
                    self.board[point[0]][point[1]] = 'X'
                    pointCopy = copy.deepcopy(self.lastMovePlayed)
                    self.lastMovePlayed = point
                    nextBox = self.getNextPlayBox()
                    max_eval_copy = max_eval
                    # print("eval at", point)
                    eval = self.minimax((depth + 1), nextBox, False)
                    # print(eval)
                    self.lastMovePlayed = pointCopy
                    self.board = boardCopy
                    playBox = self.getNextPlayBox()
                    max_eval = max(max_eval, eval)
                    # alpha = max(alpha, eval)

                    """if the child state was better than the previous state, will always be true for the first time called
                    so it will always choose a child state.
                    """

                    #pruning
                    # if (alpha >= beta):
                    #     break

                    if (max_eval > max_eval_copy):
                        #print("max_eval is", max_eval)
                        #print("at ", point)
                        moveChosen = point


                self.lastMovePlayed = moveChosen
                self.board = boardCopy
                #self.movesList = listCopy
                #print(self.movesList)
                self.board[moveChosen[0]][moveChosen[1]] = 'X'
                #self.movesList.append(copy.deepcopy(moveChosen))
                self.gameBoardList.append(copy.deepcopy(self.board))

                #print("returning max", )
                return max_eval #ALSO STORE SOMEWHERE WHAT NEXT BOARD WAS CHOSEN!!!

            else:
                # print("min call")
                min_eval = (self.winnerMaxUtility * 10) #sentinel value
                for point in self.getNextPoints():
                    boardCopy = copy.deepcopy(self.board)
                    #listCopy  = copy.deepcopy(self.movesList)
                    self.board[point[0]][point[1]] = 'O'
                    pointCopy = copy.deepcopy(self.lastMovePlayed)
                    self.lastMovePlayed = point
                    nextBox = self.getNextPlayBox()
                    min_eval_copy = min_eval

                    eval = self.minimax((depth + 1), nextBox, True)
                    self.lastMovePlayed = pointCopy
                    self.board = boardCopy
                    #self.movesList = listCopy
                    self.board[point[0]][point[1]] = '_'
                    min_eval = min(min_eval, eval)
                    # beta = min(beta, eval)

                    #pruning
                    # if (alpha >= beta):
                    #     break

                    if (min_eval < min_eval_copy):
                        # print("min eval is ", min_eval)
                        moveChosen = point

                self.lastMovePlayed = moveChosen
                self.board = boardCopy
                #self.movesList = listCopy
                #self.movesList.append(moveChosen)
                #print(self.movesList)
                self.board[moveChosen[0]][moveChosen[1]] = 'O'
                self.gameBoardList.append(copy.deepcopy(self.board))

                #print("returning min:", min_eval)
                return min_eval






    def playGamePredifinedAgent(self,maxFirst,isMinimaxOffensive,isMinimaxDefensive):
        """
        This function implements the processes of the game of predifined offensive agent vs defensive agent.
        input args:
        maxFirst(bool): boolean variable indicates whether maxPlayer or minPlayer plays first.
                        True for maxPlayer plays first, and False for minPlayer plays first.
        isMinimaxOffensive(bool):boolean variable indicates whether it's using minimax or alpha-beta pruning algorithm for offensive agent.
                        True is minimax and False is alpha-beta.
        isMinimaxOffensive(bool):boolean variable indicates whether it's using minimax or alpha-beta pruning algorithm for defensive agent.
                        True is minimax and False is alpha-beta.
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        bestValue(list of float): list of bestValue at each move
        expandedNodes(list of int): list of expanded nodes at each move
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """
        #YOUR CODE HERE

        self.maxPlayerSmart = False
        self.minPlayerSmart = False
        nextPoints = self.getNextPoints()
        expandedNodes = []
        gameBoards = []
        beginState = copy.deepcopy(self)
        bestMove = []
        bestValue = []

        #print("hello")
        while (len(nextPoints) > 0) and (self.checkWinner() == 0):
            if maxFirst:

                if not isMinimaxOffensive:
                    #print("FIRST")
                    bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, True))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if self.checkWinner():
                        break
                else:
                    bestValue.append(self.minimax(0, self.getNextPlayBox(), True))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if self.checkWinner():
                        break

                if not isMinimaxDefensive:
                    bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, False))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if self.checkWinner():
                        break

                else:
                    bestValue.append(self.minimax(0, self.getNextPlayBox(), False))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if self.checkWinner():
                        break

            else:
                if not isMinimaxDefensive:
                    #print("lmao")
                    bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, False))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if self.checkWinner():
                        break
                else:
                    # print("yo")
                    bestValue.append(self.minimax(0, self.getNextPlayBox(), False))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if self.checkWinner():
                        break

                if not isMinimaxOffensive:
                    # print("HAI ")
                    bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, True))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    # print("lmao")
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if (self.checkWinner()):
                        break
                else:
                    # print("HAI ??")
                    bestValue.append(self.minimax(0, self.getNextPlayBox(), True))
                    gameBoards.append(copy.deepcopy(self.board))
                    bestMove.append(self.lastMovePlayed)
                    #self.printGameBoard()
                    expandedNodes.append(self.explored)
                    self.explored = 0
                    if (self.checkWinner()):
                        break


        #print("expandedNodes")
        for board in gameBoards:
            self.boardPrinter(board)
            #print()
            #print()

        # print(expandedNodes)
        # print()
        # print(bestMove)
        # print(bestValue)
        winner= self.checkWinner()
        return gameBoards, bestMove, expandedNodes, bestValue, winner

    def playGameYourAgent(self):
        self.maxPlayerSmart = False
        self.minPlayerSmart = True
        nextPoints = self.getNextPoints()
        expandedNodes = []
        gameBoards = []
        bestValue = []
        bestMove=[]
        #beginState = copy.deepcopy(self)

        firstRand = random.sample([True, False], 1)
        yRand = random.randint(0,8)
        xRand = random.randint(0,8)

        self.lastMovePlayed = (yRand, xRand)

        maxFirst = firstRand

        while (len(nextPoints) > 0) and (self.checkWinner() == 0):

            if (maxFirst):
                bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, True))
                #self.printGameBoard()
                gameBoards.append(copy.deepcopy(self.board))
                expandedNodes.append(self.explored)
                bestMove.append(self.lastMovePlayed)
                self.explored = 0
                if self.checkWinner():
                    break

                bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, False))
                #self.printGameBoard()
                expandedNodes.append(self.explored)
                bestMove.append(self.lastMovePlayed)
                self.explored = 0
                if self.checkWinner():
                    break
            else:
                bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, True))
                #self.printGameBoard()
                expandedNodes.append(self.explored)
                self.explored = 0
                bestMove.append(self.lastMovePlayed)
                gameBoards.append(copy.deepcopy(self.board))
                if self.checkWinner():
                    break

                bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, False))
                #self.printGameBoard()
                expandedNodes.append(self.explored)
                bestMove.append(self.lastMovePlayed)
                self.explored = 0
                if self.checkWinner():
                    break


        # print("expandedNodes")
        print(expandedNodes)
        #self.printGameBoard()
        winner= self.checkWinner()
        return gameBoards, bestMove, expandedNodes, bestValue, winner




        """
        This function implements the processes of the game of your own agent vs predifined offensive agent.
        input args:
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """
        #YOUR CODE HERE
        bestMove=[]
        gameBoards=[]
        winner=0
        #print(self.board)
        return gameBoards, bestMove, winner


    def playGameHuman(self):
        """
        This function implements the processes of the game of your own agent vs a human.
        output:
        bestMove(list of tuple): list of bestMove coordinates at each step
        gameBoards(list of 2d lists): list of game board positions at each move
        winner(int): 1 for maxPlayer is the winner, -1 for minPlayer is the winner, and 0 for tie.
        """
        #YOUR CODE HERE
        bestMove=[]
        gameBoards=[]
        winner=0
        bestValue = []
        self.maxPlayerSmart = True
        self.minPlayerSmart = True

        while(len(self.getNextPoints()) > 0) and (self.checkWinner() == 0):

            bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, True))
            bestMove.append(self.lastMovePlayed)
            gameBoards.append(copy.deepcopy(self.board))
            self.printGameBoard()
            if (self.checkWinner() != 0):
                break

            print ("enter ycoord input, you can choose from: ",)
            for point in self.getNextPoints():
                print(point[0])
            y_userMove = int(input(""))
            print(("enter xcoord move, you can choose from: "))
            for point in self.getNextPoints():
                print(point[1])
            x_userMove = int(input(""))

            if (y_userMove, x_userMove) in self.getNextPoints():
                self_copy = copy.deepcopy(self)
                bestValue.append(self.alphabeta(0, self.getNextPlayBox(), -1000000, 1000000, True))
                self = self_copy
                self.board[y_userMove][x_userMove] = 'O'
                self.lastMovePlayed = (y_userMove, x_userMove)
                gameBoards.append(copy.deepcopy(self.board))
                bestMove.append(self.lastMovePlayed)
                self.printGameBoard()
                # print("HELLO????")
                # print(self.checkWinner())
                if (self.checkWinner() != 0):
                    break
                # print()
                # print()
            else:
                print("crash lol")
                return None

        winner = self.checkWinner()
        return gameBoards, bestMove, winner

if __name__=="__main__":
    uttt=ultimateTicTacToe()
    wins = 0
    # for i in range(5):
    #      winner = uttt.playGameYourAgent()[4]
    #      if (winner == -1):
    #          #print("YO")
    #          wins += 1
    #      uttt = ultimateTicTacToe()
    # print("wins:",  wins)
    # uttt.playGameYourAgent()[4]
    gameBoards, bestMove, winner = uttt.playGameHuman()
    #gameBoards, bestMove, expandedNodes, bestValue, winner = uttt.playGamePredifinedAgent(True, False, False)
    if winner == 1:
        print("The winner is maxPlayer!!!")
    elif winner == -1:
        print("The winner is minPlayer!!!")
    else:
        print("Tie. No winner:(")
