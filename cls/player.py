from .player_piece import Player_Piece

#------------------------------Game Player Class------------------------------
#All data for a game player and its associated piece
class Player:
    #Constructor for Player class
    #I'm going to guess this is relatively self-explanatory - it is called when the class in instantiated (creating an object) and sets up the instance variables of the new object
    def __init__(self, initial_money, new_piece, new_pos, new_name, new_in_jail=False, new_active=True):
        #Last 2 parameters are optional so they can be changed when loading in data, for example
        self.board_pos = new_pos
        self.piece = new_piece
        self.p_name = new_name
        self.money = initial_money
        self.inJail = new_in_jail
        self.active = new_active
        self.nextRollMod = 1 #The reciprocal of this is used if a Card decreases the movement value of this player's next roll of the dice
        self.turnsToMiss = 0 #Number of turns they still have to come that they may not move for
        self.hasBogMap = False #Will become true if they collect a 'Map out of Bogside'

    def getPos(self):
        return self.board_pos

    def setPos(self, newPos):
        self.board_pos = newPos
        
    def getName(self):
        return self.p_name
    
    def getMoney(self):
        return self.money

    def spendMoney(self, amount):
        self.money = self.money - amount

    def addMoney(self, amount):
        self.money = self.money + amount

    def getPiece(self):
        return self.piece
    
    def getActive(self):
        return self.active

    def deactivate(self):
        self.active = False

    def getInJail(self):
        return self.inJail

    def enterJail(self):
        self.inJail = True

    def leaveJail(self):
        self.inJail = False
        
    def movePlayer(self, movePos, board):
        self.board_pos = self.board_pos + int(movePos/self.nextRollMod) #Same as movePos * (1/nextRollMod)
        self.nextRollMod = 1 #Effects are only ever valid for one turn
        if self.board_pos > board.max_pos:
            self.board_pos = self.board_pos - (board.max_pos + 1)
            self.money = self.money + board.JC_money #If player passes Job Centre, the collect the requisite amount of money

    def setMissTurns(self, num):
        self.turnsToMiss = num

    def getMissTurns(self):
        return self.turnsToMiss
    
    def setRollMod(self, newMod):
        self.nextRollMod = newMod

    def getHasMap(self):
        return self.hasBogMap

    def giveBogMap(self):
        self.hasBogMap = True

    def useBogMap(self):
        self.hasBogMap = False