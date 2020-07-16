#------------------------------Game Player Class------------------------------
#All data for a game player and its associated piece
class Player:
    #Constructor for Player class
    #I'm going to guess this is relatively self-explanatory - it is called when the class in instantiated (creating an object) and sets up the instance variables of the new object
    def __init__(self, initial_money, new_piece, new_pos, new_name, new_in_jail=False, new_active=True):
        #Last 2 parameters are optional so they can be changed when loading in data, for example
        self.player_pos = new_pos
        self.player_piece_num = new_piece
        self.player_name = new_name
        self.player_money = initial_money
        self.player_inJail = new_in_jail
        self.player_active = new_active
        self.player_nextRollMod = 1 #The reciprocal of this is used if a Card decreases the movement value of this player's next roll of the dice
        self.player_turnsToMiss = 0 #Number of turns they still have to come that they may not move for
        self.player_hasBogMap = False #Will become true if they collect a 'Map out of Bogside'
        self.player_x = self.calcPieceX(self.player_pos)
        self.player_y = self.calcPieceY(self.player_pos)
    
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

        #Determine the x and y coordinates of a player's token based on which property of the board it is occupying
    #The calculations were based off of testing that used linear regression to find an 'optimal' relationship between board position and coordinate positions
    #Scale factor (sf) is used so board size can easily be changed, as calculations were created with a 768x768 board
    def calcPieceX(self, pos, sf):
        p_x = 0
        if 10 <= pos <= 20:
            p_x = 10
        elif pos == 0 or pos >= 30:
            p_x = 710
        elif pos < 10:
            p_x = 666 - 61*pos
        elif 20 < pos < 30:
            p_x = 61*pos - 1168
        return p_x * sf

    def calcPieceY(self, pos, sf):
        p_y = 0
        if 0 <= pos <= 10:
            p_y = 710
        elif 20 <= pos <= 30:
            p_y = 10
        elif 10 < pos < 20:
            p_y = 1281 - 61*pos
        elif 30 < pos:
            p_y = 61*pos - 1767
        return p_y * sf