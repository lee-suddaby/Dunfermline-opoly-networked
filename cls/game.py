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

    def getCurPlayerNum(self): #Returns element in the players array of the current player, rather than a Player object
        return self.cur_player 

    def getCurPlayer(self):
        return self.players[self.cur_player]
    
    def advancePlayer(self): #Next player's turn
        self.cur_player += 1
        self.controller.reset()
        if self.cur_player > len(self.players)-1:
            self.cur_player = 0 #Restart from first player
            if self.autosave: #If game is set to autosave, it does so every time the player loop back to the first player
                self.saveGame()
        if self.players[self.cur_player].getMissTurns() > 0 or self.players[self.cur_player].getActive() == False:
            if self.players[self.cur_player].getMissTurns() > 0:
                self.players[self.cur_player].setMissTurns(self.players[self.cur_player].getMissTurns()-1) #Player is skipped; the number of turns still to be missed decrements
            self.advancePlayer() #Recursively call function to try and advance to the player after the one missing a turn

    def getPlayer(self, p_num): #Return a specific player
        return self.players[p_num]

    def countActivePlayers(self): #Number of players that have not yet gone bankrupt
        ret_count = 0
        for counter in range(len(self.players)): #All players, active or not
            if self.players[counter].getActive():
                ret_count += 1
        return ret_count

    def getBoard(self):
        return self.board

    def getThumbs(self):
        return self.prop_thumbs

    def updateThumbs(self, thumbs): #Replace thumbnails with new, already-generated image
        self.prop_thumbs = thumbs

    def getDie(self, num):
        return self.dice[num]

    def getDiceTotal(self): #Sum score on both dice
        return self.dice[0].getScore() + self.dice[1].getScore()

    def getSavePath(self): 
        return self.save_path

    def updateSavePath(self, new_path):
        self.save_path = new_path

    def getController(self):
        return self.controller

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
            fh.write(cur_player.p_name + ',' + str(cur_player.money) + ',' + str(cur_player.getPos()) + ',' + str(cur_player.getPiece().piece_num) + ',' + str(int(cur_player.hasBogMap)) + ',' + str(cur_player.nextRollMod) + ',' + str(cur_player.turnsToMiss) + ',' + str(int(cur_player.active)) + ',' + str(int(cur_player.inJail)) + '\n')

        for counter in range(self.board.max_pos+1):
            if self.board.getProp(counter).getType() == Prop_Type.NORMAL: #NORMAL properties have different attributes that change in-game
                if self.board.getProp(counter).getOwner() != -1: #Nothing will have changed of the property is not owned
                    #Write all important/changing data for a NORMAL property on a new line
                    fh.write(str(counter) + ',' + str(self.board.getProp(counter).getOwner()) + ',' + str(self.board.getProp(counter).getCH()) + ',' + str(self.board.getProp(counter).getTB()) + ',' + str(int(self.board.getProp(counter).getMortgageStatus())) + '\n')
                    
            if self.board.getProp(counter).getType() == Prop_Type.SCHOOL or self.board.getProp(counter).getType() == Prop_Type.STATION: #SCHOOL and STATION properties have slightly different changing attributes than NORMAL ones
                if self.board.getProp(counter).getOwner() != -1: #Nothing will have changed of the property is not owned
                    #Write all important/changing data for a SCHOOL or STATION property on a new line
                    fh.write(str(counter) + ',' + str(self.board.getProp(counter).getOwner()) + ',' + str(int(self.board.getProp(counter).getMortgageStatus())) + '\n')
                    
        fh.close() #Close file


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