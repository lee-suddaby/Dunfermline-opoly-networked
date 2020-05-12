from .player_piece import Player_Piece

#------------------------------Game Player Class------------------------------
#All data for a game player and its associated piece
class Player:
    #Constructor for Player class
    #I'm going to guess this is relatively self-explanatory - it is called when the class in instantiated (creating an object) and sets up the instance variables of the new object
    def __init__(self, initial_money, new_piece, new_pos, new_name, new_in_jail=False, new_active=True):
        #Last 2 parameters are optional so they can be changed when loading in data, for example
        self.player_pos = new_pos
        self.player_piece = new_piece
        self.player_name = new_name
        self.player_money = initial_money
        self.player_inJail = new_in_jail
        self.player_active = new_active
        self.player_nextRollMod = 1 #The reciprocal of this is used if a Card decreases the movement value of this player's next roll of the dice
        self.player_turnsToMiss = 0 #Number of turns they still have to come that they may not move for
        self.player_hasBogMap = False #Will become true if they collect a 'Map out of Bogside'
    
    def spendMoney(self, amount):
        self.player_money = self.player_money - amount

    def addMoney(self, amount):
        self.player_money = self.player_money + amount

    def deactivate(self):
        self.player_active = False

    def enterJail(self):
        self.player_inJail = True

    def leaveJail(self):
        self.player_inJail = False
        
    def movePlayer(self, movePos, board):
        self.player_pos = self.player_pos + int(movePos/self.player_nextRollMod) #Same as movePos * (1/nextRollMod)
        self.player_nextRollMod = 1 #Effects are only ever valid for one turn
        if self.player_pos > board.max_pos:
            self.player_pos = self.player_pos - (board.max_pos + 1)
            self.player_money = self.player_money + board.JC_Money #If player passes Job Centre, the collect the requisite amount of money

    def setMissTurns(self, num):
        self.player_turnsToMiss = num

    def setRollMod(self, newMod):
        self.player_nextRollMod = newMod

    def giveBogMap(self):
        self.player_hasBogMap = True

    def useBogMap(self):
        self.player_hasBogMap = False