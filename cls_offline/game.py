import numpy as np
import pygame
from .property import Prop_Type

#------------------------------Game Class------------------------------
#Brings all the game data together into one cohesive object that can be controlled more easily than all other data/objects independently
class Game:
    def __init__(self, new_players, new_dice, new_board, new_save, new_auto=True):
        self.players = np.array(new_players) #The 2-6 players of the game
        self.dice = np.array(new_dice) #Game's two dice
        self.cur_player = 0 #Index of current player in he players array
        self.prop_thumbs = None #Will become an image object showing all properties owned by one player
        self.board = new_board
        self.save_path = new_save #location of the game's save file
        self.controller = Game_Controller()
        self.autosave = new_auto
        self.pause = False #Whether the background music is paused of not

    def getCurPlayer(self):
        return self.players[self.cur_player]
    
    def getCurProp(self):
        return self.board.getProp(self.getCurPlayer().player_pos)

    def advancePlayer(self): #Next player's turn
        self.cur_player += 1
        self.controller.reset()
        if self.cur_player > len(self.players)-1:
            self.cur_player = 0 #Restart from first player
            if self.autosave: #If game is set to autosave, it does so every time the player loop back to the first player
                self.saveGame()
        if self.players[self.cur_player].player_turnsToMiss > 0 or self.players[self.cur_player].player_active == False:
            if self.players[self.cur_player].player_turnsToMiss > 0:
                self.players[self.cur_player].setMissTurns(self.players[self.cur_player].player_turnsToMiss - 1) #Player is skipped; the number of turns still to be missed decrements
            self.advancePlayer() #Recursively call function to try and advance to the player after the one missing a turn

    def getPlayer(self, p_num): #Return a specific player
        return self.players[p_num]

    def countActivePlayers(self): #Number of players that have not yet gone bankrupt
        ret_count = 0
        for counter in range(len(self.players)): #All players, active or not
            if self.players[counter].player_active:
                ret_count += 1
        return ret_count

    def getDie(self, num):
        return self.dice[num]

    def getDiceTotal(self): #Sum score on both dice
        return self.dice[0].cur_score + self.dice[1].cur_score

    #Save all data required to restart the game at a later date to the game's save file
    def saveGame(self):
        #',' is used to separate data within lines
        #'\n' is used to identify the end of a line, so that the next lot of data written to the file will be on a new line
        #Booleans are saved as a 0 or 1, where 0 is false and 1 true. This is because bool('False') returns True, meaning that saving them as strings does not allow for them to be read in with any real amount of ease.
        fh = open(self.save_path, 'w')
        fh.write(str(self.cur_player) + ',' + str(len(self.players)) + ',' + str(int(self.autosave)) + '\n') #Save the game class data

        for counter in range(len(self.players)):
            cur_player = self.players[counter]
            #Write all volatile data for the current player to a new line in the file
            fh.write(cur_player.player_name + ',' + str(cur_player.player_money) + ',' + str(cur_player.player_pos) + ',' + str(cur_player.player_piece.piece_num) + ',' + str(int(cur_player.player_hasBogMap)) + ',' + str(cur_player.player_nextRollMod) + ',' + str(cur_player.player_turnsToMiss) + ',' + str(int(cur_player.player_active)) + ',' + str(int(cur_player.player_inJail)) + '\n')

        for counter in range(self.board.max_pos+1):
            if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #NORMAL properties have different attributes that change in-game
                if self.board.getProp(counter).prop_owner != -1: #Nothing will have changed of the property is not owned
                    #Write all important/changing data for a NORMAL property on a new line
                    fh.write(str(counter) + ',' + str(self.board.getProp(counter).prop_owner) + ',' + str(self.board.getProp(counter).C_Houses) + ',' + str(self.board.getProp(counter).T_Blocks) + ',' + str(int(self.board.getProp(counter).mortgage_status)) + '\n')
                    
            if self.board.getProp(counter).prop_type == Prop_Type.SCHOOL or self.board.getProp(counter).prop_type == Prop_Type.STATION: #SCHOOL and STATION properties have slightly different changing attributes than NORMAL ones
                if self.board.getProp(counter).prop_owner != -1: #Nothing will have changed of the property is not owned
                    #Write all important/changing data for a SCHOOL or STATION property on a new line
                    fh.write(str(counter) + ',' + str(self.board.getProp(counter).prop_owner) + ',' + str(int(self.board.getProp(counter).mortgage_status)) + '\n')
                    
        fh.close() #Close file

    def determineRent(self):
        ret_rent = 0
        if self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.NORMAL or self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.SCHOOL or self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.STATION: #If property actually has a rent attrubite(s)
            if self.board.getProp(self.getCurPlayer().player_pos).prop_owner != -1 and self.board.getProp(self.getCurPlayer().player_pos).prop_owner != self.cur_player: #If the property is not unowned (i.e. owned) and not owned by current player
                if self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.NORMAL: #Normal Property
                    ret_rent = self.board.getProp(self.getCurPlayer().player_pos).getRent()
                    if self.board.wholeGroupOwned(self.board.getProp(self.getCurPlayer().player_pos).prop_owner, self.getCurPlayer().player_pos) and self.board.getProp(self.getCurPlayer().player_pos).C_Houses == 0:
                        ret_rent = ret_rent * 2
                elif self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.SCHOOL: #School (dependent on ownership of other schools)
                    ret_rent = self.board.getProp(self.getCurPlayer().player_pos).getRent(self.board, self.board.getProp(self.getCurPlayer().player_pos).prop_owner)
                elif self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.STATION: #Station (depedent on ownership of the other station and the roll of the dice)
                    ret_rent = self.board.getProp(self.getCurPlayer().player_pos).getRent(self.board, self.board.getProp(self.getCurPlayer().player_pos).prop_owner, self.getDiceTotal())
        if self.board.getProp(self.getCurPlayer().player_pos).prop_type == Prop_Type.PAYMENT: #Property that cannot be owned by incurs a charge when landed upon (taxes, etc.)
            ret_rent = self.board.getProp(self.getCurPlayer().player_pos).surcharge
        return ret_rent

    def sendCurPlayerToBog(self):
        self.getCurPlayer().player_pos = self.board.bogside_pos #Move the player
        self.getCurPlayer().player_piece.piece_x = self.players[0].calcPieceX(self.board.bogside_pos, self.board.board_sf)
        self.getCurPlayer().player_piece.piece_y = self.players[0].calcPieceY(self.board.bogside_pos, self.board.board_sf)
        self.getCurPlayer().enterJail()

    #Apply the effects of a certain card
    def applyCardEffects(self):
        card_effects = self.controller.card_effs

        if card_effects[0] != -1: #Player collects money
            self.getCurPlayer().addMoney(card_effects[0])
        if card_effects[1] != -1: #Player pays money
            self.getCurPlayer().spendMoney(card_effects[1])
        if card_effects[2] != -1: #Player gets money from each other player
            pay_counter = 0 #No of players who have individually paid
            for counter in range(6):
                if counter != self.cur_player: #Player cannot pay themselves
                    try:
                        self.getPlayer(counter).spendMoney(card_effects[2])
                        pay_counter += 1
                    except IndexError: #If index does not exist in the game's Players array, no more players are left that can pay, thus the break
                        break
            self.getCurPlayer().addMoney(pay_counter * card_effects[2]) #Credit the player as many lots of money as players who paid it
        if card_effects[3] != -1: #Miss a number of turns
            self.getCurPlayer().setMissTurns(card_effects[3])
        if card_effects[4] != -1: #Move a number of spaces
            self.getCurPlayer().movePlayer(card_effects[4], self.board)
            self.getCurPlayer().player_piece.piece_x = self.getCurPlayer().calcPieceX(self.getCurPlayer().player_pos, self.board.board_sf)
            self.getCurPlayer().player_piece.piece_y = self.getCurPlayer().calcPieceY(self.getCurPlayer().player_pos, self.board.board_sf)

            #Determine rent if applicable
            self.controller.turn_rent = self.determineRent()

            if self.controller.turn_rent != 0:
                self.getCurPlayer().spendMoney(self.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if self.board.getProp(self.getCurPlayer().player_pos).prop_type != Prop_Type.PAYMENT:
                    self.getPlayer(self.board.getProp(self.getCurPlayer().player_pos).prop_owner).addMoney(self.controller.turn_rent)
        if card_effects[5] != -1: #Move to a certain spot (and collect money if passing Job Centre)
            orig_pos = self.getCurPlayer().player_pos
            self.getCurPlayer().player_pos = card_effects[5]
            self.getCurPlayer().player_piece.piece_x = self.getCurPlayer().calcPieceX(self.getCurPlayer().player_pos, self.board.board_sf)
            self.getCurPlayer().player_piece.piece_y = self.getCurPlayer().calcPieceY(self.getCurPlayer().player_pos, self.board.board_sf)
            if self.getCurPlayer().player_pos < orig_pos: #Means player must have 'passed' the Job Centre
                self.getCurPlayer().addMoney(self.board.JC_Money)

            #Determine rent if applicable
            self.controller.turn_rent = self.determineRent()

            if self.controller.turn_rent != 0:
                self.getCurPlayer().spendMoney(self.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if self.board.getProp(self.getCurPlayer().player_pos).prop_type != Prop_Type.PAYMENT:
                    self.getPlayer(self.board.getProp(self.getCurPlayer().player_pos).prop_owner).addMoney(self.controller.turn_rent)
        if card_effects[6] != -1: #Move to a certain spot (but do not collect money if passing Job Centre)
            self.getCurPlayer().player_pos = card_effects[6]
            self.getCurPlayer().player_piece.piece_x = self.getCurPlayer().calcPieceX(self.getCurPlayer().player_pos, self.board.board_sf)
            self.getCurPlayer().player_piece.piece_y = self.getCurPlayer().calcPieceY(self.getCurPlayer().player_pos, self.board.board_sf)

            #Determine rent if applicable
            self.controller.turn_rent = self.determineRent()

            if self.controller.turn_rent != 0:
                self.getCurPlayer().spendMoney(self.controller.turn_rent) #Decrease the player's money and credit the owner of the property that amount
                if self.board.getProp(self.getCurPlayer().player_pos).prop_type != Prop_Type.PAYMENT:
                    self.getPlayer(self.board.getProp(self.getCurPlayer().player_pos).prop_owner).addMoney(self.controller.turn_rent)
        if card_effects[7] != -1: #Go to Bogside
            self.sendCurPlayerToBog()
        if card_effects[8] != -1: #Collect a Map out of Bogside
            self.getCurPlayer().giveBogMap()
        if card_effects[9] != -1: #Pay a certain amount of money for each Council House and Tower Block
            to_pay = 0
            for counter in range(self.board.max_pos+1):
                if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                    if self.board.getProp(counter).prop_owner == self.cur_player: #The current property is owned by this player
                        to_pay += card_effects[9] * (self.board.getProp(counter).C_Houses + self.board.getProp(counter).T_Blocks) #Sum the number of CH and TB
            self.getCurPlayer().spendMoney(to_pay)
        if card_effects[10] != -1: #Next dice roll's value is decreased
            self.getCurPlayer().setRollMod(card_effects[10])
        if card_effects[11] != -1: #Pay a certain amount of money for each Council House only
            to_pay = 0
            for counter in range(self.board.max_pos+1):
                if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                    if self.board.getProp(counter).prop_owner == self.cur_player: #The current property is owned by this player
                        to_pay += card_effects[11] * self.board.getProp(counter).C_Houses #Sum the number of CH
            self.getCurPlayer().spendMoney(to_pay)
        if card_effects[12] != -1: #Pay a certain amount of money for each Tower Block only
            to_pay = 0
            for counter in range(self.board.max_pos+1):
                if self.board.getProp(counter).prop_type == Prop_Type.NORMAL: #Only NORMAL properties acutually possess these upgrades
                    if self.board.getProp(counter).prop_owner == self.cur_player: #The current property is owned by this player
                        to_pay += card_effects[12] * self.board.getProp(counter).T_Blocks #Sum the number of TB
            self.getCurPlayer().spendMoney(to_pay)


#------------------------------Game_Controller Class------------------------------
#Used for storing the miscellaneous variables needed for controlling a player taking their turn
#Having them stored as part of the Game class means that moving to another screen does not allow the current player to restart their turn
class Game_Controller:
    def __init__(self):
        self.player_rolled = False #False if the player may roll
        self.card_used = True #Is only false if a card is available for use. True even if a card has not been drawn during a particular turn
        self.may_buy = False #True is player can buy a buyable property if they are on it
        self.turn_rent = 0
        self.cur_card = None #Pot Luck or Council Chest card drawn on a particular turn
        self.cur_doubles = 0
        self.roll_img1 = None #First dice image
        self.roll_img2 = None #Second dice image
        self.card_effs = [] #Integer effects of cur_card
        self.card_texts = [] #pygame-rendered texts telling the user the effects

    def reset(self):
        self.player_rolled = False
        self.card_used = True
        self.may_buy = False
        self.turn_rent = 0
        self.cur_card = None
        self.cur_doubles = 0
        self.roll_img1 = None
        self.roll_img2 = None
        self.card_effs = []
        self.card_texts = []